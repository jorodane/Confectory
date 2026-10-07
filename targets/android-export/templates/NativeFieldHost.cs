using Android.App;
using Android.Views;
using Android.Views.InputMethods;
using Android.Widget;
using System.Text.Json.Nodes;
namespace Confectory.Android;

// Borrow Activity lifetime; each semantic Field retains one native EditText/IME state.
internal sealed class NativeFieldHost : IDisposable
{
    readonly Activity activity;
    readonly FrameLayout overlay;
    readonly Dictionary<string,Field> fields=new();
    readonly Queue<int> events=new();
    sealed class Field
    {
        public required EditText Edit;
        public required string Binding;
        public int Id;
        public bool ReadOnly,Deferred;
        public global::Android.Text.Method.IKeyListener? KeyListener;
        public HashSet<int> Commands=new();
    }
    public NativeFieldHost(Activity activity)
    {
        this.activity=activity;overlay=new FrameLayout(activity);
        activity.AddContentView(overlay,new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MatchParent,ViewGroup.LayoutParams.MatchParent));
    }
    static bool Composing(EditText e)=>e.EditableText is not null&&BaseInputConnection.GetComposingSpanStart(e.EditableText)>=0;
    static JsonObject Snapshot(Field f)=>new()
    {
        ["id"]=f.Id,["binding"]=f.Binding,["value"]=f.Edit.Text??"",["caret"]=Math.Max(0,f.Edit.SelectionEnd),["anchor"]=Math.Max(0,f.Edit.SelectionStart),
        ["focus"]=f.Edit.HasFocus,["visible"]=f.Edit.Visibility==ViewStates.Visible,["enabled"]=f.Edit.Enabled,["readonly"]=f.ReadOnly,
        ["composing"]=Composing(f.Edit),["deferredExternal"]=f.Deferred,["native"]=true
    };
    public string Request(string operation,string payload)
    {
        var args=JsonNode.Parse(payload)!.AsObject();
        if(operation=="configure")
        {
            int id=args["id"]!.GetValue<int>();string binding=args["binding"]!.ToString(),key=id+":"+binding;
            if(!fields.TryGetValue(key,out var field))
            {
                var edit=new EditText(activity);field=new Field{Edit=edit,Binding=binding,Id=id,KeyListener=edit.KeyListener};fields.Add(key,field);overlay.AddView(edit);
                var captured=field;edit.KeyPress+=(_,e)=>
                {
                    int code=e.KeyCode switch{Keycode.Enter=>13,Keycode.Tab=>9,Keycode.Escape=>27,_=>0};
                    if(code==0||Composing(edit)||!captured.Commands.Contains(code))return;
                    foreach(int n in new[]{id,e.Event?.Action==KeyEventActions.Up?6:5,0,0,code,e.Event?.RepeatCount>0?1:0})events.Enqueue(n);e.Handled=true;
                };
            }
            string value=args["value"]!.ToString(),mode=args["mode"]!.ToString();bool changed=value!=(field.Edit.Text??"");
            field.Deferred=changed&&(field.Edit.HasFocus||Composing(field.Edit));
            if(changed&&!field.Deferred){field.Edit.Text=value;field.Edit.SetSelection(Math.Clamp(args["anchor"]!.GetValue<int>(),0,value.Length),Math.Clamp(args["caret"]!.GetValue<int>(),0,value.Length));}
            field.ReadOnly=args["readonly"]!.GetValue<bool>();field.Edit.Enabled=args["enabled"]!.GetValue<bool>();
            field.Edit.Focusable=!field.ReadOnly;field.Edit.FocusableInTouchMode=!field.ReadOnly;
            field.Edit.Hint=args["hint"]?.ToString()??"";field.Edit.SetSingleLine(mode=="singleline");field.Edit.KeyListener=field.ReadOnly?null:field.KeyListener;
            field.Edit.Visibility=args["visible"]!.GetValue<bool>()?ViewStates.Visible:ViewStates.Gone;
            var rect=args["bounds"]!.AsArray();float d=activity.Resources!.DisplayMetrics!.Density;
            field.Edit.LayoutParameters=new FrameLayout.LayoutParams((int)(rect[2]!.GetValue<int>()*d),(int)(rect[3]!.GetValue<int>()*d))
            {LeftMargin=(int)(rect[0]!.GetValue<int>()*d),TopMargin=(int)(rect[1]!.GetValue<int>()*d)};
            return Snapshot(field).ToJsonString();
        }
        if(operation=="snapshot"){var result=new JsonArray();foreach(var f in fields.Values)result.Add(Snapshot(f));return result.ToJsonString();}
        if(operation=="events"){var result=new JsonArray();while(events.Count>0)result.Add(events.Dequeue());return result.ToJsonString();}
        if(operation=="frame"){var shown=args["shown"]!.AsArray().Select(n=>n!.ToString()).ToHashSet();foreach(var item in fields)if(!shown.Contains(item.Key)){item.Value.Edit.ClearFocus();item.Value.Edit.Visibility=ViewStates.Gone;}return "{}";}
        if(operation=="focus"){int id=args["id"]!.GetValue<int>();foreach(var f in fields.Values)if(f.Id==id&&f.Edit.Enabled&&f.Edit.Visibility==ViewStates.Visible){f.Edit.RequestFocus();((InputMethodManager?)activity.GetSystemService(global::Android.Content.Context.InputMethodService))?.ShowSoftInput(f.Edit,ShowFlags.Implicit);}return "{}";}
        if(operation=="commands"){int id=args["id"]!.GetValue<int>();foreach(var f in fields.Values)if(f.Id==id)f.Commands=args["keys"]!.AsArray().Select(n=>n!.GetValue<int>()).ToHashSet();return "{}";}
        if(operation=="forget"){string binding=args["binding"]!.ToString();foreach(string key in fields.Keys.Where(k=>fields[k].Binding==binding).ToArray()){overlay.RemoveView(fields[key].Edit);fields[key].Edit.Dispose();fields.Remove(key);}return "{}";}
        if(operation=="close"){Dispose();return "{}";}
        throw new PlatformNotSupportedException("Android native field operation unavailable: "+operation+"; folder paths and arbitrary native clip regions are not desktop-equivalent");
    }
    public void Dispose(){foreach(var f in fields.Values){overlay.RemoveView(f.Edit);f.Edit.Dispose();}fields.Clear();if(overlay.Parent is ViewGroup parent)parent.RemoveView(overlay);overlay.Dispose();}
}
