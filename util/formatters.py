from pygments.formatter import Formatter
import hashlib
import random

class TokenFormatter(Formatter):
    def __init__(self):
        rstr = str(random.randint(0,10000000));
        self.hash = hashlib.sha224(rstr.encode('utf-8')).hexdigest()

    def format(self, tokensource, outfile):
        for ttype, value in tokensource:
            outfile.write(f"[{self.hash}{self.hash}{ttype}{self.hash}]{value}")