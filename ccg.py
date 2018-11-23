import re, sys, html
from ccgbank_format import CCGBank_Format as CB
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
    def test(text):
        # ignore comments
        text = '\n'.join([l for l in text.split('\n') if not l.strip().startswith('#')])
        if not text.strip().startswith('('): return False
        depth = 0
        for ch in text:
            if ch == '(': depth += 1
            if ch == ')': depth -= 1
            if depth < 0: return False
        if not depth == 0: return False
        return True

    @staticmethod
    def ccg_iter(text):
        text = re.sub('\n\s*ID=[0-9]+\s*\n', '\n\n', text)
        Split_RE = re.compile('\n\s*\n')
        for text in Split_RE.split(text):
            text = text.strip()
            if text and CCG.test(text):
                yield text

    def __str__(self):
        ccg = self.text
        for p in CB.Phrase_RE.finditer(ccg):
            tag = p.group('tag').replace('(','<p>').replace(')','</p>')
            ccg = ccg.replace(p.group(), tag)
        for w in CB.Word_RE.finditer(ccg):
            tag = w.group('tag').replace('(','<p>').replace(')','</p>')
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
        ccg = ccg.replace(')','}')
        ccg = ccg.replace('<p>', '(').replace('</p>', ')')

        return ccg


def main():
    test_file = r'test-data/ccg.txt'

    with open(test_file, 'r', encoding='utf8') as f:
        for ccg in CCG.ccg_iter(f.read()):
            ccg = CCG(ccg)
            print(ccg)



if __name__ == "__main__":
    main()
