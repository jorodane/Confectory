using System.Text;
using System.Text.Json;
using Confectory.Core;

if(args.Length is < 2 or > 3 || (args.Length == 3 && args[2] != "--package")){Console.Error.WriteLine("Usage: AndroidExport <ProjectPack> <new-output-directory> [--package]");return 2;}
string project=Path.GetFullPath(args[0]),output=Path.GetFullPath(args[1]);
if(Directory.Exists(output)){Console.Error.WriteLine("Output directory must be new; preserve existing exports.");return 2;}
var builder=new Builder(project,"android");
var settings=ExportSettings.Read(builder.Registry);
var report=builder.Build();
var registry=builder.Registry;
var statistics=builder.Statistics;
var plan=new Planner(registry,"android").Plan();
var entry=registry.Project.Entry!;var binding=plan.Bindings[new(entry,entry)];
Directory.CreateDirectory(output);string generated=Path.Combine(output,"Generated");Directory.CreateDirectory(generated);
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
var facade=new StringBuilder("namespace Confectory.Android;\npublic static class PackCalls\n{\n");
foreach(var (alias,imported) in binding.Imports.OrderBy(x=>x.Key,StringComparer.Ordinal))
{
 var signature=registry.Get(imported[1],"function").Signature!;
 var names=signature.Args.Select(x=>x.Name).ToArray();
 var parameters=string.Join(", ",signature.Args.Select(x=>x.Type+" "+x.Name));
 facade.AppendLine($" public static {signature.Return} {alias}({parameters}) {{ {(signature.Return=="void"?"":"return ")}new {Generation.BindingSymbol(new(imported[0],imported[1]))}().Invoke({string.Join(", ",names)}); }}");
}
facade.AppendLine("}");File.WriteAllText(Path.Combine(generated,"PackCalls.cs"),facade.ToString());
string templateRoot=Path.Combine(AppContext.BaseDirectory,"templates");
File.Copy(PackPaths.Owned(Path.GetDirectoryName(registry.Paths["Confectory.Window"])!,"android/AndroidSurfaceBridge.cs"),Path.Combine(output,"AndroidSurfaceBridge.cs"));
bool home=registry.Project.Namespace=="Confectory.EditorHome";
File.Copy(Path.Combine(templateRoot,home?"EditorHomeActivity.cs":"MainActivity.cs"),Path.Combine(output,"MainActivity.cs"));
if(home){File.Copy(Path.Combine(templateRoot,"NativeFieldHost.cs"),Path.Combine(output,"NativeFieldHost.cs"));string core=typeof(Parser).Assembly.Location;File.Copy(core,Path.Combine(managed,"Confectory.Core.dll"),true);if(!references.Contains("Confectory.Core.dll"))references.Add("Confectory.Core.dll");}
string projectText=File.ReadAllText(Path.Combine(templateRoot,"App.csproj.template"));
projectText=settings.Apply(projectText);
string referenceItems=string.Join("\n",references.Select(name=>$"<Reference Include=\"{Path.GetFileNameWithoutExtension(name)}\"><HintPath>Managed/{name}</HintPath></Reference>"));
File.WriteAllText(Path.Combine(output,"Confectory.Android.csproj"),projectText.Replace("</Project>","<ItemGroup>\n"+referenceItems+"\n</ItemGroup>\n</Project>",StringComparison.Ordinal));
File.WriteAllText(Path.Combine(output,"export-report.json"),JsonSerializer.Serialize(new{kind="android-source-export",managedCompiled=true,androidAppCompiled=false,apkProduced=false,project=registry.Project.Namespace,entry,bodySelections=selections,contracts,statistics},JsonData.Options));
if(args.Length==3)return UnsignedPackage.Build(output,settings);
Console.WriteLine(JsonSerializer.Serialize(new{output,managedCompiled=true,androidAppCompiled=false,apkProduced=false,implementations=selections.Count,contracts=contracts.Length}));return 0;
