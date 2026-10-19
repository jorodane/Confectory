// Presentation only: no clock, authentication, permission or session lifetime.
// The native window and portable lifecycle tests use these same transitions.
internal sealed class SiteRelayPresentation
{
    public enum Stage { Preparing, Navigating, AwaitingLogin, Connecting, Connected, Failed, Disconnected, Closed }
    public Stage Current { get; private set; } = Stage.Preparing;
    public long Attempt { get; private set; } = 1;
    public ulong? NavigationId { get; private set; }
    public bool ShowDocument { get; private set; }
    bool loginDestination;
    string failure = "";
    public bool CanRetry => Current is Stage.Failed or Stage.Disconnected;
    public bool Busy => Current is Stage.Preparing or Stage.Navigating or Stage.Connecting;
    public string Message => Current switch {
        Stage.Preparing => "연결 창을 준비하고 있습니다. 처음 실행할 때는 시간이 걸릴 수 있습니다.",
        Stage.Navigating => loginDestination ? "ChatGPT 로그인 화면을 불러오고 있습니다. 아직 실패한 상태가 아닙니다." : "연결 페이지를 불러오고 있습니다. 페이지가 준비될 때까지 기다려 주세요.",
        Stage.AwaitingLogin => "ChatGPT 로그인을 기다리고 있습니다. 아래 로그인 화면에서 직접 진행해 주세요.",
        Stage.Connecting => "페이지 준비가 끝났습니다. 로그인 또는 엔진 연결 응답을 기다리고 있습니다.",
        Stage.Connected => "엔진 연결 완료 · 창 숨김과 다시 열기는 연결을 유지합니다. 연결 해제를 누르면 통신을 끝냅니다.",
        Stage.Failed => "연결을 진행하지 못했습니다. 다시 연결을 누르세요. 계속 실패하면 이 창을 닫고 다시 여세요. [" + failure + "]",
        Stage.Disconnected => "연결이 종료되었습니다. 다시 연결하려면 다시 연결을 누르세요.",
        _ => "연결 창을 닫았습니다."
    };
    public bool IsCurrent(long attempt) => Current != Stage.Closed && Attempt == attempt;
    public bool IsNavigation(long attempt, ulong navigation) => IsCurrent(attempt) && NavigationId == navigation;
    public bool CanRelay(long attempt, ulong navigation) => IsNavigation(attempt,navigation) && Current is not (Stage.Failed or Stage.Disconnected);
    public bool Navigate(long attempt, ulong navigation, bool login)
    {
        if(!IsCurrent(attempt))return false;
        NavigationId=navigation;loginDestination=login;ShowDocument=false;Current=Stage.Navigating;return true;
    }
    public bool DocumentReady(long attempt, ulong navigation, bool relay)
    {
        if(!CanRelay(attempt,navigation))return false;
        ShowDocument=true;
        if(Current==Stage.Navigating)Current=relay?Stage.Connecting:Stage.AwaitingLogin;
        return true;
    }
    public bool BridgeReady(long attempt, ulong navigation)
    {
        if(!CanRelay(attempt,navigation)||Current==Stage.Connected)return false;
        ShowDocument=true;Current=Stage.Connecting;return true;
    }
    public bool Paired(long attempt, ulong navigation)
    {
        if(!CanRelay(attempt,navigation)||Current!=Stage.Connecting)return false;
        ShowDocument=true;Current=Stage.Connected;return true;
    }
    public bool Fail(long attempt, string code, ulong? navigation=null)
    {
        if(!IsCurrent(attempt)||navigation is not null&&NavigationId!=navigation)return false;
        failure=code;Current=Stage.Failed;ShowDocument=false;return true;
    }
    public bool Disconnect(long attempt, ulong navigation)
    {
        if(!IsNavigation(attempt,navigation)||Current==Stage.Failed)return false;
        Current=Stage.Disconnected;return true;
    }
    public void Stop(){if(Current==Stage.Closed)return;Attempt++;NavigationId=null;Current=Stage.Disconnected;}
    public bool TryRetry(out long attempt)
    {
        attempt=Attempt;if(!CanRetry)return false;
        attempt=++Attempt;NavigationId=null;ShowDocument=false;Current=Stage.Preparing;failure="";return true;
    }
    public async Task<bool> AcceptPreparedAsync(long attempt, Action accept, Func<Task> retire)
    {
        if(!IsCurrent(attempt)){await retire();return false;}
        accept();return true;
    }
    public void Close(){Attempt++;NavigationId=null;ShowDocument=false;Current=Stage.Closed;}
}
