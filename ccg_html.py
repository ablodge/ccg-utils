
from ccgbank_format import CCGBank_Format as CB
from ccg import CCG
import re

class CCG_HTML:

    @staticmethod
    def tohtml(ccg):
        WORDS = []
        for j,w in enumerate(CB.words(ccg)):
            WORDS.append(f'<td><span class="word" tok-id="{j}"><span class="tok">{j}/</span>{w.word()}</span></td>')
        TAGS = []
        for j,w in enumerate(CB.words(ccg)):
            tag = w.tag()
            TAGS.append(f'<td class="ccg-phrase" colspan="1"><span class="ccg-tag" tok-id="{j}">{tag}</span></td>')
        PHRASES = [[]]
        taken = set()
        for p,i in zip(CB.phrases(ccg),CB.phrase_indices(ccg)):
            start, end = int(i.split('-')[0]), int(i.split('-')[1])
            tag = p.tag()
            combinator = p.combinator().replace('>','&gt;').replace('<','&lt;')
            for n in range(start, end + 1):
                if n in taken:
                    PHRASES.append([])
                    taken = set()
            l = f'<td class="ccg-phrase" colspan="{end-start+1}" span="{start}:{end}">{tag}<span class="ccg-combinator">{combinator}</span></td>'
            PHRASES[-1].append(l)
            for n in range(start,end+1):
                taken.add(n)
        # add empty columns
        Span_RE = re.compile('span="(?P<a>[0-9]+):(?P<b>[0-9]+)"')
        for i, row in enumerate(PHRASES):
            span_end = 0
            for j, con in enumerate(row):
                x = Span_RE.search(con)
                a = int(x.group('a'))
                b = int(x.group('b'))
                if a > span_end:
                    PHRASES[i][j] = f'<td class="ccg-empty" colspan="{a-span_end}" span="{span_end}:{a}"/>' + PHRASES[i][j]
                span_end = b

        html_elems = []
        html_elems += ['<div class="ccg-container">']
        html_elems += ['<table class="visccg wordsbelow"><tbody>']
        ccg_parse = ['<tr class="ccg-phrases">' + ''.join(p) + '</tr>' for p in PHRASES]
        ccg_parse.reverse()
        html_elems += ccg_parse
        html_elems += ['<tr class="ccg-tags">'] + TAGS + ['</tr>']
        html_elems += ['<tr class="ccg-words">'] + WORDS + ['</tr>']
        html_elems += ['</tbody></table>']
        html_elems += ['</div>']
        return '\n'.join(html_elems)

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


def main():
    ccg = r'''
(<T S[dcl] 1 2> (<T S/S 0 2> (<T S/S 0 2> (<L (S/S)/NP IN IN In (S/S)/NP>) (<T NP 0 2> (<L NP/N DT DT the NP/N>) (<L N NN NN story N>) ) ) (<L , , , , ,>) ) (<T S[dcl] 1 2> (<T NP 0 1> (<T N 1 2> (<L N/N NN NN evildoer N/N>) (<T N 1 2> (<L N/N NNP NNP Cruella N/N>) (<T N 1 2> (<L N/N IN IN de N/N>) (<L N NNP NNP Vil N>) ) ) ) ) (<T S[dcl]\NP 0 2> (<L (S[dcl]\NP)/NP VBZ VBZ makes (S[dcl]\NP)/NP>) (<T NP 0 2> (<L NP/N DT DT no NP/N>) (<T N 0 2> (<L N/(S[to]\NP) NN NN attempt N/(S[to]\NP)>) (<T S[to]\NP 0 2> (<T S[to]\NP 0 2> (<L (S[to]\NP)/(S[b]\NP) TO TO to (S[to]\NP)/(S[b]\NP)>) (<T S[b]\NP 0 2> (<L (S[b]\NP)/NP VB VB conceal (S[b]\NP)/NP>) (<T NP 0 2> (<L NP/(N/PP) PRP$ PRP$ her NP/(N/PP)>) (<T N/PP 0 2> (<L N/PP NN NN glee N/PP>) (<T (N/PP)\(N/PP) 1 2> (<L conj CC CC and conj>) (<T N/PP 0 2> (<L (N/PP)/PP NN NN lack (N/PP)/PP>) (<T PP 0 2> (<L PP/NP IN IN of PP/NP>) (<T NP 0 1> (<L N NN NN conscience N>) ) ) ) ) ) ) ) ) (<L . . . . .>) ) ) ) ) ) ) 
    '''

    button = '<button class="expand">CCG parse ▲</button><br/>'
    print(CCG_HTML.tohtml(ccg))


if __name__ == "__main__":
    main()
