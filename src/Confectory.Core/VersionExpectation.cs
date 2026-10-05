namespace Confectory.Core;

/// <summary>Pure numeric version expectation policy. Unsupported labels remain exact-only.</summary>
public static class VersionExpectation
{
    public static bool Matches(string expectation,string selected)
    {
        if(expectation=="*"||expectation==selected)return true;
        if(!Parse(selected,out var actual))return false;
        if(expectation.EndsWith(".*",StringComparison.Ordinal))
        {
            string[] prefix=expectation[..^2].Split('.');if(prefix.Length is <1 or >2)return false;
            for(int i=0;i<prefix.Length;i++)if(!int.TryParse(prefix[i],System.Globalization.NumberStyles.None,System.Globalization.CultureInfo.InvariantCulture,out int value)||value!=actual[i])return false;
            return true;
        }
        string[] rules=expectation.Split(' ',StringSplitOptions.RemoveEmptyEntries);if(rules.Length==0)return false;
        foreach(string rule in rules)
        {
            string op=rule.StartsWith(">=",StringComparison.Ordinal)||rule.StartsWith("<=",StringComparison.Ordinal)?rule[..2]:rule.StartsWith('>')||rule.StartsWith('<')||rule.StartsWith('^')||rule.StartsWith('~')?rule[..1]:"=";
            string text=op=="="?rule:rule[op.Length..];if(!Parse(text,out var bound))return false;int compared=Compare(actual,bound);
            if(op is "^" or "~")
            {
                if(compared<0)return false;var upper=(int[])bound.Clone();int index=op=="~"?1:bound[0]!=0?0:bound[1]!=0?1:2;if(op=="~"&&!text.Contains('.'))return false;
                if(upper[index]==int.MaxValue)return false;upper[index]++;for(int i=index+1;i<3;i++)upper[i]=0;if(Compare(actual,upper)>=0)return false;
            }
            else if(op switch{"="=>compared!=0,">"=>compared<=0,">="=>compared<0,"<"=>compared>=0,"<="=>compared>0,_=>true})return false;
        }
        return true;
    }
    private static bool Parse(string text,out int[] version)
    {
        version=new int[3];string[] parts=text.Split('.');if(parts.Length is <1 or >3)return false;
        for(int i=0;i<parts.Length;i++)if(!int.TryParse(parts[i],System.Globalization.NumberStyles.None,System.Globalization.CultureInfo.InvariantCulture,out version[i]))return false;
        return true;
    }
    private static int Compare(int[] left,int[] right)
    {for(int i=0;i<3;i++){int order=left[i].CompareTo(right[i]);if(order!=0)return order;}return 0;}
}
