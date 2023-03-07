from rePDFer import RePDFer
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("file", help="PDF file to parse", type=str)
parser.add_argument("-o", "--output", help="output file", type=str, default="output")
parser.add_argument("-p", "--pages", help="number of pages to skip at the beginning of the pdf", type=int, default=1)
parser.add_argument("-s", "--select", help="page index to ask informations about title/subtitle/section ", type=int, default=5)
args = parser.parse_args()
output_name = "output/AutoCours - " + args.output

rePDFer = RePDFer(args.file, output_name, args.pages, args.select)
rePDFer.main()
rePDFer.close()