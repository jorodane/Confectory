using Confectory.Core;
using System.Text;
using System.Text.Json.Nodes;

// Explicit binding in an owned, non-inherited function scope. Only declarations
// in direct, version-matching dependencies are read; no provider body is loaded.
internal static class RegisteredFunctionProvider
{
    public static string Prepare(string project, string manifestText, string sourceText, string function, string implementation, Func<Element,string> format)
    {
        var observations = new Dictionary<string,string>(OperatingSystem.IsWindows()?StringComparer.OrdinalIgnoreCase:StringComparer.Ordinal);
        string Read(string path)
        {
            path=Path.GetFullPath(path);
            for(FileSystemInfo? node=new FileInfo(path);node is not null;node=node is FileInfo file?file.Directory:((DirectoryInfo)node).Parent)
                if(node.LinkTarget is not null)throw new ArgumentException("Provider declaration cannot traverse links");
            var info=new FileInfo(path);
            if(!info.Exists||info.Length>1048576)throw new ArgumentException("Bounded provider declaration required");
            string text=File.ReadAllText(path,new UTF8Encoding(false,true));
            if(observations.TryGetValue(path,out var old)&&old!=text)throw new InvalidOperationException("Provider declaration changed while reading");
            observations[path]=text;return text;
        }
        string Owned(string root,string relative)
        {
            string lexical=Path.GetFullPath(Path.Combine(root,relative));
            if(!string.Equals(PackPaths.Owned(root,relative),lexical,OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal))throw new ArgumentException("Provider declaration must use its owned lexical path");
            return lexical;
        }
        if(function.Length>256||implementation.Length>256)throw new ArgumentException("Bounded qualified provider IDs required");
        if(Read(project)!=manifestText||sourceText.Length>1048576)throw new InvalidOperationException("Confirm the ProjectPack manifest before binding a provider");
        var manifest=new Parser(manifestText,project).ParseManifest();
        var source=new Parser(sourceText,"<provider-owner>").ParseElement();
        if(manifest.Kind!="project"||source.Kind!="function"||source.Parent is not null||PackPaths.Namespace(source.Id)!=manifest.Namespace||!manifest.Elements.TryGetValue(source.Id[(manifest.Namespace.Length+2)..],out var owner)||owner.Kind!="function")throw new ArgumentException("Direct owned function scope required");
        if(Read(Owned(Path.GetDirectoryName(Path.GetFullPath(project))!,owner.Path))!=sourceText)throw new InvalidOperationException("Confirm the function declaration before binding a provider");
        Element Resolve(string id,string kind)
        {
            string ns=PackPaths.Namespace(id);
            if(!manifest.Dependencies.TryGetValue(ns,out var dependency)||!manifest.Registry.TryGetValue(ns,out var registration))throw new ArgumentException("Direct registered dependency required");
            string manifestPath=Path.GetFullPath(Path.Combine(Path.GetDirectoryName(Path.GetFullPath(project))!,registration.Path));
            var pack=new Parser(Read(manifestPath),manifestPath).ParseManifest();
            if(pack.Kind!="pack"||pack.Namespace!=ns||!VersionExpectation.Matches(dependency.Version,pack.Version)||!pack.Elements.TryGetValue(id[(ns.Length+2)..],out var locator)||locator.Kind!=kind)throw new ArgumentException("Registered provider identity or dependency version differs");
            string path=Owned(Path.GetDirectoryName(manifestPath)!,locator.Path);
            var element=new Parser(Read(path),path).ParseElement();
            if(element.Id!=id||element.Kind!=kind||element.Parent is not null)throw new ArgumentException("Direct registered declaration required");
            return element;
        }
        var contract=Resolve(function,"function");var provider=Resolve(implementation,"implementation");
        if(provider.Function!=contract.Id||provider.Signature is null||contract.Signature is null||!contract.Signature.Matches(provider.Signature))throw new ArgumentException("Provider does not match the exact function contract");
        if(source.Provides.TryGetValue(function,out var prior))
        {
            if(prior.Id!=implementation)throw new InvalidOperationException("Existing provider binding must not be replaced implicitly");
            return sourceText;
        }
        source.Provides.Add(function,new ElementReference(implementation,new(),source.Id));
        string next=DeclarationTextMerge.MergeFunction(sourceText,format(source),format);
        foreach(var pair in observations.ToArray())Read(pair.Key);
        return next;
    }
}
