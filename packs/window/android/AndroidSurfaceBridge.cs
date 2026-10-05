using Android.Graphics;

namespace Confectory.Android;

// Native surface resource registry, never model or View state. Activity disposes its own token.
public sealed class AndroidSurfaceBridge : IDisposable
{
    private readonly Queue<int> events=new();
    private readonly int[][] rectangles=new int[2][];
    private readonly string[][] labels=new string[2][];
    public long[] Token {get;}
    public AndroidSurfaceBridge()
    {
        long id;do{id=BitConverter.ToInt64(Guid.NewGuid().ToByteArray(),0);}while(id==0||AppDomain.CurrentDomain.GetData("Confectory.Android.Surface."+id) is not null);
        Token=new[]{id,1L,2L};AppDomain.CurrentDomain.SetData("Confectory.Android.Surface."+id,new object[]{(Action<int,int[],string[]>)Draw,(Func<int[]>)Pump});
    }
    public void Emit(int view,int type,int x=0,int y=0,int code=0,int flags=0)
    {foreach(int value in new[]{view,type,x,y,code,flags})events.Enqueue(value);}
    public int[] Pump(){var result=events.ToArray();events.Clear();return result;}
    public void Draw(int view,int[] request,string[] text)
    {
        if(view<0||view>1||request.Length%5!=0||text.Length!=request.Length/5)throw new ArgumentException("Invalid render request.");
        rectangles[view]=(int[])request.Clone();labels[view]=(string[])text.Clone();
    }
    public void Paint(Canvas canvas,int view,float density,float originY)
    {
        if(rectangles[view] is null)return;
        int save=canvas.Save();canvas.Translate(0,originY);canvas.Scale(density,density);
        using var paint=new Paint{AntiAlias=true,TextSize=14};
        try
        {
            var r=rectangles[view];var text=labels[view];
            for(int i=0;i<r.Length;i+=5)
            {
                paint.Color=new Color(unchecked((int)(0xFF000000u|(uint)r[i+4])));canvas.DrawRect(r[i],r[i+1],r[i]+r[i+2],r[i+1]+r[i+3],paint);
                paint.Color=Color.White;canvas.DrawText(text[i/5],r[i]+10,r[i+1]+24,paint);
            }
        }
        finally{canvas.RestoreToCount(save);}
    }
    public void Dispose(){AppDomain.CurrentDomain.SetData("Confectory.Android.Surface."+Token[0],null);events.Clear();Token[0]=0;Token[1]=0;Token[2]=0;}
}
