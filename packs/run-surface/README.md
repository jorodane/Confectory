# RunSurface software output 0.1

Optional producer pack. Open(frameOwner) explicitly attaches the primary software output to the
caller's existing cooperative frame owner; another active attachment is rejected. Present accepts
1..512 x 1..512, at most 1 MiB, canonical base64 of top-down straight-alpha sRGB RGBA8 pixels and
returns its monotonic submitted revision. Publication copies bytes and atomically replaces the
latest complete image. Wire encoding is unpadded base64url to avoid JSON escaping amplification.

The project explicitly imports this pack and calls Present at its rendering boundary. It does not
run a renderer, discover/capture Window, infer pixels from stdout, emit audio or alter existing C#.
The existing authenticated CurrentUserOnly FrameControl channel serves latest image reads, tied to
its actual runtime epoch. Image reads do not ACK/advance a frame or renew its execution heartbeat.
No extra socket/environment capability/cleanup class is introduced. Without an owned launch the
frame loop remains local, with no IPC. Close must run on the owning loop thread and detaches only
its own reader. Frame ownership may close first; the output can then retire safely. Pixels/owners
are volatile, never files or layout data. GPU, native Window capture, render FPS, resizing and
Android/browser execution are outside this software-output slice.
