# Anki 2 Database Schema

## Tables Overview
The Anki 2 database consists of five main tables:
- `cards`: Stores individual flashcards
- `notes`: Stores note content and metadata
- `col`: Collection configuration and metadata (always contains exactly 1 row)
- `graves`: Deleted items tracking
- `revlog`: Review history

> **Note**: For complete examples of the JSON structures described in this document, see `test_data/sample_anki2.txt`.

## Detailed Schema

### cards
```sql
CREATE TABLE cards (
    id              integer primary key,   /* unique card id */
    nid             integer not null,      /* note id, references notes.id */
    did             integer not null,      /* deck id, references col.decks */
    ord             integer not null,      /* template sequence number */
    mod             integer not null,      /* last modified timestamp */
    usn             integer not null,      /* update sequence number */
    type            integer not null,      /* 0=new, 1=learning, 2=review, 3=relearning */
    queue           integer not null,      /* -3=sched buried, -2=user buried, -1=suspended, 0=new, 1=learning */
    due             integer not null,      /* due date for reviews */
    ivl             integer not null,      /* interval (days) */
    factor          integer not null,      /* ease factor */
    reps            integer not null,      /* number of reviews */
    lapses          integer not null,      /* number of lapses */
    left            integer not null,      /* steps left today */
    odue            integer not null,      /* original due date */
    odid            integer not null,      /* original deck id */
    flags           integer not null,      /* flags */
    data            text not null         /* additional data */
);
CREATE INDEX ix_cards_usn on cards (usn);
CREATE INDEX ix_cards_nid on cards (nid);
CREATE INDEX ix_cards_sched on cards (did, queue, due);
```

### notes
```sql
CREATE TABLE notes (
    id              integer primary key,   /* unique note id */
    guid            text not null,         /* globally unique id */
    mid             integer not null,      /* model id, references col.models */
    mod             integer not null,      /* last modified timestamp */
    usn             integer not null,      /* update sequence number */
    tags            text not null,         /* space-separated tags */
    flds            text not null,         /* field data, separated by 0x1f */
    sfld            integer not null,      /* sort field */
    csum            integer not null,      /* checksum of first field */
    flags           integer not null,      /* flags */
    data            text not null         /* additional data */
);
CREATE INDEX ix_notes_usn on notes (usn);
CREATE INDEX ix_notes_csum on notes (csum);
```

### col (Collection)
The collection table always contains exactly one row that stores all configuration for the Anki collection.

```sql
CREATE TABLE col (
    id              integer primary key,   /* unique collection id */
    crt             integer not null,      /* collection creation time */
    mod             integer not null,      /* last modified timestamp */
    scm             integer not null,      /* schema modification time */
    ver             integer not null,      /* version */
    dty             integer not null,      /* dirty flag */
    usn             integer not null,      /* update sequence number */
    ls              integer not null,      /* last sync time */
    conf            text not null,         /* configuration */
    models          text not null,         /* note types */
    decks           text not null,         /* deck configuration */
    dconf           text not null,         /* deck options */
    tags            text not null         /* tags cache */
);
```

### graves
```sql
CREATE TABLE graves (
    usn             integer not null,      /* update sequence number */
    oid             integer not null,      /* original id */
    type            integer not null      /* type of deleted object */
);
```

### revlog (Review Log)
```sql
CREATE TABLE revlog (
    id              integer primary key,   /* unique review id */
    cid             integer not null,      /* card id */
    usn             integer not null,      /* update sequence number */
    ease            integer not null,      /* ease factor */
    ivl             integer not null,      /* interval */
    lastIvl         integer not null,      /* last interval */
    factor          integer not null,      /* ease factor */
    time            integer not null,      /* time taken */
    type            integer not null      /* review type */
);
```

## JSON Fields in col Table
The `col` table contains several JSON fields that store complex configuration data. Below is a detailed description of each field's structure:

### conf (Configuration)
Contains general configuration settings stored as a JSON object:
```json
{
    "activeDecks": [1],              // Array of active deck IDs
    "curDeck": 1,                    // Current deck ID
    "newSpread": 0,                  // How to distribute new cards: 0=distribute, 1=last, 2=first
    "collapseTime": 1200,            // Deck browser collapse time (milliseconds)
    "timeLim": 0,                    // Time limit for answer in minutes
    "estTimes": true,                // Show estimated time for review?
    "dueCounts": true,               // Show due counts in deck list?
    "curModel": null,                // Current model ID
    "nextPos": 1,                    // Next card position
    "sortType": "noteFld",           // Sort field in browser
    "sortBackwards": false,          // Reverse sort in browser?
    "addToCur": true,               // Add new cards to current deck?
    "dayLearnFirst": false          // Show learning cards before reviews?
}
```

