using Confectory.Core;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;

// Three-way, same-declaration merge. Unchanged raw text is copied verbatim.
// Statements have native identities; an overlapping material edit fails closed.
internal static class DeclarationTextMerge
{
    sealed record Token(int Start, int End, string Text, string Key);
    sealed record Part(int Start, int End, string Text, List<Token> Tokens);
    sealed record Parts(Dictionary<string, Part> Statements, int Closing);
    static readonly Regex Lex = new(@"\G(?:(?<space>\s+)|(?<comment>//[^\n]*)|(?<string>""(?:[^""\\]|\\.)*"")|->|[A-Za-z_][A-Za-z_0-9.]*(?:::[A-Za-z_][A-Za-z_0-9]*)?|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|[{}();,=\[\]])", RegexOptions.CultureInvariant);
    static List<Token> Tokens(string text)
    {
        List<Token> tokens = []; int offset = 0;
        while (offset < text.Length)
        {
            var match = Lex.Match(text, offset);
            if (!match.Success || tokens.Count >= 65536) throw new ArgumentException("Bounded declaration tokens required; raw input retained");
            if (!match.Groups["space"].Success && !match.Groups["comment"].Success)
                tokens.Add(new(offset, offset + match.Length, match.Value, match.Groups["string"].Success ? "s:" + JsonSerializer.Deserialize<string>(match.Value) : "w:" + match.Value));
            offset += match.Length;
        }
        return tokens;
    }
    static Parts Read(string text)
    {
        var tokens = Tokens(text); int open = tokens.FindIndex(t => t.Text == "{");
        if (open < 2) throw new ArgumentException("Owned declaration header required");
        Dictionary<string, Part> parts = new(StringComparer.Ordinal);
        void Add(string key, List<Token> section)
        {
            if (parts.TryGetValue(key, out var repeated) && (key.StartsWith("module:", StringComparison.Ordinal) || key.StartsWith("use:", StringComparison.Ordinal) || key.StartsWith("contain:", StringComparison.Ordinal) || key.StartsWith("always:", StringComparison.Ordinal)))
            {
                if (!repeated.Tokens.Select(t => t.Key).SequenceEqual(section.Select(t => t.Key))) throw new ArgumentException("Ambiguous raw list entry");
                string prefix = key; int count = 1; while (parts.ContainsKey(key)) key = prefix + "#" + count++;
            }
            if (parts.Count >= 2048 || !parts.TryAdd(key, new(section[0].Start, section[^1].End, text[section[0].Start..section[^1].End], section)))
                throw new ArgumentException("Ambiguous repeated raw statement; retain input and reconcile explicitly");
        }
        Add("$header", tokens.Take(open + 1).ToList());
        int start = open + 1, depth = 1;
        for (int i = start; i < tokens.Count; i++)
        {
            if (tokens[i].Text == "{") depth++;
            if (tokens[i].Text == "}" && --depth == 0) { if (start != i || i != tokens.Count - 1) throw new ArgumentException("Complete declaration required"); return new(parts, tokens[i].Start); }
            else if (tokens[i].Text == "}") { /* nested compound ends */ }
            if (tokens[i].Text != ";" || depth != 1) continue;
            var section = tokens.GetRange(start, i - start + 1); string word = section[0].Text;
            string key = word switch
            {
                "description" or "standalone" or "entry" => word,
                "field" or "data" or "value" or "provide" or "module" => word + ":" + section[1].Key,
                "element" or "dependency" or "registry" or "target" or "always" => word + ":" + section[1].Key,
                "use" or "contain" => word + ":" + section[1].Key + ":" + section[2].Key,
                _ => throw new ArgumentException("This raw statement has no same-owner merge contract")
            };
            Add(key, section); start = i + 1;
        }
        throw new ArgumentException("Complete raw declaration required");
    }
    static string Fingerprint(Part? part) => part is null ? "<missing>" : JsonSerializer.Serialize(part.Tokens.Select(t => t.Key));
    public static string Merge(string baseline, string typed, string raw, Func<Element, string> format)
    {
        if (baseline.Length > 1048576 || typed.Length > 1048576 || raw.Length > 1048576) throw new ArgumentException("Raw candidate byte budget");
        var original = new Parser(baseline, "<raw-baseline>").ParseElement();
        foreach (string text in new[] { typed, raw }) { var element = new Parser(text, "<raw-candidate>").ParseElement(); if (element.Id != original.Id || element.Kind != original.Kind || element.Kind is not ("object" or "schema")) throw new ArgumentException("Raw declaration identity/kind changed; all input retained"); }
        return Combine(baseline, typed, raw, s => format(new Parser(s, "<merge>").ParseElement()));
    }
    public static string MergeFunction(string baseline, string typed, Func<Element, string> format)
    {
        var original = new Parser(baseline, "<function-baseline>").ParseElement();
        var next = new Parser(typed, "<function-candidate>").ParseElement();
        if (original.Kind != "function" || next.Kind != "function" || original.Id != next.Id || original.Parent != next.Parent)
            throw new ArgumentException("Same owned function identity required; retain all input");
        return Combine(baseline, typed, baseline, s => format(new Parser(s, "<function-merge>").ParseElement()));
    }
    public static string MergeManifest(string baseline, string typed, Func<Manifest, string> format)
    {
        var original = new Parser(baseline, "<registration-baseline>").ParseManifest(); var next = new Parser(typed, "<registration-candidate>").ParseManifest();
        if (original.Kind != next.Kind || original.Namespace != next.Namespace) throw new ArgumentException("Registration identity must remain unchanged");
        return Combine(baseline, typed, baseline, s => format(new Parser(s, "<registration-merge>").ParseManifest()));
    }
    static string Combine(string baseline, string typed, string raw, Func<string, string> canonical)
    {
        if (baseline.Length > 1048576 || typed.Length > 1048576 || raw.Length > 1048576) throw new ArgumentException("Source merge budget");
        var b = Read(canonical(baseline)); var t = Read(canonical(typed)); var r = Read(canonical(raw));
        var source = Read(raw); var oldSource = Read(baseline); var typedSource = Read(typed); List<(int Start, int End, string Text)> patches = []; List<string> additions = [];
        var expected = r.Statements.ToDictionary(p => p.Key, p => Fingerprint(p.Value), StringComparer.Ordinal);
        foreach (string key in b.Statements.Keys.Concat(t.Statements.Keys).Distinct(StringComparer.Ordinal))
        {
            b.Statements.TryGetValue(key, out var prior); t.Statements.TryGetValue(key, out var next); r.Statements.TryGetValue(key, out var observed);
            string before = Fingerprint(prior), after = Fingerprint(next), current = Fingerprint(observed);
            if (before == after) continue;
            if (current == after) continue;
            if (before != current) throw new InvalidOperationException("Raw and property edits overlap; no changes applied, retain both inputs");
            if (next is null) expected.Remove(key); else expected[key] = after;
            typedSource.Statements.TryGetValue(key, out var replacement);
            if (!source.Statements.TryGetValue(key, out var actual)) { if (replacement is not null) additions.Add(replacement.Text); continue; }
            if (next is null)
            {
                // Comments inside a removed clause have no safe destination.
                if (HasComments(actual)) throw new InvalidOperationException("Keep the raw clause annotation before deleting it");
                patches.Add((actual.Start, actual.End, "")); continue;
            }
            if (replacement is null) throw new InvalidOperationException("Explicit typed source statement missing");
            if (actual.Tokens.Count == replacement.Tokens.Count)
            {
                for (int i = 0; i < actual.Tokens.Count; i++) if (actual.Tokens[i].Key != replacement.Tokens[i].Key) patches.Add((actual.Tokens[i].Start, actual.Tokens[i].End, replacement.Tokens[i].Text));
            }
            else
            {
                // A structural replacement is safe only when the raw clause
                // itself was untouched, with no inline annotation to discard.
                if (HasComments(actual) || !oldSource.Statements.TryGetValue(key, out var old) || old.Text != actual.Text)
                    throw new InvalidOperationException("Raw formatting overlaps a structural edit; retain both inputs");
                patches.Add((actual.Start, actual.End, replacement.Text));
            }
        }
        if (additions.Count != 0) patches.Add((source.Closing, source.Closing, "\n  " + string.Join("\n  ", additions) + "\n"));
        var result = new StringBuilder(raw);
        foreach (var patch in patches.OrderByDescending(p => p.Start)) { result.Remove(patch.Start, patch.End - patch.Start); result.Insert(patch.Start, patch.Text); }
        string merged = result.ToString(); var final = Read(canonical(merged));
        if (merged.Length > 1048576 || final.Statements.Count != expected.Count || final.Statements.Any(p => !expected.TryGetValue(p.Key, out string? proof) || proof != Fingerprint(p.Value)))
            throw new InvalidOperationException("Merged declaration differs from explicit candidates; all input retained");
        return merged;
    }
    static bool HasComments(Part part)
    {
        // Only gaps between significant tokens can contain comments. A literal
        // URL or // inside a JSON string is never treated as an annotation.
        int offset = 0;
        foreach (var token in part.Tokens) { int start = token.Start - part.Start; if (part.Text[offset..start].Contains("//", StringComparison.Ordinal)) return true; offset = token.End - part.Start; }
        return false;
    }
}
