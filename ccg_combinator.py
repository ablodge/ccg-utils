
class CCG_Combinator:

    @staticmethod
    def get_combinator_unary(before_tag, after_tag):
        TR1_RE = re.compile(r'(?P<T1>\S+)/[(](?P<T2>\S+)\\(?P<X>\S+)[)]')
        TR2_RE = re.compile(r'(?P<T1>\S+)\\[(](?P<T2>\S+)/(?P<X>\S+)[)]')

        before_tag = CCGTagUtils.remove_features(before_tag)
        after_tag = CCGTagUtils.remove_features(after_tag)
        # Type Raising
        tr = TR1_RE.match(after_tag)
        if tr and tr.group('T1') == tr.group('T2'):
            X = tr.group('X')
            if X in [before_tag, f'({before_tag})']:
                return 'TR>'
        tr = TR2_RE.match(after_tag)
        if tr and tr.group('T1') == tr.group('T2'):
            X = tr.group('X')
            if X in [before_tag, f'({before_tag})']:
                return 'TR<'
        # Raising to NP
        if before_tag == 'N' and after_tag == 'NP':
            return 'NP'
        # Clauses
        if before_tag in ['S/NP', 'S\\NP']:
            if after_tag in ['N\\N', 'NP\\NP']:
                return 'Rel'
            if after_tag in ['S\\S', 'S/S']:
                return 'AdvCl'
            if after_tag == 'NP':
                return 'NomCl'
        print('U?', before_tag, '=>', after_tag)
        return '?'

    @staticmethod
    def get_combinator_binary(left_tag, right_tag, tag):
        FA1_RE = re.compile(r'(?P<X>\S+)[*]/[*](?P<Y>\S+)')
        FA2_RE = re.compile(r'(?P<X>\S+)[*]\\[*](?P<Y>\S+)')

        left_tag = CCGTagUtils.remove_features(left_tag)
        right_tag = CCGTagUtils.remove_features(right_tag)
        tag = CCGTagUtils.remove_features(tag)

        # Right Function Application
        fa = FA1_RE.match(CCGTagUtils.mark_first_arg(left_tag))
        if fa and CCGTagUtils.clean_parens(fa.group('Y')) == right_tag \
                and CCGTagUtils.clean_parens(fa.group('X')) in tag:
            return '>'
        # Left Function Application
        fa = FA2_RE.match(CCGTagUtils.mark_first_arg(right_tag))
        if fa and CCGTagUtils.clean_parens(fa.group('Y')) == left_tag \
                and CCGTagUtils.clean_parens(fa.group('X'))  == tag:
            return '<'

        # Other
        if left_tag in ['.', ',', '?', ';', ':', 'LRB', 'RRB', 'RQU']:
            return left_tag
        if right_tag in ['.', ',', '?', ';', ':', 'LRB', 'RRB', 'RQU']:
            return right_tag
        if left_tag == 'conj' and tag in [f'{right_tag}\\{right_tag}', f'({right_tag})\\({right_tag})']:
            return 'conj'
        # Composition
        B_RE = re.compile(r'(?P<X>\S+)[*][\\/][*](?P<Y>\S+)')

        l = B_RE.match(CCGTagUtils.mark_first_arg(left_tag))
        r = B_RE.match(CCGTagUtils.mark_first_arg(right_tag))
        t = B_RE.match(CCGTagUtils.mark_first_arg(tag))
        if l and r and t:
            lx, ly = CCGTagUtils.clean_parens(l.group('X')), CCGTagUtils.clean_parens(l.group('Y'))
            rx, ry = CCGTagUtils.clean_parens(r.group('X')), CCGTagUtils.clean_parens(r.group('Y'))
            tx, ty = CCGTagUtils.clean_parens(t.group('X')), CCGTagUtils.clean_parens(t.group('Y'))
            if ly == rx and lx == tx and ry == ty:
                return 'B>'
            elif lx == ry and rx == tx and ly == ty:
                return 'B<'
        if right_tag == r'S\S' and tag == left_tag:
            return 'B<$'
        if left_tag == r'S/S' and tag == right_tag:
            return 'B>$'
        print('B?', left_tag, '+', right_tag, '=>', tag)
        return '?'
