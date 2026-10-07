using System.Buffers.Binary;
using System.IO.Compression;
using System.Text.Json;
namespace Confectory.AndroidExport;
public static class NativePackageInspection
{
    public static bool Elf64Aligned(byte[] data)
    {
        if(data.Length<64||data[0]!=0x7f||data[1]!='E'||data[2]!='L'||data[3]!='F'||data[4]!=2||data[5]!=1)return false;
        ulong table=BinaryPrimitives.ReadUInt64LittleEndian(data.AsSpan(32,8));
        int size=BinaryPrimitives.ReadUInt16LittleEndian(data.AsSpan(54,2)),count=BinaryPrimitives.ReadUInt16LittleEndian(data.AsSpan(56,2));
        if(size<56||count==0||table>(ulong)data.Length||(ulong)count*(ulong)size>(ulong)data.Length-table)return false;
        bool load=false;
        for(int i=0;i<count;i++)
        {
            var p=data.AsSpan((int)table+i*size,56);uint type=BinaryPrimitives.ReadUInt32LittleEndian(p);
            ulong offset=BinaryPrimitives.ReadUInt64LittleEndian(p[8..]),address=BinaryPrimitives.ReadUInt64LittleEndian(p[16..]),memory=BinaryPrimitives.ReadUInt64LittleEndian(p[40..]),alignment=BinaryPrimitives.ReadUInt64LittleEndian(p[48..]);
            if(type==1){load=true;if(alignment<16384||(offset%16384)!=(address%16384))return false;}
            if(type==0x6474e552&&(address+memory)%16384!=0)return false;
        }
        return load;
    }
    public static int Inspect(string path)
    {
        using var archive=ZipFile.OpenRead(path);
        var native=archive.Entries.Where(e=>e.FullName.EndsWith(".so",StringComparison.Ordinal)&&(e.FullName.Contains("/arm64-v8a/",StringComparison.Ordinal)||e.FullName.Contains("/x86_64/",StringComparison.Ordinal)))
            .Select(e=>{using var stream=e.Open();using var memory=new MemoryStream();stream.CopyTo(memory);return new{entry=e.FullName,elf16KiBAligned=Elf64Aligned(memory.ToArray())};}).ToArray();
        bool aligned=native.Length>0&&native.All(x=>x.elf16KiBAligned);
        Console.WriteLine(JsonSerializer.Serialize(new{artifact=Path.GetFullPath(path),native,elf16KiBAligned=aligned,zipAlignmentVerified=false,device16KiBTested=false,playAcceptanceVerified=false},new JsonSerializerOptions{WriteIndented=true}));
        return aligned?0:1;
    }
}
