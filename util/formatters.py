from pygments.formatter import Formatter
import hashlib
import random
import re
from spellchecker import SpellChecker

class TokenFormatter(Formatter):
    def __init__(self):
        rstr = str(random.randint(0,10000000))
        self.hash = hashlib.sha224(rstr.encode('utf-8')).hexdigest()
        self.spell = SpellChecker()

    def format(self, tokensource, outfile):
        for ttype, value in tokensource:
            regex = r"(\s|#)+"
            strings = value.split(" ")
            strings = re.split(regex, value) #.split("[\\s@&.?$+-]+")
            print(strings)

            for _str in strings:
                # if regez failed
                if _str == None:
                    continue
                # misspelled = self.spell.unknown([_str])
                style = "Style.Default"
                # Check if we have a comment, want to spellcheck text, and there is a spelling error 
                if 'Comment' in str(ttype) and len(re.findall(regex, _str)) == 0 and len(self.spell.unknown([_str])) >= 1:
                    style = "style.SpellingError"
                outfile.write(f"[{self.hash}{self.hash}{ttype}|{style}{self.hash}]{_str}")