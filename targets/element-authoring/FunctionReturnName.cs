using Confectory.Core;
using System.Text.Json;

// Presentation for the fixed return slot. Never a C# name, output ID or contract.
internal static class FunctionReturnName
{
 internal const string Key="editorReturnName";
 internal const string Default="결과";
 static bool Valid(string value)=>value.Length is >=1 and <=60&&value==value.Trim()&&!value.Any(char.IsControl);
 public static string Read(Element function)=>function.Values.TryGetValue(Key,out var value)&&value.Value.ValueKind==JsonValueKind.String&&Valid(value.Value.GetString()!)?value.Value.GetString()!:Default;
 public static void Set(Element function,string value)
 {
  value=value.Trim();if(function.Kind!="function"||!Valid(value))throw new ArgumentException("Bounded return pin display name required; native return identity is unchanged");
  if(value==Default)function.Values.Remove(Key);else function.Values[Key]=new(JsonSerializer.SerializeToElement(value),function.Id,new());
 }
}
