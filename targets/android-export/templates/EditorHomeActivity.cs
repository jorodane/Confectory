using Android.App;
using Android.Content;
using Android.OS;
using Android.Provider;
using Android.Views;
using Android.Widget;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json.Nodes;
using Confectory.Core;

namespace Confectory.Android;

// Android owns one Activity, native text/IME/touch, and user-granted import.
// Project selection, drafts, Leave, catalogs, and shell ownership remain pack calls.
[Activity(MainLauncher=true,Exported=true,LaunchMode=global::Android.Content.PM.LaunchMode.SingleTop,
    WindowSoftInputMode=SoftInput.AdjustResize)]
[IntentFilter(new[]{Intent.ActionView},Categories=new[]{Intent.CategoryDefault,Intent.CategoryBrowsable},DataMimeType="application/octet-stream",DataScheme="content")]
[IntentFilter(new[]{Intent.ActionView},Categories=new[]{Intent.CategoryDefault,Intent.CategoryBrowsable},DataMimeType="text/plain",DataScheme="content")]
public sealed class MainActivity : Activity
{
    const int ImportRequest=402;
    static HomeState? retained;
    sealed class HomeState
    {
        public string Session="",Source="",Saved="",Origin="",Path="",Draft="";
        public bool Picker;
        public bool Dirty=>Source!=Saved;
    }
    HomeState State=>retained??throw new InvalidOperationException("Activity session is closed");
    LinearLayout? panel;
    TextView? status;
    EditText? draft,source;
    bool assigning;
    readonly Dictionary<string,NativeFieldHost> nativeHosts=new();
    protected override void OnCreate(Bundle? saved)
    {
        base.OnCreate(saved);
        AppDomain.CurrentDomain.SetData("Confectory.Android.NativeUI",(Func<string,string,string,long,string>)Request);
        AppDomain.CurrentDomain.SetData("Confectory.Android.DescribeProject",(Func<string,string[]>)Describe);
        if(retained is null)
        {
            string storage=System.IO.Path.Combine(FilesDir!.AbsolutePath,"home");
            retained=new HomeState{Session=PackCalls.CreateSession(FilesDir.AbsolutePath,storage)};
            RestoreLocalDraft();
        }
        DrawHome();if(saved is null&&Intent?.Data is not null)Import(Intent);
    }
    protected override void OnNewIntent(Intent? intent){base.OnNewIntent(intent);if(intent is not null){Intent=intent;Import(intent);}}
    static string[] Describe(string path)
    {
        var m=new Parser(System.IO.File.ReadAllText(path),path).ParseManifest();
        return new[]{m.Namespace,m.Entry??"",string.Join(",",m.Targets.Keys),m.Kind,m.SupportsStandalone?"true":"false"};
    }
    JsonObject Model()=>JsonNode.Parse(PackCalls.Snapshot(State.Session))!.AsObject();
    void Command(string op,JsonObject args)=>PackCalls.Command(State.Session,op,args.ToJsonString());
    void Message(string text){if(status is not null)status.Text=text;}
    void DrawHome()
    {
        var scroll=new ScrollView(this);panel=new LinearLayout(this){Orientation=Orientation.Vertical};scroll.AddView(panel);SetContentView(scroll);
        status=new TextView(this);panel.AddView(status);
        AddButton("Open .cproj / .cpack",()=>
        {
            if(State.Picker){Message("A file chooser is already pending");return;}
            State.Picker=true;var pick=new Intent(Intent.ActionOpenDocument);pick.AddCategory(Intent.CategoryOpenable);pick.SetType("*/*");pick.AddFlags(ActivityFlags.GrantReadUriPermission);
            try{StartActivityForResult(pick,ImportRequest);}catch(Exception){State.Picker=false;Message("No document picker available");}
        });
        AddButton("Leave project (retain draft)",()=>
        {
            if(State.Dirty){Message("Save the imported manifest copy or discard its changes before Leave");return;}
            if(Model()["selected"] is null){Message("No project is selected");return;}
            Command("leave",new JsonObject{["draft"]=State.Draft});State.Path="";State.Origin="";State.Source="";State.Saved="";Refresh();
        });
        AddButton("Save imported manifest copy",()=>
        {
            try{if(State.Path.Length==0)throw new InvalidOperationException("Open a pack first");new Parser(State.Source,State.Path).ParseManifest();
                if(System.IO.Path.GetExtension(State.Path)==".cproj"&&new Parser(State.Source,State.Path).ParseManifest().Kind!="project")throw new ArgumentException(".cproj must remain a ProjectPack");
                string temporary=State.Path+".draft";System.IO.File.WriteAllText(temporary,State.Source,new UTF8Encoding(false));System.IO.File.Move(temporary,State.Path,true);State.Saved=State.Source;Message("Saved application-owned copy; original document unchanged");}
            catch(Exception e){Message("Save refused: "+e.Message);}
        });
        AddButton("Discard imported manifest changes",()=>{State.Source=State.Saved;assigning=true;if(source is not null)source.Text=State.Source;assigning=false;Message("Discarded changes to application-owned copy");});
        panel.AddView(new TextView(this){Text="Local project draft (no AI connection)"});
        draft=new EditText(this){Hint="Project draft",Text=State.Draft};draft.SetMaxLines(6);draft.SetFilters(new global::Android.Text.IInputFilter[]{new global::Android.Text.InputFilterLengthFilter(4096)});draft.TextChanged+=(_,__)=>{if(!assigning){State.Draft=draft.Text??"";RetainDraft();}};panel.AddView(draft);
        panel.AddView(new TextView(this){Text="Imported manifest copy — registry siblings are not imported or executed"});
        source=new EditText(this){Text=State.Source,Gravity=GravityFlags.Top,InputType=global::Android.Text.InputTypes.ClassText|global::Android.Text.InputTypes.TextFlagMultiLine};source.SetMinLines(10);source.TextChanged+=(_,__)=>{if(!assigning)State.Source=source.Text??"";};panel.AddView(source);
        panel.AddView(new TextView(this){Text="Run, linked source authoring, native folder access and dynamic compilation are unavailable in this Android host. This app imports metadata and edits its private manifest copy. Use a packaged ProjectPack to run an app."});
        Refresh();
    }
    void AddButton(string text,Action action){var b=new Button(this){Text=text};b.Click+=(_,__)=>action();panel!.AddView(b);}
    void Refresh()
    {
        var model=Model();string name=model["selected"]?["namespace"]?.ToString()??"Home";
        Message(name+" — "+model["status"]);assigning=true;if(source is not null)source.Text=State.Source;if(draft is not null)draft.Text=State.Draft;assigning=false;
    }
    void RetainDraft(){if(Model()["selected"] is not null)Command("shell",new JsonObject{["action"]="draft",["value"]=State.Draft});}
    protected override void OnActivityResult(int request,Result result,Intent? data)
    {
        base.OnActivityResult(request,result,data);if(request!=ImportRequest)return;State.Picker=false;
        if(result!=Result.Ok||data?.Data is null){Message("Import cancelled; current project and edits retained");return;}Import(data);
    }
    void Import(Intent intent)
    {
        try
        {
            if(State.Picker){Message("Document picker is pending; current edits retained");return;}
            var uri=intent.Data??throw new ArgumentException("A document URI is required");
            if(uri.Scheme!="content")throw new ArgumentException("Only user-granted content URIs are accepted");
            string origin=uri.ToString()??throw new ArgumentException("URI identity unavailable");
            if(origin==State.Origin&&Model()["selected"] is not null){Message("Already open; edits retained");return;}
            if(Model()["selected"] is not null||State.Dirty){Message("Leave the current project before importing another; edits retained");return;}
            string name="";using(var cursor=ContentResolver!.Query(uri,new[]{IOpenableColumns.DisplayName},null,null,null))
                if(cursor?.MoveToFirst()==true)name=cursor.GetString(0)??"";
            string extension=System.IO.Path.GetExtension(name).ToLowerInvariant();
            if(extension!=".cproj"&&extension!=".cpack")throw new ArgumentException("Select a .cproj or legacy .cpack document");
            // Permission is scoped to this intent/picker result. No persistent tree grant or URI path guessing.
            using var input=ContentResolver.OpenInputStream(uri)??throw new UnauthorizedAccessException("Read permission unavailable");
            using var bytes=new System.IO.MemoryStream();var chunk=new byte[8192];int count;
            while((count=input.Read(chunk,0,chunk.Length))>0){if(bytes.Length+count>1048576)throw new ArgumentException("Manifest budget exceeded");bytes.Write(chunk,0,count);}
            string content=new UTF8Encoding(false,true).GetString(bytes.ToArray()).TrimStart('\uFEFF');var declaration=new Parser(content,name).ParseManifest();
            if(extension==".cproj"&&declaration.Kind!="project")throw new ArgumentException(".cproj must contain a ProjectPack");
            string imports=System.IO.Path.Combine(FilesDir!.AbsolutePath,"imports");System.IO.Directory.CreateDirectory(imports);
            string path=System.IO.Path.Combine(imports,Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(origin)))+extension);
            // No execution, registry traversal, source build, or original-provider write occurs on import.
            System.IO.File.WriteAllText(path,content,new UTF8Encoding(false));Command("open-request",new JsonObject{["path"]=path});
            var model=Model();if(model["selected"]?["path"]?.ToString()!=path)throw new InvalidOperationException(model["status"]?.ToString());
            State.Origin=origin;State.Path=path;State.Source=content;State.Saved=content;State.Draft=model["shell"]?["draft"]?.ToString()??"";Refresh();
        }
        catch(Exception e){Message("Import refused: "+e.Message);}
    }
    string Request(string host,string operation,string payload,long parent)
    {
        if(Looper.MyLooper()!=Looper.MainLooper)throw new InvalidOperationException("Activity UI thread required");
        if(operation=="android-home"){DrawHome();return "{}";}
        if(operation=="create"){string token=Guid.NewGuid().ToString("N");nativeHosts.Add(token,new NativeFieldHost(this));return token;}
        if(!nativeHosts.TryGetValue(host,out var native))throw new ObjectDisposedException("Android native UI host");
        var result=native.Request(operation,payload);if(operation=="close")nativeHosts.Remove(host);return result;
    }
    void SaveLocalDraft()
    {
        string directory=System.IO.Path.Combine(FilesDir!.AbsolutePath,"home");System.IO.Directory.CreateDirectory(directory);
        string path=System.IO.Path.Combine(directory,"android-ui-draft.json"),temporary=path+".pending";
        var json=new JsonObject{["source"]=State.Source,["saved"]=State.Saved,["origin"]=State.Origin,["path"]=State.Path,["draft"]=State.Draft};
        System.IO.File.WriteAllText(temporary,json.ToJsonString(),new UTF8Encoding(false));System.IO.File.Move(temporary,path,true);
    }
    void RestoreLocalDraft()
    {
        string file=System.IO.Path.Combine(FilesDir!.AbsolutePath,"home","android-ui-draft.json");if(!System.IO.File.Exists(file))return;
        try
        {
            var data=JsonNode.Parse(System.IO.File.ReadAllText(file))!.AsObject();string path=data["path"]?.ToString()??"";
            string root=System.IO.Path.GetFullPath(System.IO.Path.Combine(FilesDir.AbsolutePath,"imports"))+System.IO.Path.DirectorySeparatorChar;
            if(path.Length==0)return;
            if(!System.IO.Path.GetFullPath(path).StartsWith(root,StringComparison.Ordinal)||!System.IO.File.Exists(path))return;
            State.Path=path;State.Origin=data["origin"]?.ToString()??"";State.Source=data["source"]?.ToString()??"";State.Saved=data["saved"]?.ToString()??"";State.Draft=data["draft"]?.ToString()??"";
            Command("open-request",new JsonObject{["path"]=path});RetainDraft();
        }
        catch(Exception){State.Path="";State.Origin="";State.Source="";State.Saved="";State.Draft="";}
    }
    protected override void OnPause(){RetainDraft();SaveLocalDraft();base.OnPause();}
    protected override void OnDestroy()
    {
        foreach(var host in nativeHosts.Values)host.Dispose();nativeHosts.Clear();
        AppDomain.CurrentDomain.SetData("Confectory.Android.NativeUI",null);AppDomain.CurrentDomain.SetData("Confectory.Android.DescribeProject",null);
        if(IsFinishing&&retained is not null){PackCalls.CloseSession(retained.Session);retained=null;}
        base.OnDestroy();
    }
}
