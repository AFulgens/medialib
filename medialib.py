# coding: utf-8
import sys
import codecs
import locale
import os

import argparse
import re

from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
# print EasyID3.valid_keys.keys()

# unicode magic
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

### GLOBALS ###
# Ignore words for capitalization checks
ignore_upper = [
  # en
  u'a', u'an', u'and', u'at',
  u'by',
  u'feat.', u'for', u'from',
  u'in', u'into',
  u'of', u'on', u'or'
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
# Regular expressions
name_regex = re.compile(u'.*') #TODO: something more clever?
correct_spacing_regex = \
  re.compile(u'( ,)|( .)|[ ]{2}') # No double-spaces
                                  # No space before ',' or '.'

cd_regex = re.compile(u'CD[1-9]') # CD1, CD2, ..., CD9
artist_regex = \
  re.compile(u'(\w|[áéíóúäöüÁÉÍÓÚÄÖÜőűŐŰ])+') # Maybe additional characters
                                              # would be needed
type_regex = re.compile(
  u'((E|L|S)P)|(Compilation)|(Live)|(Remix)|(OST)|(Unofficial)'
) # EP, LP, SP, ...
year_regex = \
  re.compile(u'0000|19[0-9]{2}|20[0-9]{2}') # 0000 == unknown
                                            # 19xx-20xx

music_extension_regex = re.compile(u'(mp3)|(flac)')
aux_extension_regex = re.compile(u'(m3u)|(cue)|(log)')
numbering_regex = \
  re.compile(u'([1-9]\.)?[0-9]{2}') # stricly two digit (i.e., 01, 02, ..., 99)
                                    # possibility to note CDs with n.01, etc.

# Delimiters
delim = {
  'dir_path':u'/',
  'parts':u' - ',
  'ext':u'.',
  'words':u' ',
}

# Messages
msg = {
  'check':u'Checking naming conventions recursively in directory',
  'check_dir':u'\tChecking directory',
  'check_file':u'\t\tChecking file',
  'ok':u'<= OK',
  'w_dir':u'W Incorrectly named directory ',
  'w_dir_parts':u' <= Not correct number of parts',
  'w_dir_artist':u' <= Incorrect artist naming',
  'w_dir_second':u' <= Second part is not type nor year',
  'w_dir_no_year_after_type':u' <= No year after type',
  'w_dir_name':u' <= Incorrect album naming',
  'w_spacing':u' <= Incorrect spacing',
  'w_caps_start':u' <= Incorrect capitalization' + \
    ' (must start with uppercase/number)',
  'w_caps':u' <= Incorrect capitalization',
  'w_&':u' <= Standalone character must be "a", "&", "I" or digit',
  'a_caps':u'A Double-check capitalization for ',
  'w_file_ext':u'W Incorrect file extension ',
  'ff':u' for file ',
  'w_file_numbering':u'W Incorrect numbering ',
  'w_file_artist':u'W Incorrect artist name ',
  'a_file_artist':u'A Double-check artist name ',
  'w_file_name':u'W Incorrect song name ',
  'w_file_ends_dot':u'A Song name ends with "."',
  'w_file_spacing':u'W Incorrect spacing for file ',

  'delete':u'Deleting ID3 tags recursively in directory',
  'delete_dir':u'\tDeleting ID3 tags in directory',
  'delete_file':u'\t\tDeleting ID3 tags in file',
  'update':u'Updating ID3 tags recursively in directory',
  'update_dir':u'\tUpdating ID3 tags in directory',
  'update_file':u'\t\tUpdating ID3 tags in file',
}

### FUNCTIONS ###


def check_naming(directory):
    udir = unicode(directory, 'utf-8')
    print msg['check'], udir
    for subdir, dirs, files in os.walk(udir):
        if subdir != directory:
            if subdir.find('Multimedia') is not -1: # skipping Multimedia dirs
                continue
            print msg['check_dir'], subdir,
            if not files or not dirs or 'Multimedia' in dirs:
                # this conditions seems OK this far, revisit if need be
                result = check_dir_naming(subdir)
                if result != None:
                    print
                    print result
                else:
                    print msg['ok']
            for f in files:
                print msg['check_file'], f,
                result = check_file_naming(f, subdir)
                if result != None:
                    print
                    print result
                else:
                    print msg['ok']


def delete_id3(directory):
    udir = unicode(directory, 'utf-8')
    print msg['delete'], udir
    for subdir, dirs, files in os.walk(udir):
        if subdir != directory:
            if subdir.find('Multimedia') is not -1: # skipping Multimedia dirs
                continue
            print msg['delete_dir'], subdir
            for f in files:
                print msg['delete_file'], f
                extension = f.split(delim['ext'])[-1]
                if extension == 'mp3':
                    id3 = MP3(os.path.join(subdir, f))
                    id3.delete()
                    id3.save()
                elif extension == 'flac':
                    id3 = FLAC(os.path.join(subdir, f))
                    id3.delete()
                    id3.save()


def update_id3(directory):
    #TODO: Genre is omitted
    udir = unicode(directory, 'utf-8')
    print msg['update'], udir
    for subdir, dirs, files in os.walk(udir):
        if subdir != directory:
            if subdir.find('Multimedia') is not -1: # skipping Multimedia dirs
                continue
            print msg['update_dir'], subdir
            if not dirs:
                total_tracks = sorted(
                  [f for f in os.listdir(subdir) 
                    if os.path.isfile(os.path.join(subdir, f))
                    and music_extension_regex.match(f.split(delim['ext'])[-1]) \
                      != None])[-1][:2]
                if total_tracks[1] == '.':
                    total_tracks = sorted(
                      [f for f in os.listdir(subdir) 
                        if os.path.isfile(os.path.join(subdir, f))
                        and music_extension_regex.match(
                          f.split(delim['ext'])[-1]
                        ) \
                          != None])[-1][2:4]
                    
                for f in files:
                    print msg['update_file'], f
                    extension = f.split(delim['ext'])[-1]
                    if music_extension_regex.match(extension) == None:
                        continue
                    track_number = f.split(delim['parts'])[0]
                    track_title  = \
                      f.split(delim['parts'])[2].rsplit(delim['ext'], 1)[0]

                    if cd_regex.match(subdir.split(delim['dir_path'])[-1] \
                      .split(delim['parts'])[-1]) == None:
                        artist_name  = \
                          subdir.split(delim['dir_path'])[-1] \
                            .split(delim['parts'])[0]
                        album_title  = \
                          subdir.split(delim['dir_path'])[-1] \
                            .split(delim['parts'])[-1]
                        year  = \
                          subdir.split(delim['dir_path'])[-1] \
                            .split(delim['parts'])[-2]
                        disc_number = 1
                        total_discs = 1
                    else:
                        artist_name  = \
                          subdir.split(delim['dir_path'])[-2] \
                            .split(delim['parts'])[0]
                        album_title  = \
                          subdir.split(delim['dir_path'])[-2] \
                            .split(delim['parts'])[-1]
                        year  = \
                          subdir.split(delim['dir_path'])[-2] \
                            .split(delim['parts'])[-2]
                        disc_number = subdir.split(delim['dir_path'])[-1][-1]

                    if extension == 'mp3':
                        id3 = MP3(os.path.join(subdir, f), ID3=EasyID3)
                        id3['tracknumber'] = \
                          str(track_number) + '/' + str(total_tracks)
                        id3['discnumber'] = \
                          str(disc_number) + '/' + str(total_discs)
                    elif extension == 'flac':
                        id3 = FLAC(os.path.join(subdir, f))
                        id3['tracknumber'] = str(track_number)
                        id3['tracktotal'] = str(total_tracks)
                        id3['discnumber'] = str(disc_number)
                        id3['disctotal'] = str(total_discs)
                    id3['artist'] = artist_name
                    id3['title'] = track_title
                    id3['album'] = album_title
                    id3['date'] = year
                    id3.save()
            else:
                total_discs = sorted(
                  [f for f in os.listdir(subdir)
                    if os.path.isdir(os.path.join(subdir, f))])[-1][2]


def check_capitalization(string, message, va = False):
    parts = string.split(delim['words'])
    if parts[0] == u'VA':
        return None

    start = 0
    if not (parts[start][0].isupper() or parts[start][0].isdigit()):
        return message + string + msg['w_caps_start']
    start += 1

    for i in range(start, len(parts)):
        w = parts[i]
        if len(w) == 1 and w != 'a' and w != '&' and w!= 'I' \
          and not w.isdigit():
            return message + string + msg['w_&']
        if len(w) == 1: return

        # Exactly one upper-case letter or all-number
        if sum(1 for c in w if c.isupper()) != 1:
            if w not in ignore_upper \
              and (sum(1 for c in w if c.isdigit()) != len(w)):
                return message + string + msg['w_caps'] + '/1'
        
        if not (w[0].isupper() or w[0].isdigit()):
            if w[0] == '(':
                if not w[1].isupper() and not w[1].isdigit() and w != '(feat.':
                    return message + string + msg['w_caps'] + '/2'
            elif w not in ignore_upper:
                return message + string + msg['w_caps'] + '/3'
            else:
                return msg['a_caps'] + string + '/1'
        if w[0].isupper() and w in ignore_upper:
            return msg['a_caps'] + string + '/2'
    return None


def check_dir_naming(dir_name):
    last_part = dir_name.split(delim['dir_path'])[-1]

    # It's a CD subdir
    if cd_regex.match(last_part) != None:
        return None
    
    # Checking spacing
    if correct_spacing_regex.match(last_part) != None:
        return msg['w_dir'] + last_part + msg['w_spacing']

    # Checking parts according to:
    #   {artist} [- {type}] - {year} - {album name} - {FLAC|MP3@{bitrate}}
    parts = last_part.split(delim['parts'])
    if len(parts) != 3 and len(parts) != 4:
        return msg['w_dir'] + last_part + msg['w_dir_parts']

    index = 0
    if artist_regex.match(parts[index]) == None:
        return msg['w_dir'] + last_part + msg['w_dir_artist']
    index += 1

    parts_type_declared = None
    if type_regex.match(parts[index]) != None:
        parts_type_declared = True
    elif year_regex.match(parts[index]) != None:
        parts_type_declared = False
    else:
        return msg['w_dir'] + last_part + msg['w_dir_second']
    index += 1
    
    if parts_type_declared:
        if year_regex.match(parts[index]) == None:
            return msg['w_dir'] + last_part + msg['w_dir_no_year_after_type']
        index += 1

    if name_regex.match(parts[index]) == None:
        return msg['w_dir'] + last_part + msg['w_dir_name']
    
    result = check_capitalization(parts[0], msg['w_dir'], va = True)
    if result != None:
        return result

    result = check_capitalization(parts[index], msg['w_dir'], va = True)
    if result != None:
        return result

    #TODO: check for FLAC/MP3@ tag

    return None


def check_file_naming(file_name, dir_name):
    extension = file_name.split(delim['ext'])[-1]

    # Checking spacing
    if correct_spacing_regex.match(file_name) != None:
        return msg['w_file_spacing'] + file_name

    is_music = True
    if music_extension_regex.match(extension) == None:
        is_music = False
        if aux_extension_regex.match(extension) == None:
            return msg['w_file_ext'] + extension + msg['ff'] + file_name

    if is_music:
        # Getting file name without extension
        parts = file_name.split(delim['parts'], 3)
        parts[2] = parts[2].rsplit(delim['ext'], 1)[0]

        if parts[2].endswith(u'.'):
            return msg['w_file_ends_dot'] + parts[2] + msg['ff'] + file_name

        # Checking file name according to:
        #  {title number} - {artist name} - {song title}
        if numbering_regex.match(parts[0]) == None:
            return msg['w_file_numbering'] + parts[0] + msg['ff'] + file_name

        # Get artist's name from dir
        artist_name = dir_name.split(delim['dir_path'])[-1]
        if cd_regex.match(artist_name) != None:
            artist_name = dir_name.split(delim['dir_path'])[-2]
        artist_name = artist_name.split(delim['parts'])[0]

        if parts[1] != artist_name:
            if artist_name != u'VA':
                return msg['w_file_artist'] + parts[1] + msg['ff'] + file_name
            else:
                return msg['a_file_artist'] + parts[1] + msg['ff'] + file_name

        if name_regex.match(parts[2]) == None:
            return msg['w_file_name'] + parts[2] + msg['ff'] + file_name

        result = check_capitalization(parts[2], msg['w_file_name'])
        if result != None:
            return result

    else:
        #TODO: non-music file name checking
        pass

    return None

if __name__ == "__main__":
    if sys.argv[2] == '1':
        check_naming(sys.argv[1])
    if sys.argv[3] == '1':
        delete_id3(sys.argv[1])
    if sys.argv[4] == '1':
        update_id3(sys.argv[1])

