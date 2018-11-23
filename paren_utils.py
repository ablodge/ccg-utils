import re

Paren_TopDown_RE = re.compile('^(?P<pre>([^()])*)(?P<inside>[()])')
Paren_BottomUp_RE = re.compile('[(](?P<inside>[^()]*)[)]')


def mark_depth(text, bottom_up=False):
    text = _ignore_escaped_parens(text)
    if bottom_up:
        i = 1
        while Paren_BottomUp_RE.search(text):
            for p in Paren_BottomUp_RE.finditer(text):
                s = p.group('inside')
                text = text.replace(p.group(), f'<{i}>{s}</{i}>', 1)
            i += 1
    else:
        i = 0
        while Paren_TopDown_RE.match(text):
            x = Paren_TopDown_RE.match(text)
            s = x.group('pre')
            p = x.group('inside')
            if p == '(':
                i += 1
                text = Paren_TopDown_RE.sub(s + f'<{i}>', text, 1)
            else:
                text = Paren_TopDown_RE.sub(s + f'</{i}>', text, 1)
                i -= 1
    text = _fix_escaped_parens(text)
    return text


def unmark_depth(deep_text):
    text = re.sub('<[0-9]+>', '(', deep_text)
    text = re.sub('</[0-9]+>', ')', text)
    return text


def depth_at(text, i):
    text = _ignore_escaped_parens(text)
    depth = 0
    for j, ch in enumerate(text):
        if ch == ')': depth -= 1
        if j == i: return depth
        if ch == '(': depth += 1
    return -1


def paren_iter(text, bottom_up=False):
    deep_text = mark_depth(text, bottom_up)
    j = 1
    while f'<{j}>' in deep_text:
        Paren_RE = re.compile(f'<{j}>(?P<text>.*?)</{j}>', re.DOTALL)
        for p in Paren_RE.finditer(deep_text):
            p = p.group('text')
            p = re.sub('<[0-9]+>', '(', p)
            p = re.sub('</[0-9]+>', ')', p)
            yield p
        j += 1


def test_parens(text):
    text = _ignore_escaped_parens(text)
    depth = 0
    for ch in text:
        if ch == '(': depth += 1
        if ch == ')': depth -= 1
        if depth < 0: return False
    if not depth == 0: return False
    return True


def max_depth(text):
    text = _ignore_escaped_parens(text)
    max = 0
    depth = 0
    for ch in text:
        if ch == '(': depth += 1
        if max < depth: max = depth
        if ch == ')': depth -= 1
    return max


def escape_parens(text):
    return text.replace('(',r'\(').replace(')',r'\)')


def unescape_parens(text):
    return text.replace(r'\(','(').replace(r'\)',')')


def _ignore_escaped_parens(text):
    return text.replace(r'\(','*L_PAREN*').replace(r'\)','*R_PAREN*')

def _fix_escaped_parens(text):
    return text.replace('*L_PAREN*',r'\(').replace('*R_PAREN*',r'\)')
