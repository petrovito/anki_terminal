# Anki 21 Database Schema

This document describes the schema of Anki 21 databases based on actual database samples.

## Core Tables

The Anki 21 database consists of the following core tables:

### cards
```sql
CREATE TABLE cards (
    id     integer primary key,
    nid    integer not null,    /* note id */
    did    integer not null,    /* deck id */
    ord    integer not null,    /* template order */
    mod    integer not null,    /* last modified timestamp */
    usn    integer not null,    /* update sequence number */
    type   integer not null,    /* 0=new, 1=learning, 2=review, 3=relearning */
    queue  integer not null,    /* -3=sched buried, -2=user buried, -1=suspended, 0=new */
    due    integer not null,    /* due time, interpreted based on type */
    ivl    integer not null,    /* interval (days) */
    factor integer not null,    /* ease factor */
    reps   integer not null,    /* number of reviews */
    lapses integer not null,    /* number of lapses */
    left   integer not null,    /* steps left today */
    odue   integer not null,    /* original due time */
    odid   integer not null,    /* original deck id */
    flags  integer not null,    /* flags */
    data   text not null       /* additional data in JSON format */
);

CREATE INDEX ix_cards_usn on cards (usn);
CREATE INDEX ix_cards_nid on cards (nid);
CREATE INDEX ix_cards_sched on cards (did, queue, due);
```

### notes
```sql
CREATE TABLE notes (
    id    integer primary key,
    guid  text not null,       /* globally unique id */
    mid   integer not null,    /* model id */
    mod   integer not null,    /* last modified timestamp */
    usn   integer not null,    /* update sequence number */
    tags  text not null,       /* space-separated tags */
    flds  text not null,       /* fields separated by \x1f character */
    sfld  integer not null,    /* sort field */
    csum  integer not null,    /* checksum for duplicate check */
    flags integer not null,    /* flags */
    data  text not null       /* additional data in JSON format */
);

CREATE INDEX ix_notes_usn on notes (usn);
CREATE INDEX ix_notes_csum on notes (csum);
```

### col (Collection)
```sql
CREATE TABLE col (
    id     integer primary key,
    crt    integer not null,    /* collection creation time */
    mod    integer not null,    /* last modified timestamp */
    scm    integer not null,    /* schema modified time */
    ver    integer not null,    /* version */
    dty    integer not null,    /* dirty: need full sync */
    usn    integer not null,    /* update sequence number */
    ls     integer not null,    /* last sync time */
    conf   text not null,       /* configuration in JSON format */
    models text not null,       /* note types in JSON format */
    decks  text not null,       /* decks in JSON format */
    dconf  text not null,       /* deck configuration in JSON format */
    tags   text not null        /* tags in JSON format */
);
```

### graves
```sql
CREATE TABLE graves (
    usn integer not null,     /* update sequence number */
    oid integer not null,     /* original id */
    type integer not null     /* type of deleted object */
);
```

### revlog (Review Log)
```sql
CREATE TABLE revlog (
    id       integer primary key,
    cid      integer not null,    /* card id */
    usn      integer not null,    /* update sequence number */
    ease     integer not null,    /* ease factor */
    ivl      integer not null,    /* interval */
    lastIvl  integer not null,    /* last interval */
    factor   integer not null,    /* ease factor */
    time     integer not null,    /* time taken */
    type     integer not null     /* review type */
);
```

## JSON Fields

### col.conf (Configuration)
Contains general configuration settings:
```json
{
    "curDeck": 1,                    // Current deck ID
    "newSpread": 0,                  // How to distribute new cards
    "collapseTime": 1200,           // Deck browser collapse time (ms)
    "timeLim": 0,                   // Time limit for answer (minutes)
    "estTimes": true,               // Show estimated time for review
    "dueCounts": true,              // Show due counts in deck list
    "curModel": 1234567890,        // Current model ID
    "nextPos": 1,                   // Next card position
    "sortType": "noteFld",         // Sort field in browser
    "sortBackwards": false,        // Reverse sort in browser
    "addToCur": true,              // Add new cards to current deck
    "dayLearnFirst": false,        // Show learning cards before reviews
    "schedVer": 1                  // Scheduler version
}
```

### col.models (Note Types)
Contains note type definitions:
```json
{
    "1234567890": {
        "id": 1234567890,
        "name": "Basic",
        "type": 0,                 // 0=standard, 1=cloze
        "mod": 1234567890,         // Modified timestamp
        "usn": -1,                 // Update sequence number
        "sortf": 0,                // Sort field index
        "did": 1,                  // Deck ID
        "tmpls": [{                // Templates array
            "name": "Card 1",
            "ord": 0,              // Template order
            "qfmt": "{{Front}}",   // Question format
            "afmt": "{{Back}}",    // Answer format
            "bqfmt": "",           // Browser question format
            "bafmt": "",           // Browser answer format
            "did": null,           // Deck override
            "bfont": "",           // Browser font
            "bsize": 0             // Browser font size
        }],
        "flds": [{                 // Fields array
            "name": "Front",
            "ord": 0,              // Field order
            "sticky": false,       // Sticky fields
            "rtl": false,          // Right to left script
            "font": "Arial",
            "size": 20,
            "plainText": false,    // Whether field should be plain text only
            "excludeFromSearch": false, // Whether to exclude from search
            "preventDeletion": false,   // Whether field can be deleted
            "description": "",     // Field description
            "media": [],          // Media references
            "tag": null,          // Field tag
            "id": null           // Field ID
        }],
        "css": ".card { }",        // Card styling
        "latexPre": "",           // LaTeX header
        "latexPost": "",          // LaTeX footer
        "latexsvg": false,        // Use SVG for LaTeX
        "req": [[0, "any", [0]]]  // Required fields
    }
}
```

### col.decks (Decks)
Contains deck definitions:
```json
{
    "1": {
        "id": 1,
        "name": "Default",
        "mod": 1234567890,         // Modified timestamp
        "usn": -1,                 // Update sequence number
        "lrnToday": [0, 0],        // Learning cards today [day, count]
        "revToday": [0, 0],        // Review cards today [day, count]
        "newToday": [0, 0],        // New cards today [day, count]
        "timeToday": [0, 0],       // Time spent today [day, ms]
        "collapsed": false,         // Collapsed in deck list
        "desc": "",                // Description
        "dyn": 0,                  // Dynamic deck
        "conf": 1                  // Configuration group ID
    }
}
```

### col.dconf (Deck Configuration)
Contains deck options:
```json
{
    "1": {
        "id": 1,
        "name": "Default",
        "maxTaken": 60,            // Max answer time secs
        "autoplay": true,          // Automatically play audio
        "timer": 0,                // Timer mode
        "replayq": true,           // Replay question audio
        "dyn": false,              // Dynamic deck
        "new": {
            "bury": false,         // Bury related new cards
            "delays": [1, 10],     // Learning steps (minutes)
            "initialFactor": 2500, // Starting ease
            "perDay": 20,          // New cards/day
            "order": 1             // New card order
        },
        "rev": {
            "bury": false,         // Bury related reviews
            "ease4": 1.3,          // Easy bonus
            "ivlFct": 1.0,         // Interval modifier
            "maxIvl": 36500,       // Maximum interval
            "perDay": 200,         // Reviews/day
            "hardFactor": 1.2      // Hard button factor
        },
        "lapse": {
            "delays": [10],        // Lapse steps (minutes)
            "leechAction": 1,      // Leech action
            "leechFails": 8,       // Leech threshold
            "minInt": 1,           // Minimum interval
            "mult": 0              // New interval multiplier
        }
    }
}
```
