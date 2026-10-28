"""Real original picker for explicit common/Windows/caller C# source edits."""
import sys
import v536_information_csharp_context_fixture as fixture
fixture.native_context = True
fixture.edited = fixture.edited.replace("\r\n", "\n")
fixture.edited_files = {path: text.replace("\r\n", "\n") for path, text in fixture.edited_files.items()}
fixture.context_bodies = {fixture.body_id: fixture.body_path, fixture.fn + "Body/body:windows": "manual-windows.csbody", fixture.caller + "Body/body:common": "manual-caller.csbody"}
sys.modules['v536_information_csharp_fixture'] = fixture
import v536_information_csharp_ui
