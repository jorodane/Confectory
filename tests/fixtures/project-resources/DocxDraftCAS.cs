using System.Text.Json.Nodes;
using System.Text;
using System.Security.Cryptography;
class Calls{
 public Func<string[],string,string[]> Context=null!;
 public Func<string[],string,string> Identity=null!;
 public Func<string,string,string,string,string> Layout=(a,b,c,d)=>throw new Exception("draft touched project content");
 public Func<string,string,string,string,string> Request=(a,b,c,d)=>throw new Exception("draft touched immutable import");
 public Func<string,int,string[]> DraftSnapshot=Program.Snapshot;
 public Func<string,string,string[]> DraftCommit=null!;
 public Func<string,string> LeasePath=Program.Lease;
 public Action<string,string> WriteAtomic=Program.Write;
}
class Program{
 public static string Resources(string session,string operation,string payload,Calls calls){DRAFT_BODY}
 public static string[] Snapshot(string path,int limit){SNAPSHOT_BODY}
 public static string[] Plan(string root,string plan,Calls calls){PLAN_BODY}
 public static void Write(string path,string text){WRITE_BODY}
 public static string Lease(string root){LEASE_BODY}
 static void Check(bool value,string text){if(!value)throw new Exception(text);Console.WriteLine("PASS "+text);}
 static void Main(string[] args){
  string root=args[0],manifest=Path.Combine(root,"project.cproj"),home=Path.Combine(root,"profile"),project=Guid.NewGuid().ToString("N"),id=Guid.NewGuid().ToString("N"),session=Guid.NewGuid().ToString("N"),hash=new string('a',64);Directory.CreateDirectory(home);File.WriteAllText(manifest,"source");var owner=new object[7];owner[0]=Array.Empty<string>();owner[2]=Path.Combine(home,"projects.json");owner[3]=new JsonObject{["selected"]=new JsonObject{["context"]="context",["path"]=manifest,["projectId"]=project}};owner[6]=false;AppDomain.CurrentDomain.SetData("Confectory.EditorHome."+session,owner);var calls=new Calls{Context=(m,c)=>new[]{"",manifest,"","","","open"},Identity=(m,c)=>project};calls.DraftCommit=(r,p)=>Plan(r,p,calls);
  JsonObject Call(string action,JsonObject input){input["project"]=project;return JsonNode.Parse(Resources(session,"draft-"+action,input.ToJsonString(),calls))!.AsObject();}
  var first=Call("load",new(){["id"]=id});Check(first["revision"]!.ToString()=="missing"&&first["value"]is null,"private draft absent without project content access");string a=Convert.ToBase64String(Encoding.UTF8.GetBytes(new string('A',1048576))),b=Convert.ToBase64String(Encoding.UTF8.GetBytes(new string('B',1048576))),command=Guid.NewGuid().ToString("N");var pending=new JsonObject{["action"]="save-content",["input"]=new JsonObject{["revision"]=hash,["command"]=command,["id"]=id,["hash"]=hash,["type"]="text/plain",["size"]=1048576}};var value=new JsonObject{["generation"]=hash,["hash"]=hash,["revision"]=hash,["encoding"]="utf-8",["data"]=a,["pending"]=pending};
  var request=new JsonObject{["id"]=id,["revision"]="missing",["value"]=value.DeepClone()};Check(request.ToJsonString().Length<2097152,"full-size pending draft request stays below unchanged 2MiB transport cap");var saved=Call("save",request);Check(Call("save",request)["revision"]!.ToString()==saved["revision"]!.ToString(),"lost private save reply accepts exact candidate without rebasing another value");value["data"]=b;var later=Call("save",new(){["id"]=id,["revision"]=saved["revision"]!.DeepClone(),["value"]=value.DeepClone()});
  var read=Call("load",new(){["id"]=id});Check(read.ToJsonString().Length<2097152&&read["value"]!["data"]!.ToString()==b&&read["value"]!["pending"]!["input"]!["data"]is null,"current full-size late input is separately readable within transport cap");var staged=Call("pending",new(){["id"]=id});Check(staged.ToJsonString().Length<2097152&&staged["pending"]!["input"]!["data"]!.ToString()==a,"full-size exact pending bytes survive newer input and independent observation");
  bool rejected=false;try{Call("save",request);}catch{rejected=true;}Check(rejected,"old private input cannot replace newer acknowledged input");string file=Directory.GetFiles(home,"*.json",SearchOption.AllDirectories).Single(),prior=File.ReadAllText(file);calls.DraftCommit=(r,p)=>{File.AppendAllText(file," ");return Plan(r,p,calls);};rejected=false;try{Call("save",new(){["id"]=id,["revision"]=later["revision"]!.DeepClone(),["value"]=null});}catch{rejected=true;}Check(rejected&&File.ReadAllText(file)==prior+" ","private final-CAS race preserves peer bytes and pending intent");Check(File.ReadAllText(manifest)=="source","private draft never writes project source or immutable resources");
  calls.DraftCommit=(r,p)=>Plan(r,p,calls);string docxId=Guid.NewGuid().ToString("N");var changes=new JsonObject{["p:0"]=new string('\0',98304)};var docx=new JsonObject{["generation"]=hash,["hash"]=hash,["revision"]=hash,["encoding"]="docx-v1",["data"]=a,["changes"]=changes,["pending"]=new JsonObject{["action"]="save-content",["input"]=new JsonObject{["revision"]=hash,["command"]=Guid.NewGuid().ToString("N"),["id"]=docxId,["hash"]=hash,["type"]="application/vnd.openxmlformats-officedocument.wordprocessingml.document",["size"]=1048576}}};
  var docxRequest=new JsonObject{["id"]=docxId,["revision"]="missing",["value"]=docx.DeepClone()};Check(Encoding.UTF8.GetByteCount(docxRequest.ToJsonString())<2097152,"full-size DOCX plus worst escaped 96Ki character input fits unchanged transport");var docxSaved=Call("save",docxRequest);var docxRead=Call("load",new(){["id"]=docxId});Check(docxRead["value"]!["changes"]!["p:0"]!.ToString().Length==98304&&docxRead["value"]!["data"]!.ToString()==a,"full-size DOCX private input survives independent native read");Check(Call("pending",new(){["id"]=docxId})["pending"]!["input"]!["data"]!.ToString()==a,"binary intended ZIP is reconstructed once without duplicating request data");
  docx["changes"]!["p:0"]="late paragraph";var docxLater=Call("save",new(){["id"]=docxId,["revision"]=docxSaved["revision"]!.DeepClone(),["value"]=docx.DeepClone()});Check(Call("pending",new(){["id"]=docxId})["pending"]!["input"]!["data"]!.ToString()==a,"late DOCX paragraph input never replaces frozen pending ZIP");
  bool Bad(JsonObject candidate){try{Call("save",new(){["id"]=docxId,["revision"]=docxLater["revision"]!.DeepClone(),["value"]=candidate});return false;}catch{return true;}}var invalid=docx.DeepClone().AsObject();invalid["changes"]!["p:1500"]="unsupported";Check(Bad(invalid),"DOCX private field index is bounded");invalid=docx.DeepClone().AsObject();invalid["changes"]!["p:0"]=new string('x',98305);Check(Bad(invalid),"DOCX change budget cannot bypass native private validation");invalid=docx.DeepClone().AsObject();invalid["encoding"]="other";Check(Bad(invalid),"unknown private codec cannot bypass the exact schema");
  Check(File.ReadAllText(manifest)=="source","DOCX recovery remains private and never writes source/contracts");
 }
}
