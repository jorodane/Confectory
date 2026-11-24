using System.Diagnostics;
using System.Security.Cryptography;
using System.Text.Json.Nodes;
using Confectory.Core;
namespace Confectory.Desktop;
internal static class DesktopPackage
{
    internal static JsonObject Build(string repository,string destination,string rid=PackageLayout.WindowsRid)
    {
        bool linux=PackageLayout.IsLinux(rid);
        if(linux&&!PackageLayout.IsLinuxX64)throw new PlatformNotSupportedException("Building a Linux x64 editor package requires a Linux x64 build host.");
        string repo=Path.GetFullPath(repository),output=Path.GetFullPath(destination);
        if(!File.Exists(Path.Combine(repo,"examples/editor-home/project.cpack")))throw new IOException("An installed Confectory checkout is required");
        if(output==repo||new[]{"packs","targets","examples/editor-home"}.Any(part=>output.Equals(Path.GetFullPath(Path.Combine(repo,part)),StringComparison.OrdinalIgnoreCase)||output.StartsWith(Path.GetFullPath(Path.Combine(repo,part))+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase)))throw new IOException("Choose a build result folder outside packaged source directories");
        if(File.Exists(output))throw new IOException("Output path is a file");
        if(Directory.Exists(output)&&!File.Exists(Path.Combine(output,PackageLayout.Marker)))throw new IOException("Existing folder is not a Confectory package; choose an empty output location");
        string parent=Path.GetDirectoryName(output)??throw new IOException("Output folder has no parent");Directory.CreateDirectory(parent);
        string stage=Path.Combine(parent,".confectory-desktop-"+Guid.NewGuid().ToString("N"));Directory.CreateDirectory(stage);
        try
        {
            string dotnet=Environment.GetEnvironmentVariable("CONFECTORY_DOTNET")??"dotnet";
            var built=new Builder(Path.Combine(repo,"examples/editor-home/project.cpack"),linux?"linux":"windows").Build();
            string engine=Path.GetDirectoryName(built["run"]!.AsArray().Last()!.GetValue<string>())!;
            string content=Path.Combine(stage,"content");Directory.CreateDirectory(content);
            Copy(Path.Combine(repo,"packs"),Path.Combine(content,"packs"),true);
            Copy(Path.Combine(repo,"targets"),Path.Combine(content,"targets"),true);
            Copy(Path.Combine(repo,"examples/editor-home"),Path.Combine(content,"examples/editor-home"),true);
            Copy(engine,Path.Combine(content,"runtime"),false);
            foreach(string tool in PackageLayout.RequiredTools.Concat(new[]{"targets/desktop-entry","targets/browser-wasm","targets/android-export","targets/mcp-host"}))
            {
                string from=Path.Combine(repo,tool,"bin/Release/net10.0");
                if(!Directory.Exists(from)){if(PackageLayout.RequiredTools.Contains(tool))throw new IOException("Build the solution in Release first; required tool missing: "+tool);continue;}
                Copy(from,Path.Combine(content,tool,"bin/Release/net10.0"),false);
            }
            string launcherProject=Path.Combine(repo,"targets/editor-desktop/Confectory.EditorDesktop.csproj");
            if(linux)
            {
                Run(dotnet,repo,"publish",launcherProject,"-c","Release","--self-contained","false","-p:UseAppHost=false","-o",stage,"--nologo");
                WriteLinuxLauncher(stage);
            }
            else
            {
                Run(dotnet,repo,"publish",launcherProject,"-c","Release","-r","win-x64","--self-contained","false","-o",stage,"--nologo");
                Run(dotnet,repo,"publish",Path.Combine(repo,"targets/webview-windows/Confectory.WebView.Windows.csproj"),"-c","Release","-r","win-x64","--self-contained","false","-o",Path.GetDirectoryName(PackageLayout.Owned(stage,PackageLayout.Host))!,"--nologo");
                File.WriteAllText(Path.Combine(stage,"README.txt"),"Confectory for Windows x64\r\n\r\nOpen Confectory.exe. Keep this entire folder together; the exe is not a single-file bundle.\r\nRequires Microsoft .NET Desktop Runtime 10.0 x64 and Microsoft Edge WebView2 Runtime, installed separately. No runtime is installed by Confectory.\r\nThe .NET 10 SDK is additionally needed for building user projects, not for opening this editor.\r\nDefault editor data: %LOCALAPPDATA%\\Confectory\\EditorHome. Existing explicit CONFECTORY_HOME_STORAGE/CONFECTORY_ENTRY_STORAGE is respected. A Builds/Windows-x64 result reuses the existing checkout .confectory/editor-home profile when present.\r\nNo user settings, credentials or projects are bundled.\r\n");
            }
            var files=new JsonObject();foreach(string path in Directory.GetFiles(stage,"*",SearchOption.AllDirectories).Order(StringComparer.Ordinal))files[Path.GetRelativePath(stage,path).Replace('\\','/')]=Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path))).ToLowerInvariant();
            File.WriteAllText(Path.Combine(stage,PackageLayout.Marker),new JsonObject{["schema"]="confectory-desktop-package-v1",["rid"]=rid,["files"]=files}.ToJsonString());
            var check=PackageLayout.Check(stage);string? previous=null;
            if(Directory.Exists(output)){PackageLayout.Check(output);previous=output+".previous-"+DateTime.UtcNow.ToString("yyyyMMddHHmmssfffffff");Directory.Move(output,previous);}
            try{Directory.Move(stage,output);}catch{if(previous is not null&&!Directory.Exists(output))Directory.Move(previous,output);throw;}
            check["output"]=output;check["executable"]=Path.Combine(output,PackageLayout.Launcher(rid));if(previous is not null)check["previousPackage"]=previous;return check;
        }
        catch{if(Directory.Exists(stage))Directory.Delete(stage,true);throw;}
    }
    static void WriteLinuxLauncher(string stage)
    {
        if(!OperatingSystem.IsLinux())throw new PlatformNotSupportedException("Linux is required to write the Linux launcher.");
        string launcher=Path.Combine(stage,PackageLayout.Launcher(PackageLayout.LinuxRid));
        File.WriteAllText(launcher,"""
            #!/bin/sh
            set -eu
            root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
            dotnet=${CONFECTORY_DOTNET:-dotnet}
            if ! command -v "$dotnet" >/dev/null 2>&1; then
                echo "Confectory requires .NET Runtime 10.0 x64. Install the .NET 10 SDK to also build and run projects." >&2
                exit 1
            fi
            exec "$dotnet" "$root/Confectory.dll" "$@"
            """+"\n");
        File.SetUnixFileMode(launcher,UnixFileMode.UserRead|UnixFileMode.UserWrite|UnixFileMode.UserExecute|
            UnixFileMode.GroupRead|UnixFileMode.GroupExecute|UnixFileMode.OtherRead|UnixFileMode.OtherExecute);
        File.WriteAllText(Path.Combine(stage,"README.txt"),"""
            Confectory for Linux x64

            Run ./run from an extracted copy of this folder. Keep the whole folder together.
            Requires an X11 session with GTK 3 and GtkSourceView 4, plus .NET Runtime 10.0 x64.
            Compiler-backed review, Build and Run require the separately installed .NET 10 SDK.
            Put dotnet on PATH or set CONFECTORY_DOTNET to its executable. Nothing is installed by Confectory.
            The default profile is under $XDG_DATA_HOME/Confectory/EditorHome (or ~/.local/share/Confectory/EditorHome).
            No source checkout, build cache or credentials are required.
            To edit Logic Code, create a project in GTK and close the window. Run ./run --logic-code,
            open the printed loopback address in your browser, and select the project from Recent.
            Keep the terminal open while editing; use Ctrl+C there when finished.
            Run ./run --check-package to verify the package contents.
            """+"\n");
    }
    static void Run(string dotnet,string cwd,params string[] args)
    {
        var start=new ProcessStartInfo(dotnet){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true,WorkingDirectory=cwd};foreach(string arg in args)start.ArgumentList.Add(arg);
        using var process=Process.Start(start)??throw new IOException("Build process did not start");var output=process.StandardOutput.ReadToEndAsync();var error=process.StandardError.ReadToEndAsync();
        if(!process.WaitForExit(240000)){process.Kill(true);process.WaitForExit();throw new TimeoutException("Desktop publish timed out");}
        string text=output.GetAwaiter().GetResult()+error.GetAwaiter().GetResult();if(process.ExitCode!=0)throw new IOException("Desktop publish failed: "+text);
    }
    static void Copy(string source,string target,bool metadata)
    {
        var root=new DirectoryInfo(source);if(root.LinkTarget is not null)throw new IOException("Linked package source");Directory.CreateDirectory(target);
        foreach(string path in Directory.GetFiles(source)){var file=new FileInfo(path);if(file.LinkTarget is not null)throw new IOException("Linked package source");if(file.Name.EndsWith(".pdb",StringComparison.OrdinalIgnoreCase))continue;File.Copy(path,Path.Combine(target,file.Name),true);}
        foreach(string directory in Directory.GetDirectories(source)){string name=Path.GetFileName(directory);if(metadata&&name is "bin" or "obj" or ".confectory" or ".git" or "Builds" or "__pycache__")continue;Copy(directory,Path.Combine(target,name),metadata);}
    }
}
