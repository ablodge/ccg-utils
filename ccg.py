import re, sys, html
from ccg_format import CCGBank, Readible
import paren_utils
from ccg_tag import CCG_Tag

TAG_SET = set()
ARG_STRUCTURE = set()


class CCG:
    def __init__(self, text):
        # remove comments
        self.text = '\n'.join([l for l in text.split('\n') if l.strip() and not l.strip().startswith('#')])
        # for t in re.finditer('<[LT] (?P<tag>[^\s>]+) [^>]*>', self.text):
        #     tag = t.group('tag')
        #     self.text = self.text.replace(tag, tag.replace('(', '<p>').replace(')','</p>'))


    @staticmethod
    def ccg_iter(text):
        text = re.sub('\n\s*ID=[0-9]+\s*\n', '\n\n', text)
        Split_RE = re.compile('\n\s*\n')
        for text in Split_RE.split(text):
            text = text.strip()
            if text and CCG.test(text):
                yield text

    def __str__(self):
        if CCGBank.test(self.text):
            ccg = self.text
            for p in CCGBank.Phrase_RE.finditer(ccg):
                tag = paren_utils.escape_parens(p.group('tag'))
                ccg = ccg.replace(p.group(), tag)
            for w in CCGBank.Word_RE.finditer(ccg):
                tag = paren_utils.escape_parens(w.group('tag'))
                word = w.group('word')
                ccg = ccg.replace(w.group(), tag+' '+word)
            max = paren_utils.max_depth(ccg)
            ccg = paren_utils.mark_depth(ccg)
            j=1
            while j <= max:
                tabs = ''.join('    ' for i in range(j-1))
                ccg = ccg.replace(f'<{j}>', '\n'+tabs+'{')
                j += 1

            ccg = paren_utils.unmark_depth(ccg)
            ccg = re.sub(r'(?<!\\)[)]','}', ccg)
            ccg = paren_utils.unescape_parens(ccg)
            return ccg
        else:
            return self.text



    @staticmethod
    def test(ccg):
        Formats = [CCGBank, Readible]
        for F in Formats:
            if F.test(ccg):
                return True
        return False

def main():
    test_file = r'test-data/ccg.txt'

    with open(test_file, 'r', encoding='utf8') as f:
        for ccg in CCG.ccg_iter(f.read()):
            ccg = CCG(ccg)
            print(ccg)



if __name__ == "__main__":
    main()
