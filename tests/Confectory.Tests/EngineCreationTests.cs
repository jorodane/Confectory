using Confectory.Core;
namespace Confectory.Tests;
public sealed class EngineCreationTests : TestCase
{
 public void test_actual_engine_only_project_proposals_local_confirmation_and_retirement()
 {
  string consumer=Path.Combine(f.Root,"creation-consumer");Fixture.CopyTree(Path.Combine(Fixture.Repo,"examples","editor-home"),consumer);
  foreach(string file in Directory.GetFiles(consumer,"*.cpack"))File.WriteAllText(file,File.ReadAllText(file).Replace("../../",Fixture.Repo+"/",StringComparison.Ordinal));
  string body=Path.Combine(consumer,"VerifyBody.celem");File.WriteAllText(body,File.ReadAllText(body).Replace("body common", "import Confectory.EditorHome.Model::McpBridge as McpBridge (string,string,string) -> string;\nbody common",StringComparison.Ordinal));
  File.WriteAllText(Path.Combine(consumer,"Verify.csbody"),"""
  void Check(bool ok,string message){if(!ok)throw new Exception(message);}
  string root=Environment.GetEnvironmentVariable("CONFECTORY_CREATION_FIXTURE")!,repo=Environment.GetEnvironmentVariable("CONFECTORY_EDITOR_REPO")!;
  string session=calls.CreateSession.Invoke(repo,System.IO.Path.Combine(root,"settings"));
  System.Text.Json.Nodes.JsonNode M(string operation,object value)=>System.Text.Json.Nodes.JsonNode.Parse(calls.McpBridge.Invoke(session,operation,System.Text.Json.JsonSerializer.Serialize(value)))!;
  System.Text.Json.Nodes.JsonNode S()=>System.Text.Json.Nodes.JsonNode.Parse(calls.Snapshot.Invoke(session))!;
  bool Refused(Action action){try{action();return false;}catch{return true;}}
  try{
   var connected=M("start",new{});string instance=connected["instance"]!.ToString();Check(connected["scope"] is null&&S()["selected"] is null,"engine before project");
   string nonce="",sid="";
   void Pair(){nonce=M("site-prepare",new{})["nonce"]!.ToString();sid=Guid.NewGuid().ToString("N");M("site-message",new{type="paired",nonce,sessionId=sid,expiresAt=DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()+600000});}
   System.Text.Json.Nodes.JsonNode Call(string name,object args,string callId="owned-call")=>M("site-message",new{type="dispatch",nonce,sessionId=sid,job=new{instanceId=instance,scopeVersion=0,scopeId="",projectId="",callId,name,arguments=args}})["value"]!;
   Pair();var pulse=M("site-message",new{type="pulse",nonce,sessionId=sid});Check(pulse["scope"] is null&&pulse["tools"]!.AsArray().Count==3,"only engine-level definitions before project");
   var options=Call("engine_project_options",new{});Check(options["templates"]![0]!["buildTargets"]!.AsArray().Count==3&&!options.ToJsonString().Contains(repo),"actual supported options without paths");
   var args=new{title="Fixture Created",description="User reviewed this description",intent="Please propose a new project",templateId="empty-projectpack",targetId="dotnet"};
   var proposal=Call("engine_project_propose",args);string id=proposal["id"]!.ToString();Check(proposal["status"]!.ToString()=="pending"&&proposal["projectId"] is null&&!proposal["projectAccessGranted"]!.GetValue<bool>(),"proposal only");
   Check(Call("engine_project_propose",args)["id"]!.ToString()==id,"duplicate call once");Check(S()["selected"] is null&&!System.IO.Directory.Exists(System.IO.Path.Combine(root,args.title)),"proposal never creates or selects a project");
   Check(Refused(()=>Call("engine_project_propose",new{title="Changed",description="",intent="Explicit",templateId="empty-projectpack",targetId="dotnet"})),"changed duplicate refused");
   Check(Refused(()=>Call("engine_project_propose",new{args.title,args.description,args.intent,args.templateId,args.targetId,directory=root},"bad-path")),"no remote parent-folder argument");
   Check(Refused(()=>Call("workspace_read",new{id="foreign"},"read")),"no workspace access at scope null");Check(Refused(()=>Call("engine_project_confirm",new{proposalId=id},"confirm")),"no remote creation confirmation");
   Check(M("creation-review",new{proposalId=id})["title"]!.ToString()==args.title,"same proposal reviewed locally");
   M("creation-confirm",new{proposalId=id,directory=root,args.title,args.description});string project=System.IO.Path.Combine(root,args.title,"project.cproj");Check(System.IO.File.Exists(project)&&System.IO.File.ReadAllText(System.IO.Path.Combine(root,args.title,"main.csbody"))=="return 0;\n","existing atomic creator used only after explicit fixture confirmation");
   Check(M("status",new{})["scope"] is null&&M("site-message",new{type="pulse",nonce,sessionId=sid})["scope"] is null,"creation never grants project access");
   var result=Call("engine_project_status",new{proposalId=id},"status");Check(result["status"]!.ToString()=="created"&&!result["projectAccessGranted"]!.GetValue<bool>()&&!result.ToJsonString().Contains(root),"sanitized created receipt");
   Check(Refused(()=>M("creation-confirm",new{proposalId=id,directory=root,args.title,args.description})),"no duplicate creation");
   calls.Command.Invoke(session,"leave","{}");var pending=Call("engine_project_propose",new{title="Never Created",description="",intent="Explicit proposal",templateId="empty-projectpack",targetId="dotnet"},"later");
   M("site-message",new{type="close",nonce,sessionId=sid});Check(Refused(()=>M("creation-confirm",new{proposalId=pending["id"]!.ToString(),directory=root,title="Never Created",description=""})),"disconnect retires pending confirmation");
   Pair();Check(Refused(()=>Call("engine_project_status",new{proposalId=id},"foreign-owner")),"new connection cannot read another connection's proposal");
   Check(!System.IO.Directory.Exists(System.IO.Path.Combine(root,"Never Created")),"retired proposal creates no files");
   nonce=M("site-prepare",new{})["nonce"]!.ToString();sid=Guid.NewGuid().ToString("N");M("site-message",new{type="paired",nonce,sessionId=sid,expiresAt=DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()+1000});
   var expiring=Call("engine_project_propose",new{title="Expired Proposal",description="",intent="Explicit proposal",templateId="empty-projectpack",targetId="dotnet"},"expiry");System.Threading.Thread.Sleep(1100);
   Check(Refused(()=>M("creation-confirm",new{proposalId=expiring["id"]!.ToString(),directory=root,title="Expired Proposal",description=""})),"expired connection cannot confirm");Check(!System.IO.Directory.Exists(System.IO.Path.Combine(root,"Expired Proposal")),"expired proposal creates no files");
   M("stop",new{});M("start",new{});Check(S()["engineCreationProposal"] is null&&M("status",new{})["scope"] is null,"restart never restores proposal or grant");
   Console.WriteLine("PASS actual engine-only creation options/proposal/duplicate/local-confirm/no-auto-scope/disconnect/restart");return 0;
  }finally{calls.CloseSession.Invoke(session);}
  """);
  string root=Path.Combine(f.Root,"owned-created-projects");Directory.CreateDirectory(root);
  string? repo=Environment.GetEnvironmentVariable("CONFECTORY_EDITOR_REPO"),fixture=Environment.GetEnvironmentVariable("CONFECTORY_CREATION_FIXTURE"),discovery=Environment.GetEnvironmentVariable("CONFECTORY_MCP_DIRECTORY");
  try{
   Environment.SetEnvironmentVariable("CONFECTORY_EDITOR_REPO",Fixture.Repo);Environment.SetEnvironmentVariable("CONFECTORY_CREATION_FIXTURE",root);Environment.SetEnvironmentVariable("CONFECTORY_MCP_DIRECTORY",Path.Combine(root,"private-mcp"));
   var built=new Builder(Path.Combine(consumer,"verify.cpack"),"linux").Build();var run=Processes.Run(Strings(built,"run"),timeoutSeconds:180);Console.WriteLine(run.Stdout.Trim());True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual engine-only creation"));
  }finally{Environment.SetEnvironmentVariable("CONFECTORY_EDITOR_REPO",repo);Environment.SetEnvironmentVariable("CONFECTORY_CREATION_FIXTURE",fixture);Environment.SetEnvironmentVariable("CONFECTORY_MCP_DIRECTORY",discovery);}
 }
}
