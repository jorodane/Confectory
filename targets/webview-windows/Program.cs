using System.Text.Json;
using System.Text.Json.Nodes;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

// Only this generic rendering process depends on WindowsDesktop/WebView2.
// The owning ProjectPack retains the domain context and validates every request.
internal static class Program
{
    [STAThread]
    static int Main()
    {
        if (!OperatingSystem.IsWindows()) { Console.Error.WriteLine("Embedded WebUI requires Windows."); return 2; }
        ApplicationConfiguration.Initialize();
        using var rpc = new PackChannel();
        using var form = new Form { Text = "Confectory", Width = 1440, Height = 960 };
        using var view = new WebView2 { Dock = DockStyle.Fill };
        form.Controls.Add(view);
        int result = 0;
        string origin = "https://" + Guid.NewGuid().ToString("N") + ".confectory.invalid";
        string profile = Path.Combine(Path.GetTempPath(), "Confectory", "webview", Guid.NewGuid().ToString("N"));
        bool closing = false;
        form.FormClosing += (_, _) => { closing = true; rpc.Dispose(); };
        form.Shown += async (_, _) =>
        {
            try
            {
                if (rpc.IsClosed) { result = 2; form.Close(); return; }
                // No runtime downloader or installer. A missing runtime fails explicitly.
                _ = CoreWebView2Environment.GetAvailableBrowserVersionString();
                var environment = await CoreWebView2Environment.CreateAsync(null, profile);
                await view.EnsureCoreWebView2Async(environment);
                if (closing) return;
                var core = view.CoreWebView2;
                core.Settings.AreHostObjectsAllowed = false;
                core.Settings.AreDevToolsEnabled = false;
                core.Settings.AreDefaultContextMenusEnabled = false;
                core.Settings.IsStatusBarEnabled = false;
                core.Settings.IsPasswordAutosaveEnabled = false;
                core.Settings.IsGeneralAutofillEnabled = false;
                bool Owned(string url) => Uri.TryCreate(url, UriKind.Absolute, out var uri) && uri.GetLeftPart(UriPartial.Authority) == origin;
                core.NavigationStarting += (_, e) => { if (!Owned(e.Uri)) e.Cancel = true; };
                core.FrameNavigationStarting += (_, e) => e.Cancel = true;
                core.NewWindowRequested += (_, e) => e.Handled = true;
                core.PermissionRequested += (_, e) => e.State = CoreWebView2PermissionState.Deny;
                core.DownloadStarting += (_, e) => e.Cancel = true;
                core.AddWebResourceRequestedFilter("*", CoreWebView2WebResourceContext.All, CoreWebView2WebResourceRequestSourceKinds.All);
                core.WebResourceRequested += async (_, e) =>
                {
                    using var defer = e.GetDeferral();
                    try
                    {
                        if (!Owned(e.Request.Uri) || e.Request.Method != "GET") throw new InvalidOperationException();
                        var path = new Uri(e.Request.Uri).AbsolutePath;
                        var asset = (await rpc.Call("resource", JsonValue.Create(path)))!.AsArray();
                        byte[] bytes = Convert.FromBase64String(asset[1]!.GetValue<string>());
                        const string policy = "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'none'; frame-src 'none'; worker-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'";
                        e.Response = environment.CreateWebResourceResponse(new MemoryStream(bytes, false), 200, "OK", "Content-Type: " + asset[0]!.GetValue<string>() + "\r\nCache-Control: no-store\r\nX-Content-Type-Options: nosniff\r\nContent-Security-Policy: " + policy);
                    }
                    catch { if (!closing) e.Response = environment.CreateWebResourceResponse(null, 403, "Resource unavailable", "Content-Type: text/plain"); }
                };
                core.WebMessageReceived += async (_, e) =>
                {
                    string id = "";
                    try
                    {
                        if (!Owned(e.Source) || e.WebMessageAsJson.Length > 2097152) return;
                        var message = JsonNode.Parse(e.WebMessageAsJson)!;
                        id = message["id"]!.GetValue<string>();
                        if (id.Length is < 1 or > 128) return;
                        var response = await rpc.Call("request", message["envelope"]?.DeepClone());
                        if (!closing && core.Source == e.Source) core.PostWebMessageAsJson(new JsonObject { ["id"] = id, ["reply"] = response }.ToJsonString());
                    }
                    catch { if (!closing && id.Length is > 0 and <= 128) core.PostWebMessageAsJson(new JsonObject { ["id"] = id, ["error"] = "transport_closed" }.ToJsonString()); }
                };
                // The page gets only an envelope transport; no host object, paths or shell.
                await core.AddScriptToExecuteOnDocumentCreatedAsync("""
                    (()=>{
                      if(window!==window.top)return;
                      const pending=new Map();let serial=0;
                      chrome.webview.addEventListener('message',event=>{
                        const p=pending.get(event.data.id);if(!p)return;pending.delete(event.data.id);
                        clearTimeout(p.timer);event.data.error?p.reject(Error(event.data.error)):p.resolve(event.data.reply);
                      });
                      Object.defineProperty(window,'confectoryWebUI',{value:Object.freeze({send(envelope){
                        if(pending.size>=64)return Promise.reject(Error('transport_busy'));
                        const id=String(++serial);return new Promise((resolve,reject)=>{
                          const timer=setTimeout(()=>{pending.delete(id);reject(Error('transport_timeout'));},30000);
                          pending.set(id,{resolve,reject,timer});chrome.webview.postMessage({id,envelope});
                        });
                      }})});
                    })();
                    """);
                core.Navigate(origin + "/");
            }
            catch (Exception e)
            {
                result = 2;
                string message = e is WebView2RuntimeNotFoundException
                    ? "Microsoft Edge WebView2 Runtime is not available. Nothing was installed."
                    : "Embedded WebUI could not start: " + e.GetType().Name;
                Console.Error.WriteLine(message);
                if (!closing) { MessageBox.Show(form, message, "Confectory", MessageBoxButtons.OK, MessageBoxIcon.Error); form.Close(); }
            }
        };
        rpc.Disconnected += () => { if (form.IsHandleCreated && !closing) form.BeginInvoke(() => { result = 2; form.Close(); }); };
        Application.Run(form);
        // Do not race WebView2's process shutdown to delete its active profile.
        return result;
    }
}

