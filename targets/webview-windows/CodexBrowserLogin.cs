namespace Confectory.WebView;
internal static class CodexBrowserLogin
{
    internal static bool Allowed(string value){try{if(value.Length is <1 or >8192||!Uri.TryCreate(value,UriKind.Absolute,out var uri)||uri.Scheme!="https"||!uri.IsDefaultPort||uri.Host!="auth.openai.com"||uri.AbsolutePath!="/oauth/authorize"||uri.UserInfo.Length>0||uri.Fragment.Length>0)return false;
        var query=new System.Collections.Generic.Dictionary<string,string>(StringComparer.Ordinal);
        foreach(string part in uri.Query.TrimStart('?').Split('&')){var pair=part.Split('=',2);if(pair.Length!=2)return false;string name=Uri.UnescapeDataString(pair[0]),item=Uri.UnescapeDataString(pair[1]);if(!query.TryAdd(name,item))return false;}
        if(!query.TryGetValue("redirect_uri",out string? redirect)||!Uri.TryCreate(redirect,UriKind.Absolute,out var callback)||callback.Scheme!="http"||callback.Host is not ("127.0.0.1" or "localhost")||callback.Port is <1 or >65535||callback.AbsolutePath!="/auth/callback"||callback.Query.Length>0||callback.Fragment.Length>0||callback.UserInfo.Length>0)return false;
        string Field(string name)=>query.TryGetValue(name,out var found)?found:"";return Field("response_type")=="code"&&Field("code_challenge_method")=="S256"&&Field("state").Length is >0 and <=512&&Field("client_id").Length is >0 and <=256&&System.Text.RegularExpressions.Regex.IsMatch(Field("code_challenge"),@"\A[A-Za-z0-9_-]{43,128}\z");}catch{return false;}}
    internal static bool TryOpen(string value,Action<string> open){if(!Allowed(value)&&value!="https://auth.openai.com/codex/device")return false;try{open(new Uri(value,UriKind.Absolute).AbsoluteUri);return true;}catch{return false;}}
}
