using Android.App;
using Android.OS;
using Android.Views;
using Android.Graphics;

namespace Confectory.Android;

[Activity(MainLauncher=true,Exported=true)]
public sealed class MainActivity : Activity
{
    private PackSurface? surface;
    protected override void OnCreate(Bundle? state)
    {
        base.OnCreate(state);surface=new PackSurface(this,state?.GetLongArray("models"));SetContentView(surface);
    }
    protected override void OnResume(){base.OnResume();surface?.Resume();}
    protected override void OnPause(){surface?.Pause();base.OnPause();}
    protected override void OnSaveInstanceState(Bundle state)
    {if(surface is not null)state.PutLongArray("models",surface.SaveModels());base.OnSaveInstanceState(state);}
    protected override void OnDestroy(){surface?.Release();surface=null;base.OnDestroy();}
}

// One OS-owned Android surface presents two independent logical Views.
// Shared control/model/camera algorithms remain ID-bound pack calls.
public sealed class PackSurface : SurfaceView,ISurfaceHolderCallback,Choreographer.IFrameCallback
{
    private readonly AndroidSurfaceBridge bridge=new();
    private readonly string[][] owners=new string[2][];
    private readonly int[][] models=new int[2][];
    private readonly long[][] views=new long[2][];
    private readonly string[][][] subscriptions=new string[2][][];
    private readonly double[][] cameras=new double[2][];
    private readonly double[][] queues=new double[2][];
    private readonly double[][] snapshots=new double[2][];
    private readonly long[] lifecycle=new long[5];
    private readonly double[] clock=new double[3];
    private readonly bool[,] keys=new bool[2,4];
    private readonly bool[] dragging=new bool[2];
    private readonly int[] lastX=new int[2],lastY=new int[2];
    private long previousFrame;
    private int primaryPointer=-1,primaryView,activeView;
    private float pinchDistance;
    private bool released,scheduled,canPresent;
    private float Density=>Resources?.DisplayMetrics?.Density??1;
    public PackSurface(global::Android.Content.Context context,long[]? restored):base(context)
    {
        Focusable=true;FocusableInTouchMode=true;Holder!.AddCallback(this);
        for(int v=0;v<2;v++)
        {
            owners[v]=PackCalls.CreateOwner(8);
            models[v]=new[]{PackCalls.CreateInstance(owners[v],"Confectory.BaseUI::Count"),PackCalls.CreateInstance(owners[v],"Confectory.BaseUI::Toggle")};
            if(restored?.Length==4){PackCalls.Write(owners[v],models[v][0],restored[v*2]);PackCalls.Write(owners[v],models[v][1],restored[v*2+1]);}
            views[v]=PackCalls.CreateView(320,280);cameras[v]=new double[]{0,0,1};queues[v]=new double[]{0,0,1};snapshots[v]=(double[])cameras[v].Clone();
        }
    }
    public long[] SaveModels()=>new[]{PackCalls.Read(owners[0],models[0][0])[0],PackCalls.Read(owners[0],models[0][1])[0],PackCalls.Read(owners[1],models[1][0])[0],PackCalls.Read(owners[1],models[1][1])[0]};
    private void Connect(int v)
    {
        if(subscriptions[v] is not null)return;
        subscriptions[v]=new[]{PackCalls.Subscribe(owners[v],models[v][0],"Confectory.BaseUI::Count"),PackCalls.Subscribe(owners[v],models[v][1],"Confectory.BaseUI::Toggle")};
        Supply(v);PackCalls.Invalidate(views[v]);
    }
    private void Supply(int v)
    {
        var count=PackCalls.Read(owners[v],models[v][0]);var toggle=PackCalls.Read(owners[v],models[v][1]);PackCalls.UpdateView(views[v],count[0],count[1],toggle[0],toggle[1]);
    }
    private void Disconnect(int v)
    {
        if(subscriptions[v] is not null)foreach(var subscription in subscriptions[v])PackCalls.Unsubscribe(subscription);
        subscriptions[v]=null!;PackCalls.Input(owners[v],models[v],views[v],9,0,0,0,0);dragging[v]=false;for(int k=0;k<4;k++)keys[v,k]=false;
    }
    public void Resume(){if(released)return;canPresent=PackCalls.SurfaceLifecycle(lifecycle,"resume",0,0);previousFrame=0;Schedule();}
    public void Pause()
    {
        if(released)return;canPresent=PackCalls.SurfaceLifecycle(lifecycle,"pause",0,0);Choreographer.Instance!.RemoveFrameCallback(this);scheduled=false;previousFrame=0;
        primaryPointer=-1;pinchDistance=0;for(int v=0;v<2;v++){PackCalls.Input(owners[v],models[v],views[v],9,0,0,0,0);dragging[v]=false;for(int k=0;k<4;k++)keys[v,k]=false;}
    }
    private void Schedule(){if(!released&&!scheduled&&canPresent){scheduled=true;Choreographer.Instance!.PostFrameCallback(this);}}
    public void SurfaceCreated(ISurfaceHolder holder)
    {
        if(released)return;canPresent=PackCalls.SurfaceLifecycle(lifecycle,"created",Math.Max(1,Width),Math.Max(1,Height));for(int v=0;v<2;v++)Connect(v);Schedule();
    }
    public void SurfaceChanged(ISurfaceHolder holder,Format format,int width,int height)
    {
        if(released)return;canPresent=PackCalls.SurfaceLifecycle(lifecycle,"changed",width,height);
        for(int v=0;v<2;v++)PackCalls.Input(owners[v],models[v],views[v],7,Math.Max(1,(int)(width/Density)),Math.Max(1,(int)(height/(2*Density))),0,0);
    }
    public void SurfaceDestroyed(ISurfaceHolder holder)
    {
        if(released)return;canPresent=PackCalls.SurfaceLifecycle(lifecycle,"surfaceDestroyed",0,0);bridge.Pump();Choreographer.Instance!.RemoveFrameCallback(this);scheduled=false;previousFrame=0;
        primaryPointer=-1;pinchDistance=0;for(int v=0;v<2;v++)Disconnect(v);
    }
    public void DoFrame(long frameTimeNanos)
    {
        scheduled=false;if(released||!canPresent)return;
        double elapsed=previousFrame==0?0:(frameTimeNanos-previousFrame)/1e9;previousFrame=frameTimeNanos;
        var cadence=PackCalls.Advance(clock,elapsed,1.0/120,1.0/60,1.0/50,4);
        var input=PackCalls.Pump(bridge.Token);
        for(int i=0;i<input.Length;i+=6)
        {
            int v=input[i],type=input[i+1],x=input[i+2],y=input[i+3],code=input[i+4],flags=input[i+5];
            PackCalls.Input(owners[v],models[v],views[v],type,x,y,code,flags);
            if(type==1&&y>PackCalls.ViewStatus(views[v])[1]*0.6){dragging[v]=true;lastX[v]=x;lastY[v]=y;}
            if(type==3&&dragging[v]){PackCalls.QueueCameraIntent(queues[v],x-lastX[v],y-lastY[v],1);lastX[v]=x;lastY[v]=y;}
            if(type==2||type==9||type==11)dragging[v]=false;
            int key=code switch{37=>0,39=>1,38=>2,40=>3,_=>-1};if(key>=0&&(type==5||type==6))keys[v,key]=type==5;
        }
        if(cadence[0]!=0)for(int v=0;v<2;v++)
        {
            if(subscriptions[v] is null)continue;
            if(PackCalls.RuntimePoll(owners[v],subscriptions[v][0]).Length!=0||PackCalls.RuntimePoll(owners[v],subscriptions[v][1]).Length!=0)Supply(v);
            PackCalls.QueueCameraIntent(queues[v],((keys[v,1]?1:0)-(keys[v,0]?1:0))*100*cadence[5],((keys[v,3]?1:0)-(keys[v,2]?1:0))*100*cadence[5],1);
        }
        for(int v=0;v<2;v++)snapshots[v]=PackCalls.PresentCamera(cameras[v],queues[v]);
        if(cadence[1]!=0)
        {
            for(int v=0;v<2;v++)PackCalls.Draw(bridge.Token,v,PackCalls.Layout(views[v]),PackCalls.Labels(views[v],snapshots[v]));
            var canvas=Holder!.LockCanvas();
            if(canvas is not null)try{canvas.DrawColor(Color.Black);bridge.Paint(canvas,0,Density,0);bridge.Paint(canvas,1,Density,Height/2f);}finally{Holder.UnlockCanvasAndPost(canvas);}
        }
        Schedule();
    }
    public override bool OnTouchEvent(MotionEvent? e)
    {
        if(e is null||released||!canPresent)return false;
        int actionIndex=e.ActionIndex;
        if(e.ActionMasked==MotionEventActions.Down)
        {
            RequestFocus();primaryPointer=e.GetPointerId(actionIndex);primaryView=e.GetY(actionIndex)<Height/2f?0:1;activeView=primaryView;
            EmitTouch(e,actionIndex,1);
        }
        if(e.ActionMasked==MotionEventActions.PointerDown&&e.PointerCount==2)
        {bridge.Emit(primaryView,11);pinchDistance=Distance(e);}
        if(e.ActionMasked==MotionEventActions.Move)
        {
            if(e.PointerCount>=2){float distance=Distance(e);if(pinchDistance>0&&distance>0)PackCalls.QueueCameraIntent(queues[primaryView],0,0,distance/pinchDistance);pinchDistance=distance;}
            else{int index=e.FindPointerIndex(primaryPointer);if(index>=0)EmitTouch(e,index,3);}
        }
        if(e.ActionMasked==MotionEventActions.Up||e.ActionMasked==MotionEventActions.PointerUp)
        {
            if(e.GetPointerId(actionIndex)==primaryPointer){EmitTouch(e,actionIndex,pinchDistance>0?11:2);primaryPointer=-1;}
            pinchDistance=0;
        }
        if(e.ActionMasked==MotionEventActions.Cancel){if(primaryPointer>=0)bridge.Emit(primaryView,11);primaryPointer=-1;pinchDistance=0;}
        return true;
    }
    private float Distance(MotionEvent e){float x=e.GetX(0)-e.GetX(1),y=e.GetY(0)-e.GetY(1);return MathF.Sqrt(x*x+y*y);}
    private void EmitTouch(MotionEvent e,int index,int type)
    {bridge.Emit(primaryView,type,(int)(e.GetX(index)/Density),(int)((e.GetY(index)-primaryView*Height/2f)/Density),0,e.GetPointerId(index));}
    private static int Key(Keycode code)=>code switch{Keycode.Enter=>13,Keycode.Space=>32,Keycode.Tab=>9,Keycode.DpadLeft=>37,Keycode.DpadRight=>39,Keycode.DpadUp=>38,Keycode.DpadDown=>40,_=>0};
    public override bool OnKeyDown(Keycode code,KeyEvent? e){int key=Key(code);if(key==0)return base.OnKeyDown(code,e);bridge.Emit(activeView,5,0,0,key,e?.RepeatCount>0?1:0);return true;}
    public override bool OnKeyUp(Keycode code,KeyEvent? e){int key=Key(code);if(key==0)return base.OnKeyUp(code,e);bridge.Emit(activeView,6,0,0,key);return true;}
    public void Release()
    {
        if(released)return;Pause();released=true;Holder!.RemoveCallback(this);
        for(int v=0;v<2;v++){Disconnect(v);PackCalls.DisposeOwner(owners[v]);}
        canPresent=PackCalls.SurfaceLifecycle(lifecycle,"destroy",0,0);bridge.Dispose();
    }
}
