FROM debian:bookworm
LABEL maintainer="Julian Didier (theredfish)" \
      description="A docker image based on Debian that provides pdflatex and common packages" \
      repo="https://github.com/theredfish/docker-pdflatex"

# Install LaTeX packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends texlive-latex-recommended \
                                            texlive-fonts-recommended \
                                            texlive-latex-extra \
                                            texlive-fonts-extra \
                                            texlive-lang-all \
                                            biber \
                                            texlive-bibtex-extra && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /root/shared/folder

# Default command
# ENTRYPOINT ["pdflatex"]
