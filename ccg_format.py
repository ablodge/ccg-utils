
import re, paren_utils
from ccg_combinator import CCG_Combinator

class CCGBank:
    # <L N NN NN question N>
    Word_RE = re.compile('<L (?P<tag>[^\s>]+) (?P<pos>[^\s>]+) [^\s>]+ (?P<word>[^\s>]+) [^\s>]+>')
    # <T NP 0 2>
    Phrase_RE = re.compile('<T (?P<tag>[^\s>]+) (?P<head>[^\s>]+) (?P<children>[^\s>]+)>')

    class Phrase:
        Children_RE = re.compile('<1>(?P<a>.*?)</1>( <1>(?P<b>.*?)</1>)?')

        def __init__(self, ccg_phrase):
            self.phrase = ccg_phrase
            self._match = CCGBank.Phrase_RE.match(self.phrase)

        def tag(self):
            return self._match.group('tag')

        def children(self):
            num_children = int(self._match.group('children'))
            ccg_phrase = paren_utils.mark_depth(self.phrase)
            x = self.Children_RE.search(ccg_phrase)
            a = x.group('a')
            a = paren_utils.unmark_depth(a)
            if num_children == 1:
                a = CCGBank.Phrase(a) if CCGBank.Phrase_RE.match(a) else CCGBank.Word(a)
                return [a]
            elif num_children == 2:
                b = x.group('b')
                if not b:
                    print(self.phrase, x.group())
                b = paren_utils.unmark_depth(b)
                a = CCGBank.Phrase(a) if CCGBank.Phrase_RE.match(a) else CCGBank.Word(a)
                b = CCGBank.Phrase(b) if CCGBank.Phrase_RE.match(b) else CCGBank.Word(b)
                return [a,b]
            else:
                return []

        def head(self):
            return self._match.group('head')

        def semantics(self):
            return ''

        def combinator(self):
            children = self.children()
            if len(children) == 2:
                return CCG_Combinator.get_binary_combinator(children[0].tag(), children[1].tag(), self.tag())
            elif len(children) == 1:
                return CCG_Combinator.get_unary_combinator(children[0].tag(), self.tag())

    class Word:
        def __init__(self, ccg_word):
            self.text = ccg_word
            self._match = CCGBank.Word_RE.match(self.text)

        def word(self):
            return self._match.group('word').replace('-LBR-','{').replace('-RBR-','}')

        def tag(self):
            return self._match.group('tag')

        def pos(self):
            return self._match.group('pos')

        def semantics(self):
            return ''

    @staticmethod
    def words(ccg):
        for w in CCGBank.Word_RE.finditer(ccg):
            yield CCGBank.Word(w.group())

    @staticmethod
    def words_and_indices(ccg):
        for i,w in enumerate(CCGBank.words(ccg)):
            yield w,i

    @staticmethod
    def phrases(ccg):
        ccg = ccg.replace('{', '-LBR-').replace('}', '-RBR-')
        ccg = ccg.replace('(', '{').replace(')', '}')
        for t in re.finditer('<[LT] (?P<tag>[^\s>]+) .*?>', ccg):
            tag = t.group('tag')
            ccg = ccg.replace(f' {tag} ', ' '+tag.replace('{','(').replace('}',')')+' ')
        for s in paren_utils.paren_iter(ccg, bottom_up=True):
            p = CCGBank.Phrase_RE.match(s)
            if not p: continue
            yield CCGBank.Phrase(s)


    @staticmethod
    def phrases_and_indices(ccg):
        phrases = CCGBank.phrases(ccg)
        ID_RE = re.compile('[*](?P<n>[0-9]+)[*]')
        for i in CCGBank.word_indices(ccg):
            ccg = CCGBank.Word_RE.sub(f'*{i}*', ccg, 1)
        for p in CCGBank.phrases(ccg):
            indices = [i.group('n') for i in ID_RE.finditer(p.phrase)]
            yield next(phrases), '{indices[0]}-{indices[-1]}'

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

