using System.Security.Cryptography;
using System.Text.Json.Nodes;

namespace Confectory.Core;

// Only a target which explicitly promises relocatable final artifacts can
// reuse a published link. Every new build still gets its own output directory,
// current report and normal plan/compile/source validation.
internal sealed class FinalLinkReuse(string project,string key,string input,string mode,string dotnet,
    Dictionary<string,string> expected,Dictionary<string,string> references)
{
    private const string ProofName="link-proof.json";
    private const string ReportName="build-report.json";
    private const string Format="dotnet-final-link-v1";
    private static string Hash(string path)
    {
        using var stream=File.OpenRead(path);return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
    }
    private static bool Recoverable(Exception ex)=>ex is IOException or UnauthorizedAccessException or System.Text.Json.JsonException or InvalidOperationException or ArgumentException or FormatException or NullReferenceException or BuildError;
    private static bool NoLinks(string path)
    {
        for(FileSystemInfo? node=new FileInfo(Path.GetFullPath(path));node is not null;node=node is FileInfo file?file.Directory:((DirectoryInfo)node).Parent)
            if(node.LinkTarget is not null)return false;
        return true;
    }
    internal static FinalLinkReuse? Prepare(TargetTool tool,string project,string key,string work,string[] references,bool presentation)
    {
        try
        {
            string? mode=tool.Info["mode"]?.ToString(),dotnet=tool.Info["dotnet"]?.ToString();
            if(tool.Info["linkReuse"]?.ToString()!="dotnet-relocatable-v1"||mode is not ("linux" or "portable")||
                string.IsNullOrEmpty(dotnet)||!Path.IsPathFullyQualified(dotnet)||!File.Exists(dotnet))return null;
            var expected=new Dictionary<string,string>(StringComparer.Ordinal);
            var inputs=new Dictionary<string,string>(StringComparer.Ordinal);
            void Add(string relative,string hash)
            {
                if(expected.TryGetValue(relative,out var prior)&&prior!=hash)throw new InvalidOperationException("Conflicting final link input file");
                expected[relative]=hash;
            }
            Add("Bindings.cs",Hash(Path.Combine(work,"Bindings.cs")));
            foreach(string name in presentation?new[]{"public-linkage.json",ConnectionPresentationResource.Name}:new[]{"public-linkage.json"})
            {
                string hash=Hash(Path.Combine(work,"sources",name));Add("sources/"+name,hash);Add(name,hash);
            }
            foreach(string path in references)
            {
                string hash=Hash(path);inputs[path]=hash;Add(Path.GetFileName(path),hash);
            }
            string identity=JsonData.Digest(new object[]{Format,project,key,tool.Identity,tool.Target,mode,dotnet,Hash(dotnet),
                expected.OrderBy(p=>p.Key,StringComparer.Ordinal).ToArray(),inputs.OrderBy(p=>p.Key,StringComparer.Ordinal).ToArray()});
            return new(project,key,identity,mode,dotnet,expected,inputs);
        }
        catch(Exception ex) when(Recoverable(ex)){return null;}
    }
    // The actual target result for this explicitly supported relocation
    // profile is fixed. Never execute a command taken from a cache manifest.
    internal JsonObject Result(string folder)
    {
        string app=Path.Combine(folder,"Confectory.App.dll");
        var artifacts=new JsonObject{["application"]=app,["runtimeconfig"]=Path.Combine(folder,"Confectory.App.runtimeconfig.json"),["publicCatalog"]=Path.Combine(folder,"public-linkage.json")};
        JsonArray run;
        if(mode=="linux"){string launcher=Path.Combine(folder,"run");artifacts["launcher"]=launcher;run=new JsonArray(launcher);}
        else run=new JsonArray(dotnet,app);
        return new JsonObject{["protocol"]=1,["ok"]=true,["artifacts"]=artifacts,["run"]=run};
    }
    private bool FreshReferences()=>references.All(p=>Hash(p.Key)==p.Value);
    private static string Relative(string root,string path)=>Path.GetRelativePath(root,path).Replace('\\','/');
    private JsonArray Snapshot(string folder)
    {
        if(!NoLinks(folder))throw new IOException("Linked output path");
        var rows=new List<(string Path,string Hash,int? Mode)>();long bytes=0;
        void Visit(DirectoryInfo directory)
        {
            foreach(var entry in directory.EnumerateFileSystemInfos())
            {
                if(entry.LinkTarget is not null)throw new IOException("Linked output member");
                if(entry is DirectoryInfo child){if(Relative(folder,child.FullName)!="sources")throw new IOException("Unexpected output directory");Visit(child);continue;}
                if(entry is not FileInfo file)throw new IOException("Unsupported output member");
                string relative=Relative(folder,file.FullName);
                if(relative is ProofName or ReportName)continue;
                if(!expected.ContainsKey(relative)&&relative is not ("Confectory.App.dll" or "Confectory.App.runtimeconfig.json")&&!(mode=="linux"&&relative=="run"))throw new IOException("Unexpected final output member");
                bytes=checked(bytes+file.Length);
                if(rows.Count>=4096||bytes>512L*1024*1024)throw new IOException("Final link reuse budget");
                rows.Add((relative,Hash(file.FullName),OperatingSystem.IsWindows()?null:(int)File.GetUnixFileMode(file.FullName)));
            }
        }
        Visit(new DirectoryInfo(folder));
        return new JsonArray(rows.OrderBy(row=>row.Path,StringComparer.Ordinal).Select(row=>(JsonNode)new JsonObject{["path"]=row.Path,["hash"]=row.Hash,["mode"]=row.Mode}).ToArray());
    }
    private bool ValidFiles(JsonArray files)
    {
        var map=files.ToDictionary(row=>row!["path"]!.GetValue<string>(),row=>row!["hash"]!.GetValue<string>(),StringComparer.Ordinal);
        if(!expected.All(p=>map.TryGetValue(p.Key,out var hash)&&hash==p.Value))return false;
        if(!map.ContainsKey("Confectory.App.dll")||!map.ContainsKey("Confectory.App.runtimeconfig.json"))return false;
        if(mode=="linux")
        {
            var launcher=files.SingleOrDefault(row=>row?["path"]?.ToString()=="run");
            if(launcher is null||launcher["mode"]?.GetValue<int>() is not int permissions||(permissions&(int)UnixFileMode.UserExecute)==0)return false;
        }
        return true;
    }
    internal bool TryRestore(string outputRoot,string destination)
    {
        bool restored=false;
        try
        {
            string latestPath=Path.Combine(outputRoot,"latest.json");
            if(!NoLinks(latestPath))return false;
            var latest=JsonNode.Parse(File.ReadAllText(latestPath))!.AsObject();
            if(latest["key"]?.ToString()!=key||latest["output"]?.GetValue<string>() is not string old)return false;
            old=Path.GetFullPath(old);
            if(!string.Equals(Path.GetDirectoryName(old),Path.GetFullPath(outputRoot),OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal)||
                !System.Text.RegularExpressions.Regex.IsMatch(Path.GetFileName(old),"^"+key+"-[0-9a-f]{12}$")||!NoLinks(old))return false;
            string proofPath=Path.Combine(old,ProofName);
            if(!NoLinks(proofPath))return false;
            var proof=JsonNode.Parse(File.ReadAllText(proofPath))!.AsObject();
            if(proof["format"]?.ToString()!=Format||proof["input"]?.ToString()!=input||proof["project"]?.ToString()!=project||proof["files"] is not JsonArray files||
                proof["checksum"]?.ToString()!=JsonData.Digest(files)||!ValidFiles(files)||!JsonNode.DeepEquals(files,Snapshot(old)))return false;
            Directory.CreateDirectory(destination);
            foreach(var row in files)
            {
                string relative=row!["path"]!.GetValue<string>(),source=PackPaths.Owned(old,relative),target=PackPaths.Owned(destination,relative);
                Directory.CreateDirectory(Path.GetDirectoryName(target)!);
                File.Copy(source,target);
                if(!OperatingSystem.IsWindows())File.SetUnixFileMode(target,(UnixFileMode)row["mode"]!.GetValue<int>());
            }
            if(!JsonNode.DeepEquals(files,Snapshot(destination))||!FreshReferences())return false;
            restored=true;return true;
        }
        catch(Exception ex) when(Recoverable(ex)){return false;}
        finally{if(!restored&&Directory.Exists(destination)){try{Directory.Delete(destination,true);}catch(Exception ex) when(Recoverable(ex)){}}}
    }
    internal void TryWriteProof(string work,JsonObject result)
    {
        try
        {
            var expectedResult=Result(work);
            if(!JsonNode.DeepEquals(result["run"],expectedResult["run"])||!JsonNode.DeepEquals(result["artifacts"],expectedResult["artifacts"])||!FreshReferences())return;
            var files=Snapshot(work);if(!ValidFiles(files))return;
            JsonData.AtomicWrite(Path.Combine(work,ProofName),new{format=Format,project,input,files,checksum=JsonData.Digest(files)});
        }
        catch(Exception ex) when(Recoverable(ex)){/* Optional reuse must not prevent a successful build. */}
    }
}
