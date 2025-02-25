# Differences Between Anki 2 and Anki 21

## Field Separators
- Both Anki 2 and Anki 21 use the 0x1f character (unit separator) as field separator in `notes.flds`

Example:
```sql
-- Both Anki 2 and Anki 21
INSERT INTO notes (flds) VALUES ('Front Field\x1fBack Field\x1fExtra Field');
```

## Configuration Fields

### col.conf
Anki 21 adds:
- `schedVer` field for scheduler version
- `dayLearnFirst` for learning card order

Example:
```json
// Anki 2
{
    "curDeck": 1,
    "newSpread": 0,
    "collapseTime": 1200,
    "timeLim": 0,
    "estTimes": true,
    "dueCounts": true,
    "sortType": "noteFld",
    "addToCur": true,
    "curModel": "1384115547412"
}

// Anki 21
{
    "curDeck": 1,
    "newSpread": 0,
    "collapseTime": 1200,
    "timeLim": 0,
    "estTimes": true,
    "dueCounts": true,
    "sortType": "noteFld",
    "addToCur": true,
    "curModel": 1352568357693,
    "schedVer": 1,
    "dayLearnFirst": false
}
```

## Model Fields
Anki 21 adds several new field attributes:

```json
// Anki 2 field
{
    "name": "Front",
    "media": [],
    "sticky": false,
    "rtl": false,
    "ord": 0,
    "font": "Arial",
    "size": 20
}

// Anki 21 field
{
    "name": "Front",
    "ord": 0,
    "sticky": false,
    "rtl": false,
    "font": "Arial",
    "size": 20,
    "plainText": false,      // Whether field should be plain text only
    "excludeFromSearch": false,  // Whether to exclude from search
    "preventDeletion": false,    // Whether field can be deleted
    "description": "",      // Field description
    "collapsed": false,     // Whether field is collapsed in editor
    "media": [],           // Media references
    "tag": null,           // Field tag
    "id": null            // Field ID
}
```

## Template Fields
Anki 21 adds browser-specific template attributes:

```json
// Anki 2 template
{
    "name": "Card 1",
    "ord": 0,
    "qfmt": "{{Front}}",
    "afmt": "{{Back}}",
    "bqfmt": "",
    "bafmt": "",
    "did": null
}

// Anki 21 template
{
    "name": "Card 1",
    "ord": 0,
    "qfmt": "{{Front}}",
    "afmt": "{{Back}}",
    "bqfmt": "",
    "bafmt": "",
    "did": null,
    "bfont": "",          // Browser font
    "bsize": 0,           // Browser font size
    "id": null           // Template ID
}
``` 