# coding: utf-8
import sys
import codecs
import locale
import os

import argparse
import re

import mutagen

# unicode magic
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

def check_naming(directory):
    udir = unicode(directory, 'utf-8')
    print 'Checking naming conventions recursively in directory', udir
    for subdir, dirs, files in os.walk(udir):
        if subdir != directory:
            if subdir.find('Multimedia') is not -1:
                continue
            print '\tChecking directory', subdir,
            if not files or not dirs or 'Multimedia' in dirs:
                result = check_dir_naming(subdir)
                if result != None:
                    print
                    print result
                else:
                    print '<= OK'
            for f in files:
                print '\t\tChecking file', f,
                result = check_file_naming(f, subdir)
                if result != None:
                    print
                    print result
                else:
                    print '<= OK'

ignore_upper = [
  # en
  u'a', u'an', u'and', u'at',
  u'by',
  u'feat.', u'for', u'from',
  u'in', u'into',
  u'of', u'on', u'or',
  u'than', u'the', u'to',
  u'with',
  # it, es, etc.
  u'di',
  u'e',
  u'y',
  # de, etc.
  u'für',
  u'von',
  # hu
  u'az',
  u'át',
  u'egy', u'el', u'ez',
  u'és',
  u'vagy',
]
name_regex = re.compile(u'.*')
correct_spacing_regex = re.compile(u'( ,)|( .)|[ ]{2}')

cd_regex = re.compile(u'CD[1-9]')
artist_regex = re.compile(u'(\w|[áéíóúäöüÁÉÍÓÚÄÖÜőűŐŰ])+')
type_regex = re.compile(
  u'((E|L|S)P)|(Compilation)|(Live)|(Remix)|(OST)|(Unofficial)'
)
year_regex = re.compile(u'0000|19[0-9]{2}|20[0-9]{2}')

def check_dir_naming(dir_name):
    last_part = dir_name.split(u'/')[-1]

    # It's a CD subdir
    if cd_regex.match(last_part) != None:
        return None
    
    parts = last_part.split(u' - ')
    if len(parts) != 3 and len(parts) != 4:
        return 'W Incorrectly named directory ' + last_part + ' <= Not correct number of parts'

    if artist_regex.match(parts[0]) == None:
        return 'W Incorrectly named directory ' + last_part + ' <= Incorrect artist naming'

    parts_type_declared = None
    if type_regex.match(parts[1]) != None:
        parts_type_declared = True
    elif year_regex.match(parts[1]) != None:
        parts_type_declared = False
    else:
        return 'W Incorrectly named directory ' + last_part + ' <= Second part is not type nor year'

    if parts_type_declared:
        if year_regex.match(parts[2]) == None:
            return 'W Incorrectly named directory ' + last_part + ' <= No year after type'
        if name_regex.match(parts[3]) == None:
            return 'W Incorrectly named directory ' + last_part + ' <= Incorrect album naming (with type)'
    else:
        if name_regex.match(parts[2]) == None:
            return 'W Incorrectly named directory ' + last_part + ' <= Incorrect album naming'
    
    artist_name = parts[0].split(u' ')
    if artist_name[0] != 'VA':
        if not artist_name[0][0].isupper() and not artist_name[0].isdigit():
            return 'W Incorrectly named directory ' + last_part + ' <= Incorrect capitalization for artist (must start with capital/number)'
        for s in artist_name:
            if not s[0].isupper() and not s[0].isdigit():
                if s not in ignore_upper:
                    return 'W Incorrectly named directory ' + last_part + ' <= Incorrect capitalization for artist'
                else:
                    return 'A Double-check capitalization for artist ' + last_part
    if correct_spacing_regex.match(parts[0]) != None:
        return 'W Incorrect spacing in artist name ' + last_part

    album_name = (parts[3] if parts_type_declared else parts[2]).split(u' ')
    if not album_name[0][0].isupper() and not album_name[0].isdigit():
        return 'W Incorrectly named directory ' + last_part + ' <= Incorrect capitalization for album (must start with capital/number)'
    for s in album_name:
        if not s[0].isupper() and not s[0].isdigit() and s[0] != '&':
            if s[0] == '(':
                if not s[1].isupper() and not s[1].isdigit():
                    return 'W Incorrectly named directory ' + last_part + ' <= Incorrect capitalization for album (word does not start uppercase/number)'
                elif len(s) > 2 and s[2].isupper():
                    return 'W Incorrectly named directory ' + last_part + ' <= Incorrect capitalization for album (word starts with double-capital)'
            elif s not in ignore_upper:
                return 'W Incorrectly named directory ' + last_part + ' <= Incorrect capitalization for album - word does not start uppercase/number'
            elif len(s) > 1 and s[1].isupper():
                return 'W Incorrectly named directory ' + last_part + ' <= Incorrect capitalization for album - word starts with double-capital'
            else:
                return 'A Double-check capitalization for album ' + last_part
            if s[0].isupper() and s in ignore_upper:
                return 'A Double-check capitalization for album ' + last_part
    if correct_spacing_regex.match(
      (parts[3] if parts_type_declared else parts[2])
    ) != None:
        return 'W Incorrect spacing in album name ' + last_part

    #TODO: check for FLAC/MP3@ tag

    return None

