pdflatex:
	- docker run -it --rm -v "${PWD}:/root/shared/folder" dimasanwaraziz/pdflatex bash

latexmk:
	- docker run --rm -it -v $PWD:/workdir arkark/latexmk latexmk -pdf Thesis_Book.tex
# command
# pdflatex main.tex
