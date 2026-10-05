using System.Diagnostics;
using System.Runtime.InteropServices;
using Confectory.Core;

namespace Confectory.Tests;

public sealed class WindowTests : TestCase
{
    [DllImport("libX11.so.6")] private static extern IntPtr XOpenDisplay(IntPtr name);
    [DllImport("libX11.so.6")] private static extern nuint XDefaultRootWindow(IntPtr display);
    [DllImport("libX11.so.6")] private static extern int XQueryTree(IntPtr display, nuint window, out nuint root, out nuint parent, out IntPtr children, out uint count);
    [DllImport("libX11.so.6")] private static extern int XFetchName(IntPtr display, nuint window, out IntPtr name);
    [DllImport("libX11.so.6")] private static extern int XFree(IntPtr data);
    [DllImport("libX11.so.6", CharSet = CharSet.Ansi)] private static extern nuint XInternAtom(IntPtr display, string name, bool onlyIfExists);
    [DllImport("libX11.so.6")] private static extern int XSendEvent(IntPtr display, nuint window, bool propagate, nint mask, IntPtr data);
    [DllImport("libX11.so.6")] private static extern int XFlush(IntPtr display);
    [DllImport("libX11.so.6")] private static extern int XCloseDisplay(IntPtr display);
    public void test_window_pack_build_cache_and_runtime_boundary()
    {
        string sample = Path.Combine(f.Root, "window-sample"), packs = Path.Combine(f.Root, "packs", "window");
        Fixture.CopyTree(Path.Combine(Fixture.Repo, "examples", "window"), sample);
        Fixture.CopyTree(Path.Combine(Fixture.Repo, "packs", "window"), packs);
        string project = Path.Combine(sample, "project.cpack");
        File.WriteAllText(project, File.ReadAllText(project)
            .Replace("../../packs/window/pack.cpack", "../packs/window/pack.cpack", StringComparison.Ordinal)
            .Replace("../../targets/dotnet/pack.cpack", "../target/pack.cpack", StringComparison.Ordinal));
        var first = new Builder(project, "portable").Build();
        Sequence(["Confectory.Window", "Example.Window"], Strings(first, "includedPacks"));
        var next = new Builder(project, "portable").Build();
        Equal(0, Strings(next, "statistics", "compiledImplementations").Length);
        var command = Strings(next, "run");
        ProcessStartInfo Start(string timeout, bool noDisplay)
        {
            var start = new ProcessStartInfo(command[0]) { RedirectStandardError = true, RedirectStandardOutput = true, UseShellExecute = false };
            foreach (string arg in command.Skip(1)) start.ArgumentList.Add(arg);
            start.Environment["CONFECTORY_WINDOW_CLOSE_AFTER_MS"] = timeout;
            if (noDisplay) start.Environment["DISPLAY"] = ":65432";
            return start;
        }
        using (var invalid = Process.Start(Start("invalid", false))!)
        {
            True(invalid.WaitForExit(10000)); Equal(2, invalid.ExitCode);
            True(invalid.StandardError.ReadToEnd().Contains("nonnegative integer", StringComparison.Ordinal));
        }
        if (OperatingSystem.IsLinux())
        {
            using var missing = Process.Start(Start("100", true))!;
            True(missing.WaitForExit(10000)); Equal(1, missing.ExitCode);
            True(missing.StandardError.ReadToEnd().Contains("Cannot open X11 display", StringComparison.Ordinal));
        }
        // A GUI session enables real creation/event-loop/cleanup verification.
        // The no-display branch above is tested on headless Linux instead.
        if (OperatingSystem.IsWindows() || (OperatingSystem.IsLinux() && !string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY"))))
        {
            using var window = Process.Start(Start("250", false))!;
            if (!window.WaitForExit(10000)) { window.Kill(true); throw new Exception("Window event loop did not close"); }
            Equal(0, window.ExitCode);
        }
        if (OperatingSystem.IsLinux() && !string.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISPLAY")))
        {
            using var window = Process.Start(Start("0", false))!;
            IntPtr display = XOpenDisplay(IntPtr.Zero), message = Marshal.AllocHGlobal(24 * IntPtr.Size);
            try
            {
                True(display != IntPtr.Zero);
                nuint found = 0; var watch = Stopwatch.StartNew();
                while (found == 0 && watch.ElapsedMilliseconds < 5000)
                {
                    XQueryTree(display, XDefaultRootWindow(display), out _, out _, out var children, out uint count);
                    try
                    {
                        for (int i = 0; i < count; i++)
                        {
                            nuint child = (nuint)Marshal.ReadIntPtr(children, i * IntPtr.Size);
                            XFetchName(display, child, out var name);
                            try { if (Marshal.PtrToStringUTF8(name) == "Confectory") found = child; }
                            finally { if (name != IntPtr.Zero) XFree(name); }
                        }
                    }
                    finally { if (children != IntPtr.Zero) XFree(children); }
                    if (found == 0) System.Threading.Thread.Sleep(10);
                }
                True(found != 0, "No actual Confectory window was mapped");
                for (int i = 0; i < 24 * IntPtr.Size; i++) Marshal.WriteByte(message, i, 0);
                Marshal.WriteInt32(message, 33); // ClientMessage
                Marshal.WriteIntPtr(message, IntPtr.Size == 8 ? 32 : 16, (nint)found);
                Marshal.WriteIntPtr(message, IntPtr.Size == 8 ? 40 : 20, (nint)XInternAtom(display, "WM_PROTOCOLS", false));
                Marshal.WriteInt32(message, IntPtr.Size == 8 ? 48 : 24, 32);
                Marshal.WriteIntPtr(message, IntPtr.Size == 8 ? 56 : 28, (nint)XInternAtom(display, "WM_DELETE_WINDOW", false));
                True(XSendEvent(display, found, false, 0, message) != 0); XFlush(display);
                True(window.WaitForExit(5000), "WM_DELETE_WINDOW did not close the event loop"); Equal(0, window.ExitCode);
            }
            finally
            {
                if (!window.HasExited) { window.Kill(true); window.WaitForExit(); }
                Marshal.FreeHGlobal(message); if (display != IntPtr.Zero) XCloseDisplay(display);
            }
        }
    }
}
