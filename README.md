# scrp-pdf

This app is made to get the information of a PDF file made by our computer science's teacher Mr. Ivan Noyer and format them in a more readable pdf version or in a mkdocs-markdown version.

## usage

usage : `usage: main.py [-h] [-o OUTPUT] [-p PAGES] [-s SELECT] [-f] [-m {libreoffice,markdown}] file`

### Positional arguments:
```
positional arguments:
  file                  PDF file to parse
```

Options:
```
options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output file
  -p PAGES, --pages PAGES
                        number of pages to skip at the beginning of the pdf
  -s SELECT, --select SELECT
                        page index to ask informations about title/subtitle/section
  -f, --force           forces the program to ask informations for the pdf and recreate a config file
  -m {libreoffice,markdown}, --module {libreoffice,markdown}
                        choose the module for the exported file (libreoffice or pdf)
```
