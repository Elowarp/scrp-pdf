import pdfminer
from pdfminer.high_level import extract_pages

from odf.opendocument import load
from odf.style import Style, TextProperties
from odf.text import H, P, Span


# Notes :
# Title 1 : 116.228,263.926,176.106,269.904
# Title 2 : 186.731,263.926,217.773,269.904
# Title 3 : 8.504,238.257,49.458,252.603
#
# Box Coordinates : x0, y0, x1, y1

TITLE_X1 = 176
TITLE_Y1 = 270

SUBTITLE_X0 = 187
SUBTITLE_Y0 = 264

SECTION_X0 = 9
SECTION_Y1 = 253

class RePDFer:
    def __init__(self, pdf_path, page_to_skip=3):
        self.pdf_path = pdf_path
        self.page_to_skip = page_to_skip

        self.file = open(pdf_path, 'rb')
        self.filename = pdf_path.split('/')[-1].split('.')[0]
        self.parser = pdfminer.pdfparser.PDFParser(self.file)
        self.document = pdfminer.pdfdocument.PDFDocument(self.parser)
        self.writing_section = {
            "title": "",
            "subtitle": "",
            "section": "",
        }

        self.doc = load("template.odt")
        self.styles = {
            "BigTitle" : Style(name="Title", family="paragraph"),
            "Title" : Style(name="Heading 1", family="paragraph"),
            "Subtitle" : Style(name="Heading 2", family="paragraph"),
            "Section" : Style(name="Heading 3", family="paragraph"),
            "Text": Style(name="Paragraphe", family="paragraph"),
        }


    def extract_content_from_pdf(self):
        """
        Extract the content from pdf file
        Parameters
            None
        
        Returns
            (list) - Which each element representing a page
                     is a dict containing : 
                        - the texts from the page
                        - the images
                        - the current title
                        - the current subtitle
                        - the current section name

                     Which are use to know where we are in the pdf
        """
        # First, we need to get every pages from the pdf while avoiding
        # the duplicated pages
        pages_temp = []
        previous_page_id = 1
        previous_page_elements = []
        i=0
        for page_layout in extract_pages(self.pdf_path):
            page_elements = []
            last_text = ""
            for element in page_layout:
                # Used to scrap the page id
                if isinstance(element, pdfminer.layout.LTTextBoxHorizontal):
                    last_text = element.get_text()

                # Adds every piece of the layout to the elements list
                page_elements.append(element)
                
                # if i==78 : print(element)
            
            # Avoid duplicated pages by getting the last one showing before
            # changing entirely
            current_page_id = last_text.split(" / ")[0]
            if current_page_id != previous_page_id:
                previous_page_id = current_page_id
                pages_temp.append(previous_page_elements)
                previous_page_elements = page_elements

            else:
                previous_page_elements = page_elements

            i+=1

        pages_temp.append(previous_page_elements)

        pages = []

        # Skips the defaults pages of every PDF's and get the content
        # out of every other pages
        for page_layout in pages_temp[self.page_to_skip:]:
            pages.append(self.extract_information_from_page(page_layout))

        return pages

    def extract_information_from_page(self, page_layout):
        """
        Extract the usefull information from a page layout
        Parameters
            page_layout (list) - List of elements from the page layout

        Returns
            (dict) - Dict containing :
                        - the texts from the page  
                        - the images
                        - the current title
                        - the current subtitle
                        - the current section name
                        - the potential code section
        """

        content = {
            "texts": [],
            "images": [],
            "title": "",
            "subtitle": "",
            "section": "",
            "code_section": "",
        }

        for element in page_layout:
            if isinstance(element, pdfminer.layout.LTTextBoxHorizontal):
                # Gets the font info of the current text
                fontinfo = set()
                for line in element:
                    for character in line:
                        if isinstance(character, pdfminer.layout.LTChar):
                            # fontinfo.add(character.fontname)
                            # fontinfo.add(character.size)
                            fontinfo.add(character.graphicstate.scolor)
                            fontinfo.add(character.graphicstate.ncolor)


                # Changes bad encoding of all his PDF's
                text = self.decode_text(element.get_text())

                # Gets the title/subtitle/section of the current page
                # to always know where this piece of text is going to
                # be at the end
                if round(element.bbox[2]) == TITLE_X1 and \
                    round(element.bbox[3]) == TITLE_Y1:
                    
                    content["title"] = text

                elif round(element.bbox[0]) == SUBTITLE_X0 and \
                    round(element.bbox[1]) == SUBTITLE_Y0:

                    content["subtitle"] = text

                elif round(element.bbox[0]) == SECTION_X0 and \
                    round(element.bbox[3]) == SECTION_Y1:

                    content["section"] = text

                else:
                    # If the text is blue, it's a kind of definition
                    if (0.2, 0.2, 0.7) in fontinfo:
                        content["texts"].append("> " + text)
                    
                    else:
                        content["texts"].append(text)

        return content

    def decode_text(self, text):
        """
        Decode the text from the pdf
        :param text: text to decode
        :return: decoded text
        """
        text = text.replace('`e', 'è')
        text = text.replace('´e', 'é')
        text = text.replace('`a', 'à')
        text = text.replace('ˆa', 'â')
        text = text.replace('ˆe', 'ê')
        text = text.replace('ˆı', 'î')
        text = text.replace('ˆo', 'ô')
        text = text.replace('¸c', 'ç')
        text = text.replace('`u', 'ù')
        text = text.replace('ˆu', 'û')

        text = text.replace('(cid:28) ', '"')
        text = text.replace(' (cid:29)', '"')
        
        # A stylised l so may change if we want to 
        # stylise the outfile in consequence
        text = text.replace('(cid:96)', 'l') 
        text = text.replace('ﬁ', 'fi') 

        # A math definition of a symbol 
        text = text.replace('(cid:124)', '') 
        text = text.replace('(cid:123)', '') 
        text = text.replace('(cid:122)', '') 
        text = text.replace('(cid:125)', '') 

        text = text.replace('(cid:26)', "") 

        text = text.replace('(cid:88)', '{sum symbol}') 
        text = text.replace('(cid:80)', '{sum symbol}') 
        text = text.replace('(cid:39)', '~=') 
        text = text.replace(' (cid:48)', "'") 


        return text

    def main(self):
        """
        Write the text in a file
        :param text: text to write
        :return: None
        """
        pages = self.extract_content_from_pdf()

        self.write_bigtitle(self.filename.upper())

        # Create text in markdown
        for page in pages:
            # Write titles/subtitles/sections when changing

            ## Avoid duplicated summuary after each title/subtitle
            if self.title_or_subtitle_changement(page): continue 
            
            self.section_changement(page)
          

            # Every thing that is NOT the last 4 string
            # Which are the name of the teacher, the course subject
            # the current page and the school  
            final_text = ""
            for line in page["texts"][:-2]:
                # If there is an image
                if "Figure" in line:
                    final_text += "\nIMAGE\n\n"
                    final_text += "*" + line[:-1] + "*\n\n"

                # If it's something you have to know
                elif "♥" in line:
                    final_text += "\n**" + line[:-1] + "**\n\n"

                else:
                    final_text += line.replace('\n', ' ') + '\n'

                text = P(stylename=self.styles["Text"], text=final_text)
            self.doc.text.addElement(text)

        # Creates final file
        self.write_file(final_text)

    def write_bigtitle(self, text):
        """
        Write the title of the file
        Parameters:
            text (string) -  text to write

        Returns:
            None
        """
        heading = H(outlinelevel=1, stylename=self.styles["BigTitle"], text=text)
        self.doc.text.addElement(heading)


    def title_or_subtitle_changement(self, page):
        changed = False
        if self.writing_section["title"] != page["title"]:
            # Write the title in the odt file
            text = H(outlinelevel=2, stylename=self.styles["Title"], text=page["title"])
            self.doc.text.addElement(text)

            # Keep up to date the current title
            self.writing_section["title"] = page["title"]
            changed = True

        if self.writing_section["subtitle"] != page["subtitle"]:
            # Write the title in the odt file
            text = H(outlinelevel=3, stylename=self.styles["Subtitle"], text=page["title"])
            self.doc.text.addElement(text)

            # Keep up to date the current subtitle
            self.writing_section["subtitle"] = page["subtitle"]
            changed = True
        
        return changed

    def section_changement(self, page):
        if self.writing_section["section"] != page["section"]:
            # Keep up to date the current section
            self.writing_section["section"] = page["section"]
            
            # Write the title in the odt file
            text = H(outlinelevel=4, stylename=self.styles["Section"], text=page["section"])
            self.doc.text.addElement(text)
        
    def write_file(self, text):
        """
        Write the text in a file
        Parameters:
            text (string) -  text to write

        Returns:
            None
        """
        with open('output.md', 'w') as f:
            f.write(text)

    def close(self):
        self.doc.save("output.odt")
        self.file.close()

def execute():
    # pdf_path = './linux.pdf'
    pdf_path = '/media/Partage/Code/scrp-pdf/cpx_moy_amortie.pdf'
    rePDFer = RePDFer(pdf_path)
    # print(rePDFer.extract_text_from_pdf()[50])
    rePDFer.main()
    rePDFer.close()
    rePDFer.doc.Dispose()

if __name__ == '__main__':
    # pdf_path = './linux.pdf'
    pdf_path = './cpx_moy_amortie.pdf'
    rePDFer = RePDFer(pdf_path)
    # # print(rePDFer.extract_text_from_pdf()[50])
    rePDFer.main()
    rePDFer.close()