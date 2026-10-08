using System.Text.Json.Nodes;
using Confectory.Android;
using Android.Widget;
void Check(bool value,string why){if(!value)throw new Exception(why);}
using var host=new NativeFieldHost(new Android.App.Activity());
JsonObject Configure(int id,string value,string mode="singleline",bool readOnly=false)=>JsonNode.Parse(host.Request("configure",new JsonObject{["id"]=id,["binding"]="buffer"+id,["value"]=value,["mode"]=mode,["readonly"]=readOnly,["enabled"]=true,["visible"]=true,["hint"]="hint",["bounds"]=new JsonArray(0,0,300,40),["anchor"]=0,["caret"]=0}.ToJsonString()))!.AsObject();
Configure(10,"");var e=(EditText)FrameLayout.Last!.Children[0];e.RequestFocus();
int modes=e.ModeWrites,listeners=e.ListenerWrites;
// Feed native composing/committed snapshots; never synthesize Hangul from jamo.
foreach(string value in new[]{"ㄱ","게","게임","게임 게임","게임 test","게임 tes","게임 test"}){
 e.Text=value;e.EditableText.Composition=0;e.SetSelection(value.Length,value.Length);int selections=e.SelectionWrites;int nativeWrites=e.TextWrites;
 for(int n=0;n<30;n++){var snapshot=Configure(10,value);Check(snapshot["composing"]!.GetValue<bool>(),"presentation destroyed composing span");Check(snapshot["value"]!.ToString()==value,"native text changed");}
 Check(e.ModeWrites==modes&&e.ListenerWrites==listeners&&e.TextWrites==nativeWrites&&e.SelectionWrites==selections,"presentation reset IME/text/selection");
 e.EditableText.Composition=-1;Check(!Configure(10,value)["composing"]!.GetValue<bool>(),"commit not reflected");
}
host.Request("commands",new JsonObject{["id"]=10,["keys"]=new JsonArray(13)}.ToJsonString());
e.EditableText.Composition=0;var composingEnter=new Android.Views.KeyArgs{KeyCode=Android.Views.Keycode.Enter,Event=new(){Action=Android.Views.KeyEventActions.Down}};e.Key(composingEnter);Check(!composingEnter.Handled&&host.Request("events","{}")=="[]","IME Enter intercepted during composition");
e.EditableText.Composition=-1;var committedEnter=new Android.Views.KeyArgs{KeyCode=Android.Views.Keycode.Enter,Event=new(){Action=Android.Views.KeyEventActions.Down}};e.Key(committedEnter);Check(committedEnter.Handled&&JsonNode.Parse(host.Request("events","{}"))!.AsArray().Count==6,"committed command delivery");
e.SetSelection(2,2);Configure(10,e.Text);Check(e.SelectionEnd==2,"cursor moved");e.SetSelection(0,2);Configure(10,e.Text);Check(e.SelectionStart==0&&e.SelectionEnd==2,"selection collapsed");
e.EditableText.Composition=0;var deferred=Configure(10,"external replacement");Check(deferred["deferredExternal"]!.GetValue<bool>()&&e.Text=="게임 test","external edit interrupted composition");
e.ClearFocus();Check(Configure(10,"external replacement")["composing"]!.GetValue<bool>(),"unfocused composition lost");
e.EditableText.Composition=-1;Configure(10,"external replacement");Check(e.Text=="external replacement","external value not applied after release");
Configure(11,"existing 영어 게임","multiline");Check(FrameLayout.Last.Children.Count==2,"focus transition recreated field");Configure(10,e.Text,readOnly:true);Check(e.KeyListener is null,"readonly transition");Configure(10,e.Text,readOnly:false);Check(e.KeyListener is not null,"editable listener not restored");
Check(e.TextColor.R==228&&e.HintColor.R==174&&e.Highlight.R==69,"contrast palette");Check(((Android.Views.ContextThemeWrapper)e.Context).Style==Resource.Style.ConfectoryNativeField,"native cursor/handle theme absent");
Console.WriteLine("PASS actual exported NativeFieldHost presentation/composition/commit/native text/selection/cursor/external edit/focus/readonly/contrast protocol; Android IME/device unrun");
