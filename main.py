from rePDFer import RePDFer
import argparse
from os import remove, path, mkdir
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("file", help="PDF file to parse", type=str)
parser.add_argument("-o", "--output", help="output file", type=str, default="output")
parser.add_argument("-p", "--pages", help="number of pages to skip at the beginning of the pdf", type=int, default=1)
parser.add_argument("-s", "--select", help="page index to ask informations about title/subtitle/section ", type=int, default=5)
parser.add_argument("-f", "--force", help="forces the program to ask informations for the pdf and recreate a config file", action="store_true")
parser.add_argument("-m", "--module", help="choose the module for the exported file (libreoffice or pdf)", default=["markdown"], type=str, choices=["libreoffice", "markdown"], nargs=1)


args = parser.parse_args()
output_name = "output/" + args.output

# Checks if the necessary files/folders are present
if args.force and path.isfile("config.json"):
    remove("config.json")

if path.isdir("tmpimages"):
    shutil.rmtree("tmpimages")
    mkdir("tmpimages")
else:
    mkdir("tmpimages")

if not path.isdir("output"):
    mkdir("images")

if not path.isdir("images"):
    mkdir("images")

rePDFer = RePDFer(args.file, output_name, args.pages, args.select, args.module[0])
rePDFer.main()
rePDFer.close()