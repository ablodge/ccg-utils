# ccg-utils
A python package of common operations for CCGs

### Requirements
Python 3.6 or higher

### Input Formats
CCGBank Machine Readible
```
(<T S[dcl] 1 2> (<T NP 0 1> (<L N NNS NNS dogs N>) ) (<T S[dcl]\NP> (<L S[dcl]\NP/NP VBP VBP chase S[dcl]\NP/NP>) (<T NP 0 1> (<L N NNS NNS cats N>) ) ) )
```
Bracket
```
{S[dcl] "chase(DOGS,CATS)"
	{NP "DOGS"
		{N dogs "DOGS"} }
	{S[dcl]\NP "\lambda y.chase(y,CATS)"
		{S[dcl]\NP/NP chase "\lambda x\lambda y.chase(y,x)"}
		{NP "CATS"
			{N cats "CATS"} } } }
```
# HTML

# Latex
![ccg latex example](https://github.com/ablodge/ccg-utils/blob/master/ccg-latex-ex.PNG)
