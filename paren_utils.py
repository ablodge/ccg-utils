import re


def mark_depth(text, bottom_up=False, lparen='(',rparen=')'):
    Paren_TopDown_RE = re.compile(f'^(?P<pre>([^{lparen}{rparen}])*)(?P<p>[{lparen}{rparen}])')
    Paren_BottomUp_RE = re.compile(f'[{lparen}](?P<inside>[^{lparen}{rparen}]*)[{rparen}]')
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
            p = x.group('p')
            if p == lparen:
                i += 1
                text = Paren_TopDown_RE.sub(s + f'<{i}>', text, 1)
            else:
                text = Paren_TopDown_RE.sub(s + f'</{i}>', text, 1)
                i -= 1
    return text


def unmark_depth(deep_text, lparen='(',rparen=')'):
    text = re.sub('<[0-9]+>', lparen, deep_text)
    text = re.sub('</[0-9]+>', rparen, text)
    return text


def depth_at(text, i, lparen='(',rparen=')'):
    depth = 0
    for j, ch in enumerate(text):
        if ch == rparen: depth -= 1
        if j == i: return depth
        if ch == lparen: depth += 1
    return -1


def paren_iter(text, bottom_up=False, lparen='(',rparen=')'):
    deep_text = mark_depth(text, bottom_up=bottom_up, lparen=lparen,rparen=rparen)
    j = 1
    while f'<{j}>' in deep_text:
        Paren_RE = re.compile(f'<{j}>(?P<text>.*?)</{j}>', re.DOTALL)
        for p in Paren_RE.finditer(deep_text):
            p = p.group('text')
            p = re.sub('<[0-9]+>', lparen, p)
            p = re.sub('</[0-9]+>', rparen, p)
            yield p
        j += 1


def test_parens(text, lparen='(',rparen=')'):
    depth = 0
    for ch in text:
        if ch == lparen: depth += 1
        if ch == rparen: depth -= 1
        if depth < 0: return False
    if not depth == 0: return False
    return True


def max_depth(text, lparen='(',rparen=')'):
    max = 0
    depth = 0
    for ch in text:
        if ch == lparen: depth += 1
        if max < depth: max = depth
        if ch == rparen: depth -= 1
    return max

