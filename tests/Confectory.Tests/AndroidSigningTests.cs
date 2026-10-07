using Confectory.AndroidExport;
namespace Confectory.Tests;
public sealed class AndroidSigningTests : TestCase
{
    public void test_native_alignment_gate_rejects_4k_and_relro_tail_even_with_16k_load_alignment()
    {
        byte[] elf=new byte[176];elf[0]=0x7f;elf[1]=(byte)'E';elf[2]=(byte)'L';elf[3]=(byte)'F';elf[4]=2;elf[5]=1;
        void U64(int p,ulong v)=>System.Buffers.Binary.BinaryPrimitives.WriteUInt64LittleEndian(elf.AsSpan(p,8),v);
        U64(32,64);elf[54]=56;elf[56]=2;elf[64]=1;U64(64+48,16384);
        System.Buffers.Binary.BinaryPrimitives.WriteUInt32LittleEndian(elf.AsSpan(120,4),0x6474e552);U64(120+16,16384);U64(120+40,16384);
        True(NativePackageInspection.Elf64Aligned(elf));U64(64+48,4096);True(!NativePackageInspection.Elf64Aligned(elf));
        U64(64+48,16384);U64(120+40,4096);True(!NativePackageInspection.Elf64Aligned(elf));
        True(!NativePackageInspection.Elf64Aligned(elf[..80]));
    }
    public void test_signing_arguments_keep_passwords_in_child_environment_without_shell_or_files()
    {
        const string store="fake store sentinel & \";$()",key="fake key sentinel 한글";
        foreach(string format in new[]{"apk","aab"})
        {
            var command=LocalSigning.SigningCommand(format,"local signer","unsigned "+format,"signed "+format,"local selected key","upload",store,key);
            True(!command.UseShellExecute);True(command.RedirectStandardInput);True(command.RedirectStandardError);
            True(!command.ArgumentList.Any(x=>x.Contains(store)||x.Contains(key)));
            Equal(store,command.Environment[LocalSigning.StoreVariable]);Equal(key,command.Environment[LocalSigning.KeyVariable]);
            True(Environment.GetEnvironmentVariable(LocalSigning.StoreVariable)!=store);
            True(command.ArgumentList.Contains(format=="aab"?"-storepass:env":"env:"+LocalSigning.StoreVariable));
            True(!command.ArgumentList.Contains("-storepass"));True(!command.ArgumentList.Any(x=>x.StartsWith("pass:")));
        }
        bool refused=false;try{LocalSigning.SigningCommand("aab","tool","in","out","key","-option",store,key);}catch(ArgumentException){refused=true;}True(refused);
        // This gate creates no key and invokes no real signer.
    }
}
