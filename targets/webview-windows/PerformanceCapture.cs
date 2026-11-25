using System.Diagnostics;
using System.Globalization;
using System.Text;
using System.Text.Json;

// Optional local timing only. This process never records envelope contents,
// resource paths, URLs, exception messages, or browser identifiers.
internal sealed class PerformanceCapture : IDisposable
{
    readonly StreamWriter? writer;
    readonly long epoch;
    readonly System.Threading.Timer? flush;
    int rows;
    public bool Enabled => writer is not null;
    public PerformanceCapture()
    {
        if(Environment.GetEnvironmentVariable("CONFECTORY_PERFORMANCE")!="1")return;
        string? path=Environment.GetEnvironmentVariable("CONFECTORY_PERFORMANCE_RENDERER_FILE");
        if(path is null||!Path.IsPathFullyQualified(path)||!long.TryParse(Environment.GetEnvironmentVariable("CONFECTORY_PERFORMANCE_EPOCH"),NumberStyles.Integer,CultureInfo.InvariantCulture,out epoch))return;
        try{writer=new StreamWriter(new FileStream(path,FileMode.CreateNew,FileAccess.Write,FileShare.Read),new UTF8Encoding(false),8192);
            flush=new System.Threading.Timer(_=>{lock(writer){try{writer.Flush();}catch(Exception error) when(error is IOException or UnauthorizedAccessException or ObjectDisposedException){rows=4096;}}},null,1000,1000); }
        catch(Exception error) when(error is IOException or UnauthorizedAccessException or ArgumentException){}
    }
    public long Start()=>Enabled?Stopwatch.GetTimestamp():0;
    public void Mark(string stage,string operation,long start)
    {
        if(writer is null||rows>=4096||stage is not ("webview-init" or "webview-navigation" or "webview-message" or "webview-resource")||operation is not ("" or "request" or "native" or "resource"))return;
        double elapsed=Stopwatch.GetElapsedTime(start).TotalMilliseconds,at=Stopwatch.GetElapsedTime(epoch).TotalMilliseconds;
        if(!double.IsFinite(elapsed)||elapsed<0||elapsed>3600000||!double.IsFinite(at)||at<0)return;
        lock(writer){if(rows>=4096)return;try{if(rows==4095){stage="capture-limit";operation="";elapsed=0;}writer.WriteLine(JsonSerializer.Serialize(new{stage,operation,elapsedMs=Math.Round(elapsed,3),atMs=Math.Round(at,3)}));if(++rows%32==0)writer.Flush();}catch(Exception error) when(error is IOException or UnauthorizedAccessException or ObjectDisposedException){rows=4096;}}
    }
    public void Dispose(){flush?.Dispose();if(writer is not null)lock(writer){try{writer.Dispose();}catch(IOException){}}}
}
