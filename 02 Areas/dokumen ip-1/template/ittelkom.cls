\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ittelkom}
\LoadClass[a4]{article}
\RequirePackage{titlesec}
\RequirePackage{graphicx}
\RequirePackage{setspace}
%\usepackage[USenglish]{babel}
%\usepackage[nodayofweek,level]{datetime}
%\renewcommand{\contentsname}{DAFTAR ISI}

\titleformat{\section}
  {\Large\sf\raggedright}
  {\thesection}
  {1em}
  {}
  [\titlerule]
  
  \titleformat{\subsection}
  {\large\sf\raggedright}
  {\thesubsection}
  {1em}
  {}

\def\flushboth{%
  \let\\\@normalcr
  \@rightskip\z@skip \rightskip\@rightskip
  \leftskip\z@skip
  \parindent 1.5em\relax}

\setlength{\parfillskip}{0pt plus 1fil}
  
\newcommand{\laporancapstonecover}[8]{
	\clearpage
	\thispagestyle{empty}
    \begin{center}
      \huge\sf
      \textbf{THESIS PROGRESS REPORT}\\     
      \textbf{(Reported on #1 #2)}\\   
      \textbf{#3}\par
      \vspace{1cm}
    \end{center}
      \Large
      \centering \textbf{Submitted by}\par
      \large
      { 
       \textbf{#4 (#5)}\\
       \textbf{(#8)} \\ 
        
      }    
      \vspace{2.25cm}
        
      \large
       
      \textbf{Approved by\\
      Supervisor (I):\\
      \vspace{1.25cm}}
      \begin{spacing}{1}
       \rule{3cm}{0.05cm}\\
      \textbf{(#6)}\\
      \end{spacing}
      \vspace{1.25cm}
      \textbf{Supervisor (II):\\
      \vspace{1.25cm}}
      \begin{spacing}{1}
      \rule{3cm}{0.05cm}\\
      \textbf{(#7)}\\
      \end{spacing}
      \par
      
 }





\linespread{2}
\newcommand{\project}[1]{
  \raggedright{\LARGE\bf\sf Judul Capstone: {#1}
\rule{\linewidth}{.2pt}
}
}
\newcommand{\submit}[1]{
  \raggedright{\large\scshape Nama : {#1}\par}
}
\newcommand{\nim}[1]{
  \raggedright{\large\scshape NIM : {#1}\par}
}

\newcommand{\email}[1]{
  \raggedright{\large\scshape{E-mail :} \textsf{{#1}}\par}
}
\newcommand{\supervisor}[2]{
  \raggedright{\large\scshape Pembimbing Akademik : {#1}}\par
  \raggedright{\large\scshape Pembimbing Lapangan : {#2}}\par
}
\newcommand{\submitdate}[3]{
  \raggedright{\large\scshape Tanggal : {#1} \\ Fakultas informatika}\par
}








\newcommand{\supervisorcomments}{
\section*{Supervisor (I)'s Comments:}
\fbox {
    \parbox{\linewidth}{\textbf{Comments about the title}
    \vspace*{3cm}
    }
}
\fbox {
    \parbox{\linewidth}{\textbf{Comments about the research method}
    \vspace*{7cm}
    }
}
\fbox {
    \parbox{\linewidth}{\textbf{Sign \hfill Date:\hspace*{3cm}\\[1.25cm]}
    (\underline{\hspace*{5cm}})
    }
}

\section*{Supervisor (II)'s Comments:}
\fbox {
    \parbox{\linewidth}{\textbf{Comments about the title}
    \vspace*{3cm}
    }
}
\fbox {
    \parbox{\linewidth}{\textbf{Comments about the research method}
    \vspace*{7cm}
    }
}
\fbox {
    \parbox{\linewidth}{\textbf{Sign \hfill Date:\hspace*{3cm}\\[1.25cm]}
    (\underline{\hspace*{5cm}})
    }
}
}
\newcommand{\contact}[5]{
    #1 {\large\textperiodcentered} #2 {\large\textperiodcentered} #3
    {\Large} #4 \ {\Large} #5}
