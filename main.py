import pdfminer
from pdfminer.high_level import extract_pages

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
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.file = open(pdf_path, 'rb')
        self.filename = pdf_path.split('/')[-1].split('.')[0]
        self.parser = pdfminer.pdfparser.PDFParser(self.file)
        self.document = pdfminer.pdfdocument.PDFDocument(self.parser)
        self.writing_section = {
            "title": "",
            "subtitle": "",
            "section": "",
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
        pages_temp = []

        previous_page_id = 1
        previous_page_elements = []

        for page_layout in extract_pages(self.pdf_path):
            page_elements = []
            last_text = ""
            for element in page_layout:
                # Used to scrap the page id
                if isinstance(element, pdfminer.layout.LTTextBoxHorizontal):
                    last_text = element.get_text()

                # Adds every piece of the layout to the elements list
                page_elements.append(element)
                
            
            # Avoid duplicated pages by getting the last one showing before
            # changing entirely
            current_page_id = last_text.split(" / ")[0]
            if current_page_id != previous_page_id:
                previous_page_id = current_page_id
                pages_temp.append(previous_page_elements)
                previous_page_elements = page_elements

            else:
                previous_page_elements = page_elements

        pages_temp.append(previous_page_elements)

        pages = []

        # Skips the defaults pages of every PDF's
        for page_index in range(3, len(pages_temp)):
            content = {
                "texts": [],
                "images": [],
                "title": "",
                "subtitle": "",
                "section": "",
            }

            for page_content in pages_temp[page_index]:
                if isinstance(page_content, pdfminer.layout.LTTextBoxHorizontal):
                    # Changes bad encoding of all his PDF's
                    text = self.decode_text(page_content.get_text())

                    # Gets the title/subtitle/section of the current page
                    # to always know where this piece of text is going to
                    # be at the end
                    if round(page_content.bbox[2]) == TITLE_X1 and \
                        round(page_content.bbox[3]) == TITLE_Y1:
                        
                        content["title"] = text

                    elif round(page_content.bbox[0]) == SUBTITLE_X0 and \
                        round(page_content.bbox[1]) == SUBTITLE_Y0:

                        content["subtitle"] = text

                    elif round(page_content.bbox[0]) == SECTION_X0 and \
                        round(page_content.bbox[3]) == SECTION_Y1:

                        content["section"] = text

                    else:
                        content["texts"].append(text)

            pages.append(content)

        return pages

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

        final_text = '# ' + self.filename.upper() + '\n\n'

        # Create text in markdown
        for page in pages:
            # Write titles/subtitles/sections when changing
            title_subtitle = self.title_or_subtitle_changement(page)

            ## Avoid duplicated summuary after each title/subtitle
            final_text += title_subtitle 
            if title_subtitle != "": continue 
            
            section = self.section_changement(page)
            final_text += section



            # Every thing that is NOT the last 4 string
            # Which are the name of the teacher, the course subject
            # the current page and the school  
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

            final_text += '\n'


        # Creates final file
        self.write_file(final_text)

    def title_or_subtitle_changement(self, page):
        string = ""
        if self.writing_section["title"] != page["title"]:
            string += "## " + page["title"]
            self.writing_section["title"] = page["title"]

        if self.writing_section["subtitle"] != page["subtitle"]:
            string += "### " + page["subtitle"]
            self.writing_section["subtitle"] = page["subtitle"]
        
        return string

    def section_changement(self, page):
        if self.writing_section["section"] != page["section"]:
            self.writing_section["section"] = page["section"]
            return "#### " + page["section"]

        return ""


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
        self.file.close()

if __name__ == '__main__':
    # pdf_path = './linux.pdf'
    pdf_path = './cpx_moy_amortie.pdf'
    rePDFer = RePDFer(pdf_path)
    # print(rePDFer.extract_text_from_pdf()[50])
    rePDFer.main()
    rePDFer.close()