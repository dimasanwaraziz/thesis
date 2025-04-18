pdflatex:
	- docker run -it --rm -v "${PWD}:/root/shared/folder" dimasanwaraziz/pdflatex bash

# command
# pdflatex main.tex