### models (Note Types)
Contains note type definitions as a JSON object where each key is the model ID:
```json
{
    "1234567890": {
        "id": "1234567890",         // Model ID (matches the key)
        "name": "Basic",            // Model name
        "type": 0,                  // 0=standard, 1=cloze
        "mod": 1234567890,          // Modification timestamp
        "usn": -1,                  // Update sequence number
        "sortf": 0,                 // Sort field index
        "did": null,                // Deck ID (null=use current)
        "tmpls": [{                 // Array of templates
            "name": "Card 1",
            "ord": 0,
            "qfmt": "{{Front}}",    // Question format
            "afmt": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}", // Answer format
            "bqfmt": "",            // Browser question format
            "bafmt": "",            // Browser answer format
            "did": null,            // Deck override (null=use default)
            "bfont": "",            // Browser font
            "bsize": 0              // Browser font size
        }],
        "flds": [{                  // Array of fields
            "name": "Front",
            "ord": 0,
            "sticky": false,        // Sticky in add dialog?
            "rtl": false,           // Right-to-left script?
            "font": "Arial",
            "size": 20,
            "media": []             // Array of media references
        }],
        "css": ".card {\n font-family: arial;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}\n", // Card styling
        "latexPre": "\\documentclass[12pt]{article}\n\\special{papersize=3in,5in}\n\\usepackage[utf8]{inputenc}\n\\usepackage{amssymb,amsmath}\n\\pagestyle{empty}\n\\setlength{\\parindent}{0in}\n\\begin{document}\n",
        "latexPost": "\\end{document}",
        "latexsvg": false,          // Use SVG for LaTeX?
        "req": [[0, "any", [0]]]    // Array of requirements: [template_index, "any"|"all", [field_index, ...]]
    }
}
```

### decks
Contains deck configurations as a JSON object where each key is the deck ID:
```json
{
    "1": {
        "id": 1,                    // Deck ID (matches the key)
        "name": "Default",          // Deck name
        "mod": 1234567890,          // Modification timestamp
        "usn": -1,                  // Update sequence number
        "lrnToday": [0, 0],        // [ease4 count, no ease4 count]
        "revToday": [0, 0],        // [mature count, young count]
        "newToday": [0, 0],        // [learning count, review count]
        "timeToday": [0, 0],       // [time in ms, review count]
        "collapsed": false,         // Collapsed in deck browser?
        "browserCollapsed": false,  // Collapsed in browser?
        "desc": "",                // Deck description
        "dyn": 0,                  // Dynamic deck?
        "conf": 1,                 // Configuration ID
        "extendNew": 10,           // Extend new card limit?
        "extendRev": 50           // Extend review card limit?
    }
}
```

### dconf (Deck Configuration)
Contains deck option group settings as a JSON object where each key is the configuration ID:
```json
{
    "1": {
        "id": 1,                    // Configuration ID (matches the key)
        "name": "Default",          // Configuration name
        "mod": 1234567890,          // Modification timestamp
        "usn": -1,                  // Update sequence number
        "maxTaken": 60,            // Maximum answer time to record
        "new": {
            "delays": [1, 10],      // Learning steps (minutes)
            "ints": [1, 4, 7],      // Intervals (days)
            "initialFactor": 2500,  // Initial ease factor
            "separate": true,       // Separate learning/review queues
            "order": 1,             // New card order: 0=random, 1=order added
            "perDay": 20,           // New cards per day
            "bury": false          // Bury related cards?
        },
        "rev": {
            "perDay": 100,         // Maximum reviews per day
            "ease4": 1.3,          // Easy bonus
            "fuzz": 0.05,          // Interval modifier
            "minSpace": 1,         // Minimum interval (days)
            "maxSpace": 36500,     // Maximum interval (days)
            "ease": 2.5           // Starting ease
        },
        "lapse": {
            "delays": [10],        // Lapse steps (minutes)
            "mult": 0,             // New interval multiplier
            "minInt": 1,           // Minimum interval (days)
            "leechFails": 8        // Leech threshold
        },
        "replayq": true,          // Replay question audio?
        "timer": 0,               // Timer: 0=off, 1=on
        "autoplay": true,         // Automatically play audio?
        "mod": 0                  // Modification time
    }
}
```

### tags
Contains a cache of all tags as a JSON object:
```json
{
    "tag1": null,                  // Tag name with null value
    "tag2": null,
    "tag3": null
}
```

> **Note**: For complete examples of these JSON structures and their usage, refer to `test_data/sample_anki2.txt`. 