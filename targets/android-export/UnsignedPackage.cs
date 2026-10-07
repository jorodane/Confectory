using System.Diagnostics;
using System.Text.Json;

internal static class UnsignedPackage
{
    public static int Build(string output, ExportSettings settings)
    {
        // Never supply signing properties or passwords to MSBuild. Package is deliberately unsigned.
        // Installed .NET Android SDK normally signs public Build; the IDE flag suppresses that step.
        var start=new ProcessStartInfo(Environment.GetEnvironmentVariable("CONFECTORY_ANDROID_DOTNET") ?? Environment.GetEnvironmentVariable("CONFECTORY_DOTNET") ?? "dotnet") { WorkingDirectory=output, UseShellExecute=false };
        foreach(string arg in new[]{"build", "Confectory.Android.csproj", "-t:Package", "-c", "Release", "-p:BuildingInsideVisualStudio=true", "-p:AndroidKeyStore=true", "-p:AndroidBuildApplicationPackage=true", "-p:AndroidPackageFormats="+settings.Format, "-p:AndroidPackageFormat="+settings.Format, "-p:EmbedAssembliesIntoApk=true", "-p:RunAOTCompilation=false"}) start.ArgumentList.Add(arg);
        using var process=Process.Start(start) ?? throw new InvalidOperationException("Cannot start Android packaging tool.");
        process.WaitForExit();
        if(process.ExitCode!=0){Console.Error.WriteLine("Android packaging failed; no successful package result is recorded.");return process.ExitCode;}
        var artifacts=Directory.GetFiles(Path.Combine(output,"bin"),"*."+settings.Format,SearchOption.AllDirectories);
        if(artifacts.Length==0){Console.Error.WriteLine("Packaging reported success without an artifact.");return 1;}
        File.WriteAllText(Path.Combine(output,"package-report.json"),JsonSerializer.Serialize(new{kind="android-unsigned-package",format=settings.Format,keyAlias=settings.KeyAlias,targetFramework=settings.Framework,targetSdkVersion=settings.TargetSdk,androidAppCompiled=true,signed=false,playAcceptanceVerified=false,artifacts},new JsonSerializerOptions{WriteIndented=true}));
        Console.WriteLine(JsonSerializer.Serialize(new{output,format=settings.Format,androidAppCompiled=true,signed=false,artifacts}));
        return 0;
    }
}
