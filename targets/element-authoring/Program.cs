using Confectory.Core;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

try
{
    var request=JsonNode.Parse(Console.In.ReadToEnd())!.AsObject();
    string S(string name)=>request[name]!.GetValue<string>();
    JsonNode? reply;
    switch(S("operation"))
    {
        case "describe":
        {
            string project=Path.GetFullPath(S("project")),root=Path.GetDirectoryName(project)!;
            var manifest=new Parser(File.ReadAllText(project),project).ParseManifest();
            if(manifest.Kind!="project")throw new ArgumentException("Explicit ProjectPack required.");
            var units=new JsonArray();
            units.Add(new JsonObject{["id"]=manifest.Namespace+"::ProjectManifest",["kind"]="project",["path"]=Path.GetFileName(project)});
            foreach(var (name,locator) in manifest.Elements)
            {
                string path=Owned(root,locator.Path);var element=new Parser(File.ReadAllText(path),path).ParseElement();
                if(element.Id!=manifest.Namespace+"::"+name||element.Kind!=locator.Kind)throw new ArgumentException("Manifest/declaration identity mismatch.");
                units.Add(new JsonObject{["id"]=element.Id,["kind"]=element.Kind,["path"]=Path.GetRelativePath(root,path)});
                foreach(var (target,body) in element.Bodies)
                {
                    string bodyPath=Owned(root,Path.GetRelativePath(root,Path.Combine(Path.GetDirectoryName(path)!,body.Path)));
                    units.Add(new JsonObject{["id"]=element.Id+"/body:"+target,["kind"]="body",["path"]=Path.GetRelativePath(root,bodyPath)});
                }
            }
            reply=new JsonObject{["project"]=project,["namespace"]=manifest.Namespace,["units"]=units};break;
        }
        case "inspect":
        {
            var element=new Parser(S("text"),"<draft>").ParseElement();
            reply=new JsonObject{["id"]=element.Id,["kind"]=element.Kind,["parent"]=element.Parent,["values"]=JsonSerializer.SerializeToNode(element.Values.ToDictionary(x=>x.Key,x=>x.Value.Value))};break;
        }
        case "setValue":
        {
            var element=new Parser(S("text"),"<draft>").ParseElement();var value=JsonSerializer.SerializeToElement(request["value"]);
            if(value.ValueKind is not (JsonValueKind.String or JsonValueKind.Number or JsonValueKind.True or JsonValueKind.False))throw new ArgumentException("Scalar metadata required.");
            element.Values[S("field")]=new(value,element.Id,new());string formatted=Format(element);new Parser(formatted,"<draft>").ParseElement();reply=JsonValue.Create(formatted);break;
        }
        case "create":
        {
            string kind=S("kind"),id=S("id");if(kind is not ("category" or "concept" or "function" or "module" or "object" or "schema"))throw new ArgumentException("Unsupported authored kind.");
            string text=$"{kind} {id}"+(kind=="function"?" () -> int":"")+" { }\n";
            new Parser(text,"<new>").ParseElement();reply=JsonValue.Create(text);break;
        }
        case "register":
        {
            var manifest=new Parser(S("text"),"<draft>").ParseManifest();string id=S("id");
            if(!id.StartsWith(manifest.Namespace+"::",StringComparison.Ordinal))throw new ArgumentException("Creation belongs to selected project namespace.");
            string name=id[(manifest.Namespace.Length+2)..];manifest.Elements.Add(name,new(S("kind"),S("path"),new()));
            string text=FormatManifest(manifest);new Parser(text,"<draft>").ParseManifest();reply=JsonValue.Create(text);break;
        }
        case "prepare":
        {
            string original=Path.GetFullPath(S("original")),candidate=Path.GetFullPath(S("candidate"));
            var manifest=new Parser(File.ReadAllText(candidate),candidate).ParseManifest();
            foreach(var ns in manifest.Registry.Keys.ToArray())manifest.Registry[ns]=manifest.Registry[ns] with{Path=Path.GetFullPath(Path.Combine(Path.GetDirectoryName(original)!,manifest.Registry[ns].Path))};
            foreach(var item in request["additions"]!.AsArray())
            {
                string path=item!["path"]!.GetValue<string>(),kind=item["kind"]!.GetValue<string>(),id=item["id"]!.GetValue<string>();
                if(!id.StartsWith(manifest.Namespace+"::",StringComparison.Ordinal))throw new ArgumentException("Creation belongs to the selected project namespace.");
                string name=id[(manifest.Namespace.Length+2)..];manifest.Elements.Add(name,new(kind,path,new()));
            }
            reply=JsonValue.Create(FormatManifest(manifest));break;
        }
        case "run":
        {
            var built=new Builder(S("project"),S("target")).Build();var command=built["run"]!.AsArray().Select(x=>x!.GetValue<string>()).ToArray();
            var start=new System.Diagnostics.ProcessStartInfo(command[0]){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true};foreach(string part in command.Skip(1))start.ArgumentList.Add(part);
            using var process=System.Diagnostics.Process.Start(start)??throw new InvalidOperationException("Preview process did not start.");
            var output=process.StandardOutput.ReadToEndAsync();var errors=process.StandardError.ReadToEndAsync();
            if(!process.WaitForExit(15000)){process.Kill(true);process.WaitForExit();throw new TimeoutException("Preview stopped after 15 seconds.");}
            reply=new JsonObject{["exit"]=process.ExitCode,["stdout"]=output.GetAwaiter().GetResult(),["stderr"]=errors.GetAwaiter().GetResult()};break;
        }
        case "validate":
        {
            var builder=new Builder(S("project"),S("target"));builder.Validate();builder.Check(builder.Registry.Project.Namespace);builder.Build();
            reply=new JsonObject{["state"]="valid"};break;
        }
        default:throw new ArgumentException("Unknown authoring operation.");
    }
    Console.Write(JsonSerializer.Serialize(new{ok=true,result=reply}));return 0;
}
catch(Exception error)
{
    Console.Write(JsonSerializer.Serialize(new{ok=false,code=error is BuildError build?build.Diagnostic.Code:"AUTHORING",message=error.Message}));return 0;
}
static string Owned(string root,string relative)
{
    string full=Path.GetFullPath(Path.Combine(root,relative));
    if(Path.IsPathRooted(relative)||!full.StartsWith(root.TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar,OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal))throw new ArgumentException("Editable unit is outside project-owned root.");
    for(string? part=full;part is not null&&part.Length>=root.Length;part=Path.GetDirectoryName(part))
        if((File.Exists(part)||Directory.Exists(part))&&(File.GetAttributes(part)&FileAttributes.ReparsePoint)!=0)throw new ArgumentException("Editable units cannot traverse symlinks.");
    return full;
}
static string Quote(string text)=>JsonSerializer.Serialize(text);
static string Signature(FunctionSignature signature,bool named)=>"("+string.Join(", ",signature.Args.Select(x=>x.Type+(named?" "+x.Name:"")))+") -> "+signature.Return;
static string Format(Element element)
{
    var text=new StringBuilder(element.Kind+" "+element.Id);
    if(element.Kind=="implementation")text.Append(" for "+element.Function);
    if(element.Signature is not null)text.Append(" "+Signature(element.Signature,true));
    if(element.Parent is not null)text.Append(" extends "+element.Parent);
    text.AppendLine(" {");
    if(element.DescriptionPresent)text.AppendLine("description "+Quote(element.Description)+";");
    foreach(var value in element.Modules)text.AppendLine("module "+value.Id+";");
    foreach(var value in element.Includes)text.AppendLine("include "+value.Id+";");
    foreach(var (id,value) in element.Requires)text.AppendLine("require "+id+" "+Signature(value.Signature,false)+";");
    foreach(var (id,value) in element.Defaults)text.AppendLine("default "+id+" with "+value.Id+";");
    foreach(var (id,value) in element.Provides)text.AppendLine("provide "+id+" with "+value.Id+";");
    foreach(var value in element.Uses)text.AppendLine("use "+value.Kind+" "+value.Id+";");
    foreach(var value in element.Contains)text.AppendLine("contain "+value.Kind+" "+value.Id+";");
    foreach(var (name,value) in element.Values)text.AppendLine("value "+name+" = "+value.Value.GetRawText()+";");
    foreach(var (alias,value) in element.Imports)text.AppendLine("import "+value.Id+" as "+alias+" "+Signature(value.Signature,false)+(value.Scope is null?"":" in "+value.Scope)+";");
    foreach(var (target,value) in element.Bodies)text.AppendLine("body "+target+" "+Quote(value.Path)+";");
    if(element.Tool is not null)text.AppendLine("tool "+Quote(element.Tool)+";");
    foreach(var (name,value) in element.Options)text.AppendLine("option "+name+" "+Quote(value)+";");
    return text.AppendLine("}").ToString();
}
static string FormatManifest(Manifest manifest)
{
    var text=new StringBuilder(manifest.Kind+" "+manifest.Namespace+" version "+Quote(manifest.Version)+" {\n");
    if(manifest.Description!="")text.AppendLine("description "+Quote(manifest.Description)+";");
    if(manifest.Entry is not null)text.AppendLine("entry "+manifest.Entry+";");
    foreach(var (id,value) in manifest.Registry)text.AppendLine("registry "+id+" "+Quote(value.Path)+";");
    foreach(var (id,value) in manifest.Dependencies)text.AppendLine("dependency "+id+" version "+Quote(value.Version)+";");
    foreach(var (id,value) in manifest.Targets)text.AppendLine("target "+id+" "+value.Id+";");
    foreach(var value in manifest.Always)text.AppendLine("always "+value.Id+";");
    foreach(var (id,value) in manifest.Elements)text.AppendLine("element "+id+" "+value.Kind+" "+Quote(value.Path)+";");
    return text.AppendLine("}").ToString();
}
