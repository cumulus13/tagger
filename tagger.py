
#encoding:UTF-8

from __future__ import print_function
import os, sys, argparse, platform
import cmdw
from PIL import Image
from make_colors import make_colors
if sys.version_info.major < 3:
    print (make_colors("Version python 3 suppoer Only!", 'lw', 'lr', attrs = ['blink', 'bold']))
from safeprint import print as sprint
try:
    from pause import pause
except:
    pass
if sys.version_info.major == 2:
    input = raw_input
from configset import configset
def debugx(*args, **kwargs):
    return None
try:
    from pydebugger.debug import debug
except:
    debug = debugx
import clipboard
import re
import traceback
if __name__ == '__main__':
    import mimelist
else:
    from . import mimelist
from mutagen import id3
from mutagen.id3 import ID3, PictureType
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from datetime import datetime

class Tagger(object):
    NOW = datetime.now()
    THIS_YEAR = NOW.year
    
    def __init__(self, files = None, dirs = None):
        super(Tagger, self)
        self.files = files
        self.dirs = dirs
        self.all_artist = []
        self.all_albumartist = []
        self.all_album = []
        self.all_original_artist = []
        self.files_passed = []
        self.len_tracks = None
    
    def format_track(self, track, numbers, change = False):
        if self.len_tracks:
            numbers = self.len_tracks
        if len(str(numbers)) == 1:
            numbers = "0" + str(numbers)
        if not "/" in track:
            if len(str(track)) == 1:
                track = "0" + str(track)
            return track + "/" + str(numbers)
        else:
            fr, to = track.split("/")
            debug(fr = fr)
            debug(to = to)
            if len(str(fr)) == 1:
                fr = "0" + str(fr)
            if len(str(to)) == 1:
                to = "0" + str(to)
            if change:
                return fr + "/" + str(numbers)
            return fr + "/" + str(to)
        return track
    
    def usage(self):
        parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter)
        parser.add_argument('PATH', help = 'file or directory contain music files', action = 'store', nargs = '*')
        parser.add_argument('-t', '--title', help = 'set Title or load from text file or take from file name just type "file"', action = 'store', nargs = '*')
        parser.add_argument('-tt', '--track', help = 'set Track', action = 'store', nargs = '*')
        parser.add_argument('-ltt', '--len-tracks', help = 'set Track', action = 'store')
        parser.add_argument('-ct', '--change-track', help = 'keep change Track', action = 'store_true')
        parser.add_argument('-a', '--artist', help = 'set Artist', action = 'store')
        parser.add_argument('-sa', '--artist-solo', help = 'set Solo Artist', action = 'store')
        parser.add_argument('-aa', '--album', help = 'set Album', action = 'store')
        parser.add_argument('-aaa', '--album-artist', help = 'set Album Artist', action = 'store')
        parser.add_argument('-d', '--disc', help = 'set Disc Number', action = 'store')
        parser.add_argument('-c', '--composer', help = 'set Composer', action = 'store')
        parser.add_argument('-o', '--original-artist', help = 'set Original Artist', action = 'store')
        parser.add_argument('-cc', '--comment', help = 'set Comment', action = 'store')
        parser.add_argument('-i', '--isrc', help = 'set ISRC Number', action = 'store')
        parser.add_argument('-b', '--barcode', help = 'set Barcode Number', action = 'store')
        parser.add_argument('-g', '--genre', help = 'set Genres', action = 'store')
        parser.add_argument('-dd', '--date', help = 'set Date/Year', action = 'store')
        parser.add_argument('-bb', '--bpm', help = 'set BPM Number', action = 'store')
        parser.add_argument('-ccc', '--copyright', help = 'set Copyright', action = 'store')
        parser.add_argument('-e', '--encodedby', help = 'set Encoded By', action = 'store')
        parser.add_argument('-k', '--key', help = 'set Key', action = 'store')
        parser.add_argument('-l', '--lyric', help = 'set Lyric or set load from txt file', action = 'store')
        parser.add_argument('-ln', '--lyric-name', help = 'set Lyric Name', action = 'store')
        parser.add_argument('-r', '--remix', help = 'set Remix', action = 'store')
        parser.add_argument('-s', '--subtitle', help = 'set Subtitle', action = 'store')
        parser.add_argument('-u', '--url', help = 'set Url', action = 'store')
        parser.add_argument('-gg', '--group', help = 'set Group', action = 'store')
        parser.add_argument('-p', '--publisher', help = 'set Publisher', action = 'store')
        parser.add_argument('-ll', '--length', help = 'set Lenght', action = 'store')
        parser.add_argument('-cd', '--comment-desc', help = 'set Comment Description', action = 'store')
        parser.add_argument('-C', '--cover', help = 'set Cover from image path', action = 'store')
        parser.add_argument('-Cn', '--cover-name', help = 'set Cover name text', action = 'store')
        parser.add_argument('-gt', '--get-title', help = 'Get titles', action = 'store_true')
        parser.add_argument('-T', '--test', action = 'store_true', help = 'Test only')
        parser.add_argument('-R', '--rename', action = 'store', help = 'rename by "file": just type "file" or "title"')
        parser.add_argument('-RP', '--rename-pattern', action = 'store', help = 'rename pattern, example:- | " ", one by one')
        parser.add_argument('-I', '--info', action = 'store_true', help = 'Get Infos')
        parser.add_argument('-A', '--licface', action = 'store', help = 'Set All by LICFACE type "1" or "2" ')
        parser.add_argument('-SA', '--help-licface', action = 'store_true', help = 'show valid licface set number')
        parser.add_argument('-ec', '--extract-cover', action = 'store_true', help = 'Extract cover to file')
        if len(sys.argv) == 1:
            parser.print_help()
        else:
            args = parser.parse_args()
            
            if args.help_licface:
                self.print_licface()
                sys.exit()
            if args.disc and len(args.disc) == 1:
                args.disc = self.format_track(args.disc, int(args.disc))
            if args.len_tracks:
                self.len_tracks = args.len_tracks

            lyric_text = ''
            if args.lyric and os.path.isfile(args.lyric):
                with open(args.lyric, 'rb') as lr:
                    lyric_text = lr.read()
                args.lyric = lyric_text
                    
            all_files = []
            all_dirs = []
            all_title = []
            all_tracks = []
            titles = []
            if len(args.PATH) == 1 and os.path.isdir(args.PATH[0]):
                #for root, dirs, files in os.walk(args.PATH[0]):
                files = os.listdir(args.PATH[0])
                for i in files:
                    #if os.path.join(root, i) and str(i).lower().endswith('.mp3'):
                    if str(i).lower().endswith('.mp3'):
                        all_files.append(os.path.join(args.PATH[0], i))
                        #all_files.append(os.path.join(root, i))
                
            else:
                for i in args.PATH:
                    i = os.path.abspath(i)
                    debug(i = i)
                    debug(i_is_file = os.path.isfile(os.path.abspath(i)))
                    if len(args.PATH) == 1 and not os.path.isfile(os.path.abspath(i)):
                        print('"' + make_colors(os.path.abspath(i), 'lw', 'lr') + '" ' + make_colors("Not a File !", 'b', 'ly'))
                    if os.path.isfile(i):
                        all_files.append(i)
                    elif os.path.isdir(i):
                        all_dirs.append(i)
            debug(all_files = all_files)
            if args.title and os.path.isfile(args.title[0]):
                with open(args.title[0], 'rb') as t:
                    titles = t.readlines()
            else:
                if args.title == 'file' and len(all_files) > 0:
                    for i in all_files:
                        mt = ID3(i)
                        try:
                            _title = mt['TIT2'].text
                        except:
                            _title = ''
                        all_title.append(_title)
                elif not titles and len(all_files) > 0 and not args.title:
                    for i in all_files:
                        mt = ID3(i)
                        try:
                            _title = mt['TIT2'].text
                        except:
                            _title = ''
                        all_title.append(_title)
                elif args.title and len(all_files) == len(args.title):
                    titles = args.title
                else:
                    titles = args.title
                
            debug(titles = titles)
            debug(args_track = args.track)
            debug(all_files = all_files)
            if titles and len(titles) == len(all_files):
                for i in titles:
                    if isinstance(i, bytes):
                        i = i.decode('utf-8')
                    
                    check_track = re.findall("(\d+)\. ", i)
                    if check_track:
                        all_tracks.append(check_track[0])
                        title = re.findall("\d+\. (.*?)$", i)
                        title = re.sub("\.mp3", '', title[0], re.I)
                        title = re.sub("\r\n", '', title, re.I)
                        all_title.append(title.title())
                    else:
                        title = re.sub("\.mp3", '', i.split("\n")[0], re.I)
                        all_title.append(title)
            elif args.track and len(args.track) == len(all_files):
                for i in args.track:
                    all_tracks.append(self.format_track(i, len(all_files)))
            else:
                if titles:
                    print(make_colors("title not same with files !", 'lw', 'lr', ['blink']))
                    sys.exit()
            
            if args.extract_cover:
                end = False
                for i in all_files:
                    tag = ID3(i)
                    for k in list(tag.keys()):
                        if "APIC:" in k:
                            self.Extract_cover(i)
                            end = True
                            break
                    if end:
                        break
                if len(sys.argv[1:]) == 2 and '-ec' in sys.argv[1:]:
                    sys.exit()
            
            if args.get_title and all_files:
                for i in all_files:
                    if os.path.isfile(i):
                        m = ID3(i)
                        print(
                            make_colors(m['TRCK'], 'lc') + ". " +\
                            make_colors(m['TIT2'], 'lc')
                        )
                    else:
                        print(make_colors("Invalid File !", 'lw', 'lr'))
                sys.exit()
            elif args.info:
                for i in all_files:
                    if os.path.isfile(i):
                        self.Get(i)
                sys.exit()

            self.files = all_files
            self.dirs = all_dirs
            debug(all_title = all_title)
            debug(all_tracks = all_tracks)
            debug(all_files = all_files)
            
            for i in all_files:
                m = ID3(i)
                c_artist = ''
                c_album = ''
                c_album_artist = ''
                c_original_artist = ''
                
                try:
                    c_artist = m['TPE1'].text[0]
                except:
                    pass
                self.all_artist.append(c_artist)
                try:
                    c_album = m['TALB'].text[0]
                except:
                    pass
                self.all_album.append(c_album)
                try:
                    c_album_artist = m['TPE2'].text[0]
                except:
                    pass
                self.all_albumartist.append(c_album_artist)
                try:
                    c_original_artist = m['TOPE'].text[0]
                except:
                    pass
                self.all_original_artist.append(c_original_artist)
            
            #debug(self_all_artist = self.all_artist)
            #debug(self_all_album = self.all_album)
            #debug(self_all_albumartist = self.all_albumartist)
            #debug(self_all_original_artist = self.all_original_artist)
            #sys.exit(0)
            c_all_artist = list(set(self.all_artist))
            c_all_album = list(set(self.all_album))
            c_all_album_artist = list(set(self.all_albumartist))
            c_all_original_artist = list(set(self.all_original_artist))
            
            debug(c_all_artist = c_all_artist)
            debug(c_all_album = c_all_artist)
            debug(c_all_album_artist = c_all_artist)
            debug(c_all_original_artist = c_all_artist)
            
            if len(c_all_artist) > 1:
                print(make_colors(", ".join(c_all_artist), 'b', 'ly'))
                print(make_colors("There more than 1 ", 'lw', 'm') + make_colors("ARTIST", 'lw', 'lr') + make_colors(" Detected !", 'lc'))
            if len(c_all_album) > 1:
                print(make_colors(", ".join(c_all_album), 'b', 'ly'))
                print(make_colors("There more than 1 ", 'lw', 'm') + make_colors("ALBUM", 'lw', 'lr') + make_colors(" Detected !", 'lc'))
            if len(c_all_album_artist) > 1:
                print(make_colors(", ".join(c_all_album_artist), 'b', 'ly'))
                print(make_colors("There more than 1 ", 'lw', 'm') + make_colors("ALBUM ARTIST", 'lw', 'lr') + make_colors(" Detected !", 'lc'))
            if len(c_all_original_artist) > 1:
                print(make_colors(", ".join(c_all_original_artist), 'b', 'ly'))
                print(make_colors("There more than 1 ", 'lw', 'm') + make_colors("ORIGINAL ARTIST", 'lw', 'lr') + make_colors(" Detected !", 'lc'))
            if len(c_all_artist) > 1 or len(c_all_album) > 1 or len(c_all_album_artist) > 1 or len(c_all_original_artist) > 1:
                qc = input(make_colors("Enter to Continue ... [q|x = Quit|Exit]", 'lw', 'lr'))
                if qc and qc.strip() == 'q' or qc.strip() == 'x':
                    sys.exit()
            if len(all_title) == len(all_files):
                for i in all_files:
                    if args.licface == '0':
                        if not args.artist:
                            m = ID3(i)
                            args.artist = m['TPE1'].text
                        args.original_artist = args.artist
                        args.group = args.artist
                        args.comment = "LICFACE (licface@yahoo.com)"
                        if not args.copyright:
                            args.copyright = str(self.THIS_YEAR)
                        if not args.date:
                            args.date = str(self.THIS_YEAR)
                        args.encodedby = 'BLACKID'
                        if not args.disc:
                            args.disc = "01/01"
                    elif args.licface == '1':
                        if not args.artist:
                            m = ID3(i)
                            args.artist = m['TPE1'].text
                        args.comment = "LICFACE (licface@yahoo.com)"
                        if not args.copyright:
                            args.copyright = str(self.THIS_YEAR)
                        if not args.date:
                            args.date = str(self.THIS_YEAR)
                        args.encodedby = 'BLACKID'
                        args.publisher = "LICFACE"
                        if not args.disc:
                            args.disc = "01/01"
                    elif args.licface == '2':
                        if not args.artist:
                            m = ID3(i)
                            args.artist = m['TPE1'].text                        
                        args.comment = "LICFACE (licface@yahoo.com)"
                        if not args.copyright:
                            args.copyright = str(self.THIS_YEAR)
                        if not args.date:
                            args.date = str(self.THIS_YEAR)
                        args.encodedby = 'BLACKID'
                        args.publisher = "LICFACE"
                        args.album_artist = args.artist
                        args.original_artist = args.artist
                        args.group = args.artist
                        args.composer = args.artist
                        args.url = 'licface@yahoo.com'
                        if not args.disc:
                            args.disc = "01/01"
                    elif args.licface == '3':
                        if not args.artist:
                            m = ID3(i)
                            args.artist = m['TPE1'].text                        
                        args.comment = "LICFACE (licface@yahoo.com)"
                        if not args.copyright:
                            args.copyright = str(self.THIS_YEAR)
                        args.encodedby = 'BLACKID'
                        args.publisher = "LICFACE"
                        args.album_artist = args.artist
                        args.original_artist = args.artist
                        args.group = args.artist
                        args.composer = args.artist
                        args.url = 'licface@yahoo.com'
                        args.isrc = ''
                        if not args.disc:
                            args.disc = "01/01"
                            
                    if len(all_tracks) == len(all_title):
                        track = self.format_track(all_tracks[all_files.index(i)], len(all_files), args.change_track)
                        
                        self.Set(i, all_title[all_files.index(i)], track, args.disc, args.album, args.artist, args.album_artist, args.original_artist, args.composer, args.comment, args.isrc, args.barcode, args.genre, args.date, args.bpm, args.copyright, args.encodedby, args.key, args.lyric, args.lyric_name, args.remix, args.subtitle, args.url, args.group, args.publisher, args.length, args.comment_desc, args.cover_name, args.cover, args.artist_solo, args.test)
                        
                        if args.rename == 'title':
                            print(make_colors("RENAME", 'lw', 'lr') + ": " + make_colors(os.path.dirname(i), 'ly') + "\\" + make_colors(os.path.basename(
                                i), 'lw', 'lr') + " " + make_colors("-->", 'lg') + " " + make_colors(str(track).split("/")[0] + ". " + str(all_title[all_files.index(i)]) + ".mp3", 'lw', 'bl'))
                            if not args.test:
                                os.rename(i, str(track).split("/")[0] + ". " + str(all_title[all_files.index(i)]) + ".mp3")
                        elif args.rename == 'file':
                            if args.rename_pattern:
                                if args.rename_pattern == '-':
                                    title = re.findall("\d+.*?-.*?(.*?)$", i)
                            else:
                                title = re.findall("\d+\. (.*?)$", i)
                            
                            if args.rename_pattern:
                                if args.rename_pattern == '-':
                                    track =  re.findall(".*?(\d+).*?-.*?", i)
                            else:
                                track =  re.findall(".*?(\d+\. )", i)
                            if track:
                                track = track[0].strip()
                            if len(track) == 1:
                                track = "0" + track
                            
                            title = re.sub("\.mp3", '', title[0], re.I)
                            title = re.sub("\r\n", '', title, re.I)
                            if title:
                                title = title.strip()                            
                            print(make_colors("RENAME", 'lw', 'lr') + ": " + make_colors(os.path.dirname(i), 'ly') + "\\" + make_colors(os.path.basename(
                                i), 'lw', 'lr') + " " + make_colors("-->", 'lg') + " " + make_colors(str(track).split("/")[0] + ". " + str(title) + ".mp3", 'lw', 'bl'))
                            if not args.test:
                                os.rename(i, str(track).split("/")[0] + ". " + str(title) + ".mp3")
                    else:
                        m = ID3(i)
                        debug(m = m)
                        debug(TRCK =  m['TRCK'])
                        if not m.get('TRCK'):
                            pass
                        track = m['TRCK'].text[0]
                        debug(track = track)
                        debug(len_all_files = len(all_files))
                        debug(args_change_track = args.change_track)
                        track = self.format_track(track, len(all_files), args.change_track)
                        if not track:
                            print(make_colors("No valid Tracks !", 'lw', 'lr', ['blink']))
                            sys.exit()
                        self.Set(i, all_title[all_files.index(i)], track, args.disc, args.album, args.artist, args.album_artist, args.original_artist, args.composer, args.comment, args.isrc, args.barcode, args.genre, args.date, args.bpm, args.copyright, args.encodedby, args.key, args.lyric, args.lyric_name, args.remix, args.subtitle, args.url, args.group, args.publisher, args.length, args.comment_desc, args.cover_name, args.cover, args.artist_solo, args.test)
                        
                        if args.rename == 'title':
                            print(make_colors("RENAME", 'lw', 'lr') + ": " + make_colors(os.path.dirname(i), 'ly') + "\\" + make_colors(os.path.basename(
                                i), 'lw', 'lr') + " " + make_colors("-->", 'lg') + " " + make_colors(str(track).split("/")[0] + ". " + str(all_title[all_files.index(i)][0]) + ".mp3", 'lw', 'bl'))
                            if not args.test:
                                os.rename(i, str(track).split("/")[0] + ". " + str(all_title[all_files.index(i)][0]) + ".mp3")
                        elif args.rename == 'file':
                            if args.rename_pattern:
                                if args.rename_pattern == '-':
                                    title = re.findall("\d+.*?-.*?(.*?)$", i)
                            else:
                                title = re.findall("\d+\. (.*?)$", i)
                            
                            
                            if args.rename_pattern:
                                if args.rename_pattern == '-':
                                    track =  re.findall(".*?(\d+).*?-.*?", i)
                            else:
                                track =  re.findall(".*?(\d+\. )", i)
                            if track:
                                track = track[0].strip()
                            if len(track) == 1:
                                track = "0" + track
                            
                            title = re.sub("\.mp3", '', title[0], re.I)
                            title = re.sub("\r\n", '', title, re.I)
                            if title:
                                title = title.strip()                            
                            print(make_colors("RENAME", 'lw', 'lr') + ": " + make_colors(os.path.dirname(i), 'ly') + "\\" + make_colors(os.path.basename(
                                i), 'lw', 'lr') + " " + make_colors("-->", 'lg') + " " + make_colors(str(track).split("/")[0] + ". " + str(title) + ".mp3", 'lw', 'bl'))
                            if not args.test:
                                os.rename(i, str(track).split("/")[0] + ". " + str(title) + ".mp3")                                                
                    sys.stdout.write(cmdw.getWidth() * "-" + "\n")
                print("\n")
            else:
                for i in all_files:
                    m = ID3(i)
                    track = m['TRCK'].text[0]
                    track = self.format_track(track, len(all_files), change=args.change_track)
                    debug(track = track)
                    
                    title = m['TIT2'].text
                    debug(title = title)
                    if not track:
                        print(make_colors("No valid Tracks !", 'lw', 'lr', ['blink']))
                        sys.exit()
                    self.Set(i, title, track, args.disc, args.album, args.artist, args.album_artist, args.original_artist, args.composer, args.comment, args.isrc, args.barcode, args.genre, args.date, args.bpm, args.copyright, args.encodedby, args.key, args.lyric, args.lyric_name, args.remix, args.subtitle, args.url, args.group, args.publisher, args.length, args.comment_desc, args.cover_name, args.cover, args.artist_solo, args.test)
                    if args.rename == 'title':
                        print(make_colors("RENAME", 'lw', 'lr') + ": " + make_colors(os.path.dirname(i), 'ly') + "\\" + make_colors(os.path.basename(
                            i), 'lw', 'lr') + " " + make_colors("-->", 'lg') + " " + make_colors(str(track).split("/")[0] + ". " + str(title) + ".mp3", 'lw', 'bl'))
                        if not args.test:
                            os.rename(i, str(track).split("/")[0] + ". " + str(title) + ".mp3")
                    elif args.rename == 'file':
                        if args.rename_pattern:
                            if args.rename_pattern == '-':
                                title = re.findall("\d+.*?-.*?(.*?)$", i)
                            else:
                                title = re.findall("\d+\. (.*?)$", i)
                            
                            
                            if args.rename_pattern:
                                if args.rename_pattern == '-':
                                    track =  re.findall(".*?(\d+).*?-.*?", i)
                            else:
                                track =  re.findall(".*?(\d+\. )", i)
                            if track:
                                track = track[0].strip()
                            if len(track) == 1:
                                track = "0" + track
                            
                            title = re.sub("\.mp3", '', title[0], re.I)
                            title = re.sub("\r\n", '', title, re.I)
                            if title:
                                title = title.strip()                            
                            print(make_colors("RENAME", 'lw', 'lr') + ": " + make_colors(os.path.dirname(i), 'ly') + "\\" + make_colors(os.path.basename(
                                i), 'lw', 'lr') + " " + make_colors("-->", 'lg') + " " + make_colors(str(track).split("/")[0] + ". " + str(title) + ".mp3", 'lw', 'bl'))
                            if not args.test:
                                os.rename(i, str(track).split("/")[0] + ". " + str(title) + ".mp3")                                                
                        
                    sys.stdout.write(cmdw.getWidth() * "-" + "\n")
                print("\n")
    def print_licface(self):
        from prettytable import PrettyTable
        head = [make_colors("     TAG     ", 'lw', 'm'), make_colors("   0   ", 'b', 'ly'), make_colors("   1   ", 'b', 'ly'), make_colors("   2   ", 'b', 'ly'), make_colors("   3   ", 'b', 'ly')]
        t = PrettyTable(head)
        t.add_row([make_colors("ARTIST", 'lw', 'bl'), make_colors("AUTO", 'lg'), make_colors("AUTO", 'lg'), make_colors("AUTO", 'lg'), make_colors("AUTO", 'lg')])
        t.add_row([make_colors("ALBUM_ARTIST", 'lw', 'bl'), make_colors("NO", 'lw', 'lr'), make_colors("NO", 'lw', 'lr'), make_colors("ARTIST", 'b', 'ly'), make_colors("ARTIST", 'b', 'ly')])
        t.add_row([make_colors("COMMENT", 'lw', 'bl'), make_colors("YES", 'lr', 'lw'), make_colors("YES", 'lr', 'lw'), make_colors("YES", 'lr', 'lw'), make_colors("YES", 'lr', 'lw')])
        t.add_row([make_colors("COMPOSER", 'lw', 'bl'), make_colors("NO", 'lw', 'lr'), make_colors("NO", 'lw', 'lr'), make_colors("ARTIST", 'b', 'ly'), make_colors("ARTIST", 'b', 'ly')])
        t.add_row([make_colors("COPYRIGHT", 'lw', 'bl'), make_colors("YES", 'lr', 'lw'), make_colors("YES", 'lr', 'lw'), make_colors("YES", 'lr', 'lw'), make_colors("YES", 'lr', 'lw')])
        t.add_row([make_colors("DATE", 'lw', 'bl'), make_colors("YES", 'lr', 'lw'), make_colors("YES", 'lr', 'lw'), make_colors("YES", 'lr', 'lw'), make_colors("NO", 'lw', 'r')])
        t.add_row([make_colors("DISC", 'lw', 'bl'), make_colors("AUTO", 'lg'), make_colors("AUTO", 'lg'), make_colors("AUTO", 'lg'), make_colors("AUTO", 'lg')])
        t.add_row([make_colors("ENCODEDBY", 'lw', 'bl'), make_colors("YES", 'lr', 'lw'), make_colors("YES", 'lr', 'lw'), make_colors("YES", 'lr', 'lw'), make_colors("YES", 'lr', 'lw')])
        t.add_row([make_colors("ORIGINAL_ARTIST", 'lw', 'bl'), make_colors("ARTIST", 'b', 'ly'), make_colors("NO", 'lw', 'lr'), make_colors("ARTIST", 'b', 'ly'), make_colors("ARTIST", 'b', 'ly')])
        t.add_row([make_colors("GROUP", 'lw', 'bl'), make_colors("ARTIST", 'b', 'ly'), make_colors("NO", 'lw', 'lr'), make_colors("ARTIST", 'b', 'ly'), make_colors("ARTIST", 'b', 'ly')])
        t.add_row([make_colors("PUBLISHER", 'lw', 'bl'), make_colors("NO", 'lw', 'lr'), make_colors("YES", 'lr', 'lw'), make_colors("YES", 'lr', 'lw'), make_colors("YES", 'lr', 'lw')])
        t.add_row([make_colors("URL", 'lw', 'bl'), make_colors("NO", 'lw', 'lr'), make_colors("NO", 'lw', 'lr'), make_colors("YES", 'lr', 'lw'), make_colors("YES", 'lr', 'lw')])
        print(t)
    def Set(self, music_file, title = None, track = None, disc = None, album = None, artist = None, album_artist = None, original = None, composer = None, comment = None, isrc = None, barcode = None, genre = None, date = None, bpm = None, copyright = None, encodedby = None, key = None, lyric = None, lyric_name = None, remix = None, subtitle = None, url = None, group = None, publisher = None, length = None, comment_desc = '', cover_name = 'Cover Album Front', cover = None, solo_artist = '', test = False):
        
        def change_split(h_frame):
            len_files = len(self.files)
            if len_files == 1:
                len_files = "0" + str(len_files)
            if len(str(h_frame)) == 1:
                h_frame = "0" + str(h_frame)
            if not "/" in str(h_frame):
                h_frame = str(h_frame) + "/" + str(len_files)
            else:
                fr, to = str(h_frame).split("/")
                if int(to) == 1:
                    if len(fr) == 1:
                        fr = "0" + fr
                    h_frame = fr + "/" + str(len_files)
            return h_frame
        
        def change_CD(h_frame, many_CD = '01'):
            len_files = len(self.files)
            if len_files == 1:
                len_files = "0" + str(len_files)
            if len(str(h_frame)) == 1:
                h_frame = "0" + str(h_frame)
            if not "/" in str(h_frame):
                h_frame = str(h_frame) + "/" + many_CD
            else:
                fr, to = str(h_frame).split("/")
                if int(to) == 1:
                    if len(fr) == 1:
                        fr = "0" + fr
                    h_frame = fr + "/" + many_CD
            return h_frame        
        
        def change(obj, h_frame_name, frame, h_frame_value = None, encoding = 3):
            if h_frame_value or h_frame_value == '':
                if h_frame_name.lower() == 'comment':
                    obj_frame = re.findall("'COMM.*?'", str(obj.keys()))
                    if obj_frame:
                        obj_frame = obj_frame[0][1:-1]
                elif h_frame_name.lower() == 'barcode':
                    obj_frame = re.findall("'TXXX.*?'", str(obj.keys()))
                    if obj_frame and 'BARCODE' in obj_frame:
                        obj_frame = obj_frame[0][1:-1]
                elif h_frame_name.lower() == 'url':
                    obj_frame = re.findall("'WXXX.*?'", str(obj.keys()))
                    if obj_frame:
                        obj_frame = obj_frame[0][1:-1]
                elif h_frame_name.lower() == 'cover name':
                    obj_frame = re.findall("'TXXX.*?'", str(obj.keys()))
                    if obj_frame:
                        obj_frame = obj_frame[0][1:-1]
                elif h_frame_name.lower() == 'lyric':
                    obj_frame = re.findall("'USLT.*?'", str(obj.keys()))
                    if obj_frame:
                        obj_frame = obj_frame[0][1:-1]                
                else:
                    obj_frame = frame
                #print("h_frame_value =", h_frame_value)
                #print("h_frame_name.lower() =", h_frame_name.lower())
                #print("obj_frame =", obj_frame)
                #print("obj[obj_frame] =", obj[obj_frame])
                if not h_frame_value == obj[obj_frame]:
                    print(make_colors("{0}:".format(h_frame_name).upper(), 'lc') + make_colors(str(obj[frame]), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(h_frame_value, 'lw', 'bl'))
                    if h_frame_value == 'clear':
                        #print("h_frame_value 2 =", h_frame_value)
                        #print("h_frame_name.lower() =", h_frame_name.lower())
                        h_frame_value = ''
                    if h_frame_name.lower() == 'title':
                        obj.add(id3.TIT2(encoding = encoding, text = h_frame_value))
                    elif h_frame_name.lower() == 'track':
                        if not h_frame_value == '' or not h_frame_value == 'clear':
                            h_frame_value = change_split(h_frame_value)
                            obj.add(id3.TRCK(encoding = encoding, text = str(h_frame_value)))
                    elif h_frame_name.lower() == 'disc':
                        if not h_frame_value == '' or not h_frame_value == 'clear':
                            h_frame_value = change_CD(h_frame_value)
                            obj.add(id3.TPOS(encoding = encoding, text = str(h_frame_value)))
                    elif h_frame_name.lower() == 'album':
                        obj.add(id3.TALB(encoding = encoding, text = h_frame_value))
                    elif h_frame_name.lower() == 'artist':
                        obj.add(id3.TPE1(encoding = encoding, text = h_frame_value))
                    elif h_frame_name.lower() == 'solo artist':
                        obj.add(id3.TXXX(encoding = encoding, desc = 'ARTIST', text = h_frame_value))
                    elif h_frame_name.lower() == 'album artist':
                        obj.add(id3.TPE2(encoding = encoding, text = h_frame_value))
                    elif h_frame_name.lower() == 'original artist':
                        obj.add(id3.TOPE(encoding = encoding, text = h_frame_value))
                    elif h_frame_name.lower() == 'composer':
                        obj.add(id3.TCOM(encoding = encoding, text = h_frame_value))
                    elif h_frame_name.lower() == 'isrc':
                        #print("h_frame_value 3 =", h_frame_value)
                        obj.add(id3.TSRC(encoding = encoding, text = h_frame_value))
                    elif h_frame_name.lower() == 'barcode':
                        obj.add(id3.TXXX(encoding = encoding, desc = 'BARCODE', text =str(h_frame_value)))
                    elif h_frame_name.lower() == 'genre':
                        obj.add(id3.TCON(encoding = encoding, text = h_frame_value))
                    elif h_frame_name.lower() == 'date':
                        obj.add(id3.TDRC(encoding = encoding, text = h_frame_value))
                    elif h_frame_name.lower() == 'bpm':
                        obj.add(id3.TBPM(encoding = encoding, text = h_frame_value))
                    elif h_frame_name.lower() == 'copyright':
                        obj.add(id3.TCOP(encoding = encoding, text = h_frame_value))
                    elif h_frame_name.lower() == 'encodedby':
                        obj.add(id3.TENC(encoding = encoding, text = h_frame_value))
                    elif h_frame_name.lower() == 'length':
                        obj.add(id3.TLEN(encoding = encoding, text = h_frame_value))
                    elif h_frame_name.lower() == 'key':
                        obj.add(id3.TKEY(encoding = encoding, text = h_frame_value))
                    elif h_frame_name.lower() == 'lyric_name':
                        obj.add(id3.TEXT(encoding = encoding, text = h_frame_value))
                    elif h_frame_name.lower() == 'lyric':
                        obj.add(id3.USLT(encoding = encoding, lang = 'xxx', desc = '', text = h_frame_value))                    
                    elif h_frame_name.lower() == 'remix':
                        obj.add(id3.TPE4(encoding = encoding, text = h_frame_value))
                    elif h_frame_name.lower() == 'subtitle':
                        obj.add(id3.TIT3(encoding = encoding, text = h_frame_value))
                    elif h_frame_name.lower() == 'url':
                        obj.add(id3.WXXX(encoding = encoding, desc = '', url = h_frame_value))
                    elif h_frame_name.lower() == 'group':
                        obj.add(id3.TIT1(encoding = encoding, text = h_frame_value))
                    elif h_frame_name.lower() == 'publisher':
                        obj.add(id3.TPUB(encoding = encoding, text = h_frame_value))
                    elif h_frame_name.lower() == 'cover name':
                        obj.add(id3.TXXX(encoding = encoding, desc = '_cover', text = h_frame_value))
                    elif h_frame_name.lower() == 'comment':
                        if not comment_desc:
                            comment_desc = ''                        
                        obj.add(id3.COMM(encoding = encoding, lang = 'eng', desc = comment_desc, text = h_frame_value))
                    elif h_frame_name.lower() == 'cover':
                        print(make_colors("Change cover", 'lw', 'r'))
                        #print("h_frame_value_cover =", h_frame_value)
                        if os.path.isfile(h_frame_value):
                            img = Image.open(h_frame_value)
                            mime = img.format
                            mime_type = mimelist.get2(mime)[0]
                            debug(mime_type = mime_type)
                            with open(h_frame_value, 'rb') as c:
                                cover_data = c.read()
                                obj.add(id3.APIC(encoding = 1, type = PictureType.COVER_FRONT, desc = 'Cover Album Front', data = cover_data, mime = mime_type))
                            obj.add(id3.TXXX(encoding = encoding, desc = '_cover', text = 'Cover Album Front'))
                else:
                    if h_frame_name.lower() == 'comment':
                        comment_key = re.findall("'COMM.*?'", str(obj.keys()))
                        debug(comment_key = comment_key)
                        if comment_key:
                            comment_key = comment_key[0][1:-1]
                            print(make_colors("{0}:".format(h_frame_name).upper(), 'lc') + " " + make_colors(str(obj[comment_key]), 'lg'))
                    elif h_frame_name.lower() == 'barcode':
                        barcode_key = re.findall("'TXXX.*?'", str(obj.keys()))
                        if barcode_key and 'BARCODE' in barcode_key:
                            barcode_key = barcode_key[0][1:-1]
                            print(make_colors("{0}:".format(h_frame_name).upper(), 'lc') + " " + make_colors(str(obj[barcode_key]), 'lg'))
                    elif h_frame_name.lower() == 'lyric':
                        print(make_colors("{0}:".format(h_frame_name).upper(), 'lc') + " " + make_colors(str(obj[h_frame_name])[:21], 'lg'))
                    elif h_frame_name.lower() == 'url':
                        url_key = re.findall("'WXXX.*?'", str(obj.keys()))
                        if url_key:
                            url_key = url_key[0][1:-1]
                            print(make_colors("{0}:".format(h_frame_name).upper(), 'lc') + " " + make_colors(str(obj[url_key]), 'lg'))
                    elif h_frame_name.lower() == 'url':
                        cover_name_key = re.findall("'TXXX.*?'", str(obj.keys()))
                        if cover_name_key:
                            cover_name_key = cover_name_key[0][1:-1]
                            print(make_colors("{0}:".format(h_frame_name).upper(), 'lc') + " " + make_colors(str(obj[cover_name_key]), 'lg'))                    
                    else:
                        print(make_colors("{0}:".format(h_frame_name).upper(), 'lc') + " " + make_colors(str(obj[frame]), 'lg'))            
                
        if os.path.splitext(music_file)[1] and os.path.splitext(music_file)[1] == ".mp3":
            debug(music_file = music_file)
            a = ID3(music_file)
            keys = a.keys()
            debug(keys = keys)
            
            try:
                change(a, 'title', 'TIT2', title)
            except:
                try:
                    print(make_colors("Title:", 'lc') + make_colors(str(a['TIT2']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(title, 'lw', 'bl'))
                except:
                    print(make_colors("Title:", 'lc') + make_colors('TIT2', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(title, 'lw', 'bl'))
                if title == '' or title == 'clear':
                    a.add(id3.TIT2(encoding = 3, text = ''))
                else:
                    a.add(id3.TIT2(encoding = 3, text = title))
            try:
                change(a, 'track', 'TRCK', track)
            except:
                track = change_split(track)
                try:
                    print(make_colors("Track:", 'lc') + make_colors(str(a['TRCK']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(track, 'lw', 'bl'))
                except:
                    print(make_colors("Track:", 'lc') + make_colors('TRCK', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(track, 'lw', 'bl'))
                if track == '' or track == 'clear':
                    a.add(id3.TRCK(encoding = 3, text = ''))
                else:
                    a.add(id3.TRCK(encoding = 3, text = track))
            try:
                change(a, 'disc', 'TPOS', disc)
            except:
                disc = change_CD(disc)
                try:
                    print(make_colors("Track:", 'lc') + make_colors(str(a['TPOS']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(disc, 'lw', 'bl'))
                except:
                    print(make_colors("Track:", 'lc') + make_colors('TPOS', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(disc, 'lw', 'bl'))
                if disc == '' or disc == "clear":
                    a.add(id3.TPOS(encoding = 3, text = ''))
                else:
                    
                    a.add(id3.TPOS(encoding = 3, text = disc))
            try:
                change(a, 'album', 'TALB', album)
            except:
                try:
                    print(make_colors("Album:", 'lc') + make_colors(str(a['TALB']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(album, 'lw', 'bl'))
                except:
                    print(make_colors("Album:", 'lc') + make_colors('TALB', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(album, 'lw', 'bl'))
                if album == '' or album == 'clear':
                    a.add(id3.TALB(encoding = 3, text = ''))
                else:
                    a.add(id3.TALB(encoding = 3, text = album))
            try:
                change(a, 'artist', 'TPE1', artist)
            except:
                try:
                    print(make_colors("Artist:", 'lc') + make_colors(str(a['TPE1']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(artist, 'lw', 'bl'))
                except:
                    print(make_colors("Artist:", 'lc') + make_colors('TPE1', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(artist, 'lw', 'bl'))
                if artist == '' or artist == 'clear':
                    a.add(id3.TPE1(encoding = 3, text = ''))
                else:
                    a.add(id3.TPE1(encoding = 3, text = artist))
            try:
                change(a, 'solor artist', 'TXXX', solo_artist)
            except:
                try:
                    print(make_colors("Solo Artist:", 'lc') + make_colors(str(a['TXXX:ARTIST']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(solo_artist, 'lw', 'bl'))
                except:
                    print(make_colors("Solo Artist:", 'lc') + make_colors('TXXX:ARTIST', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(solo_artist, 'lw', 'bl'))
                if solo_artist == '' or solo_artist == 'clear':
                    a.add(id3.TXXX(encoding = 3, desc = 'ARTIST', text = ''))
                else:
                    a.add(id3.TXXX(encoding = 3, desc = 'ARTIST', text = solo_artist))            
            try:
                change(a, 'album artist', 'TPE2', album_artist)
            except:
                try:
                    print(make_colors("Album Artist:", 'lc') + make_colors(str(a['TPE2']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(album_artist, 'lw', 'bl'))
                except:
                    print(make_colors("Album Artist:", 'lc') + make_colors('TPE2', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(album_artist, 'lw', 'bl'))
                if album_artist == '' or album_artist == 'clear':
                    a.add(id3.TPE2(encoding = 3, text = ''))
                else:
                    a.add(id3.TPE2(encoding = 3, text = album_artist))                            
            try:
                change(a, 'original artist', 'TOPE', original)
            except:
                try:
                    print(make_colors("Original Artist:", 'lc') + make_colors(str(a['TOPE']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(original, 'lw', 'bl'))
                except:
                    print(make_colors("Original Artist:", 'lc') + make_colors('TOPE', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(str(original), 'lw', 'bl'))
                if original == '' or original == 'clear':
                    a.add(id3.TOPE(encoding = 3, text = ''))
                else:
                    a.add(id3.TOPE(encoding = 3, text = original))
            try:
                change(a, 'composer', 'TCOM', composer)
            except:
                composer_key = re.findall("'TXXX.*?'", str(a.keys()))
                if composer_key:
                    composer_key = composer_key[0][1:-1]                
                try:
                    print(make_colors("Composer:", 'lc') + make_colors(str(a[comment_key]), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(composer, 'lw', 'bl'))
                except:
                    print(make_colors("Composer:", 'lc') + make_colors('TCOM', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(str(composer), 'lw', 'bl'))
                if composer == '' or composer == 'clear':
                    a.add(id3.TCOM(encoding = 3, text = ''))
                else:
                    a.add(id3.TCOM(encoding = 3, text = composer))
            try:
                change(a, 'barcode', 'TXXX', barcode)
            except:
                try:
                    barcode_key = re.findall("'TXXX.*?'", str(a.keys()))
                    if barcode_key and 'BARCODE' in barcode_key:
                        barcode_key = barcode_key[0][1:-1]                                    
                    print(make_colors("Barcode:", 'lc') + make_colors(str(a[barcode_key]), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(barcode, 'lw', 'bl'))
                except:
                    print(make_colors("Barcode:", 'lc') + make_colors('TXXX:BARCODE', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(barcode, 'lw', 'bl'))
                if barcode == '' or barcode == 'clear':
                    a.add(id3.TXXX(encoding = 3, desc = 'BARCODE', text = ''))
                else:
                    a.add(id3.TXXX(encoding = 3, desc = 'BARCODE', text = barcode))
            try:                
                change(a, 'isrc', 'TSRC', isrc)
            except:
                try:
                    print(make_colors("ISRC:", 'lc') + make_colors(str(a['TSRC']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(isrc, 'lw', 'bl'))
                except:
                    print(make_colors("ISRC:", 'lc') + make_colors('TSRC', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(isrc, 'lw', 'bl'))
                if isrc == '' or isrc == 'clear':
                    a.add(id3.TSRC(encoding = 3, text = ''))
                else:
                    a.add(id3.TSRC(encoding = 3, text = isrc))
            try:
                change(a, 'genre', 'TCON', genre)
            except:
                try:
                    print(make_colors("Genre:", 'lc') + make_colors(str(a['TCON']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(genre, 'lw', 'bl'))
                except:
                    print(make_colors("Genre:", 'lc') + make_colors('TCON', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(genre, 'lw', 'bl'))
                if genre == '' or genre == 'clear':
                    a.add(id3.TCON(encoding = 3, text = ''))
                else:
                    a.add(id3.TCON(encoding = 3, text = genre))
            try:
                change(a, 'date', 'TDRC', date)
            except:
                try:
                    print(make_colors("Date:", 'lc') + make_colors(str(a['TDRC']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(date, 'lw', 'bl'))
                except:
                    print(make_colors("Date:", 'lc') + make_colors('TDRC', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(date, 'lw', 'bl'))
                if date == '' or date == 'clear':
                    a.add(id3.TDRC(encoding = 3, text = ''))
                else:
                    a.add(id3.TDRC(encoding = 3, text = date))
            try:
                change(a, 'copyright', 'TCOP', copyright)
            except:
                try:
                    print(make_colors("Copyright:", 'lc') + make_colors(str(a['TCOP']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(copyright, 'lw', 'bl'))
                except:
                    print(make_colors("Copyright:", 'lc') + make_colors('TCOP', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(copyright, 'lw', 'bl'))
                if copyright == '' or copyright == 'clear':
                    a.add(id3.TCOP(encoding = 3, text = ''))
                else:
                    a.add(id3.TCOP(encoding = 3, text = copyright))
            try:
                change(a, 'encodedby', 'TENC', encodedby)
            except:
                try:
                    print(make_colors("Encodedby:", 'lc') + make_colors(str(a['TENC']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(encodedby, 'lw', 'bl'))
                except:
                    print(make_colors("Encodedby:", 'lc') + make_colors('TENC', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(encodedby, 'lw', 'bl'))
                if encodedby == '' or encodedby == 'clear':
                    a.add(id3.TENC(encoding = 3, text = ''))
                else:
                    a.add(id3.TENC(encoding = 3, text = encodedby))
            try:
                change(a, 'length', 'TLEN', length)
            except:
                try:
                    print(make_colors("Length:", 'lc') + make_colors(str(a['TLEN']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(length, 'lw', 'bl'))
                except:
                    print(make_colors("Length:", 'lc') + make_colors('TLEN', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(length, 'lw', 'bl'))
                if length == '' or length == 'clear':
                    a.add(id3.TLEN(encoding = 3, text = ''))
                else:
                    a.add(id3.TLEN(encoding = 3, text = length))
            try:
                change(a, 'key', 'TKEY', key)
            except:
                try:
                    print(make_colors("Key:", 'lc') + make_colors(str(a['TKEY']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(key, 'lw', 'bl'))
                except:
                    print(make_colors("Key:", 'lc') + make_colors('TKEY', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(key, 'lw', 'bl'))
                if key == '' or key == 'clear':
                    a.add(id3.TKEY(encoding = 3, text = ''))
                else:
                    a.add(id3.TKEY(encoding = 3, text = key))
            try:
                change(a, 'lyric_name', 'TEXT', lyric)
            except:
                try:
                    print(make_colors("Lyric Name:", 'lc') + make_colors(str(a['TEXT']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(lyric_name, 'lw', 'bl'))
                except:
                    print(make_colors("Lyric Name:", 'lc') + make_colors('TEXT', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(lyric_name, 'lw', 'bl'))
                if lyric_name == '' or lyric_name == 'clear':
                    a.add(id3.TEXT(encoding = 3, text = ''))
                else:
                    a.add(id3.TEXT(encoding = 3, text = lyric_name))
            try:
                change(a, 'lyric', 'USLT', lyric)
            except:
                try:
                    print(make_colors("Lyric:", 'lc') + make_colors(str(a['USLT::xxx']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(lyric[:20], 'lw', 'bl'))
                except:
                    print(make_colors("Lyric:", 'lc') + make_colors('USLT::xxx', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(lyric[:20], 'lw', 'bl'))
                if lyric == '' or lyric == 'clear':
                    a.add(id3.USLT(encoding = 3, lang = 'xxx', desc = '', text = ''))
                else:
                    a.add(id3.USLT(encoding = 3, lang = 'xxx', desc = '', text = lyric))
            try:
                change(a, 'remix', 'TPE4', remix)
            except:
                try:
                    print(make_colors("Remix:", 'lc') + make_colors(str(a['TPE4']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(remix, 'lw', 'bl'))
                except:
                    print(make_colors("Remix:", 'lc') + make_colors('TPE4', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(remix, 'lw', 'bl'))
                if remix == '' or remix == 'clear':
                    a.add(id3.TPE4(encoding = 3, text = ''))
                else:
                    a.add(id3.TPE4(encoding = 3, text = remix))
            try:
                change(a, 'subtitle', 'TIT3', subtitle)
            except:
                try:
                    print(make_colors("Subtitle:", 'lc') + make_colors(str(a['TIT3']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(subtitle, 'lw', 'bl'))
                except:
                    print(make_colors("Subtitle:", 'lc') + make_colors('TIT3', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(subtitle, 'lw', 'bl'))
                if subtitle == '' or subtitle == 'clear':
                    a.add(id3.TIT3(encoding = 3, text = ''))
                else:
                    a.add(id3.TIT3(encoding = 3, text = subtitle))
            try:
                change(a, 'url', 'WXXX', url)
            except:
                url_key = re.findall("'WXXX.*?'", str(a.keys()))
                if url_key:
                    url_key = url_key[0][1:-1]                
                try:
                    print(make_colors("URL:", 'lc') + make_colors(str(a[url_key]), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(url, 'lw', 'bl'))
                except:
                    print(make_colors("URL:", 'lc') + make_colors('WXXX:', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(url, 'lw', 'bl'))
                if url == '' or url == 'clear':
                    a.add(id3.WXXX(encoding = 3, desc = '', url = ''))
                else:
                    a.add(id3.WXXX(encoding = 3, desc = '', url = url))
            try:
                change(a, 'group', 'TIT1', group)
            except:
                try:
                    print(make_colors("Group:", 'lc') + make_colors(str(a['TIT1']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(group, 'lw', 'bl'))
                except:
                    print(make_colors("Group:", 'lc') + make_colors('TIT1', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(str(group), 'lw', 'bl'))
                if group == '' or group == 'clear':
                    a.add(id3.TIT1(encoding = 3, text = ''))
                else:
                    a.add(id3.TIT1(encoding = 3, text = group))
            try:
                change(a, 'publisher', 'TPUB', publisher)
            except:
                try:
                    print(make_colors("Puslisher:", 'lc') + make_colors(str(a['TPUB']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(publisher, 'lw', 'bl'))
                except:
                    print(make_colors("Publisher:", 'lc') + make_colors('TPUB', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(publisher, 'lw', 'bl'))
                if publisher == '' or publisher == 'clear':
                    a.add(id3.TPUB(encoding = 3, text = ''))
                else:
                    a.add(id3.TPUB(encoding = 3, text = publisher))
            try:
                change(a, 'cover name', 'TXXX', cover_name)
            except:
                cover_name_key = re.findall("'TXXX.*?'", str(a.keys()))
                if cover_name_key:
                    cover_name_key = cover_name_key[0][1:-1]                
                try:
                    print(make_colors("Cover Name:", 'lc') + make_colors(str(a[cover_name_key]), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(cover_name, 'lw', 'bl'))
                except:
                    print(make_colors("Cover Name:", 'lc') + make_colors('TXXX:_cover', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(cover_name, 'lw', 'bl'))
                if cover_name == '' or cover_name == 'clear':
                    a.add(id3.TXXX(encoding = 3, desc = '_cover', text = ''))
                else:
                    a.add(id3.TXXX(encoding = 3, desc = '_cover', text = cover_name))
            try:
                change(a, 'comment', 'COMM', comment)
            except:
                comment_key = re.findall("'COMM.*?'", str(a.keys()))
                if comment_key:
                    comment_key = comment_key[0][1:-1]                
                try:
                    print(make_colors("Comment:", 'lc') + make_colors(str(a[comment_key]), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(comment, 'lw', 'bl'))
                except:
                    print(make_colors("Comment:", 'lc') + make_colors('COMM', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(comment, 'lw', 'bl'))
                if comment == '' or comment == 'clear':
                    a.add(id3.COMM(encoding = 3, lang = 'eng', desc = '', text = ''))
                else:
                    a.add(id3.COMM(encoding = 3, lang = 'eng', desc = '', text = comment))
            try:
                change(a, 'cover', 'APIC', cover)
            except:
                try:
                    print(make_colors("Cover:", 'lc') + make_colors(str(a['APIC:']), 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(cover, 'lw', 'bl'))
                except:
                    print(make_colors("Cover:", 'lc') + make_colors('APIC', 'lw', 'lr') + " " + make_colors(" --> ", 'ly') + " " + make_colors(cover, 'lw', 'bl'))
                if os.path.isfile(cover):
                    if cover == '' or cover == 'clear':
                        a.add(id3.COMM(encoding = 1, lang = 'eng', mime = '', type = PictureType.COVER_FRONT, desc = 'Cover', data = ''))
                    else:
                        with open(cover, 'rb') as cv:
                            cover_data = cv.read()
                        mime = mimelist.get2(Image.open(cover).format)[0]                        
                        a.add(id3.COMM(encoding = 1, lang = 'eng', mime = mime, type = PictureType.COVER_FRONT, desc = 'Cover', data = cover_data))
            
            if not test:
                a.save()
        #sys.stdout.write(cmdw.getWidth() * "-")
                
    def convert_frame(self, frame):
        if frame == 'TIT1':
            return 'group'
        elif frame == 'TIT2':
            return 'title'
        elif frame == 'TIT3':
            return 'subtitle'
        elif frame == 'TPE1':
            return 'artist'
        elif frame == 'TPE2':
            return 'album artist'
        elif frame == 'TPE3':
            return 'conductor'
        elif frame == 'TPE4':
            return 'remixed by'
        elif frame == 'TALB':
            return 'album'
        elif frame == 'TBPM':
            return 'bpm'
        elif frame == 'TCON':
            return 'genre'
        elif frame == 'TLEN':
            return "length"
        elif frame == 'TPOS':
            return "disc"
        elif frame == 'TPUB':
            return 'publisher'
        elif frame == 'TRCK':
            return "track"
        elif frame == 'TSRC':
            return "isrc"
        elif frame == 'TOPE':
            return "original artist"
        elif frame == 'TCOM':
            return 'composer'
        elif frame == 'TCOP':
            return "copyright"
        elif frame == 'TENC':
            return "encoded by"
        elif frame == 'TEXT':
            return "lyric name"
        elif frame == 'TKEY':
            return "key"
        elif frame == 'COMM':
            return "comment"
        elif frame == 'TDRC':
            return "date"        
        elif "COMM" in frame:
            return "comment"
        elif "TXXX" in frame and "BARCODE" in frame:
            return "barcode"
        elif "TXXX" in frame and "cover" in frame:
            return "cover name"
        elif "TXXX" in frame and "ARTIST" in frame:
            return "solo artist"        
        elif "USLT" in frame:
            return "lyric"
        elif "WXXX" in frame:
            return "url"
        elif "APIC" in frame:
            return "cover"
        else:
            return frame
            
    def Get_Cover_Info(self, cover):
        from PIL import Image
        if isinstance(cover, str) and not os.path.isfile(cover) and len(cover) < 10:
            return '', ''
        if sys.version_info.major == 3:
            from io import BytesIO
            if isinstance(cover, bytes):
                f = cover
            else:
                f = open(cover, 'rb').read()
            st = BytesIO(f)
            img = Image.open(st)
            return img.size, img.format
        else:
            import StringIO
            if isinstance(cover, str) and not os.path.isfile(cover) and len(cover) > 10:
                f = cover
            else:
                f = open(cover, 'rb').read()
            st = StringIO.StringIO(f)
            img = Image.open(st)
            return img.size, img.format
        return '', ''
        
    def Extract_cover(self, file_music, filename='Cover'):
        tag = ID3(file_music)
        cover_key = re.findall("'APIC.*?'", str(tag.keys()))
        if cover_key:
            cover_key = cover_key[0][1:-1]
            img_data = None
            try:
                img_data = tag[cover_key].data
            except:
                pass
            if img_data:
                size, format = self.Get_Cover_Info(img_data)
                debug(size = size)
                debug(format = format)
            
                ext = mimelist.get2(format)[1]
                if not ext:
                    ext = ".jpg"
                
                with open(filename + "." + ext, 'wb') as cover:
                    cover.write(img_data)
            
            
    def Get(self, music_file, save_as = None):
        tag = ID3(music_file)
        tag_mp3 = MP3(music_file)
        info = tag_mp3.info.__dict__
        keys = tag.keys()
        #list_h_frame = []
        len_list_h_frame = []
        for i in keys:
            #list_h_frame.append(self.convert_frame(i))
            len_list_h_frame.append(len(self.convert_frame(i)))
        #debug(list_h_frame = list_h_frame)
        debug(max_len_list_h_frame = max(len_list_h_frame))
        MAX = max(len_list_h_frame)
        for i in keys:
            if not "APIC" in i:
                print(make_colors(self.convert_frame(i).upper() + (MAX - len(self.convert_frame(i))) * " " + " : ", 'lw', 'bl') + make_colors(str(tag[i]), 'lc'))
            else:
                cover_key = re.findall("'APIC.*?'", str(tag.keys()))
                if cover_key:
                    cover_key = cover_key[0][1:-1]
                    img_data = None
                    try:
                        img_data = tag[cover_key].data
                    except:
                        pass
                    if img_data:
                        size, format = self.Get_Cover_Info(img_data)
                        debug(size = size)
                        debug(format = format)
                        print(make_colors(self.convert_frame(cover_key).upper() + (MAX - len(self.convert_frame(cover_key))) * " " + " : ", 'lw', 'bl') + make_colors("size: " + str(size[0]) + "x" + str(size[1]) + ", format: " + str(format) + ", data:" + str(tag[cover_key].data[:10]), 'lc') + " ...")
        for f in info:            
            f1 = re.sub("_", " ", f)
            print(make_colors(f1.upper() + (MAX - len(f1)) * " " + " : ", 'lw', 'bl') + make_colors(str(info[f]), 'lc'))
        print(cmdw.getWidth() * "-")
        

if __name__ == '__main__':
    c = Tagger()
    c.usage()