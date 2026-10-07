namespace Confectory.DesktopEntry;
// Format only. The Windows entry tool writes an opt-in file, never modifies registry settings.
public static class WindowsAssociation
{
 public static string Format(string dotnet,string dll,string repository)
 {
  foreach(string value in new[]{dotnet,dll,repository})if(value.IndexOfAny(new[]{'\r','\n','"'})>=0)throw new ArgumentException("Invalid association installation path");
  string Escape(string value)=>value.Replace("\\","\\\\").Replace("\"","\\\"");
  string invocation="\""+dotnet+"\" \""+dll+"\" open \"%1\" --repository \""+repository+"\"";
  return "Windows Registry Editor Version 5.00\r\n\r\n[HKEY_CURRENT_USER\\Software\\Classes\\.cproj]\r\n@=\"Confectory.Project\"\r\n\r\n[HKEY_CURRENT_USER\\Software\\Classes\\.cproj\\OpenWithProgids]\r\n\"Confectory.Project\"=\"\"\r\n\r\n[HKEY_CURRENT_USER\\Software\\Classes\\Confectory.Project]\r\n@=\"Confectory ProjectPack\"\r\n\r\n[HKEY_CURRENT_USER\\Software\\Classes\\Confectory.Project\\shell\\open\\command]\r\n@=\""+Escape(invocation)+"\"\r\n";
 }
}
