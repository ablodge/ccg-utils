
import re, paren_utils
from ccg_combinator import CCG_Combinator

class CCGBank_Format:
    # <L N NN NN question N>
    Word_RE = re.compile('<L (?P<tag>[^\s>]+) (?P<pos>[^\s>]+) [^\s>]+ (?P<word>[^\s>]+) [^\s>]+>')
    # <T NP 0 2>
    Phrase_RE = re.compile('<T (?P<tag>[^\s>]+) (?P<head>[^\s>]+) (?P<children>[^\s>]+)>')

    class Phrase:
        Children_RE = re.compile('<1>(?P<a>.*?)</1>( <1>(?P<b>.*?)</1>)?')

        def __init__(self, ccg_phrase):
            self.phrase = ccg_phrase
            self._match = CCGBank_Format.Phrase_RE.match(self.phrase)

        def tag(self):
            return self._match.group('tag').replace('{','(').replace('}',')')

        def children(self):
            num_children = int(self._match.group('children'))
            ccg_phrase = paren_utils.mark_depth(self.phrase)
            x = self.Children_RE.search(ccg_phrase)
            a = x.group('a')
            a = paren_utils.unmark_depth(a)
            if num_children == 1:
                a = CCGBank_Format.Phrase(a) if CCGBank_Format.Phrase_RE.match(a) else CCGBank_Format.Word(a)
                return [a]
            elif num_children == 2:
                b = x.group('b')
                if not b:
                    print(self.phrase, x.group())
                b = paren_utils.unmark_depth(b)
                a = CCGBank_Format.Phrase(a) if CCGBank_Format.Phrase_RE.match(a) else CCGBank_Format.Word(a)
                b = CCGBank_Format.Phrase(b) if CCGBank_Format.Phrase_RE.match(b) else CCGBank_Format.Word(b)
                return [a,b]
            else:
                return []

        def head(self):
            h = self._match.group('head')
            children = self.children()
            return children[1] if h=='1' else children[0]

        def combinator(self):
            children = self.children()
            if len(children) == 2:
                return CCG_Combinator.get_binary_combinator(children[0].tag(), children[1].tag(), self.tag())
            elif len(children) == 1:
                return CCG_Combinator.get_unary_combinator(children[0].tag(), self.tag())

    class Word:
        def __init__(self, ccg_word):
            self.text = ccg_word
            self._match = CCGBank_Format.Word_RE.match(self.text)

        def word(self):
            return self._match.group('word')

        def tag(self):
            return self._match.group('tag').replace('{','(').replace('}',')')

        def pos(self):
            return self._match.group('pos')

    @staticmethod
    def words(ccg):
        for w in CCGBank_Format.Word_RE.finditer(ccg):
            yield CCGBank_Format.Word(w.group())

    @staticmethod
    def word_indices(ccg):
        for i in range(len(CCGBank_Format.Word_RE.findall(ccg))):
            yield i+1

    @staticmethod
    def phrases(ccg):
        for t in re.finditer('<[LT] (?P<tag>[^\s>]+) .*?>', ccg):
            tag = t.group('tag')
            ccg = ccg.replace(f' {tag} ', ' '+tag.replace('(', '{').replace(')', '}')+' ')
        for s in paren_utils.paren_iter(ccg, bottom_up=True):
            p = CCGBank_Format.Phrase_RE.match(s)
            if not p: continue
            yield CCGBank_Format.Phrase(s)


    @staticmethod
    def phrase_indices(ccg):
        ID_RE = re.compile('[*](?P<n>[0-9]+)[*]')
        for i in CCGBank_Format.word_indices(ccg):
            ccg = CCGBank_Format.Word_RE.sub(f'*{i}*', ccg, 1)
        for p in CCGBank_Format.phrases(ccg):
            indices = [i.group('n') for i in ID_RE.finditer(p.phrase)]
            yield f'{indices[0]}-{indices[-1]}'



def main():
    ccg = r'''
    (<T S[dcl] 1 2> (<T S/S 0 2> (<T S/S 0 2> (<L (S/S)/NP IN IN In (S/S)/NP>) (<T NP 0 2> (<L NP/N DT DT the NP/N>) (<L N NN NN story N>) ) ) (<L , , , , ,>) ) (<T S[dcl] 1 2> (<T NP 0 1> (<T N 1 2> (<L N/N NN NN evildoer N/N>) (<T N 1 2> (<L N/N NNP NNP Cruella N/N>) (<T N 1 2> (<L N/N IN IN de N/N>) (<L N NNP NNP Vil N>) ) ) ) ) (<T S[dcl]\NP 0 2> (<L (S[dcl]\NP)/NP VBZ VBZ makes (S[dcl]\NP)/NP>) (<T NP 0 2> (<L NP/N DT DT no NP/N>) (<T N 0 2> (<L N/(S[to]\NP) NN NN attempt N/(S[to]\NP)>) (<T S[to]\NP 0 2> (<T S[to]\NP 0 2> (<L (S[to]\NP)/(S[b]\NP) TO TO to (S[to]\NP)/(S[b]\NP)>) (<T S[b]\NP 0 2> (<L (S[b]\NP)/NP VB VB conceal (S[b]\NP)/NP>) (<T NP 0 2> (<L NP/(N/PP) PRP$ PRP$ her NP/(N/PP)>) (<T N/PP 0 2> (<L N/PP NN NN glee N/PP>) (<T (N/PP)\(N/PP) 1 2> (<L conj CC CC and conj>) (<T N/PP 0 2> (<L (N/PP)/PP NN NN lack (N/PP)/PP>) (<T PP 0 2> (<L PP/NP IN IN of PP/NP>) (<T NP 0 1> (<L N NN NN conscience N>) ) ) ) ) ) ) ) ) (<L . . . . .>) ) ) ) ) ) ) 
    '''
    for w,i in zip(CCGBank_Format.words(ccg),CCGBank_Format.word_indices(ccg)):
        print(i, w.word(), w.tag(), w.pos())


    for p,i in zip(CCGBank_Format.phrases(ccg), CCGBank_Format.phrase_indices(ccg)):
        print(i, p.tag(),':', ' '.join(t.tag() for t in p.children()), p.combinator())


if __name__ == "__main__":
    main()
