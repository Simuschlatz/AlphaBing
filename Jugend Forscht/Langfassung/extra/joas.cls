%% ----------------------------------------------------------------------
%% This is file `joas.cls'.
%%
%% joas --- Support for submissions to Journal of Open Aviation Science
%% Email: j.sun-1@tudelft.nl
%%
%% Released under the LaTeX Project Public License v1.3c or later
%% See http://www.latex-project.org/lppl.txt
%% ----------------------------------------------------------------------

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{joas}
  [2021/05/04 v1.0 Submission to JOAS]
\LoadClass[10pt,a4paper,twoside]{article}
% Style the sectioning elements:
\renewcommand\section{\@startsection {section}{1}{\z@}%
  {-3.5ex \@plus -1ex \@minus -.2ex}%
  {2ex \@plus .5ex \@minus -.5ex}%
  {\large\bfseries}}
\renewcommand\subsection{\@startsection{subsection}{2}{\z@}%
  {-3.25ex\@plus -1ex \@minus -.2ex}%
  {1ex \@plus .2ex \@minus .2ex}%
  {\bfseries}}
\renewcommand\subsubsection{\@startsection{subsubsection}{3}{\z@}%
  {-3.25ex\@plus -1ex \@minus -.2ex}%
  {0.5ex \@plus .2ex}%
  {}} 
\renewcommand\paragraph{\@startsection{paragraph}{4}{\z@}%
  {3.25ex \@plus1ex \@minus.2ex}%
  {-1em}%
  {\bfseries}}
\renewcommand\subparagraph{\@startsection{subparagraph}{5}{\parindent}%
  {3.25ex \@plus1ex \@minus .2ex}%
  {-1em}%
  {\bfseries}}
\def\@hangfrom#1{\setbox\@tempboxa\hbox{{#1}}%
  \hangindent 0pt%\wd\@tempboxa
  \noindent\box\@tempboxa}
\RequirePackage{parskip}
% Approximations of commercial fonts:
%\RequirePackage[T1]{fontenc}
\RequirePackage[tt=false, type1=true]{libertine}
\RequirePackage[libertine]{newtxmath}
\RequirePackage[semibold]{sourcesanspro}
\RequirePackage[scaled=0.95]{inconsolata}
\RequirePackage[italic,eulergreek,defaultmathsizes]{mathastext}

\RequirePackage[table,svgnames]{xcolor}

\RequirePackage{lastpage} % For getting the last page in the first page header
\RequirePackage{enumitem} % For list styling
\setlist{noitemsep,leftmargin=\parindent}
\RequirePackage[online]{threeparttable} % For table notes
\let\TPTnoteSettingsOrig\TPTnoteSettings
\def\TPTnoteSettings{\TPTnoteSettingsOrig\scriptsize}
%%
\newcommand*\cup@warning{\ClassWarning{joas}}
\newcommand*\cup@ifundefined[1]{%
  \begingroup\expandafter\expandafter\expandafter\endgroup
  \expandafter\ifx\csname #1\endcsname\relax
    \expandafter\@firstoftwo
  \else
    \expandafter\@secondoftwo
  \fi
}
\RequirePackage{xkeyval}
\newcommand*\cup@keyval@bool[2]{%
  \cup@ifundefined{cup@#1#2}{%
    \cup@warning{Unknown option `#2' for key #1}%
  }{%
    \@nameuse{cup@#1#2}%
  }%
}
\newif\ifcup@abbreviations
\newif\ifcup@dates
\newif\ifcup@copyright
\newif\ifcup@articletitle
\newif\ifcup@chaptertitle
\newif\ifcup@email
\newif\ifcup@hyperref
\newif\ifcup@keywords
\newif\ifcup@super
\define@key{cup}{abbreviations}[true]{%
  \cup@keyval@bool{abbreviations}{#1}%
}
\define@key{cup}{suppmat}[true]{%
  \cup@keyval@bool{suppmat}{#1}%
}
\define@key{cup}{suppdata}[true]{%
  \cup@keyval@bool{suppdata}{#1}%
}
\define@key{cup}{orcid}[true]{%
  \cup@keyval@bool{orcid}{#1}%
}
\define@key{cup}{ack}[true]{%
  \cup@keyval@bool{ack}{#1}%
}
\define@key{cup}{contrib}[true]{%
  \cup@keyval@bool{contrib}{#1}%
}
\define@key{cup}{financial}[true]{%
  \cup@keyval@bool{financial}{#1}%
}
\define@key{cup}{conflicts}[true]{%
  \cup@keyval@bool{conflicts}{#1}%
}
\define@key{cup}{ethics}[true]{%
  \cup@keyval@bool{ethics}{#1}%
}
\define@key{cup}{dates}[true]{%
  \cup@keyval@bool{dates}{#1}%
}
\define@key{cup}{copyright}[true]{%
  \cup@keyval@bool{copyright}{#1}%
}
\define@key{cup}{articletitle}[true]{%
  \cup@keyval@bool{articletitle}{#1}%
}
\define@key{cup}{chaptertitle}[true]{%
  \cup@keyval@bool{chaptertitle}{#1}%
}
\define@key{cup}{email}[true]{%
  \cup@keyval@bool{email}{#1}%
}
\define@key{cup}{hyperref}[true]{%
  \cup@keyval@bool{hyperref}{#1}%
}
\define@key{cup}{keywords}[true]{%
  \cup@keyval@bool{keywords}{#1}%
}
\define@key{cup}{super}[true]{%
  \cup@keyval@bool{super}{#1}%
}
\define@key{cup}{usetitle}[true]{%
  \cup@keyval@bool{articletitle}{#1}%
}
\newcommand*\cup@journal{joas}
\newcommand*\cup@doi{\cup@warning{No DOI provided}}
\newcommand*\cup@manuscript{rescience}
\newcommand*\cup@year{\cup@warning{No year provided}}
\newcommand*\cup@vol{\cup@warning{No volume provided}}
\newcommand*\cup@maxauthors{15}
\newcommand*\cup@layout{preprint}
\define@key{cup}{journal}{%
  \def\cup@journal{#1}%
}
\define@key{cup}{manuscript}{%
  \def\cup@manuscript{#1}%
}
\define@key{cup}{year}{%
  \def\cup@year{#1}%
}
\define@key{cup}{volume}{%
  \def\cup@vol{#1}%
}
\define@key{cup}{layout}{%
  \def\cup@layout{#1}%
}
\ProcessOptionsX*<cup>
\newcommand*\cup@manuscript@article{article}
\newcommand*\cup@manuscript@rescience{rescience}
\newcommand*\cup@manuscript@data{data}
\newcommand*\cup@manuscript@software{software}
\newcommand*\cup@manuscript@editorial{editorial}
\newcommand*\cup@layout@preprint{preprint}

\setkeys{cup}{
  articletitle,
  super,
  dates,
  copyright,
  abbreviations,
  keywords,
}
\RequirePackage{geometry}
\RequirePackage{csquotes}  
\RequirePackage{changepage}
\RequirePackage{stringstrings}
\RequirePackage[absolute]{textpos}
\RequirePackage{
  caption,
  floatrow,
  graphicx,
  url,
  mdframed,
  mfirstuc,
  alphalph
}
\urlstyle{same}
\captionsetup{
  font={footnotesize,sf},
  labelfont=bf,
  labelsep=period
}
\floatsetup{
  font={sf,footnotesize},
}
\colorlet{structure@color}{black}
\def\@seccntformat#1{\@ifundefined{#1@cntformat}%
   {\csname the#1\endcsname\quad}%  default
   {\csname #1@cntformat\endcsname}% individual control
   }
   \def\section@cntformat{\thesection.\hspace{1ex}}
\renewcommand\appendix{\par
  \setcounter{section}{0}
  \setcounter{subsection}{0}
  \gdef\thesection{Appendix \@arabic\c@section}
}
\newmdenv[
  backgroundcolor=structure@color!15,
  hidealllines=true,
  leftmargin=3mm,rightmargin=3mm,innertopmargin=2mm,innerbottommargin=3mm,
  frametitle={\abstractfont\sffamily Kurzfassung},
  frametitleaboveskip=3mm,
  frametitlebelowskip=0mm
]{cup@abstract@box}
\let\abstract@org\abstract
\def\abstract{\cup@abstract@box\small}
\def\endabstract{\endcup@abstract@box}
\ifcup@hyperref
  \expandafter\RequirePackage
\else
  \expandafter\@gobble
\fi
  {hyperref}
\renewcommand*{\title}[2][]{%
  \gdef\cup@title@short{#1}%
  \gdef\@title{#2}%
  \ifx\cup@title@short\@empty
    \global\let\cup@title@short\@title
  \fi
}
\@onlypreamble\title
\newcount\cup@author@cnt
\newcount\cup@affil@cnt
\newcount\cup@affil@alt@cnt
\newcount\cup@footnote@cnt
\newcount\cup@affil@marker@cnt
\def\author#1{%
  \global\advance\cup@author@cnt\@ne\relax
  \expandafter\gdef\csname @author@\@roman\cup@author@cnt\endcsname{#1}%
  \begingroup
    \advance\cup@affil@cnt\@ne
    \expandafter\xdef\csname @author@affil@\@roman
      \cup@author@cnt\endcsname
      {\the\cup@affil@cnt}%
  \endgroup
}
\@onlypreamble\author
\def\and{%
  \cup@warning{%
    \string\and\space not used by the joas class: please see
    the\MessageBreak package documentation for details%
  }%
}
\def\thanks{%
  \cup@warning{%
    \string\thanks\space not used by the joas class: please see
    the\MessageBreak the package documentation for details%
  }%
}
\newcommand*\affiliation[2][\relax]{%
  \ifnum\cup@author@cnt>\z@\relax
    \cup@affil@ifdup{#2}{%
      \cup@affil@swap{#2}%
    }{%
      \global\advance\cup@affil@cnt\@ne\relax
      \expandafter\gdef\csname @address@\@roman\cup@affil@cnt\endcsname
        {#2}%
      \ifx\relax#1\relax
        \expandafter\gdef\csname @affil@\@roman\cup@affil@cnt\endcsname
          {#2}%
      \else
        \expandafter\gdef\csname @affil@\@roman\cup@affil@cnt\endcsname
          {#1}%
      \fi
    }%
  \else
    \cup@warning{Affiliation with no author}%
  \fi
}
\@onlypreamble\affiliation
\newcommand*\cup@affil@ifdup[1]{%
  \begingroup
    \def\@tempa{#1}%
    \@tempswafalse
    \@tempcnta\z@\relax
    \cup@affil@ifdup@aux
    \if@tempswa
      \aftergroup\@firstoftwo
    \else
      \aftergroup\@secondoftwo
    \fi
  \endgroup
}
\newcommand*\cup@affil@ifdup@aux{%
  \advance\@tempcnta\@ne\relax
  \expandafter\expandafter\expandafter\def\expandafter\expandafter
    \expandafter\@tempb\expandafter\expandafter\expandafter
    {\csname @address@\@roman\@tempcnta\endcsname}%
  \ifx\@tempa\@tempb
    \expandafter\@tempswatrue
  \else
    \ifnum\@tempcnta<\cup@affil@cnt\relax
      \expandafter\expandafter\expandafter\cup@affil@ifdup@aux
    \fi
  \fi
}
\newcommand*\cup@affil@swap[1]{%
  \begingroup
    \def\@tempa{#1}%
    \@tempcnta\z@\relax
    \@tempcntb\z@\relax
    \cup@affil@ifdup@aux
    \advance\cup@affil@cnt\@ne\relax
    \cup@affil@swap@aux
  \endgroup
}
\newcommand*\cup@affil@swap@aux{%
  \advance\@tempcntb\@ne\relax
  \expandafter\ifnum\csname @author@affil@\@roman\@tempcntb\endcsname
    = \cup@affil@cnt\relax
    \expandafter\xdef\csname @author@affil@\@roman\@tempcntb\endcsname{%
      \the\@tempcnta
    }%
  \fi
  \ifnum\@tempcntb<\cup@author@cnt\relax
    \expandafter\cup@affil@swap@aux
  \fi
}
\newcommand*\alsoaffiliation[2][\relax]{%
  \ifnum\cup@author@cnt>\z@\relax
    \cup@affil@ifdup{#2}{%
      \cup@alsoaffil@find{#2}%
    }{%
      \global\advance\cup@affil@cnt\@ne\relax
      \@tempcnta\cup@affil@cnt\relax
      \expandafter\gdef\csname @address@\@roman\cup@affil@cnt\endcsname
        {#2}%
      \ifx\relax#1\relax
        \expandafter\gdef\csname @affil@\@roman\cup@affil@cnt\endcsname
          {#2}%
      \else
        \expandafter\gdef\csname @affil@\@roman\cup@affil@cnt\endcsname
          {#1}%
      \fi
    }%
    \@ifundefined{@author@alsoaffil@\@roman\cup@author@cnt}{%
      \expandafter\xdef\csname @author@alsoaffil@\@roman\cup@author@cnt
        \endcsname{\the\@tempcnta}%
    }{%
      \expandafter\xdef\csname @author@alsoaffil@\@roman\cup@author@cnt
        \endcsname{%
        \csname @author@alsoaffil@\@roman\cup@author@cnt\endcsname
        ,\the\@tempcnta
      }%
    }%
  \else
    \cup@warning{Affiliation with no author}%
  \fi
}
\newcommand*\cup@alsoaffil@find[1]{%
  \begingroup
    \def\@tempa{#1}%
    \@tempcnta\z@\relax
    \@tempcntb\z@\relax
    \cup@affil@ifdup@aux
  \expandafter\endgroup
  \expandafter\@tempcnta\the\@tempcnta\relax
}
\newcommand*\altaffiliation[1]{%
  \ifnum\cup@author@cnt>\z@\relax
    \begingroup
      \cup@altaffil@ifdup{#1}{%
        \expandafter\xdef\csname @author@altaffil@\\cup@author@cnt
          \endcsname{\the\@tempcnta}%
      }{%
        \global\advance\cup@affil@alt@cnt\@ne\relax
        \expandafter\gdef\csname @altaffil@\\cup@affil@alt@cnt
          \endcsname{#1}%
        \expandafter\xdef\csname @author@altaffil@\@roman\cup@author@cnt
          \endcsname{\the\cup@affil@alt@cnt}%
      }%
    \endgroup
  \else
    \cup@warning{Affiliation with no author}%
  \fi
}
\@onlypreamble\altaffiliation
\newcommand*\cup@altaffil@ifdup[1]{%
  \def\@tempa{#1}%
  \@tempswafalse
  \@tempcnta\z@\relax
  \ifnum\cup@affil@alt@cnt>\z@\relax
    \expandafter\cup@altaffil@ifdup@aux
  \fi
  \if@tempswa
    \expandafter\@firstoftwo
  \else
    \expandafter\@secondoftwo
  \fi
}
\newcommand*\cup@altaffil@ifdup@aux{%
  \advance\@tempcnta\@ne\relax
  \expandafter\expandafter\expandafter\def\expandafter\expandafter
    \expandafter\@tempb\expandafter\expandafter\expandafter
    {\csname @altaffil@\@roman\@tempcnta\endcsname}%
  \ifx\@tempa\@tempb
    \expandafter\@tempswatrue
  \else
    \ifnum\@tempcnta<\cup@affil@alt@cnt\relax
      \expandafter\expandafter\expandafter\cup@altaffil@ifdup@aux
    \fi
  \fi
}
\newcommand*\email[2][]{%
  \ifnum\cup@author@cnt>\z@\relax
    \cup@emailtrue%
    \expandafter\gdef\csname @emailname@\@roman\cup@author@cnt\endcsname
      {#1}%
    \expandafter\gdef\csname @email@\@roman\cup@author@cnt\endcsname
      {#2}%
  \else
    \cup@warning{E-mail with no author}%
  \fi
}
\@onlypreamble\email
\newcommand*\fax[1]{%
  \ifnum\cup@author@cnt>\z@\relax
    \expandafter\gdef\csname @fax@\@roman\cup@author@cnt\endcsname
      {#1}%
  \else
    \cup@warning{Fax number with no author}%
  \fi
}
\@onlypreamble\fax
\newcommand*\phone[1]{%
  \ifnum\cup@author@cnt>\z@\relax
    \expandafter\gdef\csname @phone@\@roman\cup@author@cnt\endcsname
      {#1}%
  \else
    \cup@warning{Phone number with no author}%
  \fi
}
\@onlypreamble\phone
\newcommand*\abbreviations[1]{%
  \gdef\@abbreviations{#1}%
}
\newcommand*\@abbreviations{}
\@onlypreamble\abbreviations
\newcommand*\keywords[1]{%
  \gdef\@keywords{#1}%
}
\newcommand*\@keywords{}
\@onlypreamble\keywords
\newcommand*\cup@abbreviations@print{%
  \ifx\@abbreviations\@empty\else
    {\noindent\bfseries Abbreviations: }
    \@abbreviations
    \par
  \fi
}
\newcommand*\cup@keywords@print{%
  \ifx\@keywords\@empty\else
    {\noindent\bfseries Keywords: }
    \@keywords
    \par
  \fi
}
\newcommand*\doi[1]{\gdef\cup@doi{#1}}
\@onlypreamble\doi
\newcommand*\received[1] {\gdef\cup@recvd{#1}}
\newcommand*\revised[1]  {\gdef\cup@revd{#1}}
\newcommand*\accepted[1] {\gdef\cup@accptd{#1}}
\newcommand*\published[1]{\gdef\cup@publd{#1}}
\newcommand*\editor[1] {\gdef\cup@editor{#1}}
\newcommand*\reviewers[1] {\gdef\cup@reviewers{#1}}
\newlength\cup@space@pre@title
\setlength\cup@space@pre@title{1em}
\newlength\cup@space@post@title
\setlength\cup@space@post@title{1em}
\newlength\cup@space@post@author
\setlength\cup@space@post@author{0.7em}
\newlength\cup@space@post@address
\setlength\cup@space@post@address{0.2em}
\newlength\cup@space@post@email
\setlength\cup@space@post@email{1em}
\newlength\cup@space@post@date
\setlength\cup@space@post@date{0.5em}
\newlength\cup@space@inter@extra
\setlength\cup@space@inter@extra{0.5em}
\newlength\cup@maketitle@width
\setlength\cup@maketitle@width{\textwidth}
\newcommand*\affilsize{\footnotesize}
\newcommand*\authorsize{\normalsize}
\newcommand*\emailsize{\footnotesize}
\newcommand*\titlesize{\Large}
\newcommand*\datesize{\footnotesize}
\newcommand*\firstheadsize{\scriptsize}
\newcommand*\affilfont{\footnotesize}
\newcommand*\authorfont{}
\newcommand*\emailfont{\footnotesize}
\newcommand*\emailsymbol{*}
\newcommand*\titlefont{\sffamily\bfseries\raggedright\color{structure@color}}
\newcommand*\datefont{\footnotesize}
\newcommand*\extrasfont{\footnotesize}
\newcommand*\abstractfont{\small}
\newcommand*\journalnamefont{\itshape}
\newcommand*\volumefont{\bfseries}
\newcommand*\cup@etal{\emph{et al.}}
\def\ps@plain{
  \renewcommand{\@oddhead}{\hfill{\journalnamefont\footnotesize\cup@journal@name}\qquad\normalsize\thepage}%
  \renewcommand{\@evenhead}{\thepage\qquad\footnotesize\@author@i\space\cup@etal\hfill}%
  \renewcommand{\@evenfoot}{}%
  \renewcommand{\@oddfoot}{\@evenfoot}%
}
\pagestyle{plain}

\newcommand*\cup@type@list{article,rescience,data,software,editorial}
\newcommand*\cup@type@default{article}
\newcommand*\cup@type@check{%
  \@tempswafalse
  \@for\@tempa:=\cup@type@list\do{%
    \ifx\@tempa\cup@manuscript
      \expandafter\@tempswatrue
    \fi
  }%
  \if@tempswa\else
    \cup@warning{%
      Invalid manuscript type \cup@manuscript:\MessageBreak
      changed to default type \cup@type@default
    }%
    \let\cup@manuscript\cup@type@default
  \fi
}


\cup@type@check


\def\@maketitle{%
  \setlength\parindent{\z@}
  \setlength{\parskip}{1pt}
  \ifnum\cup@author@cnt<\z@\relax
    \cup@warning{No authors defined: At least one author is required}%
  \fi
  \newpage\vspace*{\dimexpr-\headsep-\headheight\relax}
  \parbox[b]{\dimexpr\textwidth-20mm\relax}{%
    \footnotesize{\journalnamefont\cup@journal@name} 
    }
  \vspace*{\baselineskip}
  {\sffamily\bfseries\color{structure@color}\MakeUppercase{\convertchar{\cup@manuscript}{-}{ }}\par}
  \vspace*{\cup@space@pre@title}%
        {%
          \titlefont
          \titlesize
          \let\@fnsymbol\cup@author@fnsymbol
          \let\footnote@org\footnote
          \let\footnote\cup@title@footnote
          \@title
          \cup@title@footnote@check
          \global\cup@footnote@cnt\c@footnote
          \@maketitle@title@hook
          \par
        }%
        \vspace*{\cup@space@post@title}%
        {%
          \authorsize
          \authorfont
          %\frenchspacing
          \cup@author@list
          \par
        }%
        \vspace*{\cup@space@post@author}%
        {%
          \affilsize
          \affilfont
          \cup@address@list
          \par
        }%
        \vspace*{\cup@space@post@address}%
        {%
          \emailsize
          \emailfont
          \ifcup@email
            \expandafter\cup@contact@details
            \par
            \vspace*{\cup@space@post@email}%
          \fi
        }%
        {%
          \datesize
          \datefont
          \ifcup@copyright
            \bgroup\let\thefootnote\relax
            \footnote{\cup@copyright@notice}
            \egroup
          \fi
        }%
}
\newcommand*\@maketitle@title@hook{}
\newcommand*\cup@maketitle@reproduce{}
\newcommand*\cup@maketitle@opendata{}
\newcommand*\cup@maketitle@funding{}
\newcommand*\cup@maketitle@credit{}
\newcommand*\cup@title@footnote[1]{%
  \footnotemark
  \g@addto@macro\@thanks{\footnotetext{#1}}%
}
\newcommand\cup@title@footnote@check{%
  \ifx\@thanks\@empty
  \else
    \begingroup
      \toks@=\expandafter{\@thanks}%
      \xdef\@thanks{%
        \begingroup
          \let\noexpand\@fnsymbol\noexpand\cup@author@fnsymbol
          \the\toks@
        \endgroup
      }%
    \endgroup
  \fi
}
\newcommand*\cup@contact@details{%
  { \emailsymbol{}Email Adresse: \cup@email@list}%
  \cup@number@list
}
\let\@thanks\@empty
\newcommand*\cup@author@list{%
  \@tempcnta\z@\relax
  \ifnum\cup@author@cnt=\z@\relax\else
    \expandafter\cup@author@list@main
  \fi
}
\newcommand*\cup@author@footnotes{}
\newcommand*\cup@author@list@main{%
  \advance\@tempcnta\@ne\relax
  \def\cup@author@footnotes{}%
  \cup@author@list@and
  \space
  \@nameuse{@author@\@roman\@tempcnta}%
  \cup@author@list@comma
  \cup@author@star
  \cup@author@affil
  \cup@author@affil@also
  \cup@author@affil@alt
  \ifx\@empty\cup@author@footnotes\else
    \textsuperscript{\cup@author@footnotes}%
  \fi
  \ifnum\@tempcnta<\cup@author@cnt\relax
    \expandafter\cup@author@list@main
  \fi
}
\newcommand*\cup@author@list@and{%
  \ifnum\cup@author@cnt=\@ne\relax\else
    \ifnum\@tempcnta=\cup@author@cnt\relax
      \space and%
    \fi
  \fi
}
\newcommand*\cup@author@list@comma{%
  \ifnum\cup@author@cnt>\tw@\relax
    \ifnum\@tempcnta<\cup@author@cnt\relax
      ,%
    \fi
  \fi
}
\newcommand*\cup@author@star{%
  \cup@ifundefined{@email@\@roman\@tempcnta}{}{%
    \cup@author@star@aux
  }%
}
\newcommand*\cup@author@star@aux{%
  \protected@edef\cup@author@footnotes{%
    % \cup@author@fnsymbol{\z@}%
    \emailsymbol%
    \ifnum\cup@affil@cnt>\@ne\relax
      %,%
    \else
      \ifnum\cup@affil@alt@cnt>\z@\relax
        %,%
      \fi
    \fi
  }%
}
\newcommand*\cup@author@affil{%
  \cup@ifundefined{%
    @affil@\@roman\csname @author@affil@\@roman\@tempcnta\endcsname
  }{%
    \cup@warning{%
      No affiliation given for author\MessageBreak
      \@nameuse{@author@\@roman\@tempcnta}%
    }%
  }{%
    \cup@author@affil@aux
  }%
}
\newcommand*\cup@author@affil@aux{%
  \ifnum\cup@affil@cnt>\@ne\relax
    \expandafter\cup@affil@marker@cnt\csname @author@affil@\@roman
      \@tempcnta\endcsname\relax
    \advance\cup@affil@marker@cnt\cup@footnote@cnt\relax
    \protected@edef\cup@author@footnotes{%
      \cup@author@footnotes
      \cup@author@fnsymbol{\cup@affil@marker@cnt}%
    }%
  \else
    \ifnum\cup@affil@alt@cnt>\z@\relax
      \cup@affil@marker@cnt\@ne\relax
      \advance\cup@affil@marker@cnt\cup@footnote@cnt\relax
      \protected@edef\cup@author@footnotes{%
        \cup@author@footnotes
        \cup@author@fnsymbol{\cup@affil@marker@cnt}%
      }%
    \fi
  \fi
}
\newcommand*\cup@author@affil@also{%
  \cup@ifundefined{@author@alsoaffil@\@roman\@tempcnta}{}{%
    \cup@author@affil@also@aux
  }%
}
\newcommand*\cup@author@affil@also@aux{%
  \expandafter\@for\expandafter\@tempa\expandafter:\expandafter
    =\csname @author@alsoaffil@\@roman\@tempcnta\endcsname\do{%
    \cup@affil@marker@cnt\@tempa\relax
    \advance\cup@affil@marker@cnt\cup@footnote@cnt\relax
    \protected@edef\cup@author@footnotes{%
      \cup@author@footnotes
      %,%
      \cup@author@fnsymbol{\cup@affil@marker@cnt}%
    }%
  }%
}
\newcommand*\cup@author@affil@alt{%
  \cup@ifundefined{@author@altaffil@\@roman\@tempcnta}{}{%
    \cup@author@affil@alt@aux
  }%
}
\newcommand*\cup@author@affil@alt@aux{%
  \expandafter\cup@affil@marker@cnt
    \csname @author@altaffil@\@roman\@tempcnta\endcsname\relax
  \advance\cup@affil@marker@cnt\cup@affil@cnt\relax
  \advance\cup@affil@marker@cnt\cup@footnote@cnt\relax
  \protected@edef\cup@author@footnotes{%
    \cup@author@footnotes
    %,%
    \cup@author@fnsymbol{\cup@affil@marker@cnt}%
  }%
}
\newcommand*{\cup@author@fnsymbol}[1]{%
  \ensuremath{%
    \expandafter\cup@author@fnsymbol@aux\expandafter{\number#1}%
  }%
}
\newcommand*{\cup@author@fnsymbol@aux}[1]{%
  \ifnum#1>10 %
    \expandafter\cup@author@fnsymbol@loop
  \else
    \expandafter\cup@author@fnsymbol@symbol
  \fi
    {#1}%
}
\newcommand*{\cup@author@fnsymbol@loop}[1]{%
   \cup@author@fnsymbol@loop@aux@i#1%
}
\newcommand*{\cup@author@fnsymbol@loop@aux@i}[2]{%
  \cup@author@fnsymbol@symbol{\ifnum#2=0 10\else #2\fi}%
  \expandafter\cup@author@fnsymbol@loop@aux@ii\romannumeral #1000Q{}%
    {\cup@author@fnsymbol@symbol{\ifnum#2=0 10\else #2\fi}}%
}
\newcommand*{\cup@author@fnsymbol@loop@aux@ii}[1]{%
  \@nameuse{cup@author@fnsymbol@loop@aux@#1}%
}
\def\cup@author@fnsymbol@loop@aux@m#1Q#2#3{%
  \cup@author@fnsymbol@loop@aux@ii#1Q{#2#3}{#3}%
}
\newcommand*{\cup@author@fnsymbol@loop@aux@Q}[2]{#1}
\newcommand*{\cup@author@fnsymbol@symbol}[1]{%
  \ifcase #1 *\or
    \dagger\or
      \ddagger\or
        \P\or
          \S\or
            \|\or
              \bot\or
                \#\or
                  @\or
                    \triangle\or
                      \nabla
    \fi
}
\newcommand*\cup@address@list{%
  \ifnum\cup@affil@cnt>\z@
    \expandafter\cup@address@list@auxi
  \else
    \cup@warning{No affiliations: at least one affiliation is needed}%
  \fi
}
\newcommand*\cup@address@list@auxi{%
  \ifnum0%
    \ifnum\cup@affil@cnt>\@ne    1\fi
    \ifnum\cup@affil@alt@cnt>\z@ 1\fi
      >\z@
    \expandafter\cup@address@list@auxii
  \else
    \@address@i\par
  \fi
}
\newcommand*\cup@address@list@auxii{%
  \@tempcnta\z@
  \cup@affil@marker@cnt\cup@footnote@cnt
  \loop\ifnum\@tempcnta<\cup@affil@cnt
    \advance\@tempcnta\@ne
    \advance\cup@affil@marker@cnt\@ne
    \cup@author@fnsymbol{\cup@affil@marker@cnt}%
    \@nameuse{@address@\@roman\@tempcnta}\par% and % TODO handle multiples
  \repeat
  \@tempcnta\z@
  \loop\ifnum\@tempcnta<\cup@affil@cnt
    \advance\@tempcnta\@ne
    \advance\cup@affil@marker@cnt\@ne
    \cup@ifundefined{@altaffil@\@roman\@tempcnta}
      {}
      {%
        \cup@author@fnsymbol{\cup@affil@marker@cnt}%
        \@nameuse{@altaffil@\@roman\@tempcnta}\par
      }%
  \repeat
}
\newcommand*\cup@fnsymbol@org{}
\newcommand*\cup@affil@list{%
  \let\cup@fnsymbol@org\@fnsymbol
  \let\@fnsymbol\cup@author@fnsymbol
  \@tempcnta\z@\relax
  \@tempcntb\z@\relax
  \ifnum\cup@affil@cnt>\@ne\relax
    \expandafter\cup@affil@list@aux
  \else
    \ifnum\cup@affil@alt@cnt>\z@\relax
      \cup@affil@marker@cnt\@ne\relax
      \advance\cup@affil@marker@cnt\cup@footnote@cnt\relax
      \footnotetext[^\cup@affil@marker@cnt]{\@affil@i}%
      \@tempcnta\@ne\relax
    \fi
  \fi
  \ifnum\cup@affil@alt@cnt>\z@\relax
    \expandafter\cup@affil@alt@list
  \fi
  \let\@fnsymbol\cup@fnsymbol@org
}
\newcommand*\cup@affil@list@aux{%
  \advance\@tempcnta\@ne\relax
  \cup@affil@marker@cnt\@tempcnta\relax
  \advance\cup@affil@marker@cnt\cup@footnote@cnt\relax
  \footnotetext[\cup@affil@marker@cnt]{%
    \@nameuse{@affil@\@roman\@tempcnta}%
  }%
  \ifnum\@tempcnta<\cup@affil@cnt\relax
    \expandafter\cup@affil@list@aux
  \fi
}
\newcommand*\cup@affil@alt@list{%
  \advance\@tempcntb\@ne\relax
  \cup@ifundefined{@altaffil@\@roman\@tempcntb}{}{%
    \cup@altaffil@foot@aux
  }
  \ifnum\@tempcntb<\cup@author@cnt\relax
    \expandafter\cup@affil@alt@list
  \fi
}
\newcommand*\cup@altaffil@foot@aux{%
  \advance\@tempcnta\@ne\relax
  \cup@affil@marker@cnt\@tempcnta\relax
  \advance\cup@affil@marker@cnt\cup@footnote@cnt\relax
  \footnotetext[\cup@affil@marker@cnt]{%
    \@nameuse{@altaffil@\@roman\@tempcntb}%
  }%
}
\newcommand*\cup@email@list@font{}
\newcommand*\cup@email@list{%
  \begingroup
    \def\UrlFont{\cup@email@list@font}%
    \@tempcnta\z@\relax
    \@tempcntb\z@\relax
    \cup@email@list@aux
    \ifnum\@tempcntb=\z@\relax
      \cup@warning{%
        No e-mail given:\MessageBreak
        at lest one author must have a contact e-mail%
      }%
    \fi
  \endgroup
}
\newcommand*\cup@email@list@aux{%
  \advance\@tempcnta\@ne\relax
  \ifnum\@tempcnta>\cup@author@cnt\relax\else
    \cup@ifundefined{@email@\@roman\@tempcnta}{}{%
      \advance\@tempcntb\@ne\relax
      \ifnum\@tempcntb>\@ne\relax
        ;
      \fi
      \expandafter\expandafter\expandafter\url\expandafter
        \expandafter\expandafter{%
           \csname @email@\@roman\@tempcnta\endcsname
      }%
    }%
    \expandafter\cup@email@list@aux
  \fi
}
\newcommand*\cup@number@list{%
  \begingroup
    \cup@number@list@aux@i{phone}%
    \let\@tempb\@tempa
    \cup@number@list@aux@i{fax}%
    \ifx\@tempa\@empty
      \let\@tempa\@tempb
    \else
      \ifx\@tempb\@empty\else
        \protected@edef\@tempa{%
          \@tempb.\space\@tempa
        }%
      \fi
    \fi
    \ifx\@tempa\@empty\else
      \par
      \@tempa
    \fi
  \endgroup
}
\newcommand*\cup@number@list@aux@i[1]{%
  \def\@tempa{}%
  \@tempcnta\z@\relax
  \def\cup@number@list@aux@ii{%
    \advance\@tempcnta\@ne\relax
    \ifnum\@tempcnta>\cup@author@cnt\relax\else
      \cup@ifundefined{@#1@\@roman\@tempcnta}{}{%
        \cup@ifundefined{@email@\@roman\@tempcnta}{}{%
          \ifx\@tempa\@empty
            \edef\@tempa{%
              \@nameuse{@#1@\@roman\@tempcnta}%
            }%
          \else
            \edef\@tempa{%
              \@tempa
              ;
              \@nameuse{@#1@\@roman\@tempcnta}%
            }%
          \fi
        }%
      }%
      \expandafter\cup@number@list@aux@ii
    \fi
  }%
  \cup@number@list@aux@ii
  \ifx\@tempa\@empty\else
    \protected@edef\@tempa{%
      \MakeUppercase#1: \@tempa
    }%
  \fi
}
\newcommand*\cup@number@list@aux@ii{}
\g@addto@macro\endabstract{%
  \aftergroup\cup@abstract@extras
}
\newcommand*{\cup@abstract@extras}{%
  \bgroup
  \extrasfont
  \ifcup@keywords
    \cup@keywords@print
    %\par\vspace*{\cup@space@inter@extra}
  \fi
  \ifcup@abbreviations
    \cup@abbreviations@print
    \par\vspace*{\cup@space@inter@extra}
  \fi
  \egroup
}
\newcommand*\cup@maketitle@extras{%
  \cup@maketitle@extras@hook
}
\newcommand*\cup@maketitle@extras@hook{}
\g@addto@macro{\maketitle}{\cup@maketitle@extras\thispagestyle{empty}}
\g@addto@macro{\document}{\maketitle}
\newfloat{scheme}{htbp}{los}
\floatname{scheme}{Scheme}
\newfloat{chart}{htbp}{loc}
\floatname{chart}{Chart}
\newfloat{graph}{htbp}{loh}
\floatname{graph}{Graph}
\floatplacement{table}{htbp}
\floatplacement{figure}{htbp}
\floatstyle{plaintop}
\restylefloat{table}
\let\cup@floatboxreset\@floatboxreset
\def\@floatboxreset{%
  \centering
  \cup@floatboxreset
}
\AtEndOfClass{%
  \colorlet{tbrowcolor}{structure@color!10}
  \colorlet{tbheadcolor}{structure@color!30}
  \arrayrulecolor{structure@color}
}
%% From https://tex.stackexchange.com/a/32366/226
\newcommand*{\trfiller}{%
  \arrayrulecolor{tbrowcolor}% change to cell colour
  \specialrule{\heavyrulewidth}{0pt}{-\heavyrulewidth}% "invisible" rule
  \arrayrulecolor{structure@color}% revert to regular line colour
}
\newcommand*{\thfiller}{%
  \arrayrulecolor{tbheadcolor}% change to cell colour
  \specialrule{\heavyrulewidth}{0pt}{-\heavyrulewidth}% "invisible" rule
  \arrayrulecolor{structure@color}% revert to regular line colour
}
\newcommand{\headrow}{\rowcolor{tbheadcolor}}
\newcommand{\patchCUPtables}{%
  \rowcolors*{1}{tbrowcolor}{tbrowcolor}%
  \setlength{\aboverulesep}{0pt}%
  \setlength{\belowrulesep}{0pt}%
  \setlength{\extrarowheight}{.75ex}%
}
\AtBeginEnvironment{table}{\patchCUPtables}
\AtBeginEnvironment{table*}{\patchCUPtables}
\newcommand*\cup@section{}
\let\cup@section\section
\newcommand*\cup@subsection{}
\let\cup@subsection\subsection
\newcommand*\cup@subsubsection{}
\let\cup@subsubsection\subsubsection
\newcommand*\cup@startsection@orig{}
\let\cup@startsection@orig\@startsection
\newcommand\cup@startsection[6]{%
 \if@noskipsec \leavevmode \fi
 \par \@tempskipa #4\relax
 \@afterindenttrue
 \ifdim \@tempskipa <\z@ \@tempskipa - 0.4\@tempskipa \@afterindentfalse\fi
 \if@nobreak \everypar{}\else
     \addpenalty\@secpenalty\addvspace\@tempskipa\fi
 \@ifstar{\@dblarg{\@sect{#1}{\@m}{#3}{#4}{#5}{#6}}}%
         {\@dblarg{\@sect{#1}{#2}{#3}{#4}{#5}{#6}}}%
}
\let\@startsection\cup@startsection
\newcommand*\cup@startsection@alt[6]{%
  \if@noskipsec \leavevmode \fi
  \par \@tempskipa #4\relax
  \@afterindenttrue
 \ifdim \@tempskipa <\z@ \@tempskipa - 0.4\@tempskipa \@afterindentfalse\fi
 \if@nobreak \everypar{}\else
     \addpenalty\@secpenalty\addvspace\@tempskipa\fi
  \@ifstar{\@ssect{#3}{#4}{#5}{#6}}
          {\@ssect{#3}{#4}{#5}{#6}}%
}
\newcommand*\cup@sections@none{%
  \@ifstar{%
    \cup@sections@none@aux
  }{%
    \cup@sections@none@aux
  }%
}
\newcommand*\cup@sections@none@aux[2][]{%
  \cup@warning{%
    (Sub)section `#2' ignored%
  }%
}
\patchcmd{\@ssect}{#4}{\color{structure@color}#4}{}{}
\patchcmd{\@sect}{#6}{\color{structure@color}#6}{}{}
\newcommand*\SectionNumbersOff{%
  \let\@startsection\cup@startsection@alt
}
\@onlypreamble\SectionNumbersOff
\newcommand*\SectionNumbersOn{%
  \let\@startsection\cup@startsection
}
\@onlypreamble\SectionNumbersOn
\newcommand*\SectionsOff{%
  \let\section\cup@sections@none
  \let\subsection\cup@sections@none
  \let\subsubsection\cup@sections@none
}
\@onlypreamble\SectionsOff
\newcommand*\SectionsOn{%
  \let\section\cup@section
  \let\subsection\cup@subsection
  \let\subsubsection\cup@subsubsection
}
\@onlypreamble\SectionsOn
\begingroup
  \toks@=\expandafter{\tableofcontents}
  \xdef\tableofcontents{%
    \begingroup
      \let\noexpand\@startsection\noexpand\cup@startsection@orig
      \the\toks@
    \endgroup
  }
\endgroup
\newenvironment{acknowledgement}{%
  \cup@section*{Acknowledgement}%
}{}
\newenvironment{reproduce}{%
  \cup@section*{Reproducibility statement}%
}{}
\newenvironment{opendata}{%
  \cup@section*{Open data statement}%
}{}
\newenvironment{funding}{%
  \cup@section*{Funding statement}%
}{}
\newenvironment{credit}{%
  \cup@section*{Author contributions}%
}{}
\AtEndOfClass{%
  \def\bibsection{%
    \cup@section*{\refname}%
  }%
}
\newcommand*\cup@iffalse{\iffalse}
\newtoks\cup@collect@toks
\newtoks\cup@collect@empty@toks
\newcommand*\cup@collect@begins{}
\newcommand*\cup@collect@content{}
\newcommand\cup@collect[1]{%
  \cup@collect@toks{%
    \expandafter#1\expandafter{\the\cup@collect@toks}%
  }%
  \edef\cup@collect@content{%
    \the\cup@collect@toks
    \noexpand\end{\@currenvir}%
  }%
  \cup@collect@toks\cup@collect@empty@toks
  \def\cup@collect@begins{b}%
  \begingroup
    \expandafter\let\csname\@currenvir\endcsname\cup@collect@aux
    \edef\cup@collect@content{%
      \expandafter\noexpand\csname\@currenvir\endcsname
    }%
    \cup@collect@content
}
\newcommand*\cup@collect@aux{}
\long\def\cup@collect@aux#1\end#2{%
  \edef\cup@collect@begins{%
    \cup@collect@begins@#1\begin\end
    \expandafter\@gobble\cup@collect@begins
  }%
  \ifx\@empty\cup@collect@begins
    \endgroup
    \@checkend{#2}%
    \cup@collect@body{#1}%
  \else
    \cup@collect@body{#1\end{#2}}%
  \fi
  \cup@collect@content
}
\newcommand*\cup@collect@begins@{}
\long\def\cup@collect@begins@#1\begin#2{%
  \ifx\end#2\else
    b\expandafter\cup@collect@begins@
  \fi
}
\newcommand\cup@collect@body[1]{%
  \global\cup@collect@toks\expandafter{\the\cup@collect@toks#1}%
}


\newcommand*\cup@setkeys{\setkeys{cup}}
\let\cup@killsecs\SectionsOff
\newcommand*\cup@validtype[2][article]{%
  \def\cup@type@default{#1}%
  \def\cup@type@list{#2}%
}
\newcommand*\cup@par{}
\let\cup@par\par
\let\CUPTWOCOL\relax


\newcommand*\acksize{\normalsize}
\newcommand*\suppsize{\normalsize}
\newcommand*\patch@numeric@authors{%
  %%% Make author markers numeric...
  \renewcommand{\cup@author@fnsymbol@symbol}[1]{##1}
  \pretocmd{\cup@author@fnsymbol}{\let\ensuremath\relax}{}{}
  \patchcmd{\cup@author@star@aux}{\else}{,\else}{}{}
  \patchcmd{\cup@author@star@aux}
    {\ifnum\cup@affil@alt@cnt>\z@\relax}
    {\ifnum\cup@affil@alt@cnt>\z@\relax,}
    {}{}
  \patchcmd{\cup@author@affil@also@aux}
    {\cup@author@fnsymbol}
    {,\cup@author@fnsymbol}
    {}{}
  \patchcmd{\cup@address@list@auxii}
    {\cup@author@fnsymbol{\cup@affil@marker@cnt}}
    {\textsuperscript{\cup@author@fnsymbol{\cup@affil@marker@cnt}}}
    {}{}
}

\def\cup@journal@name{Jugend Forscht Langfassung}

\geometry{
  b5paper,
  top=2.3cm, bottom=1.6cm, left=1.7cm, right=1.7cm, 
  headsep=0.8cm
}

\colorlet{structure@color}{NavyBlue!60!black}

\ifx \cup@manuscript \cup@manuscript@rescience
  \colorlet{structure@color}{Brown!60!black}
\fi

\ifx \cup@manuscript \cup@manuscript@data
  \colorlet{structure@color}{DarkSeaGreen!40!black}
\fi

\ifx \cup@manuscript \cup@manuscript@software
  \colorlet{structure@color}{DarkOrchid!60!black}
\fi

\ifx \cup@manuscript \cup@manuscript@editorial
  \colorlet{structure@color}{Red!60!black}
\fi

\RequirePackage[colorlinks=true]{hyperref}

\Hy@AtBeginDocument{
  \def\@pdfborder{0 0 0.5}
  \def\@pdfborderstyle{/S/U/W 0.5} % Hyperlink border style will be underline of width 0.5pt
}

\hypersetup{
  anchorcolor={structure@color},
  citecolor={structure@color},
  linkcolor={structure@color},
  urlcolor={structure@color},
  linkbordercolor={structure@color},
  urlbordercolor={structure@color},
  citebordercolor={structure@color},
}

\ifx \cup@layout \cup@layout@preprint
  \RequirePackage[right]{lineno}
  \linenumbers
\fi


\patch@numeric@authors
\patchcmd{\@maketitle}
  {joas-logo}{joas-logo}{}{}
\let\endnote\footnote
\let\printendnotes\relax
\AtEndOfClass{%
  \colorlet{tbrowcolor}{white}
  \colorlet{tbheadcolor}{white}
  \arrayrulecolor{black}
}
\patchcmd{\trfiller}{structure@color}{black}{}{}
\patchcmd{\thfiller}{structure@color}{black}{}{}

% \RequirePackage[authordate,natbib]{biblatex-chicago}
% \renewcommand*{\bibfont}{\small}

\RequirePackage[backend=biber,style=numeric,maxbibnames=10,sorting=none]{biblatex}

\RequirePackage{booktabs}


\SectionNumbersOn


%%
%% Based on the cup-jounal class
%%
%% Support for submissions to Cambridge University Press journals
%% Email: paul.gessler@overleaf.com
%% Released under the LaTeX Project Public License v1.3c or later
%% See http://www.latex-project.org/lppl.txt
%% 
%% Based on the achemso class
%% Originally developed by Mats Dahlgren
%% Copyright (C) 1996-1998 by Mats Dahlgren
%% Copyright (C) 2008-2018 by Joseph Wright <joseph.wright@morningstar2.co.uk>
%% Copyright (C) 2019 by Overleaf (WriteLaTeX Limited)
%% 
%% Part of this bundle is derived from cite.sty, to which the
%% following license applies:
%%   Copyright (C) 1989-2009 by Donald Arseneau
%%   These macros may be freely transmitted, reproduced, or
%%   modified provided that this notice is left intact.
%% 
%% It may be distributed and/or modified under the conditions of
%% the LaTeX Project Public License (LPPL), either version 1.3c of
%% this license or (at your option) any later version.  The latest
%% version of this license is in the file:
%% 
%%    http://www.latex-project.org/lppl.txt
%% 
%% This work is "maintained" (as per LPPL maintenance status) by
%%   Paul Gessler.
%% 
%% This work consists of the file joas.cls.
%% 
%%
%% End of file `joas.cls'.
