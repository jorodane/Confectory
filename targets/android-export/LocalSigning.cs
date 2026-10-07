using System.Diagnostics;
using System.IO.Compression;
using System.Text;
using System.Text.Json;

namespace Confectory.AndroidExport;

// Credentials belong only to this interactive process and the signing child environment.
// No shell, command-line passwords, secret files, key generation, or persisted key paths.
public static class LocalSigning
{
    public const string StoreVariable="CONFECTORY_EPHEMERAL_STORE_PASSWORD";
    public const string KeyVariable="CONFECTORY_EPHEMERAL_KEY_PASSWORD";
    public static ProcessStartInfo SigningCommand(string format,string tool,string input,string output,string key,string alias,string storePassword,string keyPassword)
    {
        if(format is not ("apk" or "aab")||alias.Length==0||alias.StartsWith('-')||alias.Any(char.IsControl))throw new ArgumentException("Invalid signing selection.");
        var start=new ProcessStartInfo(tool){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true,RedirectStandardInput=true};
        string[] args=format=="aab"
            ? new[]{"-keystore",key,"-storepass:env",StoreVariable,"-keypass:env",KeyVariable,"-signedjar",output,input,alias}
            : new[]{"sign","--ks",key,"--ks-key-alias",alias,"--ks-pass","env:"+StoreVariable,"--key-pass","env:"+KeyVariable,"--out",output,input};
        foreach(string arg in args)start.ArgumentList.Add(arg);
        start.Environment[StoreVariable]=storePassword;start.Environment[KeyVariable]=keyPassword;
        return start;
    }
    public static int Interactive(string export,string keystore)
    {
        string? temporary=null,signed=null;bool ownsSigned=false;
        try
        {
            if(Console.IsInputRedirected)throw new InvalidOperationException("Signing requires a local interactive console; passwords cannot be supplied as arguments or redirected input.");
            export=Path.GetFullPath(export);keystore=Path.GetFullPath(keystore);
            if(!File.Exists(keystore))throw new InvalidOperationException("Select an existing local keystore.");
            using var report=JsonDocument.Parse(File.ReadAllText(Path.Combine(export,"package-report.json")));
            string format=report.RootElement.GetProperty("format").GetString()!,alias=report.RootElement.GetProperty("keyAlias").GetString()!;
            string[] artifacts=report.RootElement.GetProperty("artifacts").EnumerateArray().Select(x=>Path.GetFullPath(x.GetString()!)).ToArray();
            if(artifacts.Length!=1||format is not ("apk" or "aab")||!artifacts[0].StartsWith(export+Path.DirectorySeparatorChar,OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal)||Path.GetExtension(artifacts[0])!="."+format||!File.Exists(artifacts[0]))throw new InvalidOperationException("Expected one owned unsigned package artifact.");
            string input=artifacts[0];signed=Path.Combine(Path.GetDirectoryName(input)!,Path.GetFileNameWithoutExtension(input)+"-signed."+format);
            if(File.Exists(signed)||File.Exists(Path.Combine(export,"signing-report.json")))throw new InvalidOperationException("Signed output already exists; use a new export directory.");
            ownsSigned=true;
            string javaHome=Environment.GetEnvironmentVariable("JAVA_HOME")??throw new InvalidOperationException("Set JAVA_HOME to a full compatible JDK.");
            string suffix=OperatingSystem.IsWindows()?".exe":"",tool=Path.Combine(javaHome,"bin","jarsigner"+suffix);
            string? jar=null;
            if(format=="apk")
            {
                string sdk=Environment.GetEnvironmentVariable("ANDROID_HOME")??Environment.GetEnvironmentVariable("ANDROID_SDK_ROOT")??throw new InvalidOperationException("Set ANDROID_HOME.");
                string tools=Directory.GetDirectories(Path.Combine(sdk,"build-tools")).Where(p=>File.Exists(Path.Combine(p,"zipalign"+suffix))&&File.Exists(Path.Combine(p,"lib","apksigner.jar"))).OrderByDescending(p=>Version.TryParse(Path.GetFileName(p),out var v)?v:new Version()).FirstOrDefault()??throw new InvalidOperationException("Install Android build-tools.");
                string alignment=Path.Combine(export,"aligned-unsigned.apk");
                if(File.Exists(alignment))throw new InvalidOperationException("Alignment output already exists.");
                temporary=alignment;
                Run(Command(Path.Combine(tools,"zipalign"+suffix),"-P","16","-f","4",input,temporary));input=temporary;
                tool=Path.Combine(javaHome,"bin","java"+suffix);jar=Path.Combine(tools,"lib","apksigner.jar");
            }
            if(!File.Exists(tool))throw new InvalidOperationException("Selected JDK signing tool is absent.");
            Console.WriteLine($"Sign this {format.ToUpperInvariant()} with existing key alias '{alias}'? Type SIGN to continue. No upload follows.");
            if(Console.ReadLine()!="SIGN"){Console.WriteLine("Signing cancelled; unsigned export retained.");return 2;}
            string store=Password("Keystore password: "),key=Password("Key password (Enter = same): ");if(key.Length==0)key=store;
            var command=SigningCommand(format,tool,input,signed,keystore,alias,store,key);
            if(jar is not null){command.ArgumentList.Insert(0,jar);command.ArgumentList.Insert(0,"-jar");}
            try{Run(command);}finally{command.Environment.Remove(StoreVariable);command.Environment.Remove(KeyVariable);store="";key="";}
            if(!File.Exists(signed))throw new InvalidOperationException("Signing tool produced no package.");
            if(format=="aab")
            {
                using var archive=ZipFile.OpenRead(signed);
                if(!archive.Entries.Any(e=>e.FullName.StartsWith("META-INF/",StringComparison.OrdinalIgnoreCase)&&new[]{".RSA",".DSA",".EC"}.Contains(Path.GetExtension(e.FullName).ToUpperInvariant())))throw new InvalidOperationException("No signing certificate block found.");
                Run(Command(tool,"-verify",signed));
            }
            else Run(Command(tool,"-jar",jar!,"verify","--verbose",signed));
            File.WriteAllText(Path.Combine(export,"signing-report.json"),JsonSerializer.Serialize(new{format,artifact=signed,signed=true,signatureVerified=true,uploaded=false},new JsonSerializerOptions{WriteIndented=true}));
            Console.WriteLine("Verified signed local artifact: "+signed);return 0;
        }
        catch(Exception){if(ownsSigned&&signed is not null&&File.Exists(signed))File.Delete(signed);Console.Error.WriteLine("Signing failed. No successful signing report was written; check your local tools, key alias and passwords. Unsigned export retained.");return 1;}
        finally{if(temporary is not null&&File.Exists(temporary))File.Delete(temporary);}
    }
    static ProcessStartInfo Command(string tool,params string[] args){var p=new ProcessStartInfo(tool){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true,RedirectStandardInput=true};foreach(var arg in args)p.ArgumentList.Add(arg);p.Environment.Remove(StoreVariable);p.Environment.Remove(KeyVariable);return p;}
    static void Run(ProcessStartInfo start)
    {
        using var process=Process.Start(start)??throw new InvalidOperationException("Cannot start signing tool.");process.StandardInput.Close();
        var output=process.StandardOutput.ReadToEndAsync();var error=process.StandardError.ReadToEndAsync();
        if(!process.WaitForExit(120000)){process.Kill(true);throw new TimeoutException();}
        Task.WaitAll(output,error);if(process.ExitCode!=0)throw new InvalidOperationException("Signing tool failed.");
        // Tool output is deliberately not logged: provider diagnostics can expose credentials.
    }
    static string Password(string prompt){Console.Write(prompt);var value=new StringBuilder();while(true){var key=Console.ReadKey(true);if(key.Key==ConsoleKey.Enter)break;if(key.Key==ConsoleKey.Escape)throw new OperationCanceledException();if(key.Key==ConsoleKey.Backspace){if(value.Length>0)value.Length--;continue;}if(!char.IsControl(key.KeyChar))value.Append(key.KeyChar);if(value.Length>4096)throw new InvalidOperationException();}Console.WriteLine();return value.ToString();}
}
