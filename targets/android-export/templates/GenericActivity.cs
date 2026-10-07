using Android.App;
using Android.Content;
using Android.Graphics;
using Android.OS;
using Android.Views;
using System.Text.Json.Nodes;
using Confectory.Core;
namespace Confectory.Android;

// Platform host only: generated product entry owns controls, layout, commands and model.
[Activity(MainLauncher=true,Exported=true,LaunchMode=global::Android.Content.PM.LaunchMode.SingleTask)]
public sealed class MainActivity : Activity,Choreographer.IFrameCallback
{
    ProductSurface? surface;
    readonly object owner=new();
    Func<bool>? step;Action? retire,stop;
    readonly Dictionary<string,NativeFieldHost> fields=new();
    readonly Queue<string> inbox=new();readonly HashSet<string> entryOwners=new();
    string pickerHost="",pickerState="idle",pickerPath="",pickerError="";int pickerEpoch,pickerRequest;
    readonly Dictionary<string,string> imported=new();
    bool resumed,scheduled,closed;
    protected override void OnCreate(Bundle? state)
    {
        base.OnCreate(state);
        surface=new ProductSurface(this);SetContentView(surface);
        string storage=FilesDir!.AbsolutePath;System.IO.Directory.SetCurrentDirectory(storage);
        AppDomain.CurrentDomain.SetData("Confectory.Android.Host.Owner",owner);
        AppDomain.CurrentDomain.SetData("Confectory.Android.Window",(Func<string,object[],object>)surface.Request);
        AppDomain.CurrentDomain.SetData("Confectory.Android.NativeUI",(Func<string,string,string,long,string>)NativeRequest);
        AppContext.SetData("Confectory.HostLoop.Run.android",(Func<string,int>)Run);
        AppDomain.CurrentDomain.SetData("Confectory.Android.ProjectEntry",(Func<string,string,string,string>)EntryRequest);
        AppDomain.CurrentDomain.SetData("Confectory.Android.DescribeProject",(Func<string,string[]>)Describe);
        try{int result=PackEntry.Run();if(step is null)surface.Diagnostic="Project entry completed ("+result+"); no presentation loop was registered.";AcceptIntent(Intent);}
        catch{try{Retire();}finally{ClearAdapters();}throw;}
    }
    static string[] Describe(string path)
    {
        var m=new Parser(System.IO.File.ReadAllText(path),path).ParseManifest();return new[]{m.Namespace,m.Entry??"",string.Join(",",m.Targets.Keys),m.Kind,m.SupportsStandalone?"true":"false"};
    }
    int Run(string token)
    {
        if(step is not null)throw new InvalidOperationException("One product controller per Android Activity");
        var state=AppContext.GetData("Confectory.HostLoop."+token) as object[]??throw new InvalidOperationException("Missing common product loop");
        step=(Func<bool>)state[0];retire=(Action)state[1];stop=state.Length>2?state[2] as Action:null;Schedule();return 0;
    }
    string NativeRequest(string host,string operation,string payload,long parent)
    {
        if(operation=="create")
        {
            if(parent!=1)throw new ArgumentException("Android native fields need the current surface owner");
            string id=Guid.NewGuid().ToString("N");fields.Add(id,new NativeFieldHost(this));return id;
        }
        if(!fields.TryGetValue(host,out var field))throw new InvalidOperationException("Native field owner is unavailable");
        if(operation=="folder-begin")
        {
            if(pickerState=="pending")throw new InvalidOperationException("Android document picker already pending");
            pickerHost=host;pickerState="pending";pickerPath="";pickerError="";pickerEpoch++;
            pickerRequest=700+pickerEpoch%30000;var intent=new Intent(Intent.ActionOpenDocumentTree);intent.AddFlags(ActivityFlags.GrantReadUriPermission);
            try{StartActivityForResult(intent,pickerRequest);}catch{pickerState="idle";pickerHost="";throw;}return "{}";
        }
        if(operation=="folder-poll")
        {
            if(pickerHost!=host)return "{\"state\":\"idle\"}";
            string result=new JsonObject{["state"]=pickerState,["path"]=pickerPath,["error"]=pickerError}.ToJsonString();if(pickerState!="pending")pickerState="idle";return result;
        }
        if(operation=="folder-cancel"){if(pickerHost==host){pickerEpoch++;pickerState="cancelled";}return "{}";}
        if(operation=="open-folder")throw new PlatformNotSupportedException("Android app-private folders are owned by the app; external desktop file managers are unavailable");
        if(operation=="close"){if(pickerHost==host){pickerEpoch++;pickerState="cancelled";}try{field.Dispose();}finally{fields.Remove(host);}return "{}";}
        return field.Request(operation,payload);
    }
    string EntryRequest(string handle,string operation,string payload)
    {
        if(operation=="listen"){string id=Guid.NewGuid().ToString("N");entryOwners.Add(id);return id;}
        if(!entryOwners.Contains(handle))throw new InvalidOperationException("Entry owner closed");
        if(operation=="poll")return inbox.Count==0?"{}":inbox.Dequeue();
        if(operation=="reply")return "{}"; // Android ACTION_VIEW has no synchronous caller reply channel.
        if(operation=="close"){entryOwners.Remove(handle);if(entryOwners.Count==0)inbox.Clear();return "{}";}
        throw new PlatformNotSupportedException("Android entry operation unavailable: "+operation);
    }
    protected override void OnNewIntent(Intent? intent){base.OnNewIntent(intent);if(intent is not null&&pickerState!="pending")AcceptIntent(intent);}
    async void AcceptIntent(Intent? intent)
    {
        var uri=intent?.Data;if(uri is null||intent?.Action!=Intent.ActionView)return;
        if(uri.Scheme!="content")return; // No guessed filesystem path or broad provider permission.
        try
        {
            string path=await Import(uri,false);if(closed||inbox.Count>=16)return;
            inbox.Enqueue(new JsonObject{["id"]=Guid.NewGuid().ToString("N"),["path"]=path}.ToJsonString());
        }
        catch(Exception error){global::Android.Util.Log.Warn("Confectory",error.Message);}
    }
    protected override async void OnActivityResult(int requestCode,Result resultCode,Intent? data)
    {
        base.OnActivityResult(requestCode,resultCode,data);if(requestCode!=pickerRequest)return;int epoch=pickerEpoch;
        if(pickerState!="pending")return;if(resultCode!=Result.Ok||data?.Data is null){pickerState="cancelled";return;}
        try{string path=await Import(data.Data,true);if(!closed&&epoch==pickerEpoch){pickerPath=path;pickerState="selected";}}
        catch(Exception error){if(!closed&&epoch==pickerEpoch){pickerError=error.Message;pickerState="error";}}
    }
    async System.Threading.Tasks.Task<string> Import(global::Android.Net.Uri uri,bool tree)
    {
        string key=uri.ToString()??throw new ArgumentException("URI identity required");if(imported.TryGetValue(key,out var old))return old;
        string root=System.IO.Path.Combine(FilesDir!.AbsolutePath,"imports",Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(key))));
        string path=await System.Threading.Tasks.Task.Run(()=>AndroidDocumentImport.Copy(ContentResolver!,uri,root,tree));
        if(!closed)imported[key]=path;return path;
    }
    void Schedule(){if(resumed&&!closed&&!scheduled&&step is not null){scheduled=true;Choreographer.Instance!.PostFrameCallback(this);}}
    public void DoFrame(long frameTimeNanos)
    {
        scheduled=false;if(!resumed||closed||step is null)return;
        try{if(!step()){Finish();Retire();return;}surface?.Invalidate();Schedule();}
        catch{Retire();throw;}
    }
    protected override void OnResume(){base.OnResume();resumed=true;surface?.Emit(7,surface.LogicalWidth,surface.LogicalHeight);Schedule();}
    protected override void OnPause(){resumed=false;Choreographer.Instance!.RemoveFrameCallback(this);scheduled=false;surface?.Emit(11);base.OnPause();}
    void Retire()
    {
        if(closed)return;closed=true;Choreographer.Instance!.RemoveFrameCallback(this);scheduled=false;
        try{stop?.Invoke();}finally
        {
            try{retire?.Invoke();}finally
            {
                step=null;retire=null;stop=null;
                foreach(var f in fields.Values)try{f.Dispose();}catch(Exception error){global::Android.Util.Log.Warn("Confectory",error.Message);}
                fields.Clear();entryOwners.Clear();inbox.Clear();pickerEpoch++;surface?.Close();
                // The private HostLoop token remains provider-owned until its pending jobs/resources close.
            }
        }
    }
    void ClearAdapters()
    {
        if(!ReferenceEquals(AppDomain.CurrentDomain.GetData("Confectory.Android.Host.Owner"),owner))return;
        AppDomain.CurrentDomain.SetData("Confectory.Android.Host.Owner",null);AppDomain.CurrentDomain.SetData("Confectory.Android.Window",null);AppDomain.CurrentDomain.SetData("Confectory.Android.NativeUI",null);AppContext.SetData("Confectory.HostLoop.Run.android",null);AppDomain.CurrentDomain.SetData("Confectory.Android.ProjectEntry",null);AppDomain.CurrentDomain.SetData("Confectory.Android.DescribeProject",null);
    }
    protected override void OnDestroy()
    {
        try{Retire();}finally{ClearAdapters();surface=null;base.OnDestroy();}
    }
}

