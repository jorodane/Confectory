# Explicit software audio output

Open(frameOwner) attaches one PCM stream through the public FrameControl audio role. Append accepts
canonical base64 mono PCM16LE at 16kHz, 1..1600 sample frames per complete chunk. Input is copied,
validated and SHA256-bound before atomic publication. Sequence and sample positions are Int64
strings on the wire; the queue keeps at most64 chunks/32000 samples. Reads never block production,
ACK/advance execution frames or renew heartbeat. No new socket, device, environment grant or source
rewriting. Close retires only its own reader on its owner thread.

Empty cursors establish a live baseline with no old samples. Retention loss or a publisher change
returns an explicit reset rather than inventing missing audio. Existing programs stay silent until
they import/use this pack. The caller owns sample production and its clock; a reader does not infer
frame/task completion from samples. This is bounded software preview transport, not a real-time DSP,
GPU/speaker driver or multi-channel device backend. Actual hardware output requires host validation.
