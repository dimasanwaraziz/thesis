\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ittelkom}
\LoadClass[a4]{article}
\RequirePackage{titlesec}
\RequirePackage{graphicx}
\RequirePackage{setspace}
\usepackage[USenglish,UKenglish]{babel}
\usepackage[nodayofweek,level]{datetime}

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
  
\newcommand{\progresscover}[8]{
    \begin{center}
      \huge\sf
      \textbf{THESIS PROGRESS REPORT}
      \LARGE
      \textbf{Reported on {#1}}\par     
      \vspace{1.5cm}
      \Huge
      \textbf{#2}\par
      \vspace{2cm}
      \Large
      \textbf{Submitted by}\par
      \large
      { \setstretch{1}
        \textbf{#3}\\
        \textbf{#4}\\
        \textbf{#5}\\
        \textbf{(#6)}\\
      }    
      \vspace{0.25cm}
      \Large   
      \textbf{Approved by}\\
      \large
      \textbf{Supervisor (I)}\\
      \vspace*{1.25cm}
      ({#7})\\        
      \textbf{Supervisor (II)}\\
      \vspace*{1.25cm}
      ({#8})        
      % \includegraphics[width=0.4\textwidth]{university.jpg}
    \end{center}
}


\linespread{2}
\newcommand{\project}[1]{
  \raggedright{\LARGE\bf\sf Research Proposal Title: {#1}
\rule{\linewidth}{.2pt}
}
}
\newcommand{\submit}[1]{
  \raggedright{\large\scshape Submitted by: {#1}\par}
}
\newcommand{\nim}[1]{
  \raggedright{\large\scshape NIM: {#1}\par}
}
\newcommand{\concentration}[1]{
  \raggedright{\large\scshape Concentration: {#1}\par}
}
\newcommand{\email}[1]{
  \raggedright{\large\scshape{E-mail address:} \textsf{{#1}}\par}
}
\newcommand{\supervisor}[2]{
  \raggedright{\large\scshape Supervisor (I) : {#1}}\par
  \raggedright{\large\scshape Supervisor (II): {#2}}\par
}
\newcommand{\submitdate}[3]{
  \raggedright{\large\scshape Submitted Date :
  	\selectlanguage{USenglish} \formatdate{#1}{#2}{#3}}\par
}

\newcommand{\summary}[2]{
  \justify{\LARGE\sf {#1}:
\par\large\sf {#2}}
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
