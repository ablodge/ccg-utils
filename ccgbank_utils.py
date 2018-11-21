
import re, paren_utils

class CCGBankUtils:
    # <L N NN NN question N>
    Word_RE = re.compile('<L (?P<tag>[^\s>]+) (?P<pos>[^\s>]+) [^\s>]+ (?P<word>[^\s>]+) [^\s>]+>')
    # <T NP 0 2>
    Phrase_RE = re.compile('<T (?P<tag>[^\s>]+) (?P<head>[^\s>]+) (?P<children>[^\s>]+)>')

    @staticmethod
    def toCoNLL(ccg):
        words = [(str(i+1),w.group('word'),'_',w.group('pos'),w.group('tag'),'_','_') for i,w in enumerate(CCGBankUtils.Word_RE.finditer(ccg))]
        phrases = [(i,'_','_','_',t,h,words[int(h)-1][1]) for i,t,h in zip(CCGBankUtils.phrase_indices(ccg),
                                                    CCGBankUtils.phrase_tags(ccg),
                                                    CCGBankUtils.phrase_heads(ccg))]
        return '\n'.join('\t'.join(x) for x in (words)) + '\n' + \
               '\n'.join('\t'.join(x) for x in (phrases)) + '\n'


    @staticmethod
    def words(ccg):
        for w in CCGBankUtils.Word_RE.finditer(ccg):
            yield w.group('word')

    @staticmethod
    def word_tags(ccg):
        for w in CCGBankUtils.Word_RE.finditer(ccg):
            yield w.group('tag')

    @staticmethod
    def pos(ccg):
        for w in CCGBankUtils.Word_RE.finditer(ccg):
            yield w.group('pos')

    @staticmethod
    def word_indices(ccg):
        for i in range(len(CCGBankUtils.Word_RE.findall(ccg))):
            yield i+1


    @staticmethod
    def phrase_tags(ccg):
        for t in CCGBankUtils._phrase_iter_bottom_up(ccg):
            p = CCGBankUtils.Phrase_RE.match(t)
            if not p: continue
            yield p.group('tag')


    @staticmethod
    def phrase_indices(ccg):
        ID_RE = re.compile('[*](?P<n>[0-9]+)[*]')
        for i in CCGBankUtils.word_indices(ccg):
            ccg = CCGBankUtils.Word_RE.sub(f'*{i}*', ccg, 1)
        for t in CCGBankUtils._phrase_iter_bottom_up(ccg):
            indices = [i.group('n') for i in ID_RE.finditer(t)]
            yield f'{indices[0]}-{indices[-1]}'


    @staticmethod
    def phrase_heads(ccg):
        Id_RE = re.compile('^[*](?P<n>[0-9]+)[*]$')
        for i in CCGBankUtils.word_indices(ccg):
            ccg = CCGBankUtils.Word_RE.sub(f'*{i}*', ccg, 1)

        for t in CCGBankUtils._phrase_iter_bottom_up(ccg):
            find_head = t
            while CCGBankUtils.Phrase_RE.match(find_head):
                h = CCGBankUtils.Phrase_RE.match(find_head).group('head')
                children = CCGBankUtils._phrase_children(find_head)
                find_head = children[0] if h == '0' else children[1]
            x = Id_RE.match(find_head)
            yield x.group('n')


    @staticmethod
    def _phrase_iter_bottom_up(ccg):
        tags = {}
        for t in re.finditer('<[LT] (?P<tag>[^\s>]+) .*?>', ccg):
            tag = t.group('tag')
            ccg = ccg.replace(tag, tag.replace('(', '{').replace(')', '}'))
            tags[tag.replace('(', '{').replace(')', '}')] = tag
        for s in paren_utils.paren_iter(ccg, bottom_up=True):
            p = CCGBankUtils.Phrase_RE.match(s)
            if not p: continue
            for tag in tags:
                s = s.replace(tag, tags[tag])
            yield s


    @staticmethod
    def _phrase_children(ccg_phrase):
        Head_RE = re.compile('<1>(?P<a>.*?)</1>( <1>(?P<b>.*?)</1>)?')
        p = CCGBankUtils.Phrase_RE.match(ccg_phrase)
        if not p:
            return []
        num_children = int(p.group('children'))
        ccg_phrase = CCGBankUtils._mark_depth(ccg_phrase)
        x = Head_RE.search(ccg_phrase)
        a = x.group('a')
        a = paren_utils.unmark_depth(a)
        if num_children == 1:
            return [a]
        elif num_children == 2:
            b = x.group('b')
            b = paren_utils.unmark_depth(b)
            return [a, b]
        else:
            return []


    @staticmethod
    def _mark_depth(ccg):
        tags = {}
        for t in re.finditer('<[LT] (?P<tag>[^\s>]+) .*?>', ccg):
            tag = t.group('tag')
            ccg = ccg.replace(tag, tag.replace('(', '{').replace(')', '}'))
            tags[tag.replace('(', '{').replace(')', '}')] = tag
        ccg = paren_utils.mark_depth(ccg)
        for tag in tags:
            ccg = ccg.replace(tag, tags[tag])
        return ccg

