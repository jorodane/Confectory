using Confectory.Core;
namespace Confectory.Tests;
public sealed class RunSurfaceTests : TestCase
{
 public void test_explicit_software_surface_owner_budget_copy_and_close()
 {
  f.ExtraRegistry["Confectory.RunSurface"]=Path.Combine(Fixture.Repo,"packs/run-surface/pack.cpack");f.Packs["App"].Dependencies["Confectory.RunSurface"]="0.1.0";
  f.ExtraRegistry["Confectory.FrameControl"]=Path.Combine(Fixture.Repo,"packs/frame-control/pack.cpack");f.Packs["App"].Dependencies["Confectory.FrameControl"]="0.1.0";f.Main("");f.Add("App","implementation","MainBody","""
  implementation App::MainBody for App::Main () -> int {
  import Confectory.RunSurface::Open as Open (string) -> string;import Confectory.RunSurface::Present as Present (string,int,int,string) -> long;import Confectory.RunSurface::Close as Close (string) -> void;import Confectory.FrameControl::Open as OpenFrame () -> string;import Confectory.FrameControl::Close as CloseFrame (string) -> void;body common "main.csbody";}
  """);f.Body("App","main.csbody","""
  foreach(string n in new[]{"PIPE","SECRET","HANDLE"})Environment.SetEnvironmentVariable("CONFECTORY_FRAME_"+n,null);
  void Check(bool b,string m){if(!b)throw new Exception(m);}bool Denied(Action op){try{op();return false;}catch(ArgumentException){return true;}catch(InvalidOperationException){return true;}catch(FormatException){return true;}}
  string loop=calls.OpenFrame.Invoke(),owner=calls.Open.Invoke(loop);try{
   Check(Denied(()=>calls.Open.Invoke(loop)),"second implicit output rejected");var bytes=new byte[512*512*4];Array.Fill(bytes,(byte)251);string image=Convert.ToBase64String(bytes);Check(calls.Present.Invoke(owner,512,512,image)==1,"maximum explicit frame");Array.Fill(bytes,(byte)0);Check(Denied(()=>calls.Present.Invoke(owner,513,512,image))&&Denied(()=>calls.Present.Invoke(owner,512,0,image)),"dimension budget");Check(Denied(()=>calls.Present.Invoke(owner,1,1,image))&&Denied(()=>calls.Present.Invoke(owner,1,1,"AAAA"))&&Denied(()=>calls.Present.Invoke(owner,1,1,"AAAAAA==\n")),"exact canonical pixel length");Check(calls.Present.Invoke(owner,1,1,"AAAAAA==")==2,"failed presents do not advance published revision");
  }finally{calls.Close.Invoke(owner);}calls.Close.Invoke(owner);bool closed=false;try{calls.Present.Invoke(owner,1,1,"AAAAAA==");}catch(ObjectDisposedException){closed=true;}Check(closed,"closed owner fenced");string next=calls.Open.Invoke(loop);Check(next!=owner,"explicit new owner after close");calls.Close.Invoke(next);calls.CloseFrame.Invoke(loop);Console.WriteLine("Software surface single owner/budgets/revision/close PASS");return 0;
  """);f.Sync();var report=Build();Output(report,"Software surface single owner/budgets/revision/close PASS");
 }
}
