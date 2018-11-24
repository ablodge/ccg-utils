import re, sys
from ccg_format import CCGBank, Readible
import paren_utils

TAG_SET = set()
ARG_STRUCTURE = set()


class CCG:
    def __init__(self, text):
        # remove comments
        self.text = '\n'.join([l for l in text.split('\n') if l.strip() and not l.strip().startswith('#')])

        self.Format = Readible if Readible.test(self.text) else CCGBank if CCGBank.test(self.text) else None

    def words(self):
        return self.Format.words(self.text)

    def phrases(self):
        return self.Format.phrases(self.text)

    def words_and_indices(self):
        return self.Format.words_and_indices(self.text)

    def phrases_and_indices(self):
        return self.Format.phrases_and_indices(self.text)

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
            ccg = ccg.replace('{','-LBR-').replace('}','-RBR-')
            ccg = ccg.replace('(','{').replace(')','}')
            for p in CCGBank.Phrase_RE.finditer(ccg):
                tag = p.group('tag').replace('{','(').replace('}',')')
                ccg = ccg.replace(p.group(), tag)
            for w in CCGBank.Word_RE.finditer(ccg):
                tag = w.group('tag').replace('{','(').replace('}',')')
                word = w.group('word').replace('{','(').replace('}',')')
                ccg = ccg.replace(w.group(), tag+' '+word)
            max = paren_utils.max_depth(ccg, lparen='{',rparen='}')
            ccg = paren_utils.mark_depth(ccg, lparen='{',rparen='}')
            j=1
            while j <= max:
                tabs = ''.join('    ' for i in range(j-1))
                ccg = ccg.replace(f'<{j}>', '\n'+tabs+'{')
                j += 1
            ccg = re.sub(r'</[0-9]+>','}', ccg)
            ccg = ccg.replace('-LBR-','{').replace('-RBR-','}')
            return ccg
        else:
            return self.text

    @staticmethod
    def test(ccg):
        Formats = [Readible, CCGBank]
        for F in Formats:
            if F.test(ccg):
                return True
        return False

def main():
    input_file = r'test-data/ccg.txt'
    if len(sys.argv) > 1:
        input_file = sys.argv[1]

    with open(input_file, 'r', encoding='utf8') as f:
        for ccg in CCG.ccg_iter(f.read()):
            ccg = CCG(ccg)
            print(ccg)



if __name__ == "__main__":
    main()
