// Adapter protocol doubles only: not an Android runtime or IME implementation.
namespace Android.Content { public class Context { public const string InputMethodService="ime"; } }
namespace Android.App { public class Activity:Content.Context { public Resources Resources=new();public object? GetSystemService(string s)=>null;public void AddContentView(Views.View v,Views.ViewGroup.LayoutParams p){} }public class Resources { public DisplayMetrics DisplayMetrics=new(); }public class DisplayMetrics {public float Density=1;} }
namespace Android.Graphics {public struct Color {public int R,G,B;public static Color Rgb(int r,int g,int b)=>new(){R=r,G=g,B=b};} public class Canvas {public int Save()=>0;public void ClipPath(Path p){}public void RestoreToCount(int n){} } public class Path:IDisposable {public enum Direction {Cw}public void AddRect(int x,int y,int w,int h,Direction d){}public void Dispose(){} } }
namespace Android.Text.Method { public interface IKeyListener {}public class Listener:IKeyListener{} }
namespace Android.Text {public class Editable {public int Composition=-1;} }
namespace Android.Views.InputMethods {public static class BaseInputConnection {public static int GetComposingSpanStart(Text.Editable e)=>e.Composition;}public enum ShowFlags{Implicit}public class InputMethodManager{public void ShowSoftInput(Widget.EditText e,ShowFlags f){} } }
namespace Android.Views {
 public enum ViewStates {Visible,Gone}public enum MotionEventActions{Down}public enum Keycode{Enter,Tab,Escape}public enum KeyEventActions{Up,Down}
 public class MotionEvent {public MotionEventActions ActionMasked;public float GetX()=>0;public float GetY()=>0;}
 public class KeyEvent{public KeyEventActions Action;public int RepeatCount;}public class KeyArgs:EventArgs{public Keycode KeyCode;public KeyEvent? Event;public bool Handled;}
 public class ContextThemeWrapper:Content.Context{public int Style;public ContextThemeWrapper(Content.Context c,int s){Style=s;}}
 public class View:IDisposable {public object? Parent;public ViewGroup.LayoutParams LayoutParameters=null!;public ViewStates Visibility;public bool Enabled=true,Focusable=true,FocusableInTouchMode=true,HasFocus;public virtual bool OnTouchEvent(MotionEvent? e)=>true;public virtual void Draw(Graphics.Canvas? c){}public void Invalidate(){}public void ClearFocus(){HasFocus=false;}public void RequestFocus(){HasFocus=true;}protected virtual void Dispose(bool b){}public void Dispose(){Dispose(true);} }
 public class ViewGroup:View{public virtual void RemoveView(View v){v.Parent=null;}public class LayoutParams{public const int MatchParent=-1;public int Width,Height;public LayoutParams(int w,int h){Width=w;Height=h;} } }
}
namespace Android.Widget {
 public class FrameLayout:Views.ViewGroup{public static FrameLayout? Last;public List<Views.View> Children=new();public FrameLayout(Content.Context c){Last=this;}public void AddView(Views.View v){Children.Add(v);v.Parent=this;}public override void RemoveView(Views.View v){Children.Remove(v);v.Parent=null;}public new class LayoutParams:Views.ViewGroup.LayoutParams {public int LeftMargin,TopMargin;public LayoutParams(int w,int h):base(w,h){} } }
 public class EditText:Views.View{
  public Content.Context Context;public Text.Editable EditableText=new();public int TextWrites,ModeWrites,ListenerWrites,SelectionWrites;public string Hint="";public int SelectionStart,SelectionEnd;public Graphics.Color TextColor,HintColor,Highlight;
  string text="";Text.Method.IKeyListener? listener=new Text.Method.Listener();
  public EditText(Content.Context c){Context=c;}
  public string Text{get=>text;set{text=value;TextWrites++;EditableText.Composition=-1;}}
  public Text.Method.IKeyListener? KeyListener{get=>listener;set{listener=value;ListenerWrites++;EditableText.Composition=-1;}}
  public event EventHandler<Views.KeyArgs>? KeyPress;public void Key(Views.KeyArgs e)=>KeyPress?.Invoke(this,e);
  public void SetSingleLine(bool b){ModeWrites++;EditableText.Composition=-1;}
  public void SetSelection(int a,int c){SelectionStart=a;SelectionEnd=c;SelectionWrites++;}
  public void SetTextColor(Graphics.Color c){TextColor=c;}public void SetHintTextColor(Graphics.Color c){HintColor=c;}public void SetHighlightColor(Graphics.Color c){Highlight=c;}
 }
}
namespace Confectory.Android {public static class Resource{public static class Style{public const int ConfectoryNativeField=1;}}}
