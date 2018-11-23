import re
from ccg_tag import CCG_Tag


class CCG_Combinator:
    # Type Raising
    TypeRaisingRight_RE = re.compile(r'(?P<T1>\S+)/[(](?P<T2>\S+)\\(?P<X>\S+)[)]')
    TypeRaisingLeft_RE = re.compile(r'(?P<T1>\S+)\\[(](?P<T2>\S+)/(?P<X>\S+)[)]')
    # Function Application
    FunctionApplRight_RE = re.compile(r'(?P<X>\S+)[*]/[*](?P<Y>\S+)')
    FunctionApplLeft_RE = re.compile(r'(?P<X>\S+)[*]\\[*](?P<Y>\S+)')
    # Composition
    Composition_RE = re.compile(r'(?P<X>\S+)[*][\\/][*](?P<Y>\S+)')

    @staticmethod
    def _mark_first_arg(tag):
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
    def get_unary_combinator(before_tag, after_tag):

        before_tag = CCG_Tag.remove_features(before_tag)
        after_tag = CCG_Tag.remove_features(after_tag)
        # Type Raising
        tr = CCG_Combinator.TypeRaisingRight_RE.match(after_tag)
        if tr and tr.group('T1') == tr.group('T2'):
            X = tr.group('X')
            if X in [before_tag, f'({before_tag})']:
                return 'TR>'
        tr = CCG_Combinator.TypeRaisingLeft_RE.match(after_tag)
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
    def get_binary_combinator(left_tag, right_tag, tag):

        left_tag = CCG_Tag.remove_features(left_tag)
        right_tag = CCG_Tag.remove_features(right_tag)
        tag = CCG_Tag.remove_features(tag)

        # Right Function Application
        fa = CCG_Combinator.FunctionApplRight_RE.match(CCG_Combinator._mark_first_arg(left_tag))
        if fa and fa.group('Y') in [right_tag, f'({right_tag})'] \
                and fa.group('X') in [tag, f'({tag})']:
            return '>'
        # Left Function Application
        fa = CCG_Combinator.FunctionApplLeft_RE.match(CCG_Combinator._mark_first_arg(right_tag))
        if fa and fa.group('Y') in [left_tag, f'({left_tag})'] \
                and fa.group('X') in [tag, f'({tag})']:
            return '<'

        # Other
        if left_tag in ['.', ',', '?', ';', ':', 'LRB', 'RRB', 'RQU']:
            return left_tag
        if right_tag in ['.', ',', '?', ';', ':', 'LRB', 'RRB', 'RQU']:
            return right_tag
        if left_tag == 'conj' and tag in [f'{right_tag}\\{right_tag}', f'({right_tag})\\({right_tag})']:
            return 'conj'
        # Composition

        l = CCG_Combinator.Composition_RE.match(CCG_Combinator._mark_first_arg(left_tag))
        r = CCG_Combinator.Composition_RE.match(CCG_Combinator._mark_first_arg(right_tag))
        t = CCG_Combinator.Composition_RE.match(CCG_Combinator._mark_first_arg(tag))
        if l and r and t:
            lx, ly = l.group('X'), l.group('Y')
            rx, ry = r.group('X'), r.group('Y')
            tx, ty = t.group('X'), t.group('Y')
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

