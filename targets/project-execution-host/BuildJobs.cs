using System.Diagnostics;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json.Nodes;
using Confectory.Core;

internal static class BuildJobs
{
    static readonly StringComparison Paths = OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal;
    static bool Terminal(string state) => state is "built" or "failed" or "stopped";
    static string Hash(string path) { using var stream=File.OpenRead(path);return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant(); }
    static string Text(JsonNode row,string key) => row[key]!.GetValue<string>();
    static void Owned(string root,string path)
    {
        string relative=Path.GetRelativePath(root,path);
        if(Path.IsPathRooted(relative)||relative==".."||relative.StartsWith(".."+Path.DirectorySeparatorChar,StringComparison.Ordinal))throw new ArgumentException("Build job path escapes owner");
        for(FileSystemInfo? item=new FileInfo(path);item is not null;item=item is FileInfo f?f.Directory:((DirectoryInfo)item).Parent)
        {
            if(item.LinkTarget is not null)throw new ArgumentException("Build job symbolic link refused");
            if(string.Equals(item.FullName,root,Paths))break;
        }
    }
    static FileStream Lease(string root,string path,int seconds)
    {
        Owned(root,path);Directory.CreateDirectory(Path.GetDirectoryName(path)!);var timer=Stopwatch.StartNew();
        while(true){try{return new FileStream(path,FileMode.OpenOrCreate,FileAccess.ReadWrite,FileShare.None);}catch(IOException){if(timer.Elapsed.TotalSeconds>seconds)throw new TimeoutException("Build job lease timeout");Thread.Sleep(20);}}
    }
    static void Write(string root,string path,JsonObject row,bool create=false)
    {
        Owned(root,path);string text=row.ToJsonString();if(text.Length>2097152)throw new ArgumentException("Build job metadata budget");
        string temporary=path+"."+Guid.NewGuid().ToString("N")+".pending";
        try{File.WriteAllText(temporary,text,new UTF8Encoding(false));File.Move(temporary,path,!create);}finally{if(File.Exists(temporary))File.Delete(temporary);}
    }
    static JsonObject Read(string root,string project,string job)
    {
        if(!Guid.TryParseExact(job,"N",out _))throw new ArgumentException("Explicit build job ID required");
        string path=Path.Combine(root,".confectory","build-jobs",job,"job.json");Owned(root,path);
        if(!File.Exists(path)||new FileInfo(path).Length>2097152)throw new ArgumentException("Build job metadata unavailable");
        var row=JsonNode.Parse(File.ReadAllText(path))!.AsObject();
        if(row["schema"]?.GetValue<int>()!=1||Text(row,"job")!=job||!string.Equals(Text(row,"project"),project,Paths))throw new ArgumentException("Build job scope mismatch");
        return row;
    }
    static JsonObject Change(string root,string project,string job,string owner,string state,string phase,Action<JsonObject>? extra=null)
    {
        string folder=Path.Combine(root,".confectory","build-jobs",job);using var lease=Lease(root,Path.Combine(folder,"job.lock"),5);
        var row=Read(root,project,job);if(Text(row,"owner")!=owner)throw new UnauthorizedAccessException("Build job owner changed");
        if(Terminal(Text(row,"state")))return row;
        row["state"]=state;row["phase"]=phase;row["updatedUtc"]=DateTime.UtcNow.ToString("O");if(Terminal(state))row["finishedUtc"]=row["updatedUtc"]!.DeepClone();extra?.Invoke(row);
        Write(root,Path.Combine(folder,"job.json"),row);return row;
    }
    static JsonObject Public(JsonObject row,bool files=false)
    {
        var result=new JsonObject{["scope"]="project-build-job",["kind"]="build-only"};
        foreach(string key in new[]{"job","namespace","entry","target","state","phase","startedUtc","updatedUtc","finishedUtc","error","key","artifactState","artifactCount","artifactBytes"})if(row[key] is not null)result[key]=row[key]!.DeepClone();
        if(files&&row["files"] is not null)result["files"]=row["files"]!.DeepClone();return result;
    }
    static void Artifacts(string root,JsonObject row,JsonObject built)
    {
        string output=Path.GetFullPath(Text(built,"output")),outputs=Path.Combine(root,".confectory","outputs");Owned(outputs,output);
        row["key"]=built["key"]!.DeepClone();row["output"]=output;row["artifactState"]="recorded";
        var files=new JsonArray();var folders=new Stack<(string Path,int Depth)>();folders.Push((output,0));long total=0;int entries=0;
        while(folders.Count>0)
        {
            var folder=folders.Pop();if(folder.Depth>32)throw new ArgumentException("Artifact directory depth budget");
            foreach(string path in Directory.EnumerateFileSystemEntries(folder.Path).Order(StringComparer.Ordinal))
            {
                if(++entries>8192)throw new ArgumentException("Artifact directory entry budget");Owned(output,path);if(Directory.Exists(path)){folders.Push((path,folder.Depth+1));continue;}
                var info=new FileInfo(path);if(!info.Exists||info.Length>536870912||files.Count>=4096||total+info.Length>1073741824)throw new ArgumentException("Artifact manifest budget");
                total+=info.Length;files.Add(new JsonObject{["name"]=Path.GetRelativePath(output,path),["size"]=info.Length,["sha256"]=Hash(path)});
            }
        }
        if(files.ToJsonString().Length>1048576)throw new ArgumentException("Artifact manifest transport budget");
        row["files"]=files;row["artifactCount"]=files.Count;row["artifactBytes"]=total;
    }
    static string Verify(string root,JsonObject row)
    {
        if(row["files"] is not JsonArray files||row["output"] is null)return "unavailable";
        string output=Path.GetFullPath(Text(row,"output"));Owned(Path.Combine(root,".confectory","outputs"),output);
        if(files.Count>4096||files.ToJsonString().Length>1048576)throw new ArgumentException("Artifact manifest budget");long total=0;
        foreach(var file in files)
        {
            string relative=Text(file!,"name"),path=Path.GetFullPath(Path.Combine(output,relative));if(Path.IsPathRooted(relative))throw new ArgumentException("Relative artifact name required");Owned(output,path);
            var info=new FileInfo(path);if(!info.Exists)return "missing";if(info.Length!=file!["size"]!.GetValue<long>())return "changed";
            if(info.Length>536870912||total+info.Length>1073741824)throw new ArgumentException("Artifact verification budget");total+=info.Length;
            if(Hash(path)!=Text(file,"sha256"))return "changed";
        }
        return "verified";
    }
    public static JsonObject Execute(JsonObject request)
    {
        string operation=Text(request,"operation"),project=Path.GetFullPath(Text(request,"project")),root=Path.GetDirectoryName(project)!;
        string storage=Path.Combine(root,".confectory","build-jobs");Owned(root,storage);
        if(operation=="history")
        {
            int page=request["page"]?.GetValue<int>()??0;if(page<0)throw new ArgumentException("Build history page required");
            var paths=Directory.Exists(storage)?Directory.EnumerateDirectories(storage).Take(1025).ToArray():Array.Empty<string>();if(paths.Length>1024)throw new ArgumentException("Build history capacity");
            foreach(string path in paths)Owned(root,path);
            var ordered=paths.OrderByDescending(path=>File.GetLastWriteTimeUtc(Path.Combine(path,"job.json"))).ThenBy(path=>path,StringComparer.Ordinal).ToArray();var rows=new JsonArray();
            foreach(string path in ordered.Skip(checked(page*32)).Take(32))
            {
                string id=Path.GetFileName(path);try{rows.Add(Public(Read(root,project,id)));}catch{rows.Add(new JsonObject{["job"]=id,["state"]="unavailable",["error"]="Build job metadata unavailable"});}
            }
            return new(){["scope"]="project-build-history",["page"]=page,["pageSize"]=32,["total"]=ordered.Length,["rows"]=rows};
        }
        string job=Text(request,"job");if(!Guid.TryParseExact(job,"N",out _))throw new ArgumentException("Explicit build job ID required");string folder=Path.Combine(storage,job);
        if(operation=="prepare")
        {
            string owner=Text(request,"owner"),entry=Text(request,"entry"),target=Text(request,"target");
            if(!Guid.TryParseExact(owner,"N",out _)||string.IsNullOrWhiteSpace(entry)||entry.Length>512||string.IsNullOrWhiteSpace(target)||target.Length>64)throw new ArgumentException("Explicit bounded build scope required");
            Owned(root,project);if(new FileInfo(project).Length>1048576)throw new ArgumentException("Project manifest budget");var manifest=new Parser(File.ReadAllText(project),project).ParseManifest();if(!manifest.Targets.ContainsKey(target))throw new ArgumentException("Selected target is not declared");
            if(Directory.Exists(storage)&&Directory.EnumerateDirectories(storage).Take(1024).Count()>=1024)throw new ArgumentException("Build job capacity");
            using var lease=Lease(root,Path.Combine(folder,"job.lock"),5);if(File.Exists(Path.Combine(folder,"job.json")))throw new InvalidOperationException("Build job identity already recorded");
            string now=DateTime.UtcNow.ToString("O");var row=new JsonObject{["schema"]=1,["job"]=job,["owner"]=owner,["project"]=project,["namespace"]=manifest.Namespace,["entry"]=entry,["target"]=target,["state"]="queued",["phase"]="queued",["startedUtc"]=now,["updatedUtc"]=now};Write(root,Path.Combine(folder,"job.json"),row,true);return Public(row);
        }
        var current=Read(root,project,job);
        if(operation=="status")
        {
            var result=Public(current,true);if(request["verify"]?.GetValue<bool>()==true&&Text(current,"state")=="built"){try{result["artifactState"]=Verify(root,current);}catch{result["artifactState"]="unavailable";}result["verifiedUtc"]=DateTime.UtcNow.ToString("O");}return result;
        }
        string nonce=Text(request,"owner");if(Text(current,"owner")!=nonce)throw new UnauthorizedAccessException("Build job owner changed");
        if(operation is "cancel" or "fail")return Public(Change(root,project,job,nonce,operation=="cancel"?"stopped":"failed",operation=="cancel"?"stopped":"failed",row=>{string error=request["error"]?.GetValue<string>()??"";row["error"]=error.Length>4096?error[..4096]:error;}),true);
        if(operation!="build")throw new ArgumentException("Unknown build job operation");if(Terminal(Text(current,"state")))throw new InvalidOperationException("Build job is terminal; no replay");
        try
        {
            Change(root,project,job,nonce,"building","waiting-for-lease");
            using var lease=Lease(root,Path.GetFullPath(Text(request,"lease")),120);Change(root,project,job,nonce,"building","compiling");
            var builder=new Builder(project,Text(current,"target"));builder.Registry.Project.Entry=Text(current,"entry");var built=builder.Build();
            return Public(Change(root,project,job,nonce,"built","built",row=>{try{Artifacts(root,row,built);}catch(Exception error){row.Remove("files");row["key"]=built["key"]!.DeepClone();row["artifactState"]="unavailable";row["artifactError"]=error.Message.Length>256?error.Message[..256]:error.Message;}}),true);
        }
        catch(Exception error){return Public(Change(root,project,job,nonce,"failed","failed",row=>row["error"]=error.Message.Length>4096?error.Message[..4096]:error.Message));}
    }
}
