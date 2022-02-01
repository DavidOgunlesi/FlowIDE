from pygments.formatter import Formatter
import hashlib
import random
from spellchecker import SpellChecker

class TokenFormatter(Formatter):
    def __init__(self):
        rstr = str(random.randint(0,10000000))
        self.hash = hashlib.sha224(rstr.encode('utf-8')).hexdigest()
        self.spell = SpellChecker()

    def format(self, tokensource, outfile):
        for ttype, value in tokensource:
            strings = value[1:].split(" ")
            misspelled = self.spell.unknown(strings)
            style = "Style.Default"
            if len(misspelled) >= 1 and 'Comment' in str(ttype):
                style = "style.SpellingError"
            outfile.write(f"[{self.hash}{self.hash}{ttype}|{style}{self.hash}]{value}")