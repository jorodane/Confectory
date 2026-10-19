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
        bool closing = false,nativePickerOpen=false;SiteRelayWindow? siteRelay=null;
        form.FormClosed += (_,_)=>siteRelay?.Shutdown();
        bool closeApproved=false,closePending=false,ready=false;TaskCompletionSource<bool>? presentationFlush=null;string? presentationFlushKey=null;
        form.FormClosing += async (_, e) => {
            if(ready&&!closeApproved&&!rpc.IsClosed){
                e.Cancel=true;if(closePending)return;
                if(MessageBox.Show(form,"Close this workspace completely? Background work will stop. Pending input and placement will be checked before closing.","Confectory",MessageBoxButtons.OKCancel,MessageBoxIcon.Question)!=DialogResult.OK)return;
                closePending=true;
                try{
                    presentationFlushKey=Guid.NewGuid().ToString("N");presentationFlush=new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
                    string flushKey=System.Text.Json.JsonSerializer.Serialize(presentationFlushKey);
                    await view.CoreWebView2.ExecuteScriptAsync("(()=>{const key="+flushKey+";Promise.resolve().then(()=>globalThis.confectoryFlushPresentation?.()).then(()=>chrome.webview.postMessage({presentationFlush:key,ok:true}),()=>chrome.webview.postMessage({presentationFlush:key,ok:false}));})()");
                    if(!await presentationFlush.Task.WaitAsync(TimeSpan.FromSeconds(15))){MessageBox.Show(form,"Input or placement could not be saved. The workspace remains open; retry after resolving the save failure.");return;}
                    var reply=await rpc.Call("native",new JsonObject{["action"]="close",["payload"]=new JsonObject{["confirmed"]=true}});if(reply?["ok"]?.GetValue<bool>()!=true&&reply?["error"]?["code"]?.GetValue<string>()!="host_action_denied"){MessageBox.Show(form,"Workspace could not close. Save the draft and try again.");return;}closeApproved=true;form.Close();}
                catch{MessageBox.Show(form,"Close could not be acknowledged. The workspace remains open; input and placement are retained for retry.");}finally{closePending=false;presentationFlushKey=null;presentationFlush=null;}
                return;
            }
            closing=true;rpc.Dispose();
        };
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
                string? projectParent=null,parentTicket=null;
                core.WebMessageReceived += async (_, e) =>
                {
                    string id = "";
                    try
                    {
                        if (!Owned(e.Source) || e.WebMessageAsJson.Length > 2097152) return;
                        var message = JsonNode.Parse(e.WebMessageAsJson)!;
                        if(closePending&&presentationFlushKey is not null&&message["presentationFlush"]?.GetValue<string>()==presentationFlushKey){presentationFlush?.TrySetResult(message["ok"]?.GetValue<bool>()==true);return;}
                        id = message["id"]!.GetValue<string>();
                        if (id.Length is < 1 or > 128) return;
                        JsonNode? response;
                        if(message["native"]?.GetValue<string>()=="site-connect"){
                            if(siteRelay is {IsDisposed:false}){siteRelay.OpenConnectionWindow();response=new JsonObject{["ok"]=true};}
                            else{
                            var prepared=await rpc.Call("native",new JsonObject{["action"]="site-relay",["payload"]=new JsonObject{["prepare"]=true}});
                            if(prepared?["ok"]?.GetValue<bool>()!=true)throw new InvalidOperationException("Prepare the engine connection first");
                            siteRelay=new SiteRelayWindow(rpc,prepared["result"]!.DeepClone().AsObject());siteRelay.Show(form);response=new JsonObject{["ok"]=true};
                            }
                        }else if(message["native"]?.GetValue<string>()=="site-disconnect"){
                            if(siteRelay is {IsDisposed:false})await siteRelay.DisconnectConnectionAsync();response=new JsonObject{["ok"]=true};
                        }else if(message["native"]?.GetValue<string>()=="open-file"){
                            if(nativePickerOpen)throw new InvalidOperationException("Picker busy");nativePickerOpen=true;
                            try{using var picker=new FolderBrowserDialog{Description="Open an existing project folder",UseDescriptionForTitle=true};
                            if(picker.ShowDialog(form)==DialogResult.OK){
                                response=await rpc.Call("native",new JsonObject{["action"]="open-file",["payload"]=new JsonObject{["path"]=picker.SelectedPath}});
                            }else response=new JsonObject{["ok"]=true,["cancelled"]=true};}finally{nativePickerOpen=false;}
                         }else if(message["native"]?.GetValue<string>()=="choose-project-parent"){
                            if(nativePickerOpen)throw new InvalidOperationException("Picker busy");nativePickerOpen=true;
                            try{using var picker=new FolderBrowserDialog{Description="Choose a parent directory for the new project",UseDescriptionForTitle=true};
                            if(picker.ShowDialog(form)==DialogResult.OK){projectParent=picker.SelectedPath;parentTicket=Guid.NewGuid().ToString("N");response=new JsonObject{["ok"]=true,["parent"]=parentTicket,["label"]=Path.GetFileName(Path.TrimEndingDirectorySeparator(projectParent))};}
                            else response=new JsonObject{["ok"]=true,["cancelled"]=true};}finally{nativePickerOpen=false;}
                         }else if(message["native"]?.GetValue<string>()=="create-project"){
                            if(nativePickerOpen)throw new InvalidOperationException("Picker busy");
                            string title=message["envelope"]?["title"]?.GetValue<string>()??"",description=message["envelope"]?["description"]?.GetValue<string>()??"";
                            if(string.IsNullOrWhiteSpace(title)||title.Length>128||description.Length>4096)throw new ArgumentException("Bounded project information required");
                            string? ticket=message["envelope"]?["parent"]?.GetValue<string>();
                            if(ticket is not null){
                                if(ticket!=parentTicket||projectParent is null)throw new ArgumentException("Unknown parent selection");
                                nativePickerOpen=true;try{
                                    response=await rpc.Call("native",new JsonObject{["action"]="create-project",["payload"]=new JsonObject{["directory"]=projectParent,["title"]=title,["description"]=description}});
                                    if(response?["ok"]?.GetValue<bool>()==true){projectParent=null;parentTicket=null;}
                                }finally{nativePickerOpen=false;}
                            }else{
                                nativePickerOpen=true;try{using var picker=new FolderBrowserDialog{Description="Choose a parent directory for the new project",UseDescriptionForTitle=true};
                                response=picker.ShowDialog(form)==DialogResult.OK
                                    ?await rpc.Call("native",new JsonObject{["action"]="create-project",["payload"]=new JsonObject{["directory"]=picker.SelectedPath,["title"]=title,["description"]=description}})
                                    :new JsonObject{["ok"]=true,["cancelled"]=true};}finally{nativePickerOpen=false;}
                            }
                        }else if(message["native"] is not null)response=new JsonObject{["ok"]=false,["error"]=new JsonObject{["code"]="host_action_denied"}};
                        else response = await rpc.Call("request", message["envelope"]?.DeepClone());
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
                      Object.defineProperty(window,'confectoryWebUI',{value:Object.freeze({connectSite(){return this.send(null,'site-connect');},disconnectSite(){return this.send(null,'site-disconnect');},pickFile(){return this.send(null,'open-file');},chooseProjectParent(){return this.send(null,'choose-project-parent');},createProject(title,description,parent){return this.send({title,description,parent},'create-project');},send(envelope,native){
                        if(pending.size>=64)return Promise.reject(Error('transport_busy'));
                        const id=String(++serial);return new Promise((resolve,reject)=>{
                          const timer=setTimeout(()=>{pending.delete(id);reject(Error('transport_timeout'));},30000);
                          pending.set(id,{resolve,reject,timer});chrome.webview.postMessage({id,envelope,native});
                        });
                      }})});
                    })();
                    """);
                ready=true;core.Navigate(origin + "/");
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

