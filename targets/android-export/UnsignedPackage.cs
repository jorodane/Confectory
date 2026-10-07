using System.Diagnostics;
using System.Text.Json;

internal static class UnsignedPackage
{
    public static int Build(string output, ExportSettings settings)
    {
        string? zipalign=settings.Format=="apk"?FindZipalign():null;
        // Never supply signing properties or passwords to MSBuild. Package is deliberately unsigned.
        // Installed .NET Android SDK normally signs public Build; the IDE flag suppresses that step.
        var start=new ProcessStartInfo(Environment.GetEnvironmentVariable("CONFECTORY_ANDROID_DOTNET") ?? Environment.GetEnvironmentVariable("CONFECTORY_DOTNET") ?? "dotnet") { WorkingDirectory=output, UseShellExecute=false };
        foreach(string arg in new[]{"build", "Confectory.Android.csproj", "-t:Package", "-c", "Release", "-p:BuildingInsideVisualStudio=true", "-p:AndroidKeyStore=true", "-p:AndroidBuildApplicationPackage=true", "-p:AndroidPackageFormats="+settings.Format, "-p:AndroidPackageFormat="+settings.Format, "-p:EmbedAssembliesIntoApk=true", "-p:RunAOTCompilation=false"}) start.ArgumentList.Add(arg);
        using var process=Process.Start(start) ?? throw new InvalidOperationException("Cannot start Android packaging tool.");
        process.WaitForExit();
        if(process.ExitCode!=0){Console.Error.WriteLine("Android packaging failed; no successful package result is recorded.");return process.ExitCode;}
        var artifacts=Directory.GetFiles(Path.Combine(output,"bin"),"*."+settings.Format,SearchOption.AllDirectories);
        if(artifacts.Length==0){Console.Error.WriteLine("Packaging reported success without an artifact.");return 1;}
        // Package bypasses signing targets, which normally align APKs. Align and verify
        // these newly generated unsigned files explicitly before recording success.
        if(zipalign is not null)foreach(string artifact in artifacts)
        {
            string aligned=artifact+".alignment-"+Guid.NewGuid().ToString("N")+".apk";
            try
            {
                if(Run(zipalign,"-P","16","-f","4",artifact,aligned)!=0||Run(zipalign,"-c","-P","16","-v","4",aligned)!=0)
                {Console.Error.WriteLine("Unsigned APK alignment failed; no successful package result is recorded.");return 1;}
                File.Move(aligned,artifact,true);
            }
            finally{if(File.Exists(aligned))File.Delete(aligned);}
        }
        File.WriteAllText(Path.Combine(output,"package-report.json"),JsonSerializer.Serialize(new{kind="android-unsigned-package",format=settings.Format,keyAlias=settings.KeyAlias,targetFramework=settings.Framework,targetSdkVersion=settings.TargetSdk,androidAppCompiled=true,signed=false,apkZipAlignmentVerified=zipalign is not null,playAcceptanceVerified=false,artifacts},new JsonSerializerOptions{WriteIndented=true}));
        Console.WriteLine(JsonSerializer.Serialize(new{output,format=settings.Format,androidAppCompiled=true,signed=false,artifacts}));
        return 0;
    }
    static string FindZipalign()
    {
        string sdk=Environment.GetEnvironmentVariable("ANDROID_HOME")??Environment.GetEnvironmentVariable("ANDROID_SDK_ROOT")??throw new InvalidOperationException("Set ANDROID_HOME to the installed Android SDK before APK packaging.");
        string name=OperatingSystem.IsWindows()?"zipalign.exe":"zipalign";
        return Directory.GetDirectories(Path.Combine(sdk,"build-tools")).Where(path=>Version.TryParse(Path.GetFileName(path),out _)).OrderByDescending(path=>Version.Parse(Path.GetFileName(path))).Select(path=>Path.Combine(path,name)).FirstOrDefault(File.Exists)??throw new InvalidOperationException("Install stable Android build-tools with zipalign before APK packaging.");
    }
    static int Run(string executable,params string[] args)
    {
        var start=new ProcessStartInfo(executable){UseShellExecute=false};foreach(string arg in args)start.ArgumentList.Add(arg);
        using var process=Process.Start(start)??throw new InvalidOperationException("Cannot start official APK alignment tool.");process.WaitForExit();return process.ExitCode;
    }
}
