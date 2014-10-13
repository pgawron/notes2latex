notes2latex
===========

A tool to backport notes and sticky notes from a pdf file back to LaTeX

Typical usage:

    python notes2latex.py annotated.pdf synctexed.pdf
    
where `annotated.pdf` has sticky notes and `synctexed.pdf` was produced by `pdflatex` and associated `synctex` file exists.
