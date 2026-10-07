using Android.Content;
using Android.Provider;
namespace Confectory.Android;
// Granted provider reads only. Copies are editable app-owned files; no provider write authority is retained.
internal static class AndroidDocumentImport
{
    public static string Copy(ContentResolver resolver,global::Android.Net.Uri uri,string root,bool tree)
    {
        if(uri.Scheme!="content")throw new ArgumentException("User-granted content URI required");
        // Stable URI identity reopens the existing app-owned copy without erasing edits.
        string complete=System.IO.Path.Combine(root,".complete");if(System.IO.File.Exists(complete))return System.IO.File.ReadAllText(complete);
        string staging=root+"."+Guid.NewGuid().ToString("N");System.IO.Directory.CreateDirectory(staging);int entries=0;long bytes=0;
        void File(global::Android.Net.Uri source,string target)
        {
            using var input=resolver.OpenInputStream(source)??throw new System.IO.IOException("Grant does not provide readable bytes");using var output=System.IO.File.Create(target);var buffer=new byte[65536];int count;
            while((count=input.Read(buffer,0,buffer.Length))>0){bytes+=count;if(bytes>64*1024*1024)throw new System.IO.IOException("Granted import byte budget exceeded");output.Write(buffer,0,count);}
        }
        void Directory(string id,string destination,int depth)
        {
            if(depth>16)throw new System.IO.IOException("Granted import depth budget exceeded");
            var children=DocumentsContract.BuildChildDocumentsUriUsingTree(uri,id)!;
            using var cursor=resolver.Query(children,new[]{DocumentsContract.Document.ColumnDocumentId,DocumentsContract.Document.ColumnDisplayName,DocumentsContract.Document.ColumnMimeType},null,null,null)??throw new System.IO.IOException("Grant does not permit folder enumeration");
            while(cursor.MoveToNext())
            {
                if(++entries>1024)throw new System.IO.IOException("Granted import entry budget exceeded");string child=cursor.GetString(0)!,name=cursor.GetString(1)!,mime=cursor.GetString(2)!;
                if(name is "." or ".."||name.Length==0||name.IndexOfAny(new[]{'/','\\','\0'})>=0)throw new System.IO.IOException("Unsafe provider document name");
                string target=System.IO.Path.Combine(destination,name);
                if(mime==DocumentsContract.Document.MimeTypeDir){System.IO.Directory.CreateDirectory(target);Directory(child,target,depth+1);}else File(DocumentsContract.BuildDocumentUriUsingTree(uri,child)!,target);
            }
        }
        try
        {
            string selected;
            if(tree){Directory(DocumentsContract.GetTreeDocumentId(uri)!,staging,0);selected=root;}
            else{string name="project.cpack";File(uri,System.IO.Path.Combine(staging,name));selected=System.IO.Path.Combine(root,name);}
            System.IO.File.WriteAllText(System.IO.Path.Combine(staging,".complete"),selected);if(System.IO.Directory.Exists(root))System.IO.Directory.Delete(root,true);System.IO.Directory.Move(staging,root);return selected;
        }
        catch{System.IO.Directory.Delete(staging,true);throw;}
    }
}
