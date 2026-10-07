namespace Confectory.DesktopEntry;
// Format only. The Windows entry tool writes an opt-in file, never modifies registry settings.
public static class WindowsAssociation
{
 public static string Format(string dotnet,string dll,string repository)
 {
  CheckPaths(dotnet,dll,repository);
  string invocation="\""+dotnet+"\" \""+dll+"\" open \"%1\" --repository \""+repository+"\"";
  return Registration(invocation);
 }
 public static string FormatLauncher(string commandHost,string repository)
 {
  CheckPaths(commandHost,repository);
  string launcher=repository.TrimEnd('\\','/')+"\\open-project-windows.bat";
  return Registration("\""+commandHost+"\" /d /v:off /s /c \"\""+launcher+"\" \"%1\"\"");
 }
 private static void CheckPaths(params string[] paths)
 {
  foreach(string value in paths)if(value.IndexOfAny(new[]{'\r','\n','"'})>=0)throw new ArgumentException("Invalid association installation path");
 }
 private static string Registration(string invocation)
 {
  string Escape(string value)=>value.Replace("\\","\\\\").Replace("\"","\\\"");
  return "Windows Registry Editor Version 5.00\r\n\r\n[HKEY_CURRENT_USER\\Software\\Classes\\.cproj]\r\n@=\"Confectory.Project\"\r\n\r\n[HKEY_CURRENT_USER\\Software\\Classes\\.cproj\\OpenWithProgids]\r\n\"Confectory.Project\"=\"\"\r\n\r\n[HKEY_CURRENT_USER\\Software\\Classes\\Confectory.Project]\r\n@=\"Confectory ProjectPack\"\r\n\r\n[HKEY_CURRENT_USER\\Software\\Classes\\Confectory.Project\\shell\\open\\command]\r\n@=\""+Escape(invocation)+"\"\r\n";
 }
}
