using Confectory.Core;
using System.Text;

// One before/after candidate observation. The after projection may use the
// exact bytes already observed in the same authoring request. Its own Registry,
// owner/draft overlays, validation and final physical recheck remain independent.
internal sealed class ExactMetadataReadPass
{
    private readonly Dictionary<string,string> captured=new(StringComparer.Ordinal);
    private long bytes;
    internal ExactDocumentReadMemo Parsed {get;}=new();
    internal int Captured=>captured.Count;
    internal int Reused {get;private set;}
    internal string Read(string path,Func<string,string> physical,bool after)
    {
        if(after&&captured.TryGetValue(path,out var prior)){Reused++;return prior;}
        var text=physical(path);
        if(!after){
            if(captured.TryGetValue(path,out var known)){
                if(known!=text)throw new InvalidOperationException("Slot context changed during reading");
            }else{
                int size=Encoding.UTF8.GetByteCount(text);
                if(size<=1048576&&captured.Count<2048&&bytes+size<=16777216){captured.Add(path,text);bytes+=size;}
            }
        }
        return text;
    }
}
