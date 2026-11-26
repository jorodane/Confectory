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
    private const string Format="dotnet-final-link-v2";
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
            if(references.Select(Path.GetFileName).Distinct(StringComparer.Ordinal).Count()!=references.Length)return null;
            // Final bindings are generated; reference filenames/bytes in the actual
            // compiler order, not cache-directory names, are the relocation boundary.
            string identity=JsonData.Digest(new object[]{Format,tool.Identity,tool.Target,mode,dotnet,Hash(dotnet),
                expected.OrderBy(p=>p.Key,StringComparer.Ordinal).ToArray(),
                references.Select(path=>new[]{Path.GetFileName(path),inputs[path]}).ToArray(),
                presentation&&Path.Combine(work,"sources",ConnectionPresentationResource.Name).Contains(',')});
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
    private static string Checksum(string owner,string input,JsonArray files)=>JsonData.Digest(new object[]{Format,owner,input,files});
    private static bool SamePath(string left,string right)=>string.Equals(Path.GetFullPath(left),Path.GetFullPath(right),OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal);
    private static JsonObject ReadProof(string folder)
    {
        string path=Path.Combine(folder,ProofName);
        if(!NoLinks(path)||new FileInfo(path).Length>1048576)throw new IOException("Invalid link proof location");
        var proof=JsonNode.Parse(File.ReadAllText(path))!.AsObject();
        if(proof["format"]?.ToString()!=Format||proof["files"] is not JsonArray files||
            proof["checksum"]?.ToString()!=Checksum(proof["project"]!.GetValue<string>(),proof["input"]!.GetValue<string>(),files))
            throw new IOException("Invalid link proof");
        return proof;
    }
    private static void CopyFiles(string old,string destination,JsonArray files)
    {
        Directory.CreateDirectory(destination);
        foreach(var row in files)
        {
            string relative=row!["path"]!.GetValue<string>(),source=PackPaths.Owned(old,relative),target=PackPaths.Owned(destination,relative);
            Directory.CreateDirectory(Path.GetDirectoryName(target)!);
            File.Copy(source,target);
            if(!OperatingSystem.IsWindows())File.SetUnixFileMode(target,(UnixFileMode)row["mode"]!.GetValue<int>());
        }
    }
    private bool RestoreFolder(string old,string destination)
    {
        bool restored=false;
        try
        {
            var proof=ReadProof(old);var files=proof["files"]!.AsArray();
            if(proof["project"]?.ToString()!=project||proof["input"]?.ToString()!=input||!ValidFiles(files)||!JsonNode.DeepEquals(files,Snapshot(old)))return false;
            CopyFiles(old,destination,files);
            if(!JsonNode.DeepEquals(files,Snapshot(destination))||!FreshReferences())return false;
            restored=true;return true;
        }
        catch(Exception ex) when(Recoverable(ex)){return false;}
        finally{if(!restored&&Directory.Exists(destination)){try{Directory.Delete(destination,true);}catch(Exception ex) when(Recoverable(ex)){}}}
    }
    private static string? PublishedFolder(string outputRoot,string? key)
    {
        string latestPath=Path.Combine(outputRoot,"latest.json");
        if(!NoLinks(latestPath))return null;
        var latest=JsonNode.Parse(File.ReadAllText(latestPath))!.AsObject();
        string? actualKey=latest["key"]?.ToString(),old=latest["output"]?.GetValue<string>();
        if(actualKey is null||!System.Text.RegularExpressions.Regex.IsMatch(actualKey,"^[0-9a-f]{64}$")||key is not null&&actualKey!=key||old is null)return null;
        old=Path.GetFullPath(old);
        return SamePath(Path.GetDirectoryName(old)!,outputRoot)&&System.Text.RegularExpressions.Regex.IsMatch(Path.GetFileName(old),"^"+actualKey+"-[0-9a-f]{12}$")&&NoLinks(old)?old:null;
    }
    internal bool TryRestore(string outputRoot,string destination,out bool confirmed)
    {
        confirmed=false;
        try{string? old=PublishedFolder(outputRoot,key);if(old is not null&&RestoreFolder(old,destination))return true;}
        catch(Exception ex) when(Recoverable(ex)){}
        try
        {
            string root=Path.Combine(outputRoot,"confirmed-link"),pointer=Path.Combine(root,"latest.json");
            if(!NoLinks(pointer))return false;
            string id=JsonNode.Parse(File.ReadAllText(pointer))!["id"]!.GetValue<string>();
            if(!Guid.TryParseExact(id,"N",out _))return false;
            confirmed=RestoreFolder(Path.Combine(root,id),destination);return confirmed;
        }
        catch(Exception ex) when(Recoverable(ex)){return false;}
    }
    // This is called only after a successful source CAS by ConfirmReviewed.
    // Retention is optional, never publishes an executable or changes latest Run.
    // The next ordinary Build recalculates all authoritative inputs independently.
    internal static bool RetainConfirmed(string original,string candidate,string target)
    {
        string? staging=null;
        try
        {
            original=Path.GetFullPath(original);candidate=Path.GetFullPath(candidate);
            string owner=Path.GetDirectoryName(original)!,candidateRoot=Path.GetDirectoryName(candidate)!;
            if(!Guid.TryParseExact(Path.GetFileName(candidateRoot),"N",out _)||
                !SamePath(Path.GetDirectoryName(candidateRoot)!,Path.Combine(owner,".confectory","candidates"))||
                Path.GetFileName(original)!=Path.GetFileName(candidate)||!NoLinks(original)||!NoLinks(candidate))return false;
            var live=new Parser(File.ReadAllText(original),original).ParseManifest();
            var copy=new Parser(File.ReadAllText(candidate),candidate).ParseManifest();
            if(live.Kind!="project"||copy.Kind!="project"||live.Namespace!=copy.Namespace||!live.Targets.ContainsKey(target)||!copy.Targets.ContainsKey(target))return false;
            string candidateOutputs=PackPaths.Owned(Path.Combine(candidateRoot,".confectory","outputs"),target);
            string? old=PublishedFolder(candidateOutputs,null);if(old is null)return false;
            var report=JsonNode.Parse(File.ReadAllText(Path.Combine(candidateOutputs,"latest.json")))!.AsObject();
            string? mode=report["tool"]?["mode"]?.ToString(),dotnet=report["tool"]?["dotnet"]?.ToString();
            if(mode is not ("linux" or "portable")||string.IsNullOrEmpty(dotnet)||report["tool"]?["linkReuse"]?.ToString()!="dotnet-relocatable-v1")return false;
            var proof=ReadProof(old);var files=proof["files"]!.AsArray();
            if(proof["project"]?.ToString()!=candidate)return false;
            string input=proof["input"]!.GetValue<string>();
            var expected=files.Where(row=>row!["path"]!.ToString() is not ("Confectory.App.dll" or "Confectory.App.runtimeconfig.json" or "run"))
                .ToDictionary(row=>row!["path"]!.ToString(),row=>row!["hash"]!.ToString(),StringComparer.Ordinal);
            // Retain only ordinary known generated source/resources and root DLL copies.
            if(expected.Keys.Any(path=>path is not ("Bindings.cs" or "public-linkage.json" or "sources/public-linkage.json" or "connection-preview-v1.json" or "sources/connection-preview-v1.json")
                &&(Path.GetFileName(path)!=path||!path.EndsWith(".dll",StringComparison.Ordinal))))return false;
            var reuse=new FinalLinkReuse(original,"",input,mode,dotnet,expected,new());
            if(!reuse.ValidFiles(files)||!JsonNode.DeepEquals(files,reuse.Snapshot(old)))return false;
            string root=Path.Combine(PackPaths.Owned(Path.Combine(owner,".confectory","outputs"),target),"confirmed-link");
            if(!NoLinks(root))return false;
            Directory.CreateDirectory(root);
            string id=Guid.NewGuid().ToString("N"),dest=Path.Combine(root,id);staging=dest+".pending";
            CopyFiles(old,staging,files);if(!JsonNode.DeepEquals(files,reuse.Snapshot(staging)))return false;
            JsonData.AtomicWrite(Path.Combine(staging,ProofName),new{format=Format,project=original,input,files,checksum=Checksum(original,input,files)});
            Directory.Move(staging,dest);staging=null;
            string pointer=Path.Combine(root,"latest.json");string? prior=null;
            try{if(NoLinks(pointer))prior=JsonNode.Parse(File.ReadAllText(pointer))?["id"]?.ToString();}catch(Exception ex) when(Recoverable(ex)){}
            JsonData.AtomicWrite(pointer,new{id});
            if(prior is not null&&prior!=id&&Guid.TryParseExact(prior,"N",out _)&&NoLinks(Path.Combine(root,prior)))
                try{Directory.Delete(Path.Combine(root,prior),true);}catch(Exception ex) when(Recoverable(ex)){}
            return true;
        }
        catch(Exception ex) when(Recoverable(ex)){return false;}
        finally{if(staging is not null&&Directory.Exists(staging))try{Directory.Delete(staging,true);}catch(Exception ex) when(Recoverable(ex)){}}
    }
    internal void TryWriteProof(string work,JsonObject result)
    {
        try
        {
            var expectedResult=Result(work);
            if(!JsonNode.DeepEquals(result["run"],expectedResult["run"])||!JsonNode.DeepEquals(result["artifacts"],expectedResult["artifacts"])||!FreshReferences())return;
            var files=Snapshot(work);if(!ValidFiles(files))return;
            JsonData.AtomicWrite(Path.Combine(work,ProofName),new{format=Format,project,input,files,checksum=Checksum(project,input,files)});
        }
        catch(Exception ex) when(Recoverable(ex)){/* Optional reuse must not prevent a successful build. */}
    }
}
