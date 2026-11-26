using Confectory.Core;
using System.Text;

// Reach a confirmed, directly owned object from an owned function's ordinary
// semantic use relation. No runtime instance is created and no file is written.
internal static class OwnedFunctionObjectUse
{
    internal static string Prepare(string project,string manifestText,string sourceText,string objectId,Func<Element,string> format)
    {
        string root=Path.GetDirectoryName(Path.GetFullPath(project))!;
        var observed=new Dictionary<string,string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
        string Read(string path)
        {
            path=Path.GetFullPath(path);
            for(FileSystemInfo? n=new FileInfo(path);n is not null;n=n is FileInfo file?file.Directory:((DirectoryInfo)n).Parent)if(n.LinkTarget is not null)throw new ArgumentException("Owned declaration cannot traverse links");
            var info=new FileInfo(path);if(!info.Exists||info.Length>1048576)throw new ArgumentException("Bounded published declaration required");
            string text=File.ReadAllText(path,new UTF8Encoding(false,true));if(observed.TryGetValue(path,out var prior)&&prior!=text)throw new InvalidOperationException("Published source changed");observed[path]=text;return text;
        }
        if(Read(project)!=manifestText||sourceText.Length>1048576||objectId.Length>256)throw new InvalidOperationException("Confirmed project and bounded source required");
        var manifest=new Parser(manifestText,project).ParseManifest();var source=new Parser(sourceText,"<object-use-owner>").ParseElement();
        Element Resolve(string id,string kind){
            if(manifest.Kind!="project"||PackPaths.Namespace(id)!=manifest.Namespace||!id.StartsWith(manifest.Namespace+"::",StringComparison.Ordinal)||!manifest.Elements.TryGetValue(id[(manifest.Namespace.Length+2)..],out var locator)||locator.Kind!=kind)throw new ArgumentException("Exact directly owned declaration required");
            string lexical=Path.GetFullPath(Path.Combine(root,locator.Path));if(!string.Equals(PackPaths.Owned(root,locator.Path),lexical,OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal))throw new ArgumentException("Owned lexical declaration required");
            var element=new Parser(Read(lexical),lexical).ParseElement();if(element.Id!=id||element.Kind!=kind)throw new ArgumentException("Declaration identity differs");return element;
        }
        var confirmed=Resolve(source.Id,"function");if(source.Parent is not null||confirmed.Parent is not null||Read(confirmed.Loc.File)!=sourceText)throw new InvalidOperationException("Confirm the direct function before linking an object");
        _=Resolve(objectId,"object");
        if(source.Uses.Any(r=>r.Id==objectId))return sourceText;
        source.Uses.Add(new ElementReference(objectId,new(),source.Id,"object"));
        string candidate=DeclarationTextMerge.MergeFunction(sourceText,format(source),format);
        foreach(var pair in observed.ToArray())Read(pair.Key);
        return candidate;
    }
}
