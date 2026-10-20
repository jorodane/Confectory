using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text.Json.Nodes;
namespace Confectory.Desktop;
internal static class Program
{
    [STAThread]
    static async Task<int> Main(string[] args)
    {
        try
        {
            if(args.Length==3&&args[0]=="package") { Console.WriteLine(DesktopPackage.Build(args[1],args[2]).ToJsonString());return 0; }
            if(args.Length is 1 or 2&&args[0]=="--check-package") { string packageRoot=args.Length==2?args[1]:AppContext.BaseDirectory;var check=PackageLayout.Check(packageRoot);var checkStart=PackageLayout.EngineStart(packageRoot,Environment.GetEnvironmentVariable("CONFECTORY_DOTNET")??"dotnet");check["workingDirectory"]=checkStart.WorkingDirectory;check["engineAssembly"]=checkStart.ArgumentList[0];var environment=new JsonObject();foreach(string key in new[]{"CONFECTORY_UI","CONFECTORY_EDITOR_REPO","CONFECTORY_ENTRY_SCOPE","CONFECTORY_WEBVIEW_HOST","CONFECTORY_ELEMENT_AUTHORING_HOST","CONFECTORY_PROJECT_EXECUTION_HOST","CONFECTORY_HOME_STORAGE"})environment[key]=checkStart.Environment[key];check["environment"]=environment;Console.WriteLine(check.ToJsonString());return 0; }
            if(args.Length!=0)throw new ArgumentException("Usage: package <repository> <output-folder> | --check-package [folder]");
            if(!OperatingSystem.IsWindows())throw new PlatformNotSupportedException("Run Confectory.exe on Windows. Package verification is available with --check-package.");
            string root=Path.GetFullPath(AppContext.BaseDirectory);PackageLayout.Check(root);
            string runtime=Path.GetFullPath(Path.Combine(RuntimeEnvironment.GetRuntimeDirectory(),"..","..",".."));
            string desktop=Path.Combine(runtime,"shared","Microsoft.WindowsDesktop.App");
            if(!Directory.Exists(desktop)||!Directory.EnumerateDirectories(desktop,"10.0.*").Any())throw new InvalidOperationException("Microsoft .NET Desktop Runtime 10.0 (x64) is required. Install it separately; Confectory does not install runtimes.");
            string dotnet=Environment.GetEnvironmentVariable("CONFECTORY_DOTNET")??Path.Combine(runtime,"dotnet.exe");
            var start=PackageLayout.EngineStart(root,dotnet);
            string storage=start.Environment["CONFECTORY_HOME_STORAGE"]!;Directory.CreateDirectory(storage);
            string logs=Path.Combine(storage,"logs");Directory.CreateDirectory(logs);
            using var writer=new StreamWriter(Path.Combine(logs,"launch-"+DateTime.UtcNow.ToString("yyyyMMdd-HHmmss-fffffff")+".log")){AutoFlush=true};
            using var child=Process.Start(start)??throw new IOException("Confectory engine did not start");
            async Task Drain(StreamReader stream){string? line;while((line=await stream.ReadLineAsync()) is not null){lock(writer)writer.WriteLine(line);}}
            await Task.WhenAll(Drain(child.StandardOutput),Drain(child.StandardError),child.WaitForExitAsync());
            if(child.ExitCode!=0)throw new InvalidOperationException("Confectory could not start or close normally. Check the local launch log in "+logs+". Microsoft .NET Desktop Runtime 10.0 x64 and Microsoft Edge WebView2 Runtime are required.");
            return 0;
        }
        catch(Exception error)
        {
            Console.Error.WriteLine(error.Message);
            if(args.Length==0&&OperatingSystem.IsWindows())MessageBoxW(0,error.Message,"Confectory",0x10);
            return 1;
        }
    }
    [DllImport("user32.dll",CharSet=CharSet.Unicode)]
    static extern int MessageBoxW(nint owner,string text,string caption,uint type);
}
