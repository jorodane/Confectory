using System.Text.Json;
using Confectory.Core;

if(args.Length==3&&args[0]=="--sign-export")return Confectory.AndroidExport.LocalSigning.Interactive(args[1],args[2]);
if(args.Length==2&&args[0]=="--inspect-package")return Confectory.AndroidExport.NativePackageInspection.Inspect(args[1]);
if(args.Length is < 2 or > 3 || (args.Length == 3 && args[2] != "--package")){Console.Error.WriteLine("Usage: AndroidExport <ProjectPack> <new-output-directory> [--package]");return 2;}
string project=Path.GetFullPath(args[0]),output=Path.GetFullPath(args[1]);
if(Directory.Exists(output)){Console.Error.WriteLine("Output directory must be new; preserve existing exports.");return 2;}
var builder=new Builder(project,"android");
var settings=ExportSettings.Read(builder.Registry);
string? packageSdk=null;
if(args.Length==3)
{
    string androidDotnet=Environment.GetEnvironmentVariable("CONFECTORY_ANDROID_DOTNET")??Processes.DotNet();
    var sdk=Processes.Run(new[]{androidDotnet,"--list-sdks"},directory:Path.GetTempPath(),timeoutSeconds:30);
    string required=settings.Framework.Split('.')[0][3..];
    packageSdk=sdk.Stdout.Split('\n').Select(line=>line.Trim().Split(' ')[0]).Where(version=>version.StartsWith(required+".",StringComparison.Ordinal)&&Version.TryParse(version,out _)).OrderBy(version=>Version.Parse(version)).LastOrDefault();
    if(sdk.ExitCode!=0||packageSdk is null)
    {Console.Error.WriteLine($"Install .NET {required} SDK with its Android workload for {settings.Framework}; set CONFECTORY_ANDROID_DOTNET to its installed host. No package built.");return 1;}
}
var report=builder.Build();
var registry=builder.Registry;
var statistics=builder.Statistics;
var plan=new Planner(registry,"android").Plan();
var entry=registry.Project.Entry!;
string linkedCatalog=report["publicCatalog"]?.GetValue<string>()??throw new InvalidOperationException("Public linkage metadata resource missing");
Directory.CreateDirectory(output);string generated=Path.Combine(output,"Generated");Directory.CreateDirectory(generated);
if(packageSdk is not null)File.WriteAllText(Path.Combine(output,"global.json"),JsonSerializer.Serialize(new{sdk=new{version=packageSdk,rollForward="latestPatch",allowPrerelease=false}}));
var contracts=plan.Bindings.Values.Select(x=>x.Function).Concat(plan.Implementations.Values.Select(x=>x.Function!)).Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal).ToArray();
string managed=Path.Combine(output,"Managed");Directory.CreateDirectory(managed);
string compiledOutput=report["output"]!.GetValue<string>();
var references=new List<string>();
foreach(string path in Directory.GetFiles(compiledOutput,"*.dll").Where(x=>Path.GetFileName(x)!="Confectory.App.dll").Order(StringComparer.Ordinal))
{
 File.Copy(path,Path.Combine(managed,Path.GetFileName(path)));references.Add(Path.GetFileName(path));
}
var selections=plan.Implementations.Values.OrderBy(x=>x.Id,StringComparer.Ordinal).Select(x=>(object)new{id=x.Id,selection=x.Bodies.ContainsKey("android")?"android":"common"}).ToList();
File.WriteAllText(Path.Combine(generated,"Bindings.cs"),Generation.FinalSource(plan));
string invocation=$"new {Generation.BindingSymbol(new(entry,entry))}().Invoke()";
string entryStatement=registry.Get(entry).Signature!.Return=="int"?$"return {invocation};":$"{invocation}; return 0;";
File.WriteAllText(Path.Combine(generated,"PackEntry.cs"),$"namespace Confectory.Android;\npublic static class PackEntry {{ public static int Run() {{ {entryStatement} }} }}\n");
string templateRoot=Path.Combine(AppContext.BaseDirectory,"templates");
File.Copy(Path.Combine(templateRoot,"AndroidManifest.xml"),Path.Combine(output,"AndroidManifest.xml"));
var androidManifest=System.Xml.Linq.XDocument.Load(Path.Combine(output,"AndroidManifest.xml"));
androidManifest.Root!.Element("uses-sdk")!.SetAttributeValue(System.Xml.Linq.XName.Get("minSdkVersion","http://schemas.android.com/apk/res/android"),settings.MinSdk);
androidManifest.Root!.Element("uses-sdk")!.SetAttributeValue(System.Xml.Linq.XName.Get("targetSdkVersion","http://schemas.android.com/apk/res/android"),settings.TargetSdk);
androidManifest.Save(Path.Combine(output,"AndroidManifest.xml"));
File.WriteAllText(Path.Combine(output,"bundle-config.json"),JsonSerializer.Serialize(new{optimizations=new{uncompressNativeLibraries=new{enabled=true,alignment="PAGE_ALIGNMENT_16K"}}}));
foreach(string template in new[]{"GenericActivity.cs","NativeFieldHost.cs","AndroidDocumentImport.cs","MetadataAuthoring.cs"})
 File.Copy(Path.Combine(templateRoot,template),Path.Combine(output,template=="GenericActivity.cs"?"MainActivity.cs":template));
string resourceValues=Path.Combine(output,"Resources","values");Directory.CreateDirectory(resourceValues);
File.Copy(Path.Combine(templateRoot,"NativeFieldStyle.xml"),Path.Combine(resourceValues,"NativeFieldStyle.xml"));
string core=typeof(Parser).Assembly.Location;File.Copy(core,Path.Combine(managed,"Confectory.Core.dll"),true);
if(!references.Contains("Confectory.Core.dll"))references.Add("Confectory.Core.dll");
string projectText=File.ReadAllText(Path.Combine(templateRoot,"App.csproj.template"));
projectText=settings.Apply(projectText);
File.Copy(linkedCatalog,Path.Combine(output,"public-linkage.json"));
projectText=projectText.Replace("</Project>","<ItemGroup><EmbeddedResource Include=\"public-linkage.json\"><LogicalName>public-linkage.json</LogicalName></EmbeddedResource></ItemGroup></Project>",StringComparison.Ordinal);
string referenceItems=string.Join("\n",references.Select(name=>$"<Reference Include=\"{Path.GetFileNameWithoutExtension(name)}\"><HintPath>Managed/{name}</HintPath></Reference>"));
File.WriteAllText(Path.Combine(output,"Confectory.Android.csproj"),projectText.Replace("</Project>","<ItemGroup>\n"+referenceItems+"\n</ItemGroup>\n</Project>",StringComparison.Ordinal));
File.WriteAllText(Path.Combine(output,"export-report.json"),JsonSerializer.Serialize(new{kind="android-source-export",managedCompiled=true,androidAppCompiled=false,apkProduced=false,project=registry.Project.Namespace,entry,bodySelections=selections,contracts,statistics},JsonData.Options));
if(args.Length==3)return UnsignedPackage.Build(output,settings);
Console.WriteLine(JsonSerializer.Serialize(new{output,managedCompiled=true,androidAppCompiled=false,apkProduced=false,implementations=selections.Count,contracts=contracts.Length}));return 0;
