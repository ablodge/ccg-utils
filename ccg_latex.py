
from ccgbank_format import CCGBank_Format as CB
from ccg import CCG
import re

class CCG_HTML:

    @staticmethod
    def latex(ccg):
        words = [w for w in CB.words(ccg)]
        WORDS = ' & '.join(w.word() for w in words)+r'\\'
        LINE1 = ' & '.join('\ccgline{1}{}' for w in words)+r'\\'
        TAGS = ' & '.join(w.tag().replace('\\', r' \backslash ') for w in words)+r'\\'
        PHRASES = [[]]
        LINES = [[]]
        j = 0
        for p,i in zip(CB.phrases(ccg), CB.phrase_indices(ccg)):
            start, end = int(i.split('-')[0])-1, int(i.split('-')[1])-1
            size = end-start+1
            tag = p.tag().replace('\\', r'\backslash ')
            combinator = p.combinator()
            if start <= j:
                while j < len(words):
                    PHRASES[-1].append('')
                    LINES[-1].append('')
                    j += 1
                PHRASES.append([])
                LINES.append([])
                j = 0
            while start > j:
                PHRASES[-1].append('')
                LINES[-1].append('')
                j += 1
            PHRASES[-1].append(fr'\phrase{{{size}}}{{{tag}}}')
            LINES[-1].append(fr'\ccgline{{{size}}}{{{combinator}}}')
            j += size
        PHRASES = [' & '.join(p) for p in PHRASES]
        LINES = [' & '.join(l) for l in LINES]
        cols = ' '.join('c' for i in words)
        latex_elems = [r'\resizebox{\columnwidth}{!}{']
        latex_elems += [r'\begin{tabular}{ '+cols+' }']
        latex_elems += [WORDS]
        latex_elems += [LINE1]
        latex_elems += [TAGS]
        for phrases, lines in zip(PHRASES, LINES):
            latex_elems += [lines + r'\\']
            latex_elems += [phrases+r'\\']
        latex_elems += [r'\end{tabular}']
        latex_elems += ['}']
        return '\n'.join(latex_elems)

# \newcommand{\phrase}[2]{\multicolumn{#1}{c}{#2}}
# \newcommand{\ccgline}[2]{\multicolumn{#1}{c}{\hrulefill \raisebox{-.30ex}{\tiny \mbox{#2}}}}}
# \begin{tabular}{ c c c }
#  John & likes & Mary \\
# \ccgline{1}{} & \ccgline{1}{} & \ccgline{1}{}\\
#  NP & S\NP/NP & NP \\
# & \ccgline{2}{$>$}\\
# & \phrase{2}{S\NP}\\
# \ccgline{3}{$<$}\\
# \phrase{3}{S}
# \end{tabular}

def main():
    ccg = r'''
(<T S[dcl] 1 2> (<T S/S 0 2> (<T S/S 0 2> (<L (S/S)/NP IN IN In (S/S)/NP>) (<T NP 0 2> (<L NP/N DT DT the NP/N>) (<L N NN NN story N>) ) ) (<L , , , , ,>) ) (<T S[dcl] 1 2> (<T NP 0 1> (<T N 1 2> (<L N/N NN NN evildoer N/N>) (<T N 1 2> (<L N/N NNP NNP Cruella N/N>) (<T N 1 2> (<L N/N IN IN de N/N>) (<L N NNP NNP Vil N>) ) ) ) ) (<T S[dcl]\NP 0 2> (<L (S[dcl]\NP)/NP VBZ VBZ makes (S[dcl]\NP)/NP>) (<T NP 0 2> (<L NP/N DT DT no NP/N>) (<T N 0 2> (<L N/(S[to]\NP) NN NN attempt N/(S[to]\NP)>) (<T S[to]\NP 0 2> (<T S[to]\NP 0 2> (<L (S[to]\NP)/(S[b]\NP) TO TO to (S[to]\NP)/(S[b]\NP)>) (<T S[b]\NP 0 2> (<L (S[b]\NP)/NP VB VB conceal (S[b]\NP)/NP>) (<T NP 0 2> (<L NP/(N/PP) PRP$ PRP$ her NP/(N/PP)>) (<T N/PP 0 2> (<L N/PP NN NN glee N/PP>) (<T (N/PP)\(N/PP) 1 2> (<L conj CC CC and conj>) (<T N/PP 0 2> (<L (N/PP)/PP NN NN lack (N/PP)/PP>) (<T PP 0 2> (<L PP/NP IN IN of PP/NP>) (<T NP 0 1> (<L N NN NN conscience N>) ) ) ) ) ) ) ) ) (<L . . . . .>) ) ) ) ) ) ) 
    '''

    button = '<button class="expand">CCG parse ▲</button><br/>'
    print(CCG_HTML.latex(ccg))


if __name__ == "__main__":
    main()
