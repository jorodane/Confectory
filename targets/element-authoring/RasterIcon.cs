using System.Buffers.Binary;

// The original picker decodes locally, then emits one 128x128 canvas WebP.
// Validate that bounded container here; no file paths, remote URLs or codecs run.
internal static class RasterIcon
{
    const string Prefix = "data:image/webp;base64,";
    internal static bool IsImage(string value)
    {
        if (!value.StartsWith(Prefix, StringComparison.Ordinal) || value.Length > 65500) return false;
        byte[] bytes;
        try { bytes = Convert.FromBase64String(value[Prefix.Length..]); }
        catch (FormatException) { return false; }
        if (Convert.ToBase64String(bytes) != value[Prefix.Length..] || bytes.Length < 30 ||
            !bytes.AsSpan(0, 4).SequenceEqual("RIFF"u8) || !bytes.AsSpan(8, 4).SequenceEqual("WEBP"u8) ||
            BinaryPrimitives.ReadUInt32LittleEndian(bytes.AsSpan(4, 4)) != bytes.Length - 8) return false;
        bool extended = false, profile = false, alpha = false, image = false;
        for (int offset = 12; offset < bytes.Length;)
        {
            if (bytes.Length - offset < 8) return false;
            uint size = BinaryPrimitives.ReadUInt32LittleEndian(bytes.AsSpan(offset + 4, 4));
            if (size > bytes.Length - offset - 8) return false;
            var tag = bytes.AsSpan(offset, 4);
            var data = bytes.AsSpan(offset + 8, (int)size);
            if (tag.SequenceEqual("VP8X"u8))
            {
                if (offset != 12 || size != 10 || (data[0] & ~0x30) != 0 || data[1] != 0 || data[2] != 0 || data[3] != 0 ||
                    data[4] != 127 || data[5] != 0 || data[6] != 0 || data[7] != 127 || data[8] != 0 || data[9] != 0) return false;
                extended = true;
            }
            else if (tag.SequenceEqual("ICCP"u8))
            {
                if (!extended || profile || alpha || image || size < 1 || (bytes[20] & 0x20) == 0) return false;
                profile = true;
            }
            else if (tag.SequenceEqual("ALPH"u8))
            {
                if (!extended || alpha || image || size < 1 || (bytes[20] & 0x10) == 0) return false;
                alpha = true;
            }
            else if (tag.SequenceEqual("VP8 "u8))
            {
                if (image || size < 10 || (data[0] & 1) != 0 || !data.Slice(3, 3).SequenceEqual(new byte[] { 0x9d, 0x01, 0x2a }) ||
                    (BinaryPrimitives.ReadUInt16LittleEndian(data.Slice(6, 2)) & 0x3fff) != 128 ||
                    (BinaryPrimitives.ReadUInt16LittleEndian(data.Slice(8, 2)) & 0x3fff) != 128) return false;
                image = true;
            }
            else if (tag.SequenceEqual("VP8L"u8))
            {
                if (image || alpha || size < 5 || data[0] != 0x2f) return false;
                uint header = BinaryPrimitives.ReadUInt32LittleEndian(data.Slice(1, 4));
                if ((header & 0x3fff) != 127 || ((header >> 14) & 0x3fff) != 127 || (header >> 29) != 0) return false;
                image = true;
            }
            else return false; // Canvas may emit its color profile, never animation/EXIF/XMP.
            int next = offset + 8 + (int)size;
            if ((size & 1) != 0) { if (next >= bytes.Length || bytes[next] != 0) return false; next++; }
            offset = next;
        }
        return image && (!extended || ((bytes[20] & 0x20) != 0) == profile);
    }
}
