using System.Text.Json.Nodes;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

// A separate authenticated Site surface. It never receives the editor's generic
// envelope transport, local session token, host objects, cookies or file paths.
internal sealed class SiteRelayWindow : Form
{
    const string Protocol = SiteRelayBoundary.Protocol;
    const string Address = SiteRelayBoundary.Address;
    readonly PackChannel rpc;
    readonly JsonObject configuration;
    readonly WebView2 view = new() { Dock = DockStyle.Fill };
    readonly string profile = Path.Combine(Path.GetTempPath(), "Confectory", "site-relay", Guid.NewGuid().ToString("N"));
    bool closed, closingMessage, sentHello; int navigation,inFlight;
    public SiteRelayWindow(PackChannel channel, JsonObject config)
    {
        rpc = channel; configuration = config;
        if (config["url"]?.ToString() != Address || config["protocol"]?.ToString() != Protocol || config["nonce"]?.ToString().Length != 64) throw new ArgumentException("Trusted Site configuration required");
        Text = "Confectory · 개인 플러그인 연결"; Width = 800; Height = 760;
        Controls.Add(view);
        var bar=new ToolStrip{Dock=DockStyle.Top};var reconnect=new ToolStripButton("다시 연결");bar.Items.Add(reconnect);Controls.Add(bar);
        reconnect.Click+=async(_,_)=>{if(inFlight>0||closed||view.CoreWebView2 is null)return;reconnect.Enabled=false;try{var fresh=await rpc.Call("native",new JsonObject{["action"]="site-relay",["payload"]=new JsonObject{["prepare"]=true}});if(fresh?["ok"]?.GetValue<bool>()!=true)throw new InvalidOperationException();configuration.Clear();foreach(var item in fresh["result"]!.AsObject())configuration[item.Key]=item.Value?.DeepClone();view.CoreWebView2.Navigate(Address);}catch{MessageBox.Show(this,"엔진 연결을 준비한 뒤 다시 시도하세요.");}finally{reconnect.Enabled=true;}};
        Shown += async (_, _) => await Initialize();
        FormClosed += async (_, _) => {
            closed = true;
            try { await Relay(new JsonObject { ["type"] = "close", ["nonce"] = configuration["nonce"]!.DeepClone() }); } catch { }
            view.Dispose();
            // InPrivate cookies are ephemeral. Cleanup can race the browser's exit;
            // never keep a reusable login/profile as the connection mechanism.
            try { Directory.Delete(profile, true); } catch (IOException) { } catch (UnauthorizedAccessException) { }
        };
    }
    static bool Owned(string source) => SiteRelayBoundary.Owned(source);
    async Task<JsonNode?> Relay(JsonObject input)
    {
        var reply = await rpc.Call("native", new JsonObject { ["action"] = "site-relay", ["payload"] = input });
        if (reply?["ok"]?.GetValue<bool>() != true) throw new InvalidOperationException("engine_rejected");
        return reply["result"]?.DeepClone();
    }
    async Task Initialize()
    {
        try {
            view.CreationProperties = new CoreWebView2CreationProperties { UserDataFolder = profile, ProfileName = "ConfectoryRelay", IsInPrivateModeEnabled = true };
            await view.EnsureCoreWebView2Async(); if (closed) return;
            var core = view.CoreWebView2;
            core.Settings.AreHostObjectsAllowed = false; core.Settings.AreDevToolsEnabled = false;
            core.Settings.AreDefaultContextMenusEnabled = false; core.Settings.IsStatusBarEnabled = false;
            core.Settings.IsPasswordAutosaveEnabled = false; core.Settings.IsGeneralAutofillEnabled = false;
            core.PermissionRequested += (_, e) => e.State = CoreWebView2PermissionState.Deny;
            core.DownloadStarting += (_, e) => e.Cancel = true;
            core.NavigationStarting += (_, e) => {
                if (!Uri.TryCreate(e.Uri, UriKind.Absolute, out var uri) || uri.Scheme != "https") e.Cancel = true;
                sentHello = false; navigation++;
            };
            // Login redirects may leave the Site; native messages are accepted only
            // on the exact trusted relay document. No frame bridge is registered.
            core.NewWindowRequested += (_, e) => { e.Handled = true; if (Uri.TryCreate(e.Uri, UriKind.Absolute, out var uri) && uri.Scheme == "https") core.Navigate(uri.AbsoluteUri); };
            core.WebMessageReceived += async (_, e) => {
                if (closed || !SiteRelayBoundary.TryRead(core.Source,e.Source,e.WebMessageAsJson,configuration["nonce"]!.ToString(),sentHello,out var message)) return;
                string requestId = "";bool entered=false,isClose=false;int generation=navigation;
                try {
                    string type = message!["type"]?.ToString() ?? "";
                    if (type == "ready") {
                        if (sentHello) return; sentHello = true;
                        var hello = (JsonObject)configuration.DeepClone(); hello.Remove("url"); hello["type"] = "hello";
                        core.PostWebMessageAsJson(hello.ToJsonString()); return;
                    }
                    if (!sentHello || message["nonce"]?.ToString() != configuration["nonce"]!.ToString() || type is not ("paired" or "pulse" or "dispatch" or "close")) return;
                    requestId = message["requestId"]?.GetValue<string>() ?? "";
                    if (requestId.Length is < 1 or > 128 || inFlight>0&&type!="close" || type=="close"&&closingMessage) return;
                    isClose=type=="close";if(isClose)closingMessage=true;inFlight++;entered=true;
                    // Construct the permitted relay message; never forward native
                    // prepare, grant, editor envelopes, endpoints or host actions.
                    var input = new JsonObject { ["type"] = type, ["nonce"] = configuration["nonce"]!.DeepClone() };
                    foreach (string field in new[] { "sessionId", "expiresAt", "job" }) if (message[field] is not null) input[field] = message[field]!.DeepClone();
                    var result = await Relay(input);
                    if (!closed && generation==navigation && Owned(core.Source) && sentHello) core.PostWebMessageAsJson(new JsonObject { ["protocol"] = Protocol, ["nonce"] = configuration["nonce"]!.DeepClone(), ["requestId"] = requestId, ["result"] = result }.ToJsonString());
                } catch {
                    if (!closed && generation==navigation && Owned(core.Source) && requestId.Length is > 0 and <= 128) core.PostWebMessageAsJson(new JsonObject { ["protocol"] = Protocol, ["nonce"] = configuration["nonce"]!.DeepClone(), ["requestId"] = requestId, ["error"] = "engine_rejected" }.ToJsonString());
                } finally { if(entered)inFlight--;if(isClose)closingMessage=false; }
            };
            core.Navigate(Address);
        } catch (Exception e) {
            if (!closed) { Controls.Clear(); Controls.Add(new Label { Dock = DockStyle.Fill, Padding = new Padding(24), Text = "연결 창을 시작할 수 없습니다: " + e.GetType().Name }); }
        }
    }
}
