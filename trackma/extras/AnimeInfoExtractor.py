# This file is part of Trackma.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import re
from decimal import Decimal

class AnimeInfoExtractor():
    """
    Extracts lots of information about anime from filename alone
    @author: Tyris
    @author: Uriziel
    @note: Thanks for Tyris for providing easy way to extract data
    @note: Does more than what's needed, but that behaviour is well tested
    """
    def __init__(self, filename):
        self.originalFilename = filename
        self.resolution = ''
        self.hash = ''
        self.subberTag = ''
        self.videoType = []
        self.audioType = []
        self.releaseSource = []
        self.extension = ''
        self.episodeStart = None
        self.episodeEnd = None
        self.volumeStart = None
        self.volumeEnd = None
        self.version = 1
        self.name = ''
        self.pv = -1
        self._processFilename()

    def getName(self):
        return self.name


    def getEpisodeNumbers(self, force_numbers=False):
        ep_start = self.episodeStart
        ep_end = self.episodeEnd
        if force_numbers:
            if ep_start is None:
                ep_start = 1
            if ep_end is None:
                ep_end = ep_start
            ep_start = int(ep_start)
            ep_end = int(ep_end)
        return ep_start, ep_end

    def getEpisode(self):
        ep = self.episodeStart if self.episodeEnd is None else self.episodeEnd
        ep = ep if ep is not None else 1

        return int(ep)

        
    def __testIfEp(self, filename):
        # Test if file is an episode or Special/Supplementary File, and force a failure condiion if this is the case, to avoid false positives
        z = re.search(r"((?P<show>.*?)[ _\.\-]+)((?P<spec>PV|SP|OP|ED)(([ _\.]+(?P<epa>\d{1,2}[a-u|w-z]?))|(?P<epb>\d{1,2}[a-u|w-z]?)|([ _\.]+)))+[ _\.]?(?P<version>V\d{1,2})?([ _\.\-]+(?P<eptitle>.^\[*))?", filename, flags=re.IGNORECASE)
        if z is None:
           z = re.search(r"((?P<show>.*?)[ _\.\-]+)(?P<spec>NCOP|OPENING|NCED|ENDING|SPECIAL|TRAILER|PROMO|OTHER)[ _\.]?(?P<ep>\d{1,2}[a-u|w-z]?)?[ _\.]?(?P<version>V\d{1,2})?([ _\.\-]+(?P<eptitle>.^\[*))?", filename, flags=re.IGNORECASE)
           if z is None:
               return filename        
        filename = "File is a " + z.group('spec')
        self.name = "File is a " + z.group('spec')
        return filename        

    def __extractExtension(self, filename):
        m = re.search("\.(\w{3})$", filename)
        if m:
            self.extension = m.group(1)
            filename = filename[:-4]
        return filename

    def __cleanUpSpaces(self, filename):
        filename = filename.replace('_', ' ')
        if not ' ' in filename:
            filename = re.sub('([^.])\.([^.])', r'\1 \2', filename)
            # to handle .-. case (where - is any single chara)
            filename = re.sub('([^.])\.([^.])', r'\1 \2', filename)
            # If there are still no spaces try replacing hyphens with spaces
            if not ' ' in filename:
                filename = re.sub('([^\-])-([^\-])', r'\1 \2', filename)
                # to handle -.- case (where . is any single chara)
                filename = re.sub('([^\-])-([^\-])', r'\1 \2', filename)
        return filename

    def __extractSpecialTags(self, filename):
        tags = {'video': ['H264', 'H.264', 'x264', 'XviD', 'DivX', 'MP4'],
            'audio': ['AC3', 'AAC', 'MP3', 'FLAC'],
            'source': ['TV', 'DVD', 'BluRay', 'BD', 'Blu-Ray', 'BDMV']}
        for k, v in tags.items():
            for tag in v:
                m = re.search('(?:[\(\[](?:|[^\)\]]*?[^0-9a-zA-Z\)\]]))(' + tag + ')(?:[^0-9a-zA-Z]|$)', filename, flags=re.IGNORECASE)
                if m:
                    if (k == 'video'):
                        self.videoType.append(tag)
                    elif (k == 'audio'):
                        self.audioType.append(tag)
                    elif (k == 'source'):
                        self.releaseSource.append(tag)
                    filename = filename[:m.start(1)] + '###NO#SUBBER#HERE###' + filename[m.end(1):]  # remove the match
        return filename

    def __extractVideoProfile(self, filename):
        # Check for 8bit/10bit
        tags_10bit = ['Hi10P', 'Hi10', '10bit', '10 bit', '10-bit']
        tags_8bit = ['8bit', '8-bit']
        for tag in tags_10bit:
            if tag in filename:
                self.videoType = ['H264', 'Hi10P']
                # Don't replace Hi10 coz its a subber name
                if tag != 'Hi10':
                    filename = filename.replace(tag, '')
                return filename
        if not self.videoType == ['H264', 'Hi10P']:
            for tag in tags_8bit:
                if tag in filename:
                    self.videoType = ['H264', '8bit']
                    filename = filename.replace(tag, '')
                    return filename
        return filename

    def __extractResolution(self, filename):
        # Match 3 or 4 chars followed by p, i, or x and 3 or 4 more chars, surrounded by any non-alphanumberic chars
        m = re.search('(?:[^0-9a-zA-Z])(\d{3,4}(?:p|i|x\d{3,4}))(?:[^0-9a-zA-Z]|$)', filename)
        if m:
            self.resolution = m.group(1)
            filename = filename[:m.start(1)] + filename[m.end(1):]
        else:
            m = re.search('(?:\[|\(|\d)(HD|SD)(?:\]|\)| |\.)', filename)
            if m:
                self.resolution = m.group(1)
                filename = filename[:m.start(1)] + filename[m.end(1):]
            else:
                m = re.search('(?:\d{1,3})(HD|SD)(?:[^a-zA-Z])', filename)
                if m:
                    self.resolution = m.group(1)
                    filename = filename[:m.start(1)] + filename[m.end(1):]  # Super special case for HD/SD imediately after episode
        return filename

    def __extractHash(self, filename):
        # Match anything in square or round brackets that is 8 hex digits
        m = re.search('(?:\[|\()((?:[A-F]|[a-f]|\d){8})(?:\]|\))', filename)
        if m:
            self.hash = m.group(1)
            filename = filename[:m.start()] + filename[m.end():]
        return filename

    def __checkIfRemux(self, filename):
        m = re.search('(?:[\(\[][^\)\]]*?[^0-9a-zA-Z\)\]]?)(Remux)(?:[^0-9a-zA-Z]|$)', filename, flags=re.IGNORECASE)
        return True if m else False

    def __cleanUpBrackets(self, filename):
        # Can get rid of the brackets that won't contain subber
        filename = re.sub('\((?:[^\)]*?)###NO#SUBBER#HERE##(?:.*?)\)', '', filename)
        filename = re.sub('\[(?:[^\]]*?)###NO#SUBBER#HERE##(?:.*?)\]', '', filename)
        # Strip any empty sets of brackets
        filename = re.sub('(?:\[(?:[^0-9a-zA-Z]*?)\])|(?:\((?:[^0-9a-zA-Z]*?)\))', ' ', filename)
        return filename

    def __extractSubber(self, filename, remux):
        # Extract the subber from square brackets (or round failing that)
        m = re.search('\[([^\. ].*?)\]', filename)
        if m:
            self.subberTag = m.group(1)
            filename = filename[:m.start()] + filename[m.end():]
        else:
            m = re.search('\(([^\. ].*?)\)', filename)
            if m:
                self.subberTag = m.group(1)
                filename = filename[:m.start()] + filename[m.end():]
            else:
                m = re.search('{([^\. ].*?)}', filename)
                if m:
                    self.subberTag = m.group(1)
                    filename = filename[:m.start()] + filename[m.end():]
        self.subberTag = self.subberTag.strip(' -')
        # Add the remux string if this was a remux and its not found in the subber tag
        if remux and not 'remux' in self.subberTag.lower():
            # refind remux and remove it
            m = re.search('(?:[\(\[][^\)\]]*?[^0-9a-zA-Z\)\]]?)(Remux)(?:[^0-9a-zA-Z]|$)', filename, flags=re.IGNORECASE)
            if m:
                filename = filename[:m.start(1)] + filename[m.end(1):]
            if self.subberTag:
                self.subberTag = self.subberTag + '-Remux'
            else:
                self.subberTag = 'Remux'
        return filename

    def __extractVersion(self, filename):
        # Extract the version number (limit at v7 since V8 is possible in a title...)
        m = re.search('(?:[^a-zA-Z])v([0-7])(?:[^0-9a-zA-Z]|$)', filename, flags=re.IGNORECASE)
        if m:
            self.version = int(m.group(1))
            filename = filename[:m.start(1) - 1] + filename[m.end(1):]
        return filename

    def __extractVolumeIfPack(self, filename, title_len):
    # Check if this is a volume pack - only relevant for no extension
        if not self.extension:
            m = re.search('[^0-9a-zA-Z](?:vol(?:ume)?\.? ?)(\d{1,3})(?: ?- ?(?:vol(?:ume)?\.? ?)?(\d{1,3}))?(?:[^0-9a-zA-Z]|$)', filename, flags=re.IGNORECASE)
            if m:
                self.volumeStart = int(m.group(1))
                if m.group(2):
                    self.volumeEnd = int(m.group(2))
                filename = filename[:m.start()] + filename[m.end():]
                title_len = m.start()
        return filename, title_len

    def __extractPv(self, filename):
        # Check if this is a PV release (not relevant if its a pack)
        m = re.search(' PV ?(\d)?(?:[^a-zA-Z0-9]|$)', filename)
        if not self.volumeStart and m:
            self.pv = 0
            if m.group(1):
                self.pv = int(m.group(1))
            filename = filename[:m.start(0)]
        return filename

    def __extractEpisodeNumbers(self, filename):
        # First check for concurrent episodes (with a + or &)
        m = re.search('[^0-9a-zA-Z](?:E\.?|Ep(?:i|isode)?s?(?: |\.)?)?(\d{1,4})[\+\&](\d{1,4})(?:[^0-9a-zA-Z]|$)', filename, flags=re.IGNORECASE)
        if m:
            start = int(m.group(1))
            end = int(m.group(2))
            if end == start + 1:
                self.episodeStart = start
                self.episodeEnd = end
                filename = filename[:m.start() + 1]
        if not self.episodeStart:
            # Check for multiple episodes
            if self.extension:
                # no spaces allowed around the hyphen
                ep_search_string = '[^0-9a-zA-Z](?:E\.?|Ep(?:i|isode)?(?: |\.)?)?((?:\d{1,3}|1[0-8]\d{2})(?:\.\d{1})?)-(\d{1,4}(?:\.\d{1})?)(?:[^0-9a-zA-Z]|$)'
            else:
                ep_search_string = '[^0-9a-zA-Z](?:E\.?|Ep(?:i|isode)?(?: |\.)?)?((?:\d{1,3}|1[0-8]\d{2})(?:\.\d{1})?) ?- ?(\d{1,4}(?:\.\d{1})?)(?:[^0-9a-zA-Z]|$)'  # probably a pack... so allow spaces around the hyphen
            m = re.search(ep_search_string, filename, flags=re.IGNORECASE)
            if m:
                self.episodeStart = Decimal(m.group(1))
                self.episodeEnd = Decimal(m.group(2))
                filename = filename[:m.start() + 1]
        # Check if there is an series or episode specifier, and excluding '(YYYY)' elements
        if not self.episodeStart:            
            m = re.search('(^|(?P<show>.*?(?=[ _\.\-]+\d{2,3}|[ _\.\-]+ep\d{2,3}|[ _\.\-]+e\d{2,3}|[ _\.\-]+s\d{1,2}))[ _\.\-]+)((?:(?:s\d{1,2}|S\d{1,2})?)(?:[E\.]*?|Ep(?:i|isode)?s?(?: |\.)?))?(?P<epnum>\d{1,3})(?!\))(?:\d{1,4})?(?:\W|$)', filename, flags=re.IGNORECASE)
            if m:
                self.episodeStart = Decimal(m.group('epnum'))
                filename = m.group('show')
                #filename = filename[:m.start() + 1]
        if not self.episodeStart:
            # Check any remaining lonely numbers as episode (towards the end has priority)
            # First try outside brackets
            m = re.search('(?:.*)(?:[^0-9a-zA-Z\.])((?:\d{1,3}|1[0-8]\d{2})(?:\.\d{1})?)(?:[^0-9a-zA-Z]|$)', filename)
            if m:
                self.episodeStart = Decimal(m.group(1))
                filename = filename[:m.start(1)]
        if not self.episodeStart:
            # then allow brackets
            m = re.search('(?:.*)(?:[^0-9a-zA-Z\.\[\(])((?:\d{1,3}|1[0-8]\d{2})(?:\.\d{1})?)(?:[^0-9a-zA-Z\]\)]|$)', filename)
            if m:
                self.episodeStart = Decimal(m.group(1))
                filename = filename[:m.start(1)]
        return filename

    def __extractShowName(self, filename):
        # Unfortunately, it is very hard to know whether there should be brackets in the title...
        # As such, we really should strip all brackets, as well as their contents...
        # So, to anything with brackets as part of its legitimate title: Sorry =(
        #
        # But, before we do so, we will save the first instance to a backup string,
        # just in case it actually IS the title.
        #
        #   We will also check for Year-in-Round-Brackets, (YYYY), often used as part of
        #   official series naming schemes as a suffix, usuallly in the case of sequels or remakes.
        #   If found, we will save it, and re-add it to the title as a suffix, 
        #   AFTER we have stripped everything else in brackets.

        year = ''                                                           # initialize 'year' as blank string
        backup_title = ''                                                   # initialize 'backup_title' as blank string
        y = re.search('(?P<year> \(\d{4}\))', filename)                     # Check for Year when used as part of a series name as suffix in ' (YYYY)' format.
        if y:                                                               # If Year found...
            year = y.group('year')                                          # Save to 'year' string
            
        m = re.search('\[(?P<backup_title>[^\. ].*?)\]', filename)          # Search for and capture the any string in square brackets that does not begin with either a period or space. The brackets themselves ae not captured, but ARE part of the match.
        if m:                                                               # If one or more matching strings is found...
            backup_title = m.group('backup_title')                          # Save the first capture group to the 'backup_title' string...
            filename = filename[:m.start()] + filename[m.end():]            # Then strip the match from the 'filename' string.
            
        else:                                                               # If no matching strings are found...
            m = re.search('\((?P<backup_title>[^\. ].*?)\)', filename)      # Repeat the above, this time using round brackets.
            if m:
                backup_title = m.group('backup_title')
                filename = filename[:m.start()] + filename[m.end():]
                
            else:                                                           # If no matching strings are found once again...
                m = re.search('{(?P<backup_title>[^\. ].*?)}', filename)    # Repeat again, this time using curly brackets.
                if m:
                    backup_title = m.group('backup_title')
                    filename = filename[:m.start()] + filename[m.end():]
                    
        filename = re.sub('(?:\[.*?\])|(?:\(.*?\))', ' ', filename)
        filename = filename.strip(' -')
        filename = re.sub('  (?:.*)', '', filename)
        # Strip any unclosed brackets and anything after them
        filename = re.sub('(.*)(?:[\(\[({].*)$', r'\1', filename)
        # Restore Year when part of series name in '(YYYY)' format.
        yearrestore = filename.strip(' -')
        self.name = yearrestore + year
        if self.name == year:
            self.name = backup_title
        # If we have a subber but no title!? then it must have been a title...
        if self.name == year and self.subberTag != '':
            self.name = self.subberTag + year
            self.subberTag = ''

    def _processFilename(self):
        filename = self.originalFilename
        filename = self.__testIfEp(filename)
        filename = self.__extractExtension(filename)
        filename = self.__cleanUpSpaces(filename)
        filename = self.__extractSpecialTags(filename)
        filename = self.__extractVideoProfile(filename)
        filename = self.__extractResolution(filename)
        filename = self.__extractHash(filename)
        remux = self.__checkIfRemux(filename)
        filename = self.__cleanUpBrackets(filename)
        filename = self.__extractSubber(filename, remux)
        filename = self.__extractVersion(filename)
        # Store the possible length of the title
        title_len = len(filename)
        filename, title_len = self.__extractVolumeIfPack(filename, title_len)
        filename = self.__extractPv(filename)
        if self.pv == -1:
            filename = self.__extractEpisodeNumbers(filename)
        # Truncate remainder to title length if needed (for where volume was found)
        filename = filename[:title_len]
        # Strip any trailing opening brackets
        filename = filename.rstrip('([{')
        self.__extractShowName(filename)