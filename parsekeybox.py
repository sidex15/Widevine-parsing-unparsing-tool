"""
ParseKeybox Tool (Python port of ParseKeybox.pl)

GENERAL DESCRIPTION
  Parse Widevine keybox.

USE:    python parsekeybox.py keybox.xml device_ID
Output: keybox.bin

Copyright (c) 2012 Qualcomm Incorporated.
All Rights Reserved.
Qualcomm Confidential and Proprietary
"""

import sys
import re

def extract_tag(text, tag):
    """Extract content between <tag>...</tag>, ignoring stray extra > characters."""
    match = re.search(rf'<{tag}>(.*?)</{tag}>', text)
    return match.group(1).strip() if match else None

def parse_keyboxes(content):
    """Extract all Keybox entries from raw file content using regex.
    Handles both properly closed </Keybox> tags and entries that are
    terminated by the next <Keybox or end of string."""
    return list(re.finditer(r'<Keybox\s+(.*?)>(.*?)(?=<Keybox|</Keybox|$)', content, re.DOTALL))

def get_attribute(attrs_str, attr_name):
    """Extract an attribute value from a tag's attribute string."""
    match = re.search(rf'{attr_name}=["\']([^"\']*)["\']', attrs_str)
    return match.group(1) if match else None

def main():
    if len(sys.argv) < 3:
        print("Usage: python turn.py keybox.xml device_ID")
        sys.exit(1)

    xml_path = sys.argv[1]
    target_device_id = sys.argv[2]
    output_filename = "keybox.bin"
    found = False

    with open(xml_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    for match in parse_keyboxes(content):
        attrs_str = match.group(1)
        inner     = match.group(2)

        device_id = get_attribute(attrs_str, "DeviceID")
        if device_id is None or device_id != target_device_id:
            continue

        if len(device_id) > 32:
            print("\nError: The length of DeviceID should NOT be larger than 32 bytes!")
            break

        found = True

        key   = extract_tag(inner, "Key")
        id_   = extract_tag(inner, "ID")
        magic = extract_tag(inner, "Magic")
        crc   = extract_tag(inner, "CRC")

        if any(v is None for v in [key, id_, magic, crc]):
            print("ERROR: Could not extract one or more fields (Key, ID, Magic, CRC).")
            sys.exit(1)

        print(f"DeviceID: {device_id}")
        print(f"Key:      {key}")
        print(f"ID:       {id_}")
        print(f"Magic:    {magic}")
        print(f"CRC:      {crc}")
        print()

        with open(output_filename, "wb") as f:
            # Write DeviceID as ASCII bytes, padded to 32 bytes with nulls
            device_id_bytes = device_id.encode("ascii")
            f.write(device_id_bytes)
            f.write(b"\x00" * (32 - len(device_id_bytes)))

            # Write Key, ID, Magic, CRC as raw hex-decoded bytes
            f.write(bytes.fromhex(key))
            f.write(bytes.fromhex(id_))
            f.write(bytes.fromhex(magic))
            f.write(bytes.fromhex(crc))

        break

    if not found:
        print("ERROR: Parsing keybox file failed.")
        raise SystemExit(
            f"There is no such a keybox having DeviceID = {target_device_id}"
        )

    print("Parsing keybox data succeeds!")

if __name__ == "__main__":
    main()