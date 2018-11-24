# ccg-utils
A python package of common operations for CCGs

### Requirements
Python 3.6 or higher

### Input Formats
CCGBank Machine Readible

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
