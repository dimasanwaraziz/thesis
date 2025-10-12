pdflatex:
	- podman run -it --rm -v "$PWD":/data docker.io/drpsychick/texlive-pdflatex pdflatex /data/Thesis_Book.tex

latexmk:
	- docker run --rm -it -v $PWD:/workdir arkark/latexmk latexmk -pdf Thesis_Book.tex
