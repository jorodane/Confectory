using Confectory.Core;
namespace Confectory.Tests;
public sealed class RelationsMapTests : TestCase
{
    public void test_owned_declared_map_drafts_external_references_partial_sources_and_read_only_review()
    {
        f.Add("App", "object", "Parent", "object App::Parent { value count = 3; }");
        f.Add("App", "object", "Child", "object App::Child extends App::Parent {value editorName = \"Actual child\"; use object App::Parent; data peer = App::Parent;}");
        f.Add("App", "object", "Broken", "object App::Broken {}");
        f.Add("App", "module", "Relations", "module App::Relations {require Api::Value (int) -> int; default Api::Value with Provider::ValueBody;contain object App::Child;}"); f.Sync();
        File.WriteAllText(Path.Combine(f.Packs["App"].Root, "Broken.celem"), "invalid owned declaration");
        // Metadata must never traverse this unconfigured registry or execute the source's entry.
        File.WriteAllText(f.Project, File.ReadAllText(f.Project).Replace("entry App::Main;", "entry App::Main;registry NeverRead \"../../missing-must-not-read.cpack\";"));
        string sample=Path.Combine(f.Root,"map-consumer");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples/edit-workspace"),sample);
        foreach(string name in new[]{"file-stream","schema-editing","edit-workspace","save","change-set","pack-workspace"})Fixture.CopyTree(Path.Combine(Fixture.Repo,"packs",name),Path.Combine(f.Root,"packs",name));
        string project=Path.Combine(sample,"project.cpack");File.WriteAllText(project,File.ReadAllText(project).Replace("../../packs/","../packs/").Replace("../../targets/dotnet/pack.cpack","../target/pack.cpack").Replace("element Main function","registry Confectory.PackWorkspace \"../packs/pack-workspace/pack.cpack\";dependency Confectory.PackWorkspace version \"0.1.0\";\nelement Main function"));
        File.WriteAllText(Path.Combine(sample,"main_body.celem"),"""
        implementation Example.EditWorkspace::MainBody for Example.EditWorkspace::Main () -> int {
        import Confectory.PackWorkspace::Open as Open (string,string,string) -> string;
        import Confectory.PackWorkspace::Command as Command (string,string,string) -> string;
        import Confectory.PackWorkspace::Close as Close (string) -> void;
        body common "main.csbody";}
        """);
        File.WriteAllText(Path.Combine(sample,"main.csbody"),"""
        void Check(bool ok,string message){if(!ok)throw new Exception(message);}
        string project=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT")!,source=System.IO.Path.Combine(System.IO.Path.GetDirectoryName(project)!,"Child.celem"),original=System.IO.File.ReadAllText(source);
        string view=calls.Open.Invoke(project,"owner","map"),peer=calls.Open.Invoke(project,"owner","map");
        calls.Command.Invoke(view,"select","{\"id\":\"App::Child\"}");
        var first=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(view,"relations-map","{}"))!;var map=first["relationsMap"]!;
        Check(first["unit"]!["id"]!.ToString()=="App::Child"&&map["scope"]!.ToString()=="owned-workspace-declarations"&&map["status"]!.ToString()=="partial","read-only source scope and selection");
        Check(System.Linq.Enumerable.Any(map["nodes"]!.AsArray(),n=>n!["id"]!.ToString()=="App::Child"&&n["title"]!.ToString()=="Actual child"&&n["owned"]!.GetValue<bool>()),"actual title and source identity");
        Check(System.Linq.Enumerable.Any(map["nodes"]!.AsArray(),n=>n!["id"]!.ToString()=="App::Broken"&&!n["valid"]!.GetValue<bool>()&&!string.IsNullOrWhiteSpace(n["error"]!.ToString())),"malformed source is explicit, not a demo replacement");
        Check(System.Linq.Enumerable.Any(map["nodes"]!.AsArray(),n=>n!["id"]!.ToString()=="Api::Value"&&!n["owned"]!.GetValue<bool>()&&n["availability"]!.ToString()=="outside-owned-view"),"outside-view reference is not falsely missing");
        foreach(string role in new[]{"parent","use","data"})Check(System.Linq.Enumerable.Any(map["edges"]!.AsArray(),e=>e!["source"]!.ToString()=="App::Child"&&e["target"]!.ToString()=="App::Parent"&&e["role"]!.ToString()==role),"actual declared relation "+role);
        var repeated=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(view,"relations-map","{}"))!["relationsMap"]!;Check(repeated["version"]!.ToString()==map["version"]!.ToString(),"stable repeated source snapshot");
        string changed=original.Replace("Actual child","Pending child",StringComparison.Ordinal).Replace("use object App::Parent;","use object App::Parent;module Missing::Role;",StringComparison.Ordinal);
        var edited=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(view,"edit",System.Text.Json.JsonSerializer.Serialize(new{text=changed,expectedRevision=0})))!;Check(!edited["conflict"]!.GetValue<bool>(),"actual shared draft edit");
        var review=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(view,"review","{\"target\":\"portable\"}"))!["review"]!;
        var fresh=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(view,"relations-map","{}"))!;
        Check(fresh["review"]!["token"]!.ToString()==review["token"]!.ToString(),"map read preserves exact review");
        Check(fresh["relationsMap"]!["version"]!.ToString()!=map["version"]!.ToString()&&System.Linq.Enumerable.Any(fresh["relationsMap"]!["nodes"]!.AsArray(),n=>n!["id"]!.ToString()=="App::Child"&&n["title"]!.ToString()=="Pending child"&&n["dirty"]!.GetValue<bool>()),"working draft map refresh");
        var shared=System.Text.Json.Nodes.JsonNode.Parse(calls.Command.Invoke(peer,"relations-map","{}"))!["relationsMap"]!;Check(shared["version"]!.ToString()==fresh["relationsMap"]!["version"]!.ToString(),"shared draft across independent views");
        Check(System.IO.File.ReadAllText(source)==original,"map and Review preserve final source");calls.Close.Invoke(peer);calls.Close.Invoke(view);
        Console.WriteLine("Owned declaration map real edges/drafts/partial/outside references/review/read-only PASS");return 0;
        """);
        string? host=Environment.GetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST"),selected=Environment.GetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT");
        try {Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",Path.Combine(Fixture.Repo,"targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll"));Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",f.Project);Output(new Builder(project,"portable").Build(),"Owned declaration map real edges/drafts/partial/outside references/review/read-only PASS");}
        finally{Environment.SetEnvironmentVariable("CONFECTORY_ELEMENT_AUTHORING_HOST",host);Environment.SetEnvironmentVariable("CONFECTORY_TEST_AUTHOR_PROJECT",selected);}
    }
}
