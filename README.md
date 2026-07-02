# Widevine Keybox Parse and Unparse Tools

Python utilities for converting Widevine keybox data between XML and binary
formats.

- [`parsekeybox.py`](parsekeybox.py) — extracts a single keybox entry from an
  XML file (by `DeviceID`) and writes it out as a binary `keybox.bin`.
- [`unparsekeybox.py`](unparsekeybox.py) — the reverse: reads a binary keybox
  file and writes it back out as XML.

## Binary keybox layout

| Field    | Offset | Size (bytes) | Encoding                  |
|----------|-------:|--------------:|----------------------------|
| DeviceID |      0 |             32 | ASCII, null-padded          |
| Key      |     32 |             16 | raw bytes                   |
| ID       |     48 |             72 | raw bytes                   |
| Magic    |    120 |              4 | raw bytes                   |
| CRC      |    124 |              4 | raw bytes                   |

Total size: 128 bytes.

## parsekeybox.py

Parses a Widevine keybox XML file, finds the `<Keybox>` entry matching a
given `DeviceID`, and writes its fields to `keybox.bin` in the binary layout
above.

Expected XML shape:

```xml
<Keybox DeviceID="...">
  <Key>...</Key>
  <ID>...</ID>
  <Magic>...</Magic>
  <CRC>...</CRC>
</Keybox>
```

`Key`, `ID`, `Magic`, and `CRC` are expected to be hex-encoded strings; they
are decoded to raw bytes before being written.

### Usage

```sh
python parsekeybox.py keybox.xml device_ID
```

- `keybox.xml` — path to the input XML file (may contain multiple `<Keybox>`
  entries).
- `device_ID` — the `DeviceID` attribute value to look up (max 32 bytes).

### Output

Writes `keybox.bin` in the current directory and prints the extracted
`DeviceID`, `Key`, `ID`, `Magic`, and `CRC` values. Exits with an error if no
matching `DeviceID` is found or if any required field is missing.

## unparsekeybox.py

Reverses the process: reads a binary keybox file and reconstructs the XML
representation, hex-encoding the `Key`, `ID`, `Magic`, and `CRC` fields.

### Usage

```sh
python unparsekeybox.py keybox.bin [output.xml]
```

- `keybox.bin` — path to the input binary keybox file (at least 128 bytes).
- `output.xml` — optional output path (defaults to `keybox.xml`).

### Output

Writes the reconstructed `<Keybox>` XML element to the output file and
prints the decoded `DeviceID`, `Key`, `ID`, `Magic`, and `CRC` values.
