using System.Text.Json.Nodes;
using System.Reflection.Metadata;
using System.Reflection.PortableExecutable;
using System.Security.Cryptography;
using Confectory.Core;
namespace Confectory.Tests;
public sealed class ToolchainSelectionTests : TestCase
{
    public void test_repository_sdk_selection_and_authoring_compatibility_guard()
    {
        var policy=JsonNode.Parse(File.ReadAllText(Path.Combine(Fixture.Repo,"global.json")))!["sdk"]!;
        Equal("10.0.100",policy["version"]!.GetValue<string>());
        Equal("latestFeature",policy["rollForward"]!.GetValue<string>());
        Equal(false,policy["allowPrerelease"]!.GetValue<bool>());
        string host=Processes.DotNet();
        var selected=Processes.Run(new[]{host,"--version"},directory:Fixture.Repo);
        True(selected.ExitCode==0,selected.Stdout+selected.Stderr);
        True(selected.Stdout.Trim().StartsWith("10.0.",StringComparison.Ordinal),selected.Stdout);
        string project=Path.Combine(Fixture.Repo,"targets","element-authoring","Confectory.ElementAuthoring.csproj");
        var valid=Processes.Run(new[]{host,"msbuild",project,"-target:ValidateAuthoringSdk","-nologo"},directory:Fixture.Repo);
        True(valid.ExitCode==0,valid.Stdout+valid.Stderr);
        foreach(string incompatible in new[]{"8.0.100","9.0.100"})
        {
            // Exercise the real MSBuild guard, not an installed SDK 9/10 build.
            var rejected=Processes.Run(new[]{host,"msbuild",project,"-target:ValidateAuthoringSdk","-property:NETCoreSdkVersion="+incompatible,"-nologo"},directory:Fixture.Repo);
            True(rejected.ExitCode!=0,rejected.Stdout+rejected.Stderr);
            string diagnostic=rejected.Stdout+rejected.Stderr;
            True(diagnostic.Contains("requires the .NET 10 SDK Roslyn assemblies",StringComparison.Ordinal),diagnostic);
            True(diagnostic.Contains("runtime or reference pack alone is not the SDK",StringComparison.Ordinal),diagnostic);
            True(!diagnostic.Contains("CS1705",StringComparison.Ordinal),diagnostic);
        }
    }
    public void test_wrong_major_roslyn_is_rejected_and_clean_incremental_outputs_remain_compatible()
    {
        foreach(string name in new[]{"Directory.Build.props","NuGet.Config","global.json"})
            File.Copy(Path.Combine(Fixture.Repo,name),Path.Combine(f.Root,name),true);
        string authoring=Path.Combine(f.Root,"authoring"),core=Path.Combine(f.Root,"core");
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"targets","element-authoring"),authoring);
        Fixture.CopyTree(Path.Combine(Fixture.Repo,"src","Confectory.Core"),core);
        foreach(string directory in new[]{Path.Combine(authoring,"bin"),Path.Combine(core,"bin")})
            if(Directory.Exists(directory))Directory.Delete(directory,true);
        string project=Path.Combine(authoring,"Confectory.ElementAuthoring.csproj");
        File.WriteAllText(project,File.ReadAllText(project).Replace("../../src/Confectory.Core/Confectory.Core.csproj","../core/Confectory.Core.csproj",StringComparison.Ordinal));
        string host=Processes.DotNet();
        var clean=Processes.Run(new[]{host,"build",project,"-c","Release","--nologo"},directory:f.Root);
        True(clean.ExitCode==0,clean.Stdout+clean.Stderr);
        string output=Path.Combine(authoring,"bin","Release","net10.0");
        string[] libraries={"Confectory.ElementAuthoring.dll","Microsoft.CodeAnalysis.dll","Microsoft.CodeAnalysis.CSharp.dll"};
        string[] hashes=libraries.Select(name=>Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(Path.Combine(output,name))))).ToArray();
        foreach(string name in libraries)
        {
            using var stream=File.OpenRead(Path.Combine(output,name));using var pe=new PEReader(stream);var metadata=pe.GetMetadataReader();
            True(metadata.AssemblyReferences.Any(handle=>{var reference=metadata.GetAssemblyReference(handle);return metadata.GetString(reference.Name)=="System.Runtime"&&reference.Version.Major<=10;}),name+" must remain compatible with System.Runtime10");
        }
        var incremental=Processes.Run(new[]{host,"build",project,"-c","Release","--nologo"},directory:f.Root);
        True(incremental.ExitCode==0,incremental.Stdout+incremental.Stderr);
        Sequence(hashes,libraries.Select(name=>Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(Path.Combine(output,name))))).ToArray());
        var request=new JsonObject{["operation"]="algorithmProject",["contract"]="function Demo::Move () -> int {}",["implementation"]="implementation Demo::MoveBody for Demo::Move () -> int { body common \"move.csbody\"; }",["body"]="return 1;"};
        var executed=Processes.Run(new[]{host,Path.Combine(output,"Confectory.ElementAuthoring.dll")},input:request.ToJsonString(),directory:f.Root);
        True(executed.ExitCode==0,executed.Stdout+executed.Stderr);Equal("syntax-projected",JsonNode.Parse(executed.Stdout)!["result"]!["status"]!.GetValue<string>());
        string fake=Path.Combine(f.Root,"wrong-major");Directory.CreateDirectory(fake);
        File.WriteAllText(Path.Combine(fake,"Wrong.csproj"),"<Project Sdk=\"Microsoft.NET.Sdk\"><PropertyGroup><AssemblyName>Microsoft.CodeAnalysis</AssemblyName><AssemblyVersion>4.9.0.0</AssemblyVersion></PropertyGroup></Project>");
        File.WriteAllText(Path.Combine(fake,"Marker.cs"),"public class WrongMajorFixture { }");
        var fakeBuild=Processes.Run(new[]{host,"build",Path.Combine(fake,"Wrong.csproj"),"-c","Release","--nologo"},directory:f.Root);
        True(fakeBuild.ExitCode==0,fakeBuild.Stdout+fakeBuild.Stderr);
        string wrong=Path.Combine(fake,"bin","Release","net10.0");
        File.Copy(Path.Combine(output,"Microsoft.CodeAnalysis.CSharp.dll"),Path.Combine(wrong,"Microsoft.CodeAnalysis.CSharp.dll"));
        // Synthetic major4 fixture exercises validation; it is not SDK10 or Roslyn5 execution coverage.
        var rejected=Processes.Run(new[]{host,"msbuild",project,"-target:ValidateAuthoringSdk","-property:ConfectoryRoslynDirectory="+wrong,"-nologo"},directory:f.Root);
        True(rejected.ExitCode!=0,rejected.Stdout+rejected.Stderr);
        True((rejected.Stdout+rejected.Stderr).Contains("Wrong-major Roslyn library",StringComparison.Ordinal),rejected.Stdout+rejected.Stderr);
        True(!((rejected.Stdout+rejected.Stderr).Contains("CS1705",StringComparison.Ordinal)),rejected.Stdout+rejected.Stderr);
    }
}
