using System.Runtime.InteropServices;

// Retain the normal sizeable WinForms/DWM frame and its OS resizing/maximizing
// behavior. Only the native caption is replaced when the owned HTML bar is ready.
internal sealed class AppWindowForm : Form
{
    public bool CustomCaption { get; private set; }

    public void SetCustomCaption(bool enabled)
    {
        if (CustomCaption == enabled) return;
        CustomCaption = enabled;
        if (IsHandleCreated)
            SetWindowPos(Handle, IntPtr.Zero, 0, 0, 0, 0, 0x0037); // frame changed; no move/size/activation
    }

    protected override void WndProc(ref Message message)
    {
        if (message.Msg == 0x0083 && CustomCaption && message.LParam != IntPtr.Zero && WindowState != FormWindowState.Minimized)
        {
            // RECT is also the first member of NCCALCSIZE_PARAMS (wParam != 0).
            // Ask Windows for the real per-monitor border insets first. Keep its
            // left/right/bottom sizing frame and work-area calculations intact.
            var outer = Marshal.PtrToStructure<NativeRectangle>(message.LParam);
            base.WndProc(ref message);
            var client = Marshal.PtrToStructure<NativeRectangle>(message.LParam);
            client.Top = CaptionGeometry.ClientTop(outer.Top, outer.Bottom, client.Top, client.Bottom);
            Marshal.StructureToPtr(client, message.LParam, false);
            message.Result = IntPtr.Zero;
            return;
        }
        base.WndProc(ref message);
    }

    [StructLayout(LayoutKind.Sequential)]
    struct NativeRectangle { public int Left, Top, Right, Bottom; }

    [DllImport("user32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool SetWindowPos(IntPtr window, IntPtr after, int x, int y, int width, int height, uint flags);
}

// Screen-coordinate geometry only; no cached DPI constants or invented monitor bounds.
internal static class CaptionGeometry
{
    public static int ClientTop(int outerTop, int outerBottom, int nativeTop, int nativeBottom)
    {
        int border = Math.Clamp(outerBottom - nativeBottom, 0, Math.Max(0, nativeTop - outerTop));
        return Math.Min(nativeBottom, outerTop + border);
    }
}
