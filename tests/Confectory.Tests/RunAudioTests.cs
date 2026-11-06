using Confectory.Core;
namespace Confectory.Tests;
public sealed class RunAudioTests : TestCase
{
 public void test_explicit_pcm_owner_chunk_budget_atomic_revision_thread_and_close()
 {
  foreach(var (ns,path)in new[]{("Confectory.RunAudio","run-audio"),("Confectory.FrameControl","frame-control")}){f.ExtraRegistry[ns]=Path.Combine(Fixture.Repo,"packs",path,"pack.cpack");f.Packs["App"].Dependencies[ns]="0.1.0";}
  f.Main("");f.Add("App","implementation","MainBody","""
  implementation App::MainBody for App::Main () -> int {import Confectory.FrameControl::Open as OpenFrame () -> string;import Confectory.FrameControl::Close as CloseFrame (string) -> void;import Confectory.RunAudio::Open as Open (string) -> string;import Confectory.RunAudio::Append as Append (string,string) -> long;import Confectory.RunAudio::Close as Close (string) -> void;body common "main.csbody";}
  """);f.Body("App","main.csbody","""
  foreach(string n in new[]{"PIPE","SECRET","HANDLE"})Environment.SetEnvironmentVariable("CONFECTORY_FRAME_"+n,null);
  void Check(bool b,string m){if(!b)throw new Exception(m);}bool Denied(Action a){try{a();return false;}catch(InvalidOperationException){return true;}catch(ArgumentException){return true;}catch(FormatException){return true;}}
  string frame=calls.OpenFrame.Invoke(),owner=calls.Open.Invoke(frame);try{Check(Denied(()=>calls.Open.Invoke(frame)),"one explicitly attached audio owner");Check(calls.Append.Invoke(owner,Convert.ToBase64String(new byte[3200]))==1,"maximum complete PCM chunk");Check(Denied(()=>calls.Append.Invoke(owner,""))&&Denied(()=>calls.Append.Invoke(owner,"AA=="))&&Denied(()=>calls.Append.Invoke(owner,Convert.ToBase64String(new byte[3202])))&&Denied(()=>calls.Append.Invoke(owner,"AAA=\n")),"exact canonical mono sample bounds");Check(calls.Append.Invoke(owner,"AAA=")==2,"failed chunk does not advance sequence");for(int i=0;i<80;i++)calls.Append.Invoke(owner,"AAA=");bool refused=false;System.Threading.Tasks.Task.Run(()=>{try{calls.Close.Invoke(owner);}catch(InvalidOperationException){refused=true;}}).GetAwaiter().GetResult();Check(refused,"retirement stays on creator thread");}finally{calls.Close.Invoke(owner);}calls.Close.Invoke(owner);Check(Denied(()=>calls.Append.Invoke(owner,"AAA=")),"closed stream fenced");string next=calls.Open.Invoke(frame);Check(next!=owner&&calls.Append.Invoke(next,"AAA=")==1,"new explicit publisher begins fresh");calls.Close.Invoke(next);calls.CloseFrame.Invoke(frame);Console.WriteLine("PCM owner/budget/atomic sequence/thread/close PASS");return 0;
  """);f.Sync();var report=Build();Output(report,"PCM owner/budget/atomic sequence/thread/close PASS");
 }
}
