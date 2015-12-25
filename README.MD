# medialib
## Overview
Small sanity checks and additional tools for private media library.

It will check/update the following (see below for details):
- (1st version done) naming conventions
- (1st version done) ID3 tags
- (TBD) .m3u, .cue, .log files
- (TBD) .md5, .sfv, .sha files

## Details
### Naming Conventions
Currently done for music libraries. Assumptions is that everything is ordered as albums in one big folder, which follow the naming conventions of 

`{artist}[ - {type}] - {year} - {album name}[ - {FLAC|MP3@{bitrate}]`

Where the delimiter is ' - ', i.e., `{space}{dash}{space}`. This string MUST NOT be contained in any of the fields.

- Artist name currently must conform the following regex: `(\w|[áéíóúäöüÁÉÍÓÚÄÖÜőűŐŰ])+` (i.e., any at least one character long string from latin and some extra letters)
- Type currently must conform the following regex: `((E|L|S)P)|(Compilation)|(Live)|(Remix)|(OST)|(Unofficial)` (i.e., EP, LP, SP, Compilation, Live, Remix, OST, Unofficial)
- Year is as `0000|19[0-9]{2}|20[0-9]{2}` (i.e., 0000 for unknown, 19xx and 20xx are accepted)
- Album name can be any string
- FLAC/MP3 metatag is not checked currently

Inside the album folder the following folders can be: `Multimedia`, `CD{n}` for 1 <= n <= 9. `Multimedia` folders are skipped by the script, for one CD albums `CD1` folder should be omitted. Allowed files are of extensions `.cue, .m3u, .log, .mp3, .flac` (later on the checksum files will be allowed).

File naming convention is

`{two digit track number} - {artist} - {track title}`

Where the delimiter is ' - ', i.e., `{space}{dash}{space}`. This string MUST NOT be contained in any of the fields.

- Track number is as `([1-9]\.)?[0-9]{2}` (i.e., two-digit and optinally denoting the CD as 1.xx, 2.xx, etc.)
- Artist as above
- Track title is any string.

The following addiotnal checks are done on the fields:
- No double-spacing, no spaces before comma or dot.
- Capitalization is checked, see later.
- Warning is emitted when artist does not match artist of folder.

Note: the checks will yield many false positives (i.e., if artist of folder is VA and artist of track is the real artist).

#### Capitalization
By default every word should start with capital, and that should be the only capital in the whole words (except for full-digit words). Exception list is defined in the script itself for a couple languages and additionally the string `(feat.` is excepted. False positives are currently emitted for every name which ends with `)`.

False positives are also emitted for names which are of special format (e.g., [Ao no Exoscist OST 1](http://aonoexorcist.wikia.com/wiki/Blue_Exorcist_Original_Soundtrack_1) will have two false positives at least, one for the `no` in the album name, and for most of the track titles, e.g., "Symphonic Suite DEVIL Third Movement: eXORCiST", "AOE Suite First Movement: My☆").

### ID3 tags
[mutagen](http://mutagen.readthedocs.org/) is used for ID3 field manipulation. The following fields are set based on the folder and file names:
- Artist from the folder name, e.g., `VA` instead of getting it from the file name itself
- Title from the file name
- Album from the folder name
- Date from the folder ("year")
- Track number from the file name
- Total track from the folder contents
- Disc number from the folder structure
- Total disc count from the folder structure

Note that for `.mp3` files the track number and total track count are in one field concatenated with "/", same holds for disc number and total disc count.

For later the idea will be to set the Genre from a `.csv` or similar file based on artist/album.
