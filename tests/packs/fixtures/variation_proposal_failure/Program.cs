using System.Diagnostics;
using System.Text.Json.Nodes;
if(Environment.GetEnvironmentVariable("CONFECTORY_VARIATION_FAILURE_FIXTURE")!="1")throw new Exception("Explicit synthetic fixture mode required");
string actual=Environment.GetEnvironmentVariable("CONFECTORY_REAL_AUTHOR")??throw new Exception("Fixture-only real author path needed");
var spec=new ProcessStartInfo(Environment.GetEnvironmentVariable("CONFECTORY_DOTNET")??"dotnet"){UseShellExecute=false};
spec.ArgumentList.Add(actual);
foreach(string arg in args)spec.ArgumentList.Add(arg);
if(args.Length!=0){using var stream=Process.Start(spec)!;stream.WaitForExit();return stream.ExitCode;}
string input=Console.In.ReadToEnd();
var request=JsonNode.Parse(input)!.AsObject();
if(request["operation"]?.ToString()=="prepareExistingSchemaObjectVariation"){
 string manifest=request["manifest"]!.GetValue<string>(),id=request["id"]!.GetValue<string>(),local=id[(id.IndexOf("::",StringComparison.Ordinal)+2)..];
 if(id!="Project.Timing_Puzzle::TimingRulesBatchCase"||request["parent"]?.ToString()!="Project.Timing_Puzzle::TimingRules")throw new Exception("Fixture-only injected duplicate required");
 int end=manifest.LastIndexOf('}');request["manifest"]=manifest.Insert(end,$"\n element {local} object \"elements/{local}.celem\";\n");
 input=request.ToJsonString();
}
spec.RedirectStandardInput=true;spec.RedirectStandardOutput=true;spec.RedirectStandardError=true;
using var host=Process.Start(spec)!;
var output=host.StandardOutput.ReadToEndAsync();var error=host.StandardError.ReadToEndAsync();
host.StandardInput.Write(input);host.StandardInput.Close();host.WaitForExit();
Console.Out.Write(output.GetAwaiter().GetResult());Console.Error.Write(error.GetAwaiter().GetResult());return host.ExitCode;
