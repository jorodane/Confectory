using System.Text.Json.Nodes;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

// This isolated Site view never receives the editor envelope transport, host
// objects, local WebUI token, file paths or copied browser credentials.
internal sealed class SiteRelayWindow : Form
{
    const string Protocol = SiteRelayBoundary.Protocol, Address = SiteRelayBoundary.Address;
    readonly PackChannel rpc;
    readonly JsonObject configuration;
    readonly SiteRelayPresentation presentation = new();
    readonly SiteRelayLifetime lifetime = new();
    readonly WebView2 view = new() { Dock = DockStyle.Fill, DefaultBackgroundColor = Color.FromArgb(16,20,24) };
    readonly Label status = new() { Dock = DockStyle.Fill, TextAlign = ContentAlignment.MiddleLeft };
    readonly TextBox diagnostic = new() { Dock=DockStyle.Bottom, Height=44, Multiline=true, ReadOnly=true, ScrollBars=ScrollBars.Vertical, BackColor=Color.FromArgb(24,30,35), ForeColor=Color.Gainsboro };
    readonly Label pending = new() { Dock = DockStyle.Fill, TextAlign = ContentAlignment.MiddleCenter, Padding = new Padding(28) };
    readonly Button reconnect = new() { Text = "다시 연결", Dock = DockStyle.Right, Width = 110, Visible = false };
    readonly Button hide = new() { Text = "창 숨기기", AutoSize = true, Visible = false };
    readonly Button disconnect = new() { Text = "연결 해제", AutoSize = true };
    readonly Button forget = new() { Text = "로그인 정보 지우기", AutoSize = true };
    readonly System.Windows.Forms.Timer heartbeat = new() { Interval = 2000 };
    readonly ProgressBar progress = new() { Dock = DockStyle.Bottom, Height = 4, Style = ProgressBarStyle.Marquee };
    readonly Panel placeholder = new() { Dock = DockStyle.Fill, BackColor = Color.FromArgb(16,20,24) };
    readonly string profile = SiteRelayProfile.DirectoryFor(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData));
    Task? disconnectTask;
    bool closed, closingMessage, sentHello, configured, navigationAllowed,forceClose,disconnecting,clearingLogin; int navigation,inFlight;
    public SiteRelayWindow(PackChannel channel, JsonObject config)
    {
        rpc=channel;configuration=config;Validate(config);
        Text="Confectory · 개인 플러그인 연결";Width=800;Height=760;BackColor=Color.FromArgb(16,20,24);ForeColor=Color.Gainsboro;
        view.CreationProperties=new CoreWebView2CreationProperties { UserDataFolder=profile, ProfileName=SiteRelayProfile.Name, IsInPrivateModeEnabled=SiteRelayProfile.InPrivate };
        var content=new Panel { Dock=DockStyle.Fill };content.Controls.Add(view);placeholder.Controls.Add(pending);content.Controls.Add(placeholder);Controls.Add(content);
        var header=new Panel { Dock=DockStyle.Top, Height=210, Padding=new Padding(16,10,16,10), BackColor=BackColor };
        var buttons=new FlowLayoutPanel { Dock=DockStyle.Bottom, Height=36, WrapContents=true };
        reconnect.Dock=DockStyle.None;reconnect.AutoSize=true;buttons.Controls.AddRange(new Control[]{hide,disconnect,reconnect,forget});
        var notice=new Label { Dock=DockStyle.Bottom, Height=36, Text="로그인 상태는 이 PC의 Confectory 전용 프로필에 저장됩니다. 로그인 정보 지우기로 삭제할 수 있습니다." };
        header.Controls.Add(status);header.Controls.Add(diagnostic);header.Controls.Add(notice);header.Controls.Add(buttons);header.Controls.Add(progress);Controls.Add(header);
        reconnect.Click+=async(_,_)=>await Retry();
        hide.Click+=(_,_)=>HideConnectionWindow();disconnect.Click+=async(_,_)=>await DisconnectConnectionAsync();
        forget.Click+=async(_,_)=>await ForgetLogin();
        heartbeat.Tick+=async(_,_)=>{
            if(closed||!lifetime.Connected)return;
            if(lifetime.Tick(DateTimeOffset.UtcNow.ToUnixTimeMilliseconds())){await DisconnectConnectionAsync();return;}
            try{if(lifetime.HostWake&&Owned(view.CoreWebView2.Source))view.CoreWebView2.PostWebMessageAsJson(new JsonObject{["protocol"]=Protocol,["type"]="wake",["nonce"]=configuration["nonce"]!.DeepClone()}.ToJsonString());}
            catch{await DisconnectConnectionAsync();}
        };
        Shown+=async(_,_)=>await Initialize(presentation.Attempt);
        FormClosing+=(_,e)=>{if(!forceClose&&e.CloseReason==CloseReason.UserClosing&&HideConnectionWindow())e.Cancel=true;};
        FormClosed+=async(_,_)=>{
            closed=true;lifetime.Shutdown();heartbeat.Stop();heartbeat.Dispose();presentation.Close();navigation++;sentHello=false;navigationAllowed=false;
            var retiring=(JsonObject)configuration.DeepClone();view.Dispose();
            await Retire(retiring);
            // Login data intentionally remains in this dedicated profile. No session
            // or project capability is restored from it on the next engine run.
        };
        Render();
    }
    static bool Owned(string source)=>SiteRelayBoundary.Owned(source);
    static void Validate(JsonObject config){if(config["url"]?.ToString()!=Address||config["protocol"]?.ToString()!=Protocol||config["nonce"]?.ToString().Length!=64)throw new ArgumentException("Trusted Site configuration required");}
    void Render()
    {
        if(closed)return;
        string message=disconnecting?"연결을 해제하고 있습니다.":presentation.Message;
        if(lifetime.Connected&&!lifetime.HostWake)message="엔진 연결 완료 · 이 Site 버전은 숨김 연결을 지원하지 않습니다. 창을 닫으면 연결이 해제됩니다.";
        status.Text=message;diagnostic.Text=presentation.Diagnostic;pending.Text=message+"\n\n연결 전 X는 취소합니다. 연결 후에는 창 숨김과 연결 해제를 구분해 주세요.";
        reconnect.Visible=presentation.CanRetry;reconnect.Enabled=inFlight==0&&!disconnecting&&!clearingLogin;progress.Visible=presentation.Busy;
        hide.Visible=lifetime.CanHide;disconnect.Enabled=!disconnecting&&!clearingLogin;forget.Enabled=!clearingLogin&&!disconnecting;
        placeholder.Visible=!presentation.ShowDocument;
        if(placeholder.Visible)placeholder.BringToFront();else view.BringToFront();
    }
    void ReportFailure(long attempt,string code,ulong? page=null)
    {
        if(!presentation.Fail(attempt,code,page))return;
        bool retire=lifetime.Connected;lifetime.Disconnect();heartbeat.Stop();
        if(retire)_=Retire((JsonObject)configuration.DeepClone());
        Render();if(!Visible)OpenConnectionWindow();
    }
    bool HideConnectionWindow(){if(!lifetime.Hide())return false;Hide();return true;}
    public void OpenConnectionWindow(){if(closed||!lifetime.Reopen())return;if(!Visible)Show();if(WindowState==FormWindowState.Minimized)WindowState=FormWindowState.Normal;Activate();}
    public void Shutdown(){if(closed||IsDisposed)return;forceClose=true;lifetime.Shutdown();heartbeat.Stop();Close();}
    public Task DisconnectConnectionAsync()=>disconnectTask is { IsCompleted:false } pendingTask?pendingTask:disconnectTask=DisconnectCore();
    async Task DisconnectCore()
    {
        if(closed)return;
        disconnecting=true;bool notify=lifetime.HostWake;lifetime.Disconnect();heartbeat.Stop();presentation.Stop();navigation++;sentHello=false;navigationAllowed=false;Render();
        var retiring=(JsonObject)configuration.DeepClone();
        try{
            try{if(notify&&view.CoreWebView2 is not null&&Owned(view.CoreWebView2.Source))view.CoreWebView2.PostWebMessageAsJson(new JsonObject{["protocol"]=Protocol,["type"]="disconnect",["nonce"]=retiring["nonce"]!.DeepClone()}.ToJsonString());}catch{}
            await Retire(retiring);
        }finally{disconnecting=false;Render();}
    }
    async Task ForgetLogin()
    {
        if(closed||clearingLogin||MessageBox.Show(this,"Confectory 전용 로그인 상태와 캐시를 지웁니다. 다른 Confectory 연결도 로그아웃될 수 있습니다. 일반 브라우저 정보는 바뀌지 않습니다.","저장된 로그인 지우기",MessageBoxButtons.OKCancel,MessageBoxIcon.Question)!=DialogResult.OK)return;
        clearingLogin=true;Render();
        try{
            if(!await lifetime.ForgetLoginAsync(DisconnectConnectionAsync,async()=>{
                await view.EnsureCoreWebView2Async();if(closed)return;
                view.CoreWebView2.Stop();await view.CoreWebView2.Profile.ClearBrowsingDataAsync();
            }))return;
            MessageBox.Show(this,"Confectory 전용 로그인 정보를 지웠습니다. 다음 연결에서는 다시 로그인하세요.");forceClose=true;Close();
        }catch(Exception e){if(!closed)ReportFailure(presentation.Attempt,SiteRelayPresentation.ExceptionCode("login-cleanup",e));}
        finally{clearingLogin=false;Render();}
    }
    async Task<JsonNode?> Relay(JsonObject input)
    {
        var reply=await rpc.Call("native",new JsonObject { ["action"]="site-relay",["payload"]=input });
        if(reply?["ok"]?.GetValue<bool>()!=true)throw new InvalidOperationException("engine_rejected");
        return reply["result"]?.DeepClone();
    }
    async Task Retire(JsonObject config){try{await Relay(new JsonObject { ["type"]="close",["nonce"]=config["nonce"]!.DeepClone() });}catch{}}
    async Task Retry()
    {
        if(closed||disconnecting||clearingLogin||inFlight>0||!presentation.TryRetry(out long attempt))return;
        lifetime.Disconnect();heartbeat.Stop();
        navigationAllowed=false;sentHello=false;navigation++;Render();
        try{
            try{view.CoreWebView2?.Stop();}catch(System.Runtime.InteropServices.COMException){}
            var fresh=await rpc.Call("native",new JsonObject { ["action"]="site-relay",["payload"]=new JsonObject { ["prepare"]=true } });
            if(fresh?["ok"]?.GetValue<bool>()!=true)throw new InvalidOperationException("engine_rejected");
            var next=fresh["result"]!.DeepClone().AsObject();Validate(next);
            if(!await presentation.AcceptPreparedAsync(attempt,()=>{
                configuration.Clear();foreach(var item in next)configuration[item.Key]=item.Value?.DeepClone();
            },()=>Retire(next)))return;
            await Initialize(attempt);
        }catch(Exception e){ReportFailure(attempt,SiteRelayPresentation.ExceptionCode("prepare",e));}
    }
    async Task Initialize(long attempt)
    {
        try{
            await view.EnsureCoreWebView2Async();if(!presentation.IsCurrent(attempt))return;
            var core=view.CoreWebView2;
            if(!configured){Configure(core);configured=true;}
            navigationAllowed=true;core.Navigate(Address);
        }catch(Exception e){ReportFailure(attempt,SiteRelayPresentation.ExceptionCode("initialize",e));}
    }
    void Configure(CoreWebView2 core)
    {
        core.Settings.AreHostObjectsAllowed=false;core.Settings.AreDevToolsEnabled=false;
        core.Settings.AreDefaultContextMenusEnabled=false;core.Settings.IsStatusBarEnabled=false;
        core.Settings.IsPasswordAutosaveEnabled=false;core.Settings.IsGeneralAutofillEnabled=false;
        core.PermissionRequested+=(_,e)=>e.State=CoreWebView2PermissionState.Deny;
        core.DownloadStarting+=(_,e)=>e.Cancel=true;
        core.NavigationStarting+=(_,e)=>{
            if(closed||!navigationAllowed||!Uri.TryCreate(e.Uri,UriKind.Absolute,out var uri)||uri.Scheme!="https"){e.Cancel=true;return;}
            if(lifetime.Connected){_ = DisconnectConnectionAsync();e.Cancel=true;return;}
            sentHello=false;navigation++;presentation.Navigate(presentation.Attempt,e.NavigationId,!Owned(e.Uri),e.IsRedirected);Render();
        };
        core.DOMContentLoaded+=(_,e)=>{if(!closed&&presentation.DocumentReady(presentation.Attempt,e.NavigationId,Owned(core.Source)))Render();};
        core.NavigationCompleted+=(_,e)=>{
            if(closed)return;
            if(!presentation.NavigationCompleted(presentation.Attempt,e.NavigationId,e.IsSuccess,e.WebErrorStatus.ToString(),e.HttpStatusCode,Owned(core.Source)))return;
            if(presentation.Current==SiteRelayPresentation.Stage.Failed)ReportFailure(presentation.Attempt,$"navigation: {e.WebErrorStatus}; HTTP={e.HttpStatusCode}",e.NavigationId);
            else Render();
        };
        core.ProcessFailed+=(_,e)=>{
            if(e.ProcessFailedKind is CoreWebView2ProcessFailedKind.BrowserProcessExited or CoreWebView2ProcessFailedKind.RenderProcessExited)
                ReportFailure(presentation.Attempt,"process: "+e.ProcessFailedKind);
        };
        // Authentication may navigate away. Only the exact relay document gets
        // a native message bridge; frames, host objects and generic calls are excluded.
        core.NewWindowRequested+=(_,e)=>{e.Handled=true;if(!closed&&Uri.TryCreate(e.Uri,UriKind.Absolute,out var uri)&&uri.Scheme=="https")core.Navigate(uri.AbsoluteUri);};
        core.WebMessageReceived+=async(_,e)=>{
            long attempt=presentation.Attempt;ulong? page=presentation.NavigationId;
            if(closed||page is null||!SiteRelayBoundary.TryRead(core.Source,e.Source,e.WebMessageAsJson,configuration["nonce"]!.ToString(),sentHello,out var message))return;
            string requestId="",type=message!["type"]!.ToString();bool entered=false,isClose=false;int generation=navigation;
            try{
                if(type=="ready"){
                    if(!presentation.BridgeReady(attempt,page.Value))return;
                    sentHello=true;Render();var hello=(JsonObject)configuration.DeepClone();hello.Remove("url");hello["type"]="hello";hello["hostWake"]=true;core.PostWebMessageAsJson(hello.ToJsonString());return;
                }
                if(type!="close"&&!presentation.CanRelay(attempt,page.Value))return;
                requestId=message["requestId"]!.GetValue<string>();
                if(inFlight>0&&type!="close"||type=="close"&&closingMessage)return;
                isClose=type=="close";if(isClose)closingMessage=true;inFlight++;entered=true;
                var input=new JsonObject { ["type"]=type,["nonce"]=configuration["nonce"]!.DeepClone() };
                foreach(string field in new[]{"sessionId","expiresAt","job"})if(message[field] is not null)input[field]=message[field]!.DeepClone();
                var result=await Relay(input);
                if(closed||generation!=navigation||!presentation.IsNavigation(attempt,page.Value)||!Owned(core.Source)||!sentHello)return;
                if(type!="close"&&!presentation.CanRelay(attempt,page.Value))return;
                if(type=="paired"){
                    if(!lifetime.Pair(DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),message["expiresAt"]!.GetValue<long>(),message["hostWake"]?.GetValue<bool>()==true))throw new InvalidOperationException("expired");
                    presentation.Paired(attempt,page.Value);heartbeat.Start();
                }
                if(type=="close"){lifetime.Disconnect();heartbeat.Stop();presentation.Disconnect(attempt,page.Value);}
                Render();core.PostWebMessageAsJson(new JsonObject { ["protocol"]=Protocol,["nonce"]=configuration["nonce"]!.DeepClone(),["requestId"]=requestId,["result"]=result }.ToJsonString());
                if(type=="paired")HideConnectionWindow();
            }catch(Exception error){
                if(!closed&&generation==navigation&&presentation.IsNavigation(attempt,page.Value)&&Owned(core.Source)&&requestId.Length is >0 and <=128){
                    if(type is "paired" or "pulse")ReportFailure(attempt,SiteRelayPresentation.ExceptionCode("native-"+type,error),page.Value);
                    Render();core.PostWebMessageAsJson(new JsonObject { ["protocol"]=Protocol,["nonce"]=configuration["nonce"]!.DeepClone(),["requestId"]=requestId,["error"]="engine_rejected" }.ToJsonString());
                }
            }finally{if(entered)inFlight--;if(isClose)closingMessage=false;Render();}
        };
    }
}
