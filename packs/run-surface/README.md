# RunSurface software output 0.1

Optional producer pack. Open(frameOwner) explicitly attaches the primary software output to the
caller's existing cooperative frame owner; another active attachment is rejected. Present accepts
1..640 per axis, at most 262144 pixels, at most 1 MiB, canonical base64 of top-down straight-alpha sRGB RGBA8 pixels and
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

Explicit size control is optional: ConfigureSize(owner, initialWidth, initialHeight) once before
first pixels; consume RequestedSize(owner) on the frame owner thread at a permitted frame. The
existing readonly output is unchanged unless the project opts in. Custom requests are 240..640 per axis within 262144 pixels,
initial sizes 1..640 with the same pixel budget. A distinct publisher/size sequence/command CAS permits one pending request,
up to 64 per runtime. Only matching actual Present pixels acknowledge the request. This never
resumes/steps a loop, acknowledges FrameControl commands or renews its heartbeat. Input/receipt
failure is reconciled by observation, not automatic replay; Stop/new owner clears runtime requests.
UI auto/presets use separate adapters to this size API. Larger pixel budgets, GPU capture and audio remain outside this bounded size API.

The authored 640x360 option, immutable max/maxPixels capability, legacy512 compatibility and paired-version limits are documented in [the bounded output flow](../../docs/V8_RUN_WIDE.md). Full RGBA bytes and pipe packet ceilings are unchanged.