music_extension_regex = re.compile(u'(mp3)|(flac)')
aux_extension_regex = re.compile(u'(m3u)|(cue)|(log)')
numbering_regex = re.compile(u'([1-9]\.)?[0-9]{2}')

def check_file_naming(file_name, dir_name):
    extension = file_name.split(u'.')[-1]
    is_music = True
    if music_extension_regex.match(extension) == None:
        is_music = False
        if aux_extension_regex.match(extension) == None:
            return 'W Incorrect file extension ' + extension + ' for file ' + file_name

    if is_music:
        parts = file_name.split(u' - ', 3)
        parts[2] = parts[2].rsplit(u'\.', 1)[0]
        if numbering_regex.match(parts[0]) == None:
            return 'W Incorrect numbering ' + parts[0] + ' for file ' + file_name

        artist_name = dir_name.split(u'/')[-1]
        if cd_regex.match(artist_name) != None:
            artist_name = dir_name.split(u'/')[-2]
        artist_name = artist_name.split(u' - ')[0]
        if parts[1] != artist_name:
            if artist_name != u'VA':
                return 'W Incorrect artist name ' + parts[1] + ' for file ' + file_name
            else:
                return 'A Double-check artist name ' + parts[1] + ' for file ' + file_name
        if name_regex.match(parts[2]) == None:
            return 'W Incorrect song name ' + parts[2] + ' for file ' + file_name

        song_name = parts[2].split(u' ')
        if not song_name[0][0].isupper() and not song_name[0].isdigit():
            return 'W Incorrectly named song ' + parts[2] + ' <= Incorrect capitalization (must start with capital/number)'
        for s in song_name:
            if not s[0].isupper() and not s[0].isdigit() and s[0] != '&':
                if s[0] == '(':
                    if not s[1].isupper() and not s[1].isdigit():
                        return 'W Incorrectly named song ' + parts[2] + ' <= Incorrect capitalization (word does not start with capital/number)'
                    elif len(s) > 2 and s[2].isupper():
                        return 'W Incorrectly named song ' + parts[2] + ' <= Incorrect capitalization (word starts with double-capital)'
                elif s not in ignore_upper:
                    return 'W Incorrectly named song ' + parts[2] + ' <= Incorrect capitalization - word does not start with capital/number'
                elif len(s) > 1 and s[1].isupper():
                    return 'W Incorrectly named song ' + parts[2] + ' <= Incorrect capitalization - word starts with double-capital'
                else:
                    return 'A Double-check capitalization for song ' + parts[2]
            if s[0].isupper() and s in ignore_upper:
                return 'A Double-check capitalization for song ' + parts[2]
        if correct_spacing_regex.match(parts[2]) != None:
            return 'W Incorrect spacing in song name ' + parts[2]

        if parts[2].endswith(u'\.'):
            return 'A Song name ends with "."' + parts[2]

    else:
        #TODO: non-music file name checking
        pass

    return None

if __name__ == "__main__":
    check_naming(sys.argv[1])

