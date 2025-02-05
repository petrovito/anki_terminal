# Differences Between Anki 2 and Anki 21

## Field Separators
- Anki 2: Uses 0x1f character as field separator in `notes.flds`
- Anki 21: Uses tab character as field separator in `notes.flds`

## Configuration Fields

### col.conf
Anki 21 adds:
- `schedVer` field for scheduler version
- `dayLearnFirst` for learning card order

### col.models
Anki 21 adds field metadata:
- `plainText` flag
- `excludeFromSearch` flag
- `preventDeletion` flag
- `description` field
- `media` array
- `tag` field
- `id` field

### col.dconf
Anki 21 adds:
- `hardFactor` (1.2) in rev section
- `leechAction` default changed from 0 to 1
- Root level fields:
  - `autoplay`
  - `timer`
  - `replayq`
  - `dyn`

## Model Templates
Anki 21 adds browser-specific template fields:
- `bqfmt` (browser question format)
- `bafmt` (browser answer format)
- `bfont` (browser font)
- `bsize` (browser font size)
- `did` (deck override) 