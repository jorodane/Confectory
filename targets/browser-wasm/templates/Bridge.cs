using System.Runtime.InteropServices.JavaScript;
using System.Text.Json;
using Confectory.Core;
namespace Confectory.Browser;
public static partial class Bridge
{
    private static bool initialized;
    [JSImport("render","confectory.browser.dom")] private static partial void RenderDOM(string snapshot);
    [JSExport]
    public static int Initialize()
    {
        if(initialized)return 0;
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
        (AppDomain.CurrentDomain.GetData("Confectory.Browser.Close") as Action)?.Invoke();
        AppDomain.CurrentDomain.SetData("Confectory.Browser.Metadata",null);AppDomain.CurrentDomain.SetData("Confectory.Browser.Render",null);initialized=false;
    }
}
