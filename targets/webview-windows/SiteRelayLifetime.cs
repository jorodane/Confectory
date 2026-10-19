// Running-session ownership only. Login data stays in WebView2's isolated profile;
// no remote session, project grant, cookie or token is serialized by this class.
internal sealed class SiteRelayLifetime
{
    public bool Connected { get; private set; }
    public bool Hidden { get; private set; }
    public bool Closed { get; private set; }
    public bool HostWake { get; private set; }
    public long ExpiresAt { get; private set; }
    public bool CanHide => Connected && HostWake && !Closed;
    public bool Pair(long now,long expiresAt,bool hostWake)
    {
        if(Closed||expiresAt<=now)return false;
        Connected=true;HostWake=hostWake;ExpiresAt=expiresAt;return true;
    }
    public bool Hide(){if(!CanHide)return false;Hidden=true;return true;}
    public bool Reopen(){if(Closed)return false;Hidden=false;return true;}
    public bool Tick(long now){if(!Connected||Closed||now<ExpiresAt)return false;Disconnect();return true;}
    public void Disconnect(){Connected=false;HostWake=false;ExpiresAt=0;}
    public void Shutdown(){Disconnect();Hidden=false;Closed=true;}
    public async Task<bool> ForgetLoginAsync(Func<Task> disconnect,Func<Task> clear)
    {
        await disconnect();if(Closed)return false;
        await clear();return !Closed;
    }
}
internal static class SiteRelayProfile
{
    public const string Name="ConfectoryRelay";
    public const bool InPrivate=false;
    public static string DirectoryFor(string localAppData)
    {
        if(!Path.IsPathFullyQualified(localAppData))throw new ArgumentException("Current user's LocalApplicationData is required");
        return Path.Combine(localAppData,"Confectory","SiteRelay","confectory-connect.jorodane.chatgpt.site");
    }
}