internal sealed class ProductSurface : View
{
    readonly Queue<int> events=new();
    int[] rectangles=Array.Empty<int>(),clips=Array.Empty<int>(),origins=Array.Empty<int>();
    string[] labels=Array.Empty<string>(),texts=Array.Empty<string>();
    long[]? token;bool closed;int primaryPointer=-1;bool touchCancelled;
    public string Diagnostic="";
    float Density=>Resources!.DisplayMetrics!.Density;
    public int LogicalWidth=>Math.Max(1,(int)(Width/Density));
    public int LogicalHeight=>Math.Max(1,(int)(Height/Density));
    public ProductSurface(Context context):base(context){Focusable=true;FocusableInTouchMode=true;}
    public void Emit(int type,int x=0,int y=0,int code=0,int flags=0){foreach(int n in new[]{0,type,x,y,code,flags})events.Enqueue(n);}
    void Check(object[] args){if(token is null||!ReferenceEquals(args[0],token)||closed)throw new InvalidOperationException("Surface owner closed");}
    static Paint TextPaint()
    {
        string raw=System.Environment.GetEnvironmentVariable("CONFECTORY_TEXT_SCALE")??"1";
        if(!float.TryParse(raw,System.Globalization.NumberStyles.Float,System.Globalization.CultureInfo.InvariantCulture,out float scale)||!float.IsFinite(scale)||scale<.5f||scale>3)throw new ArgumentException("Text scale must be0.5..3");
        return new Paint{AntiAlias=true,TextSize=12*scale};
    }
    public object Request(string operation,object[] args)
    {
        if(operation=="CreateSurfaces")
        {
            var titles=(string[])args[0];if((int)args[1]<1||(int)args[2]<1)throw new ArgumentException("Invalid requested surface dimensions");if(titles.Length!=1)throw new PlatformNotSupportedException("Android host has one Activity surface, not independent desktop windows");
            if(token is not null&&!closed)throw new InvalidOperationException("Surface already owned");closed=false;token=new long[]{1,1};return token;
        }
        Check(args);
        if(operation!="Pump"&&args.Length>1&&args[1] is int view&&view!=0&&!(operation=="Close"&&view==-1))throw new ArgumentOutOfRangeException("view","Android Activity owns one surface");
        switch(operation)
        {
            case "Close":Close();return new object();
            case "SurfaceDimensions":return new[]{LogicalWidth,LogicalHeight};
            case "Place":throw new PlatformNotSupportedException("Android OS owns Activity placement");
            case "Reopen":throw new PlatformNotSupportedException("Reopen is owned by Android Activity lifecycle");
            case "Pump":var e=events.ToArray();events.Clear();return e;
            case "Draw":if(((int[])args[2]).Length%5!=0||((int[])args[2]).Length/5!=((string[])args[3]).Length)throw new ArgumentException("Rectangle frame shape");rectangles=(int[])((int[])args[2]).Clone();labels=(string[])((string[])args[3]).Clone();clips=Array.Empty<int>();texts=Array.Empty<string>();Invalidate();return new object();
            case "DrawText":if(((int[])args[2]).Length%4!=0||((int[])args[2]).Length/4!=((string[])args[4]).Length||((int[])args[3]).Length!=((string[])args[4]).Length*2)throw new ArgumentException("Text frame shape");clips=(int[])((int[])args[2]).Clone();origins=(int[])((int[])args[3]).Clone();texts=(string[])((string[])args[4]).Clone();Invalidate();return new object();
            case "MeasureText":return Measure((string)args[2]);
            default:throw new PlatformNotSupportedException("Android window operation unavailable: "+operation);
        }
    }
    string Measure(string text)
    {
        if(text.Length>65536||text.Count(c=>c=='\n')>=2048)throw new ArgumentException("Native text measurement budget exceeded");
        using var p=TextPaint();var fm=p.GetFontMetrics()!;var lines=new JsonArray();int start=0;
        foreach(string line in text.Split('\n'))
        {
            var positions=new int[line.Length+1];for(int i=0;i<=line.Length;i++)positions[i]=i>0&&i<line.Length&&char.IsHighSurrogate(line[i-1])&&char.IsLowSurrogate(line[i])?-1:(int)MathF.Round(p.MeasureText(line[..i]));
            lines.Add(new JsonObject{["start"]=start,["text"]=line,["positions"]=System.Text.Json.JsonSerializer.SerializeToNode(positions)});start+=line.Length+1;
        }
        int height=(int)MathF.Ceiling(fm.Descent-fm.Ascent);
        return new JsonObject{["text"]=text,["insetX"]=10,["insetY"]=4,["ascent"]=(int)MathF.Ceiling(-fm.Ascent),["height"]=height,["lineHeight"]=height+4,["lines"]=lines}.ToJsonString();
    }
    protected override void OnDraw(Canvas canvas)
    {
        base.OnDraw(canvas);if(canvas is null||closed)return;
        int save=canvas.Save();canvas.Scale(Density,Density);canvas.DrawColor(Color.Black);
        using var p=TextPaint();
        if(token is null&&Diagnostic.Length>0){p.Color=Color.White;canvas.DrawText(Diagnostic,10,24,p);}
        try
        {
            for(int i=0;i<rectangles.Length;i+=5)
            {
                p.Color=new Color(unchecked((int)(0xff000000u|(uint)rectangles[i+4])));canvas.DrawRect(rectangles[i],rectangles[i+1],rectangles[i]+rectangles[i+2],rectangles[i+1]+rectangles[i+3],p);
                p.Color=Color.White;canvas.DrawText(labels[i/5],rectangles[i]+10,rectangles[i+1]+24,p);
            }
            var fm=p.GetFontMetrics()!;
            for(int i=0;i<texts.Length;i++)
            {
                int k=i*4,s=canvas.Save();try{canvas.ClipRect(clips[k],clips[k+1],clips[k]+clips[k+2],clips[k+1]+clips[k+3]);p.Color=Color.White;canvas.DrawText(texts[i],origins[i*2],origins[i*2+1]-fm.Ascent,p);}finally{canvas.RestoreToCount(s);}
            }
        }
        finally{canvas.RestoreToCount(save);}
    }
    protected override void OnSizeChanged(int w,int h,int oldw,int oldh){base.OnSizeChanged(w,h,oldw,oldh);Emit(7,LogicalWidth,LogicalHeight);}
    public override bool OnTouchEvent(MotionEvent? e)
    {
        if(e is null||closed)return false;
        switch(e.ActionMasked)
        {
            case MotionEventActions.Down:RequestFocus();primaryPointer=e.GetPointerId(0);touchCancelled=false;Emit(1,(int)(e.GetX()/Density),(int)(e.GetY()/Density));break;
            case MotionEventActions.PointerDown:if(!touchCancelled){Emit(11);touchCancelled=true;}break;
            case MotionEventActions.Move:if(!touchCancelled){int index=e.FindPointerIndex(primaryPointer);if(index>=0)Emit(3,(int)(e.GetX(index)/Density),(int)(e.GetY(index)/Density));}break;
            case MotionEventActions.Up:if(!touchCancelled)Emit(2,(int)(e.GetX()/Density),(int)(e.GetY()/Density));primaryPointer=-1;touchCancelled=false;break;
            case MotionEventActions.Cancel:Emit(11);primaryPointer=-1;touchCancelled=false;break;
        }
        return true;
    }
    static int Key(Keycode k)=>k switch{Keycode.Tab=>0xff09,Keycode.Enter=>0xff0d,Keycode.Escape=>0xff1b,Keycode.Space=>32,Keycode.DpadLeft=>0xff51,Keycode.DpadUp=>0xff52,Keycode.DpadRight=>0xff53,Keycode.DpadDown=>0xff54,_=>0};
    public override bool OnKeyDown(Keycode code,KeyEvent? e){int k=Key(code);if(k==0)return base.OnKeyDown(code,e);Emit(5,0,0,k,e?.RepeatCount>0?1:0);return true;}
    public override bool OnKeyUp(Keycode code,KeyEvent? e){int k=Key(code);if(k==0)return base.OnKeyUp(code,e);Emit(6,0,0,k);return true;}
    public void Close(){if(closed)return;closed=true;events.Clear();if(token is not null){token[0]=0;token[1]=0;}}
}
