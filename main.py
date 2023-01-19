from pikepdf import Pdf, OutlineItem
# import textrac

# example = Pdf.open("linux.pdf")

# page2 = example.pages[2]

# print(page2.Contents)

from glob import glob
pdf = Pdf.new()
page_count = 254

with pdf.open_outline() as outline:
    for file in glob('linux.pdf'):
        src = Pdf.open(file)
        oi = OutlineItem(file, page_count)
        outline.root.append(oi)
        page_count += len(src.pages)
        pdf.pages.extend(src.pages)

pdf.save('merged.pdf')