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
            byte[] raw=File.ReadAllBytes(path);if(raw.Length>1048576)throw new ArgumentException("Menu declaration unavailable or over budget");string hash=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(raw));
            if(observed.TryGetValue(path,out string? before)&&before!=hash)throw new InvalidOperationException("Menu source changed during discovery");
            if(!observed.ContainsKey(path)){bytes+=raw.Length;if(observed.Count>=512||bytes>4194304)throw new ArgumentException("Menu discovery budget");observed[path]=hash;}
            return new UTF8Encoding(false,true).GetString(raw);
        }
        var stats=new BuildStatistics();var docs=new Documents(Path.Combine(Path.GetTempPath(),"confectory-menu-metadata"),stats,path=>Encoding.UTF8.GetBytes(Read(path)));
        var registry=new Registry(project,docs,stats);if(registry.Packs.Count>64)throw new ArgumentException("Menu registry bound");
        var rows=new JsonArray();
        // Complete, ordered discovery in bounded pages. Only the owner pack
        // and its explicit direct dependencies contribute object locators.
        // The one query still retains the existing global observed-file/byte
        // and action budgets, and rechecks every observed file at the end.
        const int ObjectPageSize=256;
        foreach(var pack in registry.Packs.OrderBy(p=>p.Key,StringComparer.Ordinal))
        {
            // Explicit direct dependencies only; registry entries alone grant no discovery scope.
            if(pack.Key!=registry.Project.Namespace&&!registry.Project.Dependencies.ContainsKey(pack.Key))continue;
            foreach(var page in pack.Value.Elements.Where(p=>p.Value.Kind=="object").OrderBy(p=>p.Key,StringComparer.Ordinal).Chunk(ObjectPageSize))
            foreach(var locator in page)
            {
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
                        string hash=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(Encoding.UTF8.GetBytes(canonical)));
                        // The previous exact, already trusted Call body remains valid for installed packs.
                        if(hash!=pin.Value&&!(pin.Key=="Call.csbody"&&hash is PreviousCallPin or PreviousStreamCallPin or PreviousActivationCallPin or PreviousPerformanceCallPin or PreviousRestoreCallPin or PreviousBlueprintStreamCallPin or PreviousGuardStreamCallPin or PreviousConnectionStreamCallPin or PreviousSettingsStreamCallPin or PreviousOverrideStreamCallPin or PreviousReviewStreamCallPin or PreviousProposalStreamCallPin or PreviousProjectionStreamCallPin or PreviousPreparationStreamCallPin or PreviousFinalOverlayStreamCallPin or PreviousRotationStreamCallPin or PreviousSettingsTransformStreamCallPin))throw new ArgumentException("Editor route contract/body version changed");
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

    private const string PreviousCallPin="5914D69133FEB47D682F78E6C2563CDEA8FD77E05EDC6EEB5BB8335DF53E5FB6";
    private const string PreviousStreamCallPin="DA9F68475285D35B0B66ED71513862D1BFA85034934A822084B783BE03A6D037";
    private const string PreviousActivationCallPin="975F8EF2B1C36F77DE0862A8790CAEAC35AABBA24B2683C512DCF1C6386AB96B";
    private const string PreviousPerformanceCallPin="FB840A66374EF42AAC958D5C8F038E599DD38C2DC65419C7C7C0FC4F0DB470CB";
    private const string PreviousRestoreCallPin="5BE320414DB2BA48E32BF7F15887664DEEB1F430C8B26537B99A91ECC8C5BE36";
    private const string PreviousBlueprintStreamCallPin="F468678C75D3B09543B0D099CB50D3F78DE7A97DDFB9362EC7491F485981A32D";
    private const string PreviousGuardStreamCallPin="C0BB3B712C61F58708DAA7684AB8DC185E0E5E536E1DF96C64F0144A7BD0B53A";
    private const string PreviousConnectionStreamCallPin="91F35A2D80DCFC132332718140F93BC6F2FDE161E6326A1243673C58815135B5";
    private const string PreviousSettingsStreamCallPin="9B1663B6982BFA8D9377D87CD732BBCDF9915824964A2F3EC03E5FD00188E64D";
    private const string PreviousProposalStreamCallPin="7E27DDFF9FBB3980500396C680F7791E18D2485035A164E2096483D24898DCF7";
    private const string PreviousReviewStreamCallPin="F58300F4DB7999DA85BF5F2DA2195FFDFE3AA138A31EB9B765AA41C27506535D";
    private const string PreviousOverrideStreamCallPin="B0BABEBEB240ECA36DD7AAFDD895B4A72F1D317BFEFA13617F1B5DA0DDF9DDE7";
    private const string PreviousProjectionStreamCallPin="0E99595B8FE257181B748CFC844DB8372194A8F9ECFD663B91B86B3879FF30E6";
    private const string PreviousPreparationStreamCallPin="48B1C1D97EFB170B2FD9321A427B82ECFFF8F615DE9C46C2109715D29168C31C";
    private const string PreviousFinalOverlayStreamCallPin="0F9D0016054341FD83AFF6854F00997B0ECD62FF130400742B6F5F03CF761DEF";
    private const string PreviousRotationStreamCallPin="F844077FC4318E2ECC92D3D022128D062FAECF37D8CEE80DBA48F94D2AAF91AC";
    private const string PreviousSettingsTransformStreamCallPin="3C46E769399CFD923814A88BFBBA83E6ED20AA641BB2AD48C108B443A20EF2B9";
    private static readonly Dictionary<string,string> Pins=new(StringComparer.Ordinal)
    {
        // Filled from the existing statically imported SchemaEditing route.
        ["SetValue.celem"]="7D0948DBF6706CD54E9593E9B8BC3E8C16722D69C1A376F1D31618733F7CA414",
        ["SetValueBody.celem"]="EAC4074D31C52DB697B678C5299E3230A0F70AE32E35150CBE013C43843E838B",
        ["SetValue.csbody"]="7F69A5F91F0D1A71FEBC02F37CA92893A654C62DE315548080CC2D1717A4E573",
        ["Call.celem"]="7D034575C18E1DED88DF8271C7AD182958E26160106DF66F169A53B6726F43A1",
        ["CallBody.celem"]="DC3B74410F8775273554A31AEE4BF21E609FE548B0858C5D9BC0FD8572919E98",
        ["Call.csbody"]="A1C4E8D6F30103D6C382157872DC1A27DF1F012AD31794B57844EEB35438E871"
    };
}
