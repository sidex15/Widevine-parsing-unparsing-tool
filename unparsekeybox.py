"""
UnparseKeybox Tool - Reverse of ParseKeybox

GENERAL DESCRIPTION
  Convert a Widevine keybox.bin back into XML format.

USE:    python unparsekeybox.py keybox.bin [output.xml]
Output: keybox.xml (or specified output filename)

Standard Widevine keybox.bin layout:
  Offset  0: DeviceID  - 32 bytes (ASCII, null-padded)
  Offset 32: Key       - 16 bytes
  Offset 48: ID        -  4 bytes
  Offset 52: Magic     -  4 bytes
  Offset 56: CRC       -  4 bytes
  Total: 60 bytes
"""

import sys

FIELD_SIZES = {
    "DeviceID": 32,
    "Key":       16,
    "ID":         72,
    "Magic":      4,
    "CRC":        4,
}
TOTAL_SIZE = sum(FIELD_SIZES.values())  # 60 bytes

def bin_to_xml(bin_path, xml_path):
    with open(bin_path, "rb") as f:
        data = f.read()

    if len(data) < TOTAL_SIZE:
        print(f"ERROR: File is {len(data)} bytes, expected at least {TOTAL_SIZE} bytes.")
        sys.exit(1)

    if len(data) > TOTAL_SIZE:
        print(f"Warning: File is {len(data)} bytes, expected {TOTAL_SIZE}. Extra bytes will be ignored.")

    offset = 0

    # DeviceID: strip null padding
    device_id_raw = data[offset:offset + FIELD_SIZES["DeviceID"]]
    device_id = device_id_raw.rstrip(b"\x00").decode("ascii")
    offset += FIELD_SIZES["DeviceID"]

    # Key, ID, Magic, CRC: encode as uppercase hex strings
    key   = data[offset:offset + FIELD_SIZES["Key"]].hex().upper()
    offset += FIELD_SIZES["Key"]

    id_   = data[offset:offset + FIELD_SIZES["ID"]].hex().upper()
    offset += FIELD_SIZES["ID"]

    magic = data[offset:offset + FIELD_SIZES["Magic"]].hex().upper()
    offset += FIELD_SIZES["Magic"]

    crc   = data[offset:offset + FIELD_SIZES["CRC"]].hex().upper()

    print(f"DeviceID: {device_id}")
    print(f"Key:      {key}")
    print(f"ID:       {id_}")
    print(f"Magic:    {magic}")
    print(f"CRC:      {crc}")

    xml_content = (
        f'<Keybox DeviceID="{device_id}">'
        f'<Key>{key}</Key>'
        f'<ID>{id_}</ID>'
        f'<Magic>{magic}</Magic>'
        f'<CRC>{crc}</CRC>'
        f'</Keybox>\n'
    )

    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    print(f"\nWritten to: {xml_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python unparse_keybox.py keybox.bin [output.xml]")
        sys.exit(1)

    bin_path = sys.argv[1]
    xml_path = sys.argv[2] if len(sys.argv) >= 3 else "keybox.xml"

    bin_to_xml(bin_path, xml_path)
    print("Done!")

if __name__ == "__main__":
    main()