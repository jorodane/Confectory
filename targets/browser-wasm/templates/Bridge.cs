using System.Runtime.InteropServices.JavaScript;
using System.Text.Json;
using Confectory.Core;
namespace Confectory.Browser;
public static partial class Bridge
{
    private static bool initialized;
    private static readonly HashSet<string> disposed=new(),active=new();
    [JSImport("request","confectory.browser.platform")] private static partial string Platform(string operation,string payload);
    [JSImport("run","confectory.browser.platform")] private static partial void RunLoop(string token);
    [JSImport("render","confectory.browser.dom")] private static partial void RenderDOM(string snapshot);
    [JSExport]
    public static int Initialize()
    {
        if(initialized)return 0;
        string root="/confectory-owned";Directory.CreateDirectory(root);Environment.SetEnvironmentVariable("CONFECTORY_EDITOR_REPO",root);Environment.SetEnvironmentVariable("CONFECTORY_HOME_STORAGE",root+"/home");
        AppDomain.CurrentDomain.SetData("Confectory.Browser.VirtualRoot",root);
        AppContext.SetData("Confectory.Browser.Platform",(Func<string,string,string>)((operation,payload)=>Platform(operation,payload)));
        AppContext.SetData("Confectory.HostLoop.Run.browser",(Func<string,int>)(token=>{active.Add(token);RunLoop(token);return 0;}));
        AppDomain.CurrentDomain.SetData("Confectory.Browser.Render",(Action<string>)(snapshot=>RenderDOM(snapshot)));
        // Metadata only: the parser receives selected bytes in browser-owned virtual storage.
        // No registry resolution, Builder, SDK invocation, or imported code execution.
        AppDomain.CurrentDomain.SetData("Confectory.Browser.Metadata",(Func<string,string[]>)(path=>{
            string file=Path.GetFullPath(path);string ownerRoot=AppDomain.CurrentDomain.GetData("Confectory.Browser.VirtualRoot") as string??throw new ObjectDisposedException("Browser virtual storage");if(!file.StartsWith(ownerRoot+"/",StringComparison.Ordinal))throw new UnauthorizedAccessException("Only owner-scoped browser imports may be described");string text=File.ReadAllText(file);
            if(System.Text.Encoding.UTF8.GetByteCount(text)>1048576)throw new ArgumentException("Manifest budget exceeded");
            var manifest=new Parser(text,file).ParseManifest();
            return new[]{manifest.Namespace,manifest.Entry??"",string.Join(",",manifest.Targets.Keys.Order(StringComparer.Ordinal)),manifest.Kind,manifest.SupportsStandalone?"true":"false"};
        }));
        int result=global::Program.Main();initialized=result==0;return result;
    }
    [JSExport]
    public static bool Step(string token)
    {
        if(disposed.Contains(token))return false;
        var callbacks=AppContext.GetData("Confectory.HostLoop."+token) as object[];
        if(callbacks is null)return false;
        try{if(((Func<bool>)callbacks[0])())return true;}catch{DisposeLoop(token);throw;}
        DisposeLoop(token);return false;
    }
    private static void DisposeLoop(string token){if(!disposed.Add(token))return;active.Remove(token);var callbacks=AppContext.GetData("Confectory.HostLoop."+token) as object[];if(callbacks is not null)((Action)callbacks[1])();AppContext.SetData("Confectory.HostLoop."+token,null);}
    [JSExport]
    public static string ImportFiles(string names,string contents)
    {
        var paths=JsonSerializer.Deserialize<string[]>(names)!;var texts=JsonSerializer.Deserialize<string[]>(contents)!;
        if(paths.Length!=texts.Length||paths.Length>256)throw new ArgumentException("Selected file budget");
        string root=AppDomain.CurrentDomain.GetData("Confectory.Browser.VirtualRoot") as string??throw new ObjectDisposedException("storage");string folder=root+"/selected";Directory.CreateDirectory(folder);
        for(int i=0;i<paths.Length;i++){string path=Path.GetFullPath(Path.Combine(folder,paths[i]));if(!path.StartsWith(folder+"/",StringComparison.Ordinal)||texts[i].Length>1048576)throw new ArgumentException("Selected file boundary");Directory.CreateDirectory(Path.GetDirectoryName(path)!);File.WriteAllText(path,texts[i]);}return folder;
    }
    [JSExport]
    public static string Request(string operation,string payload)
    {
        try {
            if(!initialized)throw new InvalidOperationException("Browser owner must initialize first");
            var request=AppDomain.CurrentDomain.GetData("Confectory.Browser.Request") as Func<string,string,string>??throw new ObjectDisposedException("Browser owner");
            return request(operation,payload);
        }catch(Exception error){return JsonSerializer.Serialize(new{error=error.Message});}
    }
    [JSExport]
    public static void Close()
    {
        foreach(string token in active.ToArray())DisposeLoop(token);
        (AppDomain.CurrentDomain.GetData("Confectory.Browser.Close") as Action)?.Invoke();
        AppDomain.CurrentDomain.SetData("Confectory.Browser.Metadata",null);AppDomain.CurrentDomain.SetData("Confectory.Browser.Render",null);initialized=false;
    }
}
