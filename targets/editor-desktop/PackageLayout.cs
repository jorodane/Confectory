using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json.Nodes;
namespace Confectory.Desktop;
internal static class PackageLayout
{
    internal const string Marker="confectory-desktop-package.json";
    internal const string Host="content/targets/webview-windows/bin/Release/net10.0-windows/Confectory.WebView.Windows.dll";
    internal const string WindowsRid="win-x64",LinuxRid="linux-x64";
    internal static readonly string[] RequiredTools=["targets/dotnet","targets/element-authoring","targets/project-execution-host","src/Confectory.Cli"];
    internal static bool IsLinuxX64=>OperatingSystem.IsLinux()&&RuntimeInformation.OSArchitecture==Architecture.X64;
    internal static bool IsLinux(string rid)=>rid switch
    {
        LinuxRid=>true,
        WindowsRid=>false,
        _=>throw new IOException("Unsupported desktop package target: "+rid)
    };
    internal static string Launcher(string rid)=>IsLinux(rid)?"run":"Confectory.exe";
    internal static string Owned(string root,string relative)
    {
        root=Path.TrimEndingDirectorySeparator(Path.GetFullPath(root));string path=Path.GetFullPath(Path.Combine(root,relative.Replace('/',Path.DirectorySeparatorChar)));
        if(Path.IsPathRooted(relative)||!path.StartsWith(root.TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar,OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal))throw new IOException("Package path escaped its folder");
        for(string? part=path;part is not null;part=Path.GetDirectoryName(part)){var info=Directory.Exists(part)?(FileSystemInfo)new DirectoryInfo(part):new FileInfo(part);if(info.LinkTarget is not null||(info.Exists&&(info.Attributes&FileAttributes.ReparsePoint)!=0))throw new IOException("Linked package paths are unsupported");if(part==root)break;}
        return path;
    }
    internal static JsonObject Check(string root)
    {
        root=Path.TrimEndingDirectorySeparator(Path.GetFullPath(root));string marker=Owned(root,Marker);
        if(!File.Exists(marker)||new FileInfo(marker).Length>16777216)throw new IOException("Confectory package manifest is missing or too large. Keep the complete result folder together.");
        var manifest=JsonNode.Parse(File.ReadAllText(marker))!.AsObject();
        if(manifest["schema"]?.ToString()!="confectory-desktop-package-v1")throw new IOException("Unsupported desktop package");
        string rid=manifest["rid"]?.ToString()??"";
        bool linux=IsLinux(rid);
        var files=manifest["files"]!.AsObject();if(files.Count is <1 or >20000)throw new IOException("Package file budget");
        foreach(var row in files){string path=Owned(root,row.Key);if(!File.Exists(path)||Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path))).ToLowerInvariant()!=row.Value!.ToString())throw new IOException("Package file missing or changed: "+row.Key);}
        void Require(params string[] components)
        {
            foreach(string component in components)if(!files.ContainsKey(component))throw new IOException("Required package component missing: "+component);
        }
        Require(Launcher(rid),"Confectory.dll","Confectory.runtimeconfig.json","Confectory.deps.json","Confectory.Core.dll",
            "content/runtime/Confectory.App.dll","content/runtime/Confectory.App.runtimeconfig.json","content/runtime/public-linkage.json",
            "content/examples/editor-home/project.cpack","content/examples/editor-home/ui/index.html","content/packs/agent-codex/pack.cpack",
            "content/targets/dotnet/bin/Release/net10.0/Confectory.Build.DotNet.dll",
            "content/targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll",
            "content/targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.runtimeconfig.json",
            "content/targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll",
            "content/targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.runtimeconfig.json",
            "content/src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll");
        var result=new JsonObject{["ok"]=true,["rid"]=rid,["files"]=files.Count,["engine"]="content/runtime/Confectory.App.dll",
            ["resourceRoot"]="content",["launcher"]=Launcher(rid)};
        if(linux)
        {
            Require("content/targets/dotnet/pack.cpack","content/targets/dotnet/linux.celem",
                "content/targets/dotnet/bin/Release/net10.0/Confectory.Build.DotNet.runtimeconfig.json",
                "content/src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.runtimeconfig.json");
            if(OperatingSystem.IsLinux()&&(File.GetUnixFileMode(Owned(root,Launcher(rid)))&UnixFileMode.UserExecute)==0)
                throw new IOException("The Linux launcher has lost its executable permission. Extract the complete package preserving file modes.");
            result["prerequisites"]=".NET Runtime 10.0 x64; X11; GTK 3; GtkSourceView 4";
            result["buildPrerequisites"]=".NET 10 SDK for compiler-backed review, Build and Run";
            result["linuxExecuted"]=false;
        }
        else
        {
            const string hostDirectory="content/targets/webview-windows/bin/Release/net10.0-windows/";
            Require(Host,hostDirectory+"Confectory.WebView.Windows.runtimeconfig.json",hostDirectory+"Confectory.WebView.Windows.deps.json",
                hostDirectory+"Microsoft.Web.WebView2.Core.dll",hostDirectory+"Microsoft.Web.WebView2.WinForms.dll");
            CheckPE(Owned(root,Launcher(rid)),true);
            string? loader=files.Select(x=>x.Key).FirstOrDefault(x=>x.EndsWith("/WebView2Loader.dll",StringComparison.Ordinal)&&!x.Contains("win-arm64",StringComparison.Ordinal)&&!x.Contains("win-x86",StringComparison.Ordinal));
            if(loader is null)throw new IOException("x64 WebView2 native loader is missing");CheckPE(Owned(root,loader),false);
            result["prerequisites"]="Microsoft .NET Desktop Runtime 10.0 x64; Microsoft Edge WebView2 Runtime";
            result["windowsExecuted"]=false;
        }
        return result;
    }
    static void CheckPE(string path,bool gui)
    {
        using var stream=File.OpenRead(path);using var reader=new BinaryReader(stream);
        if(stream.Length<256||reader.ReadUInt16()!=0x5a4d)throw new IOException("Expected a Windows PE binary");stream.Position=0x3c;int offset=reader.ReadInt32();if(offset<0||offset>stream.Length-94)throw new IOException("Invalid PE header");stream.Position=offset;if(reader.ReadUInt32()!=0x4550||reader.ReadUInt16()!=0x8664)throw new IOException("Expected x64 PE binary");if(gui){stream.Position=offset+24+68;if(reader.ReadUInt16()!=2)throw new IOException("Expected a Windows GUI apphost");}
    }
    internal static ProcessStartInfo EngineStart(string root,string dotnet,string rid)
    {
        bool linux=IsLinux(rid);
        root=Path.TrimEndingDirectorySeparator(Path.GetFullPath(root));string content=Owned(root,"content"),tool=Path.Combine(content,"targets");
        var start=new ProcessStartInfo(dotnet){UseShellExecute=false,CreateNoWindow=!linux,RedirectStandardOutput=!linux,RedirectStandardError=!linux,WorkingDirectory=content};
        start.ArgumentList.Add(Owned(root,"content/runtime/Confectory.App.dll"));
        start.Environment["CONFECTORY_DOTNET"]=dotnet;start.Environment["CONFECTORY_UI"]=linux?"native":"embedded";start.Environment["CONFECTORY_EDITOR_REPO"]=content;start.Environment["CONFECTORY_ENTRY_SCOPE"]=root;
        if(linux)start.Environment.Remove("CONFECTORY_WEBVIEW_HOST");
        else start.Environment["CONFECTORY_WEBVIEW_HOST"]=Owned(root,Host);
        start.Environment["CONFECTORY_ELEMENT_AUTHORING_HOST"]=Path.Combine(tool,"element-authoring","bin","Release","net10.0","Confectory.ElementAuthoring.dll");
        start.Environment["CONFECTORY_PROJECT_EXECUTION_HOST"]=Path.Combine(tool,"project-execution-host","bin","Release","net10.0","Confectory.ProjectExecutionHost.dll");
        string? storage=Environment.GetEnvironmentVariable("CONFECTORY_HOME_STORAGE")??Environment.GetEnvironmentVariable("CONFECTORY_ENTRY_STORAGE");
        if(linux)
        {
            string data=Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData,Environment.SpecialFolderOption.DoNotVerify);
            if(!Path.IsPathFullyQualified(data))throw new IOException("Confectory requires a writable Linux user data directory. Check HOME or XDG_DATA_HOME.");
            string userRoot=Path.Combine(data,"Confectory");
            storage??=Path.Combine(userRoot,"EditorHome");
            if(Environment.GetEnvironmentVariable("CONFECTORY_ENTRY_STORAGE") is null)start.Environment["CONFECTORY_ENTRY_STORAGE"]=Path.Combine(userRoot,"entry");
        }
        else
        {
            // Default Builds/Windows-x64 output keeps using this checkout's existing profile.
            // No profile data is copied into the distribution, and explicit overrides win.
            string? checkout=Path.GetDirectoryName(Path.GetDirectoryName(root));
            if(storage is null&&checkout is not null&&File.Exists(Path.Combine(checkout,"examples","editor-home","project.cpack"))&&Directory.Exists(Path.Combine(checkout,".confectory","editor-home")))storage=Path.Combine(checkout,".confectory","editor-home");
            storage??=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),"Confectory","EditorHome");
        }
        start.Environment["CONFECTORY_HOME_STORAGE"]=storage;
        foreach(string key in new[]{"CONFECTORY_WEB_PROJECT","CONFECTORY_BROWSER_PROJECT","CONFECTORY_WINDOWLESS_EDIT","CONFECTORY_ELEMENT_UI","CONFECTORY_INSTALLED_LOGIC_CODE","CONFECTORY_INSTALLED_GTK"})start.Environment.Remove(key);
        return start;
    }
}
