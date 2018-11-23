import re
import paren_utils

class CCG_Tag:

    _Left_RE = re.compile(f'^<1>(?P<a>.*?)</1>')
    _Right_RE = re.compile(f'<1>(?P<a>.*?)</1>')
    _Modifier_RE = re.compile(fr'<1>(?P<a>.*?)</1>(?P<slash>[/\\])<1>(?P<b>.*?)</1>')

    @staticmethod
    def clean_parens(tag):
        marked_tag = paren_utils.mark_depth(tag)
        for t in paren_utils.paren_iter(f'({tag})', bottom_up=True):
            depth = paren_utils.depth_at(tag,tag.index(t))+1
            t = paren_utils.mark_depth(t)
            j = 2
            while f'<{j}>' in t:
                t = t.replace(f'<{j}>','(').replace(f'</{j}>',')')
                j+=1
            mod = CCG_Tag._Modifier_RE.match(t)
            if mod and CCG_Tag.remove_features(mod.group('a')) == CCG_Tag.remove_features(mod.group('b')):
                a = mod.group('a')
                b = mod.group('b')
                slash = mod.group('slash')
                marked_tag = marked_tag.replace(f'<{depth}>{a}</{depth}>{slash}<{depth}>{b}</{depth}>', f'({a}){slash}({b})', 1)
            elif CCG_Tag._Left_RE.search(t):
                x = CCG_Tag._Left_RE.match(t)
                a = x.group('a')
                marked_tag = marked_tag.replace(f'<{depth}>{a}</{depth}>', a, 1)
            elif CCG_Tag._Right_RE.search(t):
                x = CCG_Tag._Right_RE.search(t)
                a = x.group('a')
                marked_tag = marked_tag.replace(f'<{depth}>{a}</{depth}>', f'({a})', 1)

        return paren_utils.unmark_depth(marked_tag)

    @staticmethod
    def to_html(tag):
        tag = CCG_Tag.add_indices(tag)
        x = paren_utils.mark_depth(tag)
        Paren_RE = re.compile('<1>.*?</1>')
        while Paren_RE.search(x):
            x = Paren_RE.sub('X', x)
        arg_count = len(re.findall(r'[/\\]', x))

        if arg_count > 0:
            tag = tag + f'<args> : {arg_count}</args>'
        elif tag == 'conj':
            tag = 'conj<args> : 2</args>'

        tag = tag.replace('[', '<sub>').replace(']', '</sub>')
        return tag

    @staticmethod
    def add_indices(tag):
        old_tag = tag
        tag = paren_utils.mark_depth(tag)
        max = paren_utils.max_depth(tag)
        tag = tag.replace('NP[expl]','*EXPL*')
        tag = tag.replace('NP[thr]', '*THR*')

        # get spans for each modifier pattern
        modifier_spans = []
        j = 1
        while j<=max:
            Modifier_RE = re.compile(fr'<{j}>(?P<a>.*?)</{j}>(?P<slash>[/\\])<{j}>(?P<b>.*?)</{j}>')
            for mod in Modifier_RE.finditer(tag):
                a = CCG_Tag.remove_features(mod.group('a'))
                b = CCG_Tag.remove_features(mod.group('b'))
                if a == b and 'NP' in a:
                    modifier_spans.append((mod.start('a'), mod.end('a'), mod.start('b'), mod.end('b')))
            j += 1

        Cat_RE = re.compile(r'([^<>()/\\]+|</?[0-9]+>|.)')
        cats = [c.group() for c in Cat_RE.finditer(tag)]
        cat_indices = [c.start() for c in Cat_RE.finditer(tag)]
        CATS = cats.copy()

        i = 1
        for j, c in enumerate(CATS):
            if c.startswith('NP'):
                cats[j] = f'{c}.{i}'
                i += 1

        if re.match(r'^NP[/\\]NP[/\\]?', tag):
            cats[0] = 'NP.1'
            cats[2] = 'NP.1'


        # handle matching indices within a modifier
        modifier_memo = []
        for a_start, a_end, b_start, b_end in modifier_spans:
            for j, c in enumerate(CATS):
                if c.startswith('NP'):
                    me = cat_indices[j]
                    if a_start <= me < a_end:
                        x = re.match('.*[.](?P<n>[0-9]+)$', cats[j])
                        if x:
                            modifier_memo.append(int(x.group('n')))
                    elif b_start <= me < b_end:
                        m = modifier_memo.pop(0)
                        cats[j] = f'{c}.{m}'
        i = 1
        for j, c in enumerate(CATS):
            if c.startswith('NP'):
                x = re.match('.*[.](?P<n>[0-9]+)$', cats[j])
                if x and int(x.group('n')) > i:
                    cats[j] = f'{c}.{i}'
                    continue
                elif x and int(x.group('n')) < i:
                    continue
                i += 1

        tag = ''.join(cats)

        if tag.count('NP') < 2:
            tag = old_tag
        # fix parens for "want", "should", etc.
        # If nodes are the same but features are different,
        # remove parentheses around first half of expression.
        # This is important for getting number of args!
        j = 1
        while j <= max:
            Modifier_RE = re.compile(fr'<{j}>(?P<a>.*?)</{j}>(?P<slash>[/\\])<{j}>(?P<b>.*?)</{j}>')
            for mod in Modifier_RE.finditer(tag):
                a = mod.group('a')
                b = mod.group('b')
                slash = mod.group('slash')
                if a != b:
                    tag = tag.replace(mod.group(), f'{a}{slash}({b})')
            j+=1
        tag = paren_utils.unmark_depth(tag)
        obj_ctrl = re.match(r'[(]?S\[.*?\]\\NP.1[)]?/[(]S\[.*?\]\\NP.1[)]/NP.2', tag)
        obj_raise = re.match(r'[(]?S\[.*?\]\\NP.1[)]?/[(]S\[.*?\]\\NP.2/NP.3[)]', tag)
        if obj_ctrl:
            tag = tag.replace('NP.1)/NP.2','NP.2)/NP.2',1)
        if obj_raise:
            tag = tag.replace('NP.2/NP.3)','NP.2/NP.1)',1)

        r'S[adj]\NP.1/(S[to]\NP.2/NP.1)'
        tag = tag.replace('*EXPL*', 'NP[expl]')
        tag = tag.replace('*THR*', 'NP[thr]')
        return tag


    @staticmethod
    def remove_features(tag):
        return re.sub(r'\[.+?\]', '', tag)