class Readible:

    Word_RE = re.compile('{(?P<tag>[^\s{}]+) (?P<word>[^\s{}]+|"[^"]*?")( (?P<semantics>[^\s{}]+|"[^"]*?"))?}')
    Phrase_RE = re.compile('(?P<tag>[^\s{}]+)( (?P<semantics>[^\s{}]+|"[^"]*?"))?\s*{')

    class Phrase:
        Children_RE = re.compile('<1>(?P<a>.*?)</1>(\s*<1>(?P<b>.*?)</1>)?', re.DOTALL)

        def __init__(self, ccg_phrase):
            self.phrase = ccg_phrase
            self._match = Readible.Phrase_RE.match(self.phrase)

        def tag(self):
            return self._match.group('tag')

        def children(self):
            ccg_phrase = paren_utils.mark_depth(self.phrase, lparen='{',rparen='}')
            num_children = ccg_phrase.count('<1>')
            x = self.Children_RE.search(ccg_phrase)
            a = x.group('a')
            a = paren_utils.unmark_depth(a, lparen='{',rparen='}')
            if num_children == 1:
                a = Readible.Phrase(a) if '{' in a else Readible.Word('{'+a+'}')
                return [a]
            elif num_children == 2:
                a = Readible.Phrase(a) if '{' in a else Readible.Word('{'+a+'}')
                b = x.group('b')
                if not b:
                    print(self.phrase, x.group())
                b = paren_utils.unmark_depth(b, lparen='{',rparen='}')
                b = Readible.Phrase(b) if '{' in b else Readible.Word('{'+b+'}')
                return [a, b]
            else:
                return []

        def semantics(self):
            s = self._match.group('semantics')
            return s.replace('"','') if s else ''

        def combinator(self):
            children = self.children()
            if len(children) == 2:
                return CCG_Combinator.get_binary_combinator(children[0].tag(), children[1].tag(), self.tag())
            elif len(children) == 1:
                return CCG_Combinator.get_unary_combinator(children[0].tag(), self.tag())

    class Word:
        def __init__(self, ccg_word):
            self.text = ccg_word
            self._match = Readible.Word_RE.match(self.text)

        def word(self):
            return self._match.group('word')

        def tag(self):
            return self._match.group('tag')

        def pos(self):
            return ''

        def semantics(self):
            s = self._match.group('semantics')
            return s.replace('"','') if s else ''

    @staticmethod
    def words(ccg):
        for w in Readible.Word_RE.finditer(ccg):
            word = w.group()
            yield Readible.Word(word)

    @staticmethod
    def phrases(ccg):
        for s in paren_utils.paren_iter(ccg, bottom_up=True, lparen='{',rparen='}'):
            if Readible.Phrase_RE.match(s):
                yield Readible.Phrase(s)

    @staticmethod
    def words_and_indices(ccg):
        for i,w in enumerate(Readible.words(ccg)):
            yield w,i

    @staticmethod
    def phrases_and_indices(ccg):
        phrases = Readible.phrases(ccg)
        ccg_ids = ccg
        ID_RE = re.compile('[*](?P<n>[0-9]+)[*]')
        for i,w in enumerate(Readible.words(ccg)):
            word = w.text
            ccg_ids = ccg_ids.replace(word, f'{{*{i}*}}', 1)
        for s in paren_utils.paren_iter(ccg_ids, bottom_up=True, lparen='{',rparen='}'):
            if Readible.Phrase_RE.match(s):
                indices = [i.group('n') for i in ID_RE.finditer(s)]
                yield (next(phrases), f'{indices[0]}-{indices[-1]}')

    @staticmethod
    def test(text):
        # ignore comments
        text = '\n'.join([l for l in text.split('\n') if not l.strip().startswith('#')])
        if not text.strip().startswith('{'): return False
        depth = 0
        for ch in text:
            if ch == '{': depth += 1
            if ch == '}': depth -= 1
            if depth < 0: return False
        if not depth == 0: return False
        return True





def main():
    ccg = r'''
{S[dcl] "chase(DOGS,CATS)"
	{NP "DOGS"
		{N dogs "DOGS"} }
	{S[dcl]\NP "\lambda y.chase(y,CATS)"
		{S[dcl]\NP/NP chase "\lambda x\lambda y.chase(y,x)"}
		{NP "CATS"
			{N cats "CATS"} } } }
'''
    # for w in Readible.words(ccg):
    #     print(w.word(), w.tag(), w.pos(), w.text)


    for w,i in Readible.words_and_indices(ccg):
        print(i, w.word(), w.tag(), w.pos(), w.text)

    for p,i in Readible.phrases_and_indices(ccg):
        print(i, p.tag(), p.semantics(),':',' '.join(t.tag() for t in p.children()), p.combinator())


if __name__ == "__main__":
    main()
