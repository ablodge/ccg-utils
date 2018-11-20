import re


class CCGTagUtils:

    @staticmethod
    def clean_parens(tag):
        tag = CCGTagUtils.mark_depth(tag)
        max = CCGTagUtils.get_max_depth(tag)
        j = 1
        while j <= max:
            Left_RE = re.compile(f'^(?P<pre>(<[0-9]+>|[(])*)<{j}>(?P<a>.*?)</{j}>')
            Right_RE = re.compile(f'<{j}>(?P<a>.*?)</{j}>')
            Modifier_RE = re.compile(fr'<{j}>(?P<a>.*?)</{j}>(?P<slash>[/\\])<{j}>(?P<b>.*?)</{j}>')
            while re.search(f'<{j}>', tag):
                mod = Modifier_RE.search(tag)
                if mod and CCGTagUtils.remove_features(mod.group('a')) == CCGTagUtils.remove_features(mod.group('b')):
                    a = mod.group('a')
                    b = mod.group('b')
                    slash = mod.group('slash')
                    tag = tag.replace(mod.group(), f'({a}){slash}({b})')
                elif Left_RE.match(tag):
                    x = Left_RE.match(tag)
                    pre = x.group('pre')
                    a = x.group('a')
                    tag = tag.replace(x.group(), pre + a)
                elif Right_RE.search(tag):
                    x = Right_RE.search(tag)
                    a = x.group('a')
                    tag = tag.replace(x.group(), '(' + a + ')')
            j += 1
        tag = tag.replace(r'((S\NP)/NP)', r'(S\NP/NP)')
        tag = tag.replace(r'((S[to]\NP)/NP)', r'(S[to]\NP/NP)')
        tag = tag.replace(r'((S[b]\NP)/NP)', r'(S[b]\NP/NP)')
        tag = tag.replace(r'((S[ng]\NP)/NP)', r'(S[ng]\NP/NP)')
        tag = tag.replace(r'((S[adj]\NP)/NP)', r'(S[adj]\NP/NP)')
        # print(tag)
        return tag

    @staticmethod
    def to_html(tag):
        tag = CCGTagUtils.add_indices(tag)
        x = CCGTagUtils.mark_depth(tag)
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
    def mark_depth(tag):
        Paren_RE = re.compile('^(?P<pre>([^()])*)(?P<paren>[()])')
        i = 0
        while Paren_RE.match(tag):
            s = Paren_RE.match(tag).group('pre')
            p = Paren_RE.match(tag).group('paren')
            if p == '(':
                i += 1
                tag = Paren_RE.sub(s + f'<{i}>', tag, 1)
            else:
                tag = Paren_RE.sub(s + f'</{i}>', tag, 1)
                i -= 1
        return tag

    @staticmethod
    def get_max_depth(deep_tag):
        i = 1
        max = 0
        while f'<{i}>' in deep_tag:
            max = i
            i += 1
        if '<1>' not in deep_tag:
            return -1
        return max

    @staticmethod
    def unmark_depth(deep_tag):
        i = 1
        tag = deep_tag
        while f'<{i}>' in tag:
            tag = tag.replace(f'<{i}>', '(')
            tag = tag.replace(f'</{i}>', ')')
            i += 1
        return tag

    @staticmethod
    def mark_first_arg(tag):
        depth = 0
        index = -1
        for i, c in enumerate(tag):
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
            elif c in ['\\', '/'] and depth == 0:
                index = i
        if index > 0:
            return tag[:index] + '*' + tag[index] + '*' + tag[index + 1:]
        return tag

    @staticmethod
    def add_indices(tag):
        old_tag = tag
        tag = CCGTagUtils.mark_depth(tag)
        max = CCGTagUtils.get_max_depth(tag)
        tag = tag.replace('NP[expl]','*EXPL*')
        tag = tag.replace('NP[thr]', '*THR*')

        # get spans for each modifier pattern
        modifier_spans = []
        j = 1
        while j<=max:
            Modifier_RE = re.compile(fr'<{j}>(?P<a>.*?)</{j}>(?P<slash>[/\\])<{j}>(?P<b>.*?)</{j}>')
            for mod in Modifier_RE.finditer(tag):
                a = CCGTagUtils.remove_features(mod.group('a'))
                b = CCGTagUtils.remove_features(mod.group('b'))
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
        tag = CCGTagUtils.unmark_depth(tag)
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
