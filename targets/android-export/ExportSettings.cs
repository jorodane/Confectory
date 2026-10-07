using System.Security;
using System.Text.RegularExpressions;
using Confectory.Core;

// Target-owned metadata contract. Core has no Android settings grammar.
internal sealed record ExportSettings(string ApplicationId, string Title, string VersionName, int VersionCode, string Format)
{
    public const string DefaultsId = "Confectory.AndroidExport.Settings::Defaults";
    public static ExportSettings Read(Registry registry)
    {
        var candidates = registry.Project.Elements.Where(x => x.Value.Kind == "object")
            .Select(x => registry.Get(registry.Project.Namespace + "::" + x.Key, "object"))
            .Where(x => x.Parent == DefaultsId).ToArray();
        if (candidates.Length > 1) throw new InvalidOperationException("Only one owned Android export settings object is allowed.");
        if (candidates.Length == 0) return new("org.confectory.checkpoint", "Confectory BaseUI", "0.1", 1, "apk");
        var values = registry.Effective(candidates[0].Id).Values;
        string[] allowed = ["applicationId", "applicationTitle", "versionName", "versionCode", "packageFormat", "keyAlias", "keyAlgorithm", "keySize", "keyValidityDays", "keyDistinguishedName"];
        if (values.Keys.Any(x => !allowed.Contains(x, StringComparer.Ordinal)))
            throw new InvalidOperationException("Android export settings contain an unsupported field; credentials must never be saved here.");
        string Text(string key) => values[key].Value.GetString() ?? throw new InvalidOperationException("Expected text settings value.");
        string id=Text("applicationId"), title=Text("applicationTitle"), version=Text("versionName"), format=Text("packageFormat");
        int code=values["versionCode"].Value.GetInt32();
        if (!Regex.IsMatch(id, @"\A[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+\z") || code < 1 || code > 2100000000 || format is not ("apk" or "aab"))
            throw new InvalidOperationException("Invalid Android application ID, version code or package format.");
        if (title.Length is < 1 or > 128 || version.Length is < 1 or > 128 || title.Any(char.IsControl) || version.Any(char.IsControl))
            throw new InvalidOperationException("Android title/version must be bounded printable text.");
        if (Text("keyAlgorithm") is not ("RSA" or "EC") || Text("keyAlias").Length is < 1 or > 128 || Text("keyDistinguishedName").Length is < 1 or > 1024
            || values["keySize"].Value.GetInt32() is < 256 or > 8192 || values["keyValidityDays"].Value.GetInt32() is < 1 or > 36500)
            throw new InvalidOperationException("Invalid nonsecret key generation defaults.");
        return new(id,title,version,code,format);
    }
    public string Apply(string template)
    {
        // Metadata is text, never an MSBuild expression (property functions can execute I/O).
        string Literal(string value) => string.Concat(value.Select(c => "%$@;'?*()".Contains(c)
            ? "%"+((int)c).ToString("X2",System.Globalization.CultureInfo.InvariantCulture) : c.ToString()));
        string Replace(string source, string tag, string value) => Regex.Replace(source,"<"+tag+">[^<]*</"+tag+">", _ => "<"+tag+">"+SecurityElement.Escape(Literal(value))+"</"+tag+">");
        foreach(var (tag,value) in new[]{("ApplicationId",ApplicationId),("ApplicationTitle",Title),("ApplicationVersion",VersionCode.ToString(System.Globalization.CultureInfo.InvariantCulture)),("ApplicationDisplayVersion",VersionName)}) template=Replace(template,tag,value);
        return template.Replace("</PropertyGroup>", $"<AndroidPackageFormats>{Format}</AndroidPackageFormats><AndroidPackageFormat>{Format}</AndroidPackageFormat>\n</PropertyGroup>", StringComparison.Ordinal);
    }
}
