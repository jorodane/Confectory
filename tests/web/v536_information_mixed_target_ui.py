"""Original selector, explicit code and Blueprint pin mapping in the renderer."""
import sys
import v536_information_mixed_target_fixture as fixture
fixture.edited = fixture.edited.replace("\r\n", "\n")
fixture.edited_files = {path: text.replace("\r\n", "\n") for path, text in fixture.edited_files.items()}
sys.modules['v536_information_csharp_fixture'] = fixture
import v536_information_csharp_ui
