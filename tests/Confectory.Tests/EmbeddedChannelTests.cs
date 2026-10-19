using System.IO.Pipes;
using System.Text.Json.Nodes;
using Confectory.Core;
namespace Confectory.Tests;
public sealed class EmbeddedChannelTests : TestCase
{
    public void test_site_rendered_login_is_not_replaced_by_a_failure_overlay()
    {
        var state=new SiteRelayPresentation();long attempt=state.Attempt;
        state.Navigate(attempt,10,true);state.DocumentReady(attempt,10,false);
        True(state.ShowDocument);True(state.Fail(attempt,"ConnectionAborted HTTP=200",10));
        True(state.ShowDocument,"A rendered login must remain visible when navigation reports a failure");
        True(state.CanRetry&&!state.Busy);True(state.Message.Contains("ConnectionAborted"));
        True(!state.Paired(attempt,10),"Keeping the login visible must not accept a failed handshake");
    }
    public void test_site_authentication_wait_and_stopped_successful_document_remain_usable()
    {
        foreach(string error in new[]{"ValidAuthenticationCredentialsRequired","ValidProxyAuthenticationRequired"}){
            var state=new SiteRelayPresentation();long attempt=state.Attempt;
            state.Navigate(attempt,10,true);
            True(state.NavigationCompleted(attempt,10,false,error,401,false));
            Equal(SiteRelayPresentation.Stage.AwaitingLogin,state.Current);True(state.ShowDocument&&!state.CanRetry);
            True(state.Diagnostic.Contains(error)&&state.Diagnostic.Contains("HTTP=401"));
            True(!state.Paired(attempt,10),"An authentication wait is not a successful pair");
            state.Navigate(attempt,10,false,true);state.DocumentReady(attempt,10,true);state.BridgeReady(attempt,10);
            True(state.Paired(attempt,10));True(state.NavigationCompleted(attempt,10,false,"ConnectionAborted",200,true));
            Equal(SiteRelayPresentation.Stage.Connected,state.Current);True(state.ShowDocument&&!state.CanRetry);
        }
        var cancelled=new SiteRelayPresentation();long current=cancelled.Attempt;cancelled.Navigate(current,20,true);cancelled.DocumentReady(current,20,false);
        True(cancelled.NavigationCompleted(current,20,false,"OperationCanceled",0,false));Equal(SiteRelayPresentation.Stage.AwaitingLogin,cancelled.Current);
        cancelled.Navigate(current,21,false,true);True(!cancelled.NavigationCompleted(current,20,false,"ConnectionReset",0,false));
        True(cancelled.BridgeReady(current,21));True(cancelled.Paired(current,21));
    }
    public void test_site_real_navigation_failures_keep_browser_details_and_require_retry()
    {
        foreach(var failure in new[]{("ConnectionAborted",0),("HostNameNotResolved",0),("CertificateExpired",0),("UnexpectedError",403)}){
            var state=new SiteRelayPresentation();long attempt=state.Attempt;state.Navigate(attempt,10,true);
            True(state.NavigationCompleted(attempt,10,false,failure.Item1,failure.Item2,false));
            Equal(SiteRelayPresentation.Stage.Failed,state.Current);True(state.ShowDocument&&state.CanRetry&&!state.Busy);
            True(state.Diagnostic.Contains(failure.Item1)&&state.Diagnostic.Contains("HTTP="+failure.Item2));
            True(!state.BridgeReady(attempt,10)&&!state.Paired(attempt,10));
            True(state.TryRetry(out long fresh));True(!state.NavigationCompleted(attempt,10,true,"Unknown",200,true));
            state.Navigate(fresh,11,false);True(state.NavigationCompleted(fresh,11,true,"Unknown",200,true));True(state.BridgeReady(fresh,11));True(state.Paired(fresh,11));
        }
        var exception=new System.Runtime.InteropServices.COMException("secret-cookie-and-local-path",unchecked((int)0x8007139F));
        string report=SiteRelayPresentation.ExceptionCode("initialize",exception);
        True(report.Contains("initialize")&&report.Contains("COMException")&&report.Contains("0x8007139F"));True(!report.Contains("secret"));
    }
    public void test_site_hidden_relay_reopen_expiry_shutdown_and_fixed_profile()
    {
        var relay=new SiteRelayLifetime();long start=1000,expiry=start+1800000;
        True(!relay.Connected&&!relay.CanHide&&!relay.Hidden);True(!relay.Hide());
        True(relay.Pair(start,expiry,true));True(relay.CanHide);True(relay.Hide());True(relay.Hidden&&relay.Connected);
        True(relay.Reopen());True(!relay.Hidden&&relay.Connected);Equal(expiry,relay.ExpiresAt);
        for(int i=1;i<=600;i++)True(!relay.Tick(start+i*2000));True(relay.Connected);Equal(expiry,relay.ExpiresAt);
        True(relay.Hide());True(relay.Tick(expiry));True(!relay.Connected&&!relay.CanHide);True(!relay.Tick(expiry+1));
        True(relay.Reopen());True(!relay.Connected);True(relay.Pair(expiry+1,expiry+1000,true));relay.Disconnect();True(!relay.Connected&&!relay.CanHide);
        relay.Shutdown();True(relay.Closed&&!relay.Connected&&!relay.Reopen());True(!relay.Pair(0,1000,true));
        var oldSite=new SiteRelayLifetime();True(oldSite.Pair(0,1000,false));True(!oldSite.CanHide&&!oldSite.Hide());
        string local=Path.GetFullPath(Path.Combine(Path.GetTempPath(),"owned-confectory-profile"));string saved=SiteRelayProfile.DirectoryFor(local);
        Equal(saved,SiteRelayProfile.DirectoryFor(local));True(saved.Contains("Confectory")&&saved.Contains("confectory-connect.jorodane.chatgpt.site"));True(!SiteRelayProfile.InPrivate);
        var restarted=new SiteRelayLifetime();True(!restarted.Connected&&!restarted.HostWake&&restarted.ExpiresAt==0);True(!restarted.Hide());
    }
    public void test_site_login_clear_disconnects_before_profile_clear_and_does_not_claim_late_success()
    {
        var relay=new SiteRelayLifetime();relay.Pair(0,1800000,true);var events=new List<string>();bool cookie=true;
        True(relay.ForgetLoginAsync(()=>{relay.Disconnect();events.Add("disconnect");return Task.CompletedTask;},()=>{True(!relay.Connected);cookie=false;events.Add("profile-clear");return Task.CompletedTask;}).GetAwaiter().GetResult());
        True(!cookie);Equal("disconnect,profile-clear",string.Join(',',events));
        var response=new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);var closed=new SiteRelayLifetime();int cleared=0;
        var late=closed.ForgetLoginAsync(async()=>{await response.Task;},()=>{cleared++;return Task.CompletedTask;});closed.Shutdown();response.SetResult(true);True(!late.GetAwaiter().GetResult());Equal(0,cleared);
        bool failed=false;try{new SiteRelayLifetime().ForgetLoginAsync(()=>Task.CompletedTask,()=>throw new IOException("owned-clear-failure")).GetAwaiter().GetResult();}catch(IOException){failed=true;}True(failed);
    }
    public void test_site_window_slow_preparation_login_redirect_and_connected_presentation()
    {
        var state=new SiteRelayPresentation();long attempt=state.Attempt;
        Equal(SiteRelayPresentation.Stage.Preparing,state.Current);True(state.Busy&&!state.ShowDocument&&!state.CanRetry);True(state.Message.Contains("준비"));
        var ready=new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        async Task NavigateWhenReady(){await ready.Task;state.Navigate(attempt,10,false);}
        var initializing=NavigateWhenReady();True(!initializing.IsCompleted);True(!state.TryRetry(out _));
        // No elapsed-time input can turn a pending runtime/navigation into failure.
        for(int i=0;i<1000;i++)True(state.Current==SiteRelayPresentation.Stage.Preparing&&!state.CanRetry);
        ready.SetResult(true);initializing.GetAwaiter().GetResult();Equal(SiteRelayPresentation.Stage.Navigating,state.Current);
        True(!state.ShowDocument&&!state.CanRetry&&state.Busy);
        True(state.Navigate(attempt,11,true));True(!state.DocumentReady(attempt,10,true));True(!state.Fail(attempt,"old-navigation",10));
        True(state.DocumentReady(attempt,11,false));Equal(SiteRelayPresentation.Stage.AwaitingLogin,state.Current);True(state.ShowDocument&&!state.CanRetry&&!state.Busy);
        True(state.Navigate(attempt,12,false));True(state.BridgeReady(attempt,12));Equal(SiteRelayPresentation.Stage.Connecting,state.Current);
        True(state.Paired(attempt,12));Equal(SiteRelayPresentation.Stage.Connected,state.Current);True(!state.CanRetry&&!state.Busy&&state.ShowDocument);True(state.Message.Contains("숨김")&&state.Message.Contains("해제"));
        True(state.DocumentReady(attempt,12,true));Equal(SiteRelayPresentation.Stage.Connected,state.Current);True(!state.TryRetry(out _));
    }
    public void test_site_window_real_failure_retry_and_old_navigation_do_not_replace_current_state()
    {
        var state=new SiteRelayPresentation();long old=state.Attempt;state.Navigate(old,1,false);
        True(state.Fail(old,"ConnectionAborted",1));True(state.CanRetry&&!state.Busy&&!state.ShowDocument);True(state.Message.Contains("ConnectionAborted"));
        True(!state.DocumentReady(old,1,true));True(!state.Paired(old,1));True(!state.Disconnect(old,1));
        True(state.TryRetry(out long current));True(current!=old);Equal(SiteRelayPresentation.Stage.Preparing,state.Current);
        True(!state.Fail(old,"late-initialization"));True(!state.Navigate(old,2,true));True(!state.DocumentReady(old,1,true));
        state.Navigate(current,2,false);state.BridgeReady(current,2);state.Paired(current,2);
        True(!state.Fail(current,"old-completion",1));Equal(SiteRelayPresentation.Stage.Connected,state.Current);
        True(state.Disconnect(current,2));Equal(SiteRelayPresentation.Stage.Disconnected,state.Current);True(state.CanRetry);True(!state.Paired(current,2));
    }
    public void test_site_window_close_retires_late_preparation_and_ignores_late_callbacks()
    {
        var state=new SiteRelayPresentation();long initial=state.Attempt;
        state.Fail(initial,"initialization-failed");True(state.TryRetry(out long attempt));
        var response=new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);int adopted=0,retired=0;
        async Task Complete(){await response.Task;await state.AcceptPreparedAsync(attempt,()=>adopted++,()=>{retired++;return Task.CompletedTask;});}
        var pending=Complete();True(!pending.IsCompleted);state.Close();response.SetResult(true);pending.GetAwaiter().GetResult();
        Equal(0,adopted);Equal(1,retired);Equal(SiteRelayPresentation.Stage.Closed,state.Current);True(!state.CanRetry&&!state.Busy&&!state.ShowDocument);
        True(!state.IsCurrent(attempt));True(!state.Navigate(attempt,1,false));True(!state.DocumentReady(attempt,1,true));True(!state.BridgeReady(attempt,1));True(!state.Paired(attempt,1));True(!state.Fail(attempt,"late-error"));True(!state.TryRetry(out _));
        // A superseded attempt is discarded even while a newer window attempt lives.
        var retry=new SiteRelayPresentation();long old=retry.Attempt;retry.Fail(old,"network");True(retry.TryRetry(out long fresh));
        True(!retry.AcceptPreparedAsync(old,()=>adopted++,()=>{retired++;return Task.CompletedTask;}).GetAwaiter().GetResult());
        True(retry.AcceptPreparedAsync(fresh,()=>adopted++,()=>{retired++;return Task.CompletedTask;}).GetAwaiter().GetResult());Equal(1,adopted);Equal(2,retired);
    }
    public void test_windows_native_site_connect_transport_envelope_and_reply()
    {
        var run=Processes.Run(new[]{"node",Path.Combine(Fixture.Repo,"tests/web/native_site_connect.mjs")},timeoutSeconds:35);
        True(run.ExitCode==0,run.Stdout+run.Stderr);True(run.Stdout.Contains("PASS actual Windows injected Site connect native envelope"));
    }
    public void test_site_relay_pins_document_nonce_protocol_and_bounded_schema()
    {
        string address=SiteRelayBoundary.Address,nonce=new('a',64);
        var message=new JsonObject{["protocol"]=SiteRelayBoundary.Protocol,["type"]="pulse",["nonce"]=nonce,["requestId"]="1",["sessionId"]="session"};
        bool Accept(JsonObject value,string? current=null,string? source=null,bool hello=true)=>SiteRelayBoundary.TryRead(current??address,source??address,value.ToJsonString(),nonce,hello,out _);
        True(Accept(message));True(!Accept(message,hello:false));
        foreach(string foreign in new[]{"http://confectory-connect.jorodane.chatgpt.site/editor-bridge",address+"/",address+"?other",address+"#other","https://confectory-connect.jorodane.chatgpt.site/signin-with-chatgpt","https://confectory-connect.jorodane.chatgpt.site.foreign.invalid/editor-bridge","https://foreign.invalid/editor-bridge"}){True(!Accept(message,current:foreign));True(!Accept(message,source:foreign));}
        var wrong=(JsonObject)message.DeepClone();wrong["nonce"]=new string('b',64);True(!Accept(wrong));
        wrong=(JsonObject)message.DeepClone();wrong["protocol"]="packengine.editor.v1";True(!Accept(wrong));
        foreach(string action in new[]{"start","scope","revoke","prepare","confirm","request","native"}){wrong=(JsonObject)message.DeepClone();wrong["type"]=action;True(!Accept(wrong));}
        wrong=(JsonObject)message.DeepClone();wrong["prepare"]=true;True(!Accept(wrong));
        wrong=(JsonObject)message.DeepClone();wrong["requestId"]=new string('x',129);True(!Accept(wrong));
        wrong=(JsonObject)message.DeepClone();wrong["requestId"]=1;True(!Accept(wrong));
        True(!SiteRelayBoundary.TryRead(address,address,new string('x',1572865),nonce,true,out _));
        True(!SiteRelayBoundary.TryRead(address,address,"[]",nonce,true,out _));
        True(!SiteRelayBoundary.TryRead(address,address,"{",nonce,true,out _));
        var ready=new JsonObject{["protocol"]=SiteRelayBoundary.Protocol,["type"]="ready"};True(Accept(ready,hello:false));True(!Accept(ready));
        var paired=(JsonObject)message.DeepClone();paired["type"]="paired";paired["hostWake"]=true;True(Accept(paired));
        paired["hostWake"]=false;True(!Accept(paired));paired["hostWake"]="true";True(!Accept(paired));
        wrong=(JsonObject)message.DeepClone();wrong["hostWake"]=true;True(!Accept(wrong));
    }
    // Exercises the actual platform-neutral host channel, not a replacement UI.
    public void test_embedded_channel_correlates_replies_and_retires_on_eof()
    {
        using var replies = new AnonymousPipeServerStream(PipeDirection.Out);
        using var input = new AnonymousPipeClientStream(PipeDirection.In, replies.ClientSafePipeHandle);
        using var requests = new AnonymousPipeServerStream(PipeDirection.In);
        using var output = new AnonymousPipeClientStream(PipeDirection.Out, requests.ClientSafePipeHandle);
        using var reader = new StreamReader(input);
        using var writer = new StreamWriter(output) { AutoFlush = true };
        using var observed = new StreamReader(requests);
        using var response = new StreamWriter(replies) { AutoFlush = true };
        using var channel = new PackChannel(reader, writer);
        var first = channel.Call("resource", JsonValue.Create("/assets/icon.png"));
        var second = channel.Call("request", new JsonObject { ["op"] = "mount" });
        var a = JsonNode.Parse(observed.ReadLineAsync().WaitAsync(TimeSpan.FromSeconds(5)).GetAwaiter().GetResult()!)!;
        var b = JsonNode.Parse(observed.ReadLineAsync().WaitAsync(TimeSpan.FromSeconds(5)).GetAwaiter().GetResult()!)!;
        Equal("/assets/icon.png", a["input"]!.GetValue<string>());
        True(!first.IsCompleted && !second.IsCompleted, "Requests must await their own reply");
        response.WriteLine(new JsonObject { ["id"] = b["id"]!.DeepClone(), ["result"] = "second" }.ToJsonString());
        Equal("second", second.WaitAsync(TimeSpan.FromSeconds(5)).GetAwaiter().GetResult()!.GetValue<string>());
        True(!first.IsCompleted, "Out-of-order reply completed wrong request");
        response.WriteLine(new JsonObject { ["id"] = a["id"]!.DeepClone(), ["error"] = "transport_rejected" }.ToJsonString());
        bool rejected = false;
        try { first.WaitAsync(TimeSpan.FromSeconds(5)).GetAwaiter().GetResult(); } catch (IOException) { rejected = true; }
        True(rejected, "Resource rejection must not become success");
        var pending = channel.Call("request", new JsonObject { ["op"] = "update" });
        response.Dispose();
        rejected = false;
        try { pending.WaitAsync(TimeSpan.FromSeconds(5)).GetAwaiter().GetResult(); } catch (IOException) { rejected = true; }
        True(rejected && channel.IsClosed, "EOF must retire pending calls");
        try { channel.Call("request", null); throw new Exception("Closed channel accepted request"); } catch (IOException) { }
    }
}
