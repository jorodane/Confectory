using System.Text.Json;

namespace Confectory.Core;

/// <summary>A bounded parse memo for one exact read transaction. Bytes are supplied by the
/// caller's observation pass; no file stamp, ownership or validation result is reused.</summary>
public sealed class ExactDocumentReadMemo
{
    private readonly Dictionary<string,(byte[] Bytes,Element Parsed)> elements=new(StringComparer.Ordinal);
    private long bytes;
    public int Reused { get; private set; }
    public int Parsed { get; private set; }

    internal Element Read(string path, byte[] source, Func<Element> parse)
    {
        if(elements.TryGetValue(path,out var prior)&&source.AsSpan().SequenceEqual(prior.Bytes)){
            Reused++;return Copy(prior.Parsed);
        }
        var result=parse();Parsed++;
        if(source.Length<=1048576&&elements.Count<2048&&bytes+source.Length<=16777216&&!elements.ContainsKey(path)){
            elements.Add(path,(source.ToArray(),Copy(result)));bytes+=source.Length;
        }
        return result;
    }

    // Copy every mutable container. Records with only immutable fields may be
    // shared; JSON values and nested data/parameter collections are detached.
    internal static Element Copy(Element value)
    {
        static FunctionSignature? Signature(FunctionSignature? v)=>v is null?null:new(v.Args.ToList(),v.Return);
        static SchemaDatum Datum(SchemaDatum v)=>v with{
            Scalar=v.Scalar?.Clone(),Items=v.Items?.Select(Datum).ToList(),
            Members=v.Members?.ToDictionary(p=>p.Key,p=>Datum(p.Value),StringComparer.Ordinal)};
        return new Element{
            Kind=value.Kind,Id=value.Id,Loc=value.Loc,Parent=value.Parent,
            Modules=value.Modules.ToList(),Includes=value.Includes.ToList(),
            Requires=value.Requires.ToDictionary(p=>p.Key,p=>p.Value with{Signature=Signature(p.Value.Signature)!},StringComparer.Ordinal),
            Defaults=new(value.Defaults,StringComparer.Ordinal),Provides=new(value.Provides,StringComparer.Ordinal),
            Uses=value.Uses.ToList(),Contains=value.Contains.ToList(),Fields=new(value.Fields,StringComparer.Ordinal),
            Data=value.Data.ToDictionary(p=>p.Key,p=>Datum(p.Value),StringComparer.Ordinal),
            Values=value.Values.ToDictionary(p=>p.Key,p=>p.Value with{Value=p.Value.Value.Clone()},StringComparer.Ordinal),
            Imports=value.Imports.ToDictionary(p=>p.Key,p=>p.Value with{Signature=Signature(p.Value.Signature)!},StringComparer.Ordinal),
            Bodies=new(value.Bodies,StringComparer.Ordinal),Options=new(value.Options,StringComparer.Ordinal),
            Description=value.Description,DescriptionPresent=value.DescriptionPresent,Signature=Signature(value.Signature),
            Function=value.Function,Tool=value.Tool,ToolOrigin=value.ToolOrigin
        };
    }
}
