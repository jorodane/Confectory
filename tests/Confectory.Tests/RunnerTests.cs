using System.Diagnostics;
using Confectory.Core;
namespace Confectory.Tests;
public sealed class RunnerTests : TestCase
{
    public void test_skip_counts_and_required_runtime_exit_semantics()
    {
        (int Code,string Text) Run(params string[] arguments)
        {
            var info=new ProcessStartInfo(Processes.DotNet()){UseShellExecute=false,RedirectStandardOutput=true,RedirectStandardError=true};
            info.ArgumentList.Add(typeof(RunnerTests).Assembly.Location);
            foreach(string arg in arguments)info.ArgumentList.Add(arg);
            info.Environment.Remove("DISPLAY");
            using var child=Process.Start(info)!;
            string text=child.StandardOutput.ReadToEnd()+child.StandardError.ReadToEnd();
            True(child.WaitForExit(30000),"Runner subprocess timed out");return(child.ExitCode,text);
        }
        string[] names={"EntryHomeTests.test_entry_home_actual_linux_startup_navigation_create_folder_cards_resize_and_lifetime","ProjectShellTests.test_project_shell_actual_linux_menu_tabs_run_logs_resize_context_and_lifetime","EditorTests.test_editor_native_designed_create_open_edit_save_review_confirm_run_stop_and_lifetime"};
        var skipped=Run(names);True(skipped.Code!=0,skipped.Text);True(skipped.Text.Contains("0 passed, 0 failed, 3 skipped"),skipped.Text);True(!skipped.Text.Contains("PASS "),skipped.Text);
        string core=typeof(CoreTests).Name+"."+typeof(CoreTests).GetMethods().First(m=>m.Name.StartsWith("test_")).Name;
        var mixed=Run(names.Append(core).ToArray());Equal(0,mixed.Code);True(mixed.Text.Contains("1 passed, 0 failed, 3 skipped"),mixed.Text);
        var strict=Run(names.Append(core).Append("--require-runtime").ToArray());True(strict.Code!=0,strict.Text);True(strict.Text.Contains("1 passed, 0 failed, 3 skipped"),strict.Text);
        True(Run("no_such_test").Code!=0);True(Run("--bad-option").Code!=0);
    }
}
