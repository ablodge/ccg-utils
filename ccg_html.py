

class CCG_HTML:

    def elements_html(self):
        WORDS = []
        TAGS = []
        PHRASES = []
        CCG = self.elements().copy()

        for i, e in enumerate(CCG):
            if e == '(':
                CCG[i] = '<*>'
            elif e == ')':
                CCG[i] = '</*>'

        CCG = ''.join(CCG)

        # find words
        j = 0
        for word in CCGBankUtils.word_iter(CCG):
            w = word.group('word')
            tag = word.group('tag')
            tag = CCGTagUtils.clean_parens(tag)
            pos = word.group('pos')
            CCG = CCG.replace(word.group(), f'{j}={tag}', 1)
            tag = CCGTagUtils.to_html(tag)
            t = re.sub(r'<sub>.*?</sub>','',tag)
            t2 = re.sub(r'<args>.*?</args>', '', tag)
            t2 = t2.replace(r'<sub>', '[').replace('</sub>',']')
            if t.count('NP') >= 2:
                ARG_STRUCTURE.add(t2+' : '+w+' '+pos)

            WORDS.append(f'<td><word class="aligned" tok-id="{j}"><tok>{j}/</tok>{w}</word> </td>')
            TAGS.append(f'<td class="constit" colspan="1"><tag class="aligned" tok-id="{j}">{tag}</tag> </td>')
            j += 1

        # mark depth from inside out
        Parens_RE = re.compile('<\*>(?P<text>[^*]*)</\*>')
        i = 1
        while '<*>' in CCG:
            for p in Parens_RE.finditer(CCG):
                text = p.group('text')
                CCG = CCG.replace(p.group(), f'<{i}>{text}</{i}>', 1)
            i += 1
        max = i

        # Find Constituents from inside out
        j = 1
        while j <= max:
            PHRASES.append([])
            id_marker = lambda x, y: f'(?P<{x}>[0-9]+(:[0-9]+)?)=(?P<{y}>\S*?)'
            tag_pattern = CCGBankUtils.phrase_re().pattern
            Word_RE = re.compile(f'<{j}>{id_marker("a","tag")}</{j}>')
            Unary_RE = re.compile(f'<{j}>{tag_pattern} {id_marker("a","tag1")} ?</{j}>')
            Binary_RE = re.compile(f'<{j}>{tag_pattern} {id_marker("a","tag1")} {id_marker("b","tag2")} ?</{j}>')

            while re.search(f'<{j}>', CCG):
                regex = re.search(f'<{j}>.*?</{j}>', CCG).group()
                if Word_RE.match(regex):
                    a = Word_RE.match(regex).group('a')
                    tag = Word_RE.match(regex).group('tag')
                    CCG = Word_RE.sub(a + '=' + tag, CCG, 1)
                elif Unary_RE.match(regex):
                    tag = Unary_RE.match(regex).group('tag')
                    tag = CCGTagUtils.clean_parens(tag)
                    a = Unary_RE.match(regex).group('a')
                    CCG = Unary_RE.sub(a + '=' + tag, CCG, 1)
                    if ':' in a:
                        start, end = int(a.split(':')[0]), int(a.split(':')[1])
                        size = end - start
                    else:
                        start, end = int(a), int(a) + 1
                        size = 1
                    prev_tag = Unary_RE.match(regex).group('tag1')
                    combin = CCGTagUtils.get_combinator_unary(prev_tag, tag)
                    tag = CCGTagUtils.to_html(tag)
                    c = f'<td class="constit ccg-parse" colspan="{size}" span="{start}:{end}">{tag}<span class="combinator">{combin}</span></td>'
                    PHRASES[j - 1].append(c)
                elif Binary_RE.match(regex):
                    x = Binary_RE.match(regex)
                    tag = x.group('tag')
                    tag = CCGTagUtils.clean_parens(tag)
                    a = x.group('a')
                    b = x.group('b')
                    if ':' in a:
                        a = a.split(':')[0]
                    if ':' in b:
                        b = b.split(':')[1]
                    else:
                        b = str(int(b) + 1)
                    CCG = Binary_RE.sub(a + ':' + b + '=' + tag, CCG, 1)
                    size = int(b) - int(a)
                    tag1 = Binary_RE.match(regex).group('tag1')
                    tag2 = Binary_RE.match(regex).group('tag2')
                    combin = CCGTagUtils.get_combinator_binary(tag1, tag2, tag)
                    tag = CCGTagUtils.to_html(tag)
                    c = f'<td class="constit ccg-parse" colspan="{size}" span="{a}:{b}">{tag}<span class="combinator">{combin}</span></td>'
                    PHRASES[j - 1].append(c)

                else:
                    raise Exception('Parsing CCG error:', j, regex)
            j += 1
        Span_RE = re.compile('span="(?P<a>[0-9]+):(?P<b>[0-9]+)"')
        for i, row in enumerate(PHRASES):
            span_end = 0
            for j, con in enumerate(row):
                x = Span_RE.search(con)
                a = int(x.group('a'))
                b = int(x.group('b'))
                if a > span_end:
                    PHRASES[i][j] = f'<td colspan="{a-span_end}" span="{span_end}:{a}"/>' + PHRASES[i][j]
                span_end = b
        ccg_parse = ['<tr class="expand">' + ''.join(c) + '</tr>\n' for c in PHRASES]
        ccg_parse.reverse()
        html_elems = []
        html_elems += ['<button class="expand">CCG parse ▲</button><br/>']
        html_elems += ['<div class="scroll">']
        html_elems += ['<table class="visccg wordsbelow"><tbody>\n']
        html_elems += ccg_parse
        html_elems += ['<tr>\n'] + TAGS + ['</tr>\n']
        html_elems += ['<tr>\n'] + WORDS + ['</tr>\n']
        html_elems += ['</tbody></table>']
        html_elems += ['</div>']
        return html_elems

    # Example of ccg in html:
    #
    # <table class="visccg wordsabove">
    # <tbody>
    # 	<tr><td>the</td> <td>dog</td> <td>bit</td> <td>John</td> </tr>
    # 	<tr>
    # 		<td class="constit" colspan="1">NP/N</td>
    # 		<td class="constit" colspan="1">N</td>
    # 		<td class="constit" colspan="1">(S\NP)/NP</td>
    # 		<td class="constit" colspan="1">NP<sub>+proper</sub></td>
    # 	</tr>
    # 	<tr>
    # 		<td class="constit" colspan="2">NP
    # 			<span class="combinator">&gt;</span>
    # 		</td>
    # 	</tr>
    # 	<tr>
    # 		<td class="constit" colspan="2">S/(S\NP)
    # 			<span class="sem"> : λp . λy. ∃x. dog′(x) ∧ p(x,y)</span>
    # 			<span class="combinator">T&gt;</span>
    # 		</td>
    # 	</tr>
    # 	<tr>
    # 		<td class="constit" colspan="3">S/NP
    # 			<span class="combinator">B&gt;</span>
    # 		</td>
    # 	</tr>
    # 	<tr>
    # 		<td class="constit" colspan="4">S
    # 			<span class="combinator">&gt;</span>
    # 		</td>
    # 	</tr>
    # </tbody>
    # </table>

