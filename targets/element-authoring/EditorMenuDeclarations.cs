using Confectory.Core;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

// Declaration discovery only. The editor owns a closed, statically imported route;
// finding a public ID never loads or invokes the project's implementation code.
internal static class EditorMenuDeclarations
{
    internal static JsonObject Query(JsonObject request)
    {
        string project=Path.GetFullPath(request["project"]!.GetValue<string>()),target=request["target"]!.GetValue<string>();
        var observed=new SortedDictionary<string,string>(StringComparer.Ordinal);int bytes=0;
        string Read(string path)
        {
            path=Path.GetFullPath(path);var file=new FileInfo(path);
            if(!file.Exists||file.LinkTarget is not null||file.Length>1048576)throw new ArgumentException("Menu declaration unavailable or over budget");
            byte[] raw=File.ReadAllBytes(path);string hash=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(raw));
            if(observed.TryGetValue(path,out string? before)&&before!=hash)throw new InvalidOperationException("Menu source changed during discovery");
            if(!observed.ContainsKey(path)){bytes+=raw.Length;if(observed.Count>=512||bytes>4194304)throw new ArgumentException("Menu discovery budget");observed[path]=hash;}
            return new UTF8Encoding(false,true).GetString(raw);
        }
        var stats=new BuildStatistics();var docs=new Documents(Path.Combine(Path.GetTempPath(),"confectory-menu-metadata"),stats,path=>Encoding.UTF8.GetBytes(Read(path)));
        var registry=new Registry(project,docs,stats);if(registry.Packs.Count>64)throw new ArgumentException("Menu registry bound");
        var rows=new JsonArray();int objects=0;
        foreach(var pack in registry.Packs.OrderBy(p=>p.Key,StringComparer.Ordinal))
        {
            // Explicit direct dependencies only; registry entries alone grant no discovery scope.
            if(pack.Key!=registry.Project.Namespace&&!registry.Project.Dependencies.ContainsKey(pack.Key))continue;
            foreach(var locator in pack.Value.Elements.OrderBy(p=>p.Key,StringComparer.Ordinal))
            {
                if(locator.Value.Kind!="object")continue;if(++objects>256)throw new ArgumentException("Menu object scan bound");
                var action=registry.Get(pack.Key+"::"+locator.Key);
                if(!action.Values.TryGetValue("editorContextMenu",out var marker)||marker.Value.ValueKind!=JsonValueKind.True)continue;
                if(rows.Count>=32)throw new ArgumentException("Menu action bound");
                var row=new JsonObject{["id"]=action.Id,["title"]=action.Values.TryGetValue("editorName",out var name)&&name.Value.ValueKind==JsonValueKind.String?name.Value.GetString():action.Id,["available"]=false,["reason"]="No bound editor route"};rows.Add(row);
                string label=row["title"]!.ToString();if(label.Length==0||label.Length>160){row["title"]=action.Id;row["reason"]="Menu title must contain 1..160 characters";continue;}
                try
                {
                    var bindings=action.Provides.Where(p=>p.Key!="Confectory.SchemaEditing::Call").ToArray();
                    if(action.Parent is not null||bindings.Length!=1)throw new ArgumentException("One explicit menu function binding required");
                    string function=bindings[0].Key,provider=bindings[0].Value.Id;var contract=registry.Get(function,"function",action.Id);var implementation=registry.Implementation(function,provider,action.Id,action.Loc);
                    row["function"]=function;row["implementation"]=provider;row["signature"]=JsonSerializer.SerializeToNode(contract.Signature,JsonData.Options);
                    if(!registry.Project.Targets.ContainsKey(target))throw new ArgumentException("Target is not registered");
                    if(target is not ("linux" or "windows" or "portable"))throw new ArgumentException("Editor route is unavailable for this target");
                    if(function!="Confectory.SchemaEditing::SetValue"||provider!="Confectory.SchemaEditing::SetValueBody"||contract.Signature?.Format()!="(string text, string field, string value) -> string")throw new ArgumentException("Function is declared but has no bound editor route");
                    if(action.Provides.Count!=2||!action.Provides.TryGetValue("Confectory.SchemaEditing::Call",out var call)||call.Id!="Confectory.SchemaEditing::CallBody")throw new ArgumentException("Authoring route must be explicitly bound");
                    registry.Implementation("Confectory.SchemaEditing::Call",call.Id,action.Id,action.Loc);
                    // Exact known source closure for this finite route. A same-ID replacement,
                    // a project override or a new body is never silently executed by the host.
                    foreach(var pin in Pins)
                    {
                        string path=PackPaths.Owned(Path.GetDirectoryName(registry.Paths["Confectory.SchemaEditing"])!,pin.Key);Read(path);
                        string canonical=Read(path).Replace("\r\n","\n",StringComparison.Ordinal);
                        if(Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(Encoding.UTF8.GetBytes(canonical)))!=pin.Value)throw new ArgumentException("Editor route contract/body version changed");
                    }
                    row["available"]=true;row["reason"]="";
                }
                catch(Exception error) when(error is ArgumentException or BuildError){row["reason"]=error.Message;}
            }
        }
        // Re-read observed files so a query never publishes a mixed declaration snapshot.
        foreach(string path in observed.Keys.ToArray())Read(path);
        return new JsonObject{["actions"]=rows,["version"]=JsonData.Digest(observed),["target"]=target,["executed"]=false,["sourceWritten"]=false};
    }

    private static readonly Dictionary<string,string> Pins=new(StringComparer.Ordinal)
    {
        // Filled from the existing statically imported SchemaEditing route.
        ["SetValue.celem"]="7D0948DBF6706CD54E9593E9B8BC3E8C16722D69C1A376F1D31618733F7CA414",
        ["SetValueBody.celem"]="EAC4074D31C52DB697B678C5299E3230A0F70AE32E35150CBE013C43843E838B",
        ["SetValue.csbody"]="7F69A5F91F0D1A71FEBC02F37CA92893A654C62DE315548080CC2D1717A4E573",
        ["Call.celem"]="7D034575C18E1DED88DF8271C7AD182958E26160106DF66F169A53B6726F43A1",
        ["CallBody.celem"]="DC3B74410F8775273554A31AEE4BF21E609FE548B0858C5D9BC0FD8572919E98",
        ["Call.csbody"]="5914D69133FEB47D682F78E6C2563CDEA8FD77E05EDC6EEB5BB8335DF53E5FB6"
    };
}
