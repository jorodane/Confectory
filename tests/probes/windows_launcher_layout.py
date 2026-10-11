"""Static repository wiring checks; these do not emulate CMD or PowerShell."""
import pathlib,re,unittest
R=pathlib.Path(__file__).resolve().parents[2]
class LauncherLayout(unittest.TestCase):
 def test_single_root_and_explicit_actions(self):
  self.assertEqual([p.name for p in R.glob('*.bat')],['Confectory.bat'])
  self.assertEqual(list(R.glob('*.ps1')),[])
  root=(R/'Confectory.bat').read_text();self.assertIn('setlocal DisableDelayedExpansion',root)
  self.assertIn('"%~dp0scripts\\windows\\launcher.ps1"',root);self.assertNotIn('%*',root)
  menu=(R/'scripts/windows/launcher.ps1').read_text()
  self.assertIn("'2' {'unavailable'}",menu);self.assertIn("'6' {'diagnostics'}",menu)
  self.assertIn("if ($chosen -eq 'unavailable')",menu);self.assertIn("-File $PSCommandPath -Action $chosen",menu)
  self.assertIn("'examples\\editor-home\\project.cpack'",menu)
  self.assertNotIn('editor-home-web',menu);self.assertNotIn('project-browser',menu)
  self.assertIn("$env:CONFECTORY_UI = 'web'",menu);self.assertIn('$env:CONFECTORY_WEB_PROJECT = $project',menu)
  self.assertIn("if (!$project) { exit 2 }",menu);self.assertIn('exit $failureCode',menu)
 def test_moved_batch_references(self):
  for p in (R/'scripts/windows').rglob('*.bat'):
   source=p.read_text()
   self.assertIn('setlocal',source.lower(),p)
   for match in re.finditer(r'%~dp0([^"\r\n]*\.(?:bat|ps1))',source,re.I):
    target=(p.parent/match[1].replace('\\','/')).resolve();self.assertTrue(target.is_file(),(p,target))
   self.assertNotRegex(source.lower(),r'\bsetx\b|\breg(?:\.exe)?\s+(?:add|import)')
  text=(R/'scripts/windows/launcher.ps1').read_text()
  self.assertNotRegex(text.lower(),r'\bsetx\b|\breg(?:\.exe)?\s+(?:add|import)|winget|install-package')
  self.assertIn('-Unsigned',text)
 def test_registration_uses_menu(self):
  for p in ['targets/desktop-entry/WindowsAssociation.cs','targets/desktop-entry/Program.cs']:
   source=(R/p).read_text();self.assertIn('Confectory.bat',source);self.assertNotIn('open-project-windows.bat',source)
if __name__=='__main__':unittest.main()
