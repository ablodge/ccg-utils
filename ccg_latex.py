
from ccg import CCG
import re, sys

class CCG_Latex:

    @staticmethod
    def latex(ccg):
        words = [w for w in ccg.words()]
        WORDS = ' & '.join(w.word() for w in words)+r'\\'
        LINE1 = ' & '.join('\ccgline{1}{}' for w in words)+r'\\'
        TAGS = []
        for w in words:
            tag = w.tag()
            tag = tag.replace('\\', r' \backslash ')
            tag = tag.replace('[','$_{').replace(']','}$')
            TAGS.append(tag)
        TAGS = ' & '.join(TAGS)+r'\\'
        LEX = ' & '.join(fr'\sem{{{1}}}{{{w.semantics()}}}' for w in words)+r'\\'
        PHRASES = [[]]
        LINES = [[]]
        SEM = [[]]
        j = 0
        for p,i in ccg.phrases_and_indices():
            start, end = int(i.split('-')[0]), int(i.split('-')[1])
            size = end-start+1
            tag = p.tag()
            tag = tag.replace('\\', r' \backslash ')
            tag = tag.replace('[', '$_{').replace(']', '}$')
            combinator = p.combinator().replace('$',r'\$')
            semantics = p.semantics()
            semantics = re.sub(u'\u03BB',r'\lambda ', semantics, flags=re.UNICODE)
            if start < j:
                while j < len(words):
                    PHRASES[-1].append('')
                    LINES[-1].append('')
                    SEM[-1].append('')
                    j += 1
                PHRASES.append([])
                LINES.append([])
                SEM.append([])
                j = 0
            while start > j:
                PHRASES[-1].append('')
                LINES[-1].append('')
                SEM[-1].append('')
                j += 1
            PHRASES[-1].append(fr'\phrase{{{size}}}{{{tag}}}')
            LINES[-1].append(fr'\ccgline{{{size}}}{{{combinator}}}')
            SEM[-1].append(fr'\sem{{{size}}}{{{semantics}}}')
            j += size
        PHRASES = [' & '.join(p) for p in PHRASES]
        LINES = [' & '.join(l) for l in LINES]
        SEM = [' & '.join(s) for s in SEM]
        cols = ' '.join('c' for i in words)
        latex_elems = [r'\resizebox{\columnwidth}{!}{']
        latex_elems += [r'\begin{tabular}{ '+cols+' }']
        latex_elems += [WORDS]
        latex_elems += [LINE1]
        latex_elems += [TAGS]
        latex_elems += [LEX]
        for phrases, lines, semantics in zip(PHRASES, LINES, SEM):
            latex_elems += [lines + r'\\']
            latex_elems += [phrases+r'\\']
            latex_elems += [semantics + r'\\']
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
    input_file = r'test-data/EXAMPLE.txt'
    if len(sys.argv) > 1:
        input_file = sys.argv[1]

    with open(input_file, 'r', encoding='utf8') as f:
        for ccg in CCG.ccg_iter(f.read()):
            ccg = CCG(ccg)
            print(CCG_Latex.latex(ccg))
            print()

if __name__ == "__main__":
    main()
