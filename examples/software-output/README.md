# Explicit software output example

An ordinary runnable ProjectPack, not an editor mock scene. The model advances only on an actual
FrameControl permit; it renders 64x36 RGBA pixels in its own code, explicitly submits that image,
then acknowledges the completed simulation frame. Pause/Step use the existing loop contract.
Run through an owned EditorHome Run view to display the authenticated pixels. No existing project
is rewritten or selected automatically. This example is not native Window capture, GPU rendering,
audio, render FPS measurement, resizing, or Android/browser runtime support.
