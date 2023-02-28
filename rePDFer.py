'''
 Nom : Elowan
 Email : elowanh@yahoo.com
 Création : 12-01-2023 11:29:13
 Dernière modification : 28-02-2023 14:52:59
'''

import pdfminer
from pdfminer.high_level import extract_pages

from odf.opendocument import load
from odf.style import Style, TextProperties
from odf.text import H, P, Span

from pdfviewer import PDFViewer
from tkinter import Tk

import json
import os
import sys

# Usefull functions
def round_bbox(bbox):
    """
    Round the bbox to the nearest integer
    Parameters
        bbox (list) - The bbox to round

    Returns
        (list) - The rounded bbox
    """
    return [round(x) for x in bbox]

def approximatily_equal(a, b, tolerance=5):
    """
    Return True if a and b are approximatily equal (with a tolerance)
    Parameters
        a (float) - The first number
        b (float) - The second number
        tolerance (float) - The tolerance

    Returns
        (bool) - True if a and b are approximatily equal
    """
    return abs(a-b) < tolerance

def approx_tuple_equal(a, b, tolerance=5):
    """
    Return True if a and b are approximatily equal (with a tolerance)
    Parameters
        a (tuple) - The first tuple
        b (tuple) - The second tuple
        tolerance (float) - The tolerance

    Returns
        (bool) - True if a and b are approximatily equal
    """
    if len(a) != len(b):
        return False
    
    # For each element of the tuple
    for i in range(len(a)):
        if not approximatily_equal(a[i], b[i], tolerance):
            return False

    return True

class RePDFer:
    def __init__(self, pdf_path, output_name="output", page_to_skip=2):
        self.pdf_path = pdf_path
        self.page_to_skip = page_to_skip

        self.file = open(pdf_path, 'rb')
        self.filename = pdf_path.split('/')[-1].split('.')[0]
        self.output_name = output_name
        self.parser = pdfminer.pdfparser.PDFParser(self.file)
        self.document = pdfminer.pdfdocument.PDFDocument(self.parser)
        self.writing_section = {
            "title": "",
            "subtitle": "",
            "section": "",
        }

        # Sets styles for the odt document
        self.odtdoc = load("template.odt")
        self.styles = {
            "BigTitle" : Style(name="Title", family="paragraph"),
            "Title" : Style(name="Heading 1", family="paragraph"),
            "Subtitle" : Style(name="Heading 2", family="paragraph"),
            "Section" : Style(name="Heading 3", family="paragraph"),
            "Text": Style(name="Paragraphe", family="paragraph"),
            "Définition": Style(name="Définition", family="paragraph"),
        }
        
        # Get the resolution of the pdf
        self.pdfsize = [x.mediabox for x in pdfminer.pdfpage.PDFPage.create_pages(self.document)][25]
        self.pdfsize = (round(self.pdfsize[2]), round(self.pdfsize[3]))

        # Creating the window
        self.root = Tk()
        self.zoom = 2
        self.viewer = PDFViewer(pdf_path, self.pdfsize, zoom=self.zoom)
        self.root.geometry("{}x{}".format(self.pdfsize[0]*self.zoom,self.pdfsize[1]*self.zoom))
        self.root_exists = True

        # Knows whetever the windows is closed or not
        def on_quit():
            self.root_exists = False
            self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_quit)

    def extract_content_from_pdf(self, pageInformations):
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

        print("Getting pages from pdf")
        for page_layout in extract_pages(self.pdf_path):
            page_elements = []
            date = ""
            for element in page_layout:
                # Checks if the element is the page number and if it is, sets the date
                if approx_tuple_equal(round_bbox(element.bbox), pageInformations["page_number"], 5):
                    date = element.get_text()

                else:
                    # Adds every piece of the layout to the elements list                
                    page_elements.append(element)

            # Avoid transition pages by getting the last one showing before
            # changing to the next page 
            current_page_id = date.split(" / ")[0]
            if current_page_id != previous_page_id:
                previous_page_id = current_page_id
                pages_temp.append(previous_page_elements)
                previous_page_elements = page_elements

            else:
                previous_page_elements = page_elements


        pages_temp.append(previous_page_elements)

        pages = []

        # Skips the defaults pages of every PDF's and get the content
        # out of every other pages
        # print(self.page_to_skip)
        print("Getting informations from pages")
        for page_layout in pages_temp[self.page_to_skip:]:
            pages.append(self.extract_information_from_page(page_layout, pageInformations))

        return pages

    def extract_information_from_page(self, page_layout, pageInformations):
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
            "definitions": []
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

                # Todo : Find a way to enter definition in the pageInformations
                #     instead of hardcoding it
                # If the text is blue, it's a kind of definition
                if (0.2, 0.2, 0.7) in fontinfo:
                    if text != "":
                        content["definitions"].append(text)
                
                else:
                    content["texts"].append(text)

                # Checks if the text is a part of "defined" information 
                # wanted/gave by the user such as the title, subtitle, unwanted
                # information etc.
                for section, value in pageInformations.items():
                    if section == "unwanted_informations":
                        for unwanted in value:
                            if approx_tuple_equal(unwanted, round_bbox(element.bbox), 5):
                                if text in content["texts"]:
                                    content["texts"].remove(text)

                    else:   
                        # Tests if the top left corner is almost the same or the bottom right is
                        if (approximatily_equal(round_bbox(element.bbox)[0], value[0], 5) and \
                        approximatily_equal(round_bbox(element.bbox)[1], value[1], 5)) or \
                        (approximatily_equal(round_bbox(element.bbox)[2], value[2], 5) and \
                        approximatily_equal(round_bbox(element.bbox)[3], value[3], 5)):
                            # If the text is in the defined information, we need
                            # to remove it from the text list because it was 
                            # already added
                            content[section] = text
                            if text in content["texts"]:
                                content["texts"].remove(text)

        return content

    def decode_text(self, text):
        """
        Decode the text from the pdf
        :param text: text to decode
        :return: decoded text
        """
        text = text.replace('`e', 'è',)
        text = text.replace('´e', 'é',)
        text = text.replace('`a', 'à',)
        text = text.replace('ˆa', 'â',)
        text = text.replace('ˆe', 'ê',)
        text = text.replace('ˆı', 'î',)
        text = text.replace('ˆo', 'ô',)
        text = text.replace('¸c', 'ç',)
        text = text.replace('`u', 'ù',)
        text = text.replace('ˆu', 'û',)

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

    def askInformations(self):
        """
        Ask the user for the informations for a better anylizing 
        of the page
        Returns:
            (dict) - Dict containing :
                        - The place of the page numbers
                        - The place of the page titles
                        - The place of the page subtitles
                        - The place of the page sections
                        - Unwanted informations to remove
        """
        print("Asking informations from the PDF")

        # Creates a temporary list of pages
        extracted_pages = [x for x in extract_pages(self.pdf_path)]
        page_elements = []

        important_texts = []

        # Questions to ask the user
        questions = [
            "Please click on the page number",
            "Please click on the page title",
            "Please click on the page subtitle",
            "Please click on the page section",
            "Please click on the unwanted informations until you're done & close the window",
        ]

        # Todo : Make the user choose the page he wants to ask the informations
        #    because sometimes some pages does not have all the informations 
        pageToAsk = 37

        # Gets all the texts from the page and add them to the elements list
        for element in extracted_pages[pageToAsk]:
            if isinstance(element, pdfminer.layout.LTTextBoxHorizontal):
                page_elements.append(element)

        # Function called when the user clicks on a text
        def callback(event):
            # Gets the id of the text corresponding to the id of the 
            # text in the page_elements list
            id = int(event.widget.gettags("current")[0])

            # Adds the text to the important_texts list
            important_texts.append(page_elements[id])

            # Ask the user the next question incoming the questions list
            print(questions[
                len(important_texts) if len(important_texts) < len(questions) 
                else len(questions) - 1
            ])

        # Displays the page with extra rectangles to the user for it to click on
        self.viewer.displayPageWithInformations(pageToAsk, page_elements, callback)

        # Starts the question loop until it closes the window
        print(questions[0])
        while(self.root_exists):
            self.root.update()

        # Sorts informations saved by the user
        pageinformations = {
            "page_number": round_bbox(important_texts[0].bbox),
            "title": round_bbox(important_texts[1].bbox),
            "subtitle": round_bbox(important_texts[2].bbox),
            "section": round_bbox(important_texts[3].bbox),
            "unwanted_informations": [round_bbox(x.bbox) 
                                        for x in important_texts[4:]],
        }

        # Tkinter loop to keep the window open
        self.root.mainloop()

        print("Thank u for the informations")
        return pageinformations

    def save_config(self, pageinformations:dict):
        """
        Save the informations in a json file
        """
        with open("config.json", "w") as f:
            json.dump(pageinformations, f)

    def main(self):
        """
        Write the text in a file
        :param text: text to write
        :return: None
        """
        # Ask the user informations about the pdf in general so
        # we can extract the text in a better way (avoid certain texts etc)
        # but if the config file exists, we don't need to ask the user
        if not os.path.exists("config.json"): 
            pageInformations = self.askInformations()
            self.save_config(pageInformations)
        pageInformations = json.load(open("config.json", "r")) 
        
        # Extract the nectare from the pdf
        pages = self.extract_content_from_pdf(pageInformations)

        print("Writting output")

        for page in pages:
            ## Avoid duplicated summuary after each title/subtitle
            if self.title_or_subtitle_changement(page): continue 
            
            self.section_changement(page)

            final_text = ""

            for definition in page["definitions"]:
                final_text += definition

            if final_text != "":
                text = P(stylename=self.styles["Définition"], text=final_text)
                self.odtdoc.text.addElement(text)

            final_text = ""
            for line in page["texts"]:
                # If there is an image
                if "Figure" in line:
                    final_text += "\nIMAGE\n\n"
                    final_text += "*" + line[:-1] + "*\n\n"

                # If it's something you have to know by heart
                elif "♥" in line:
                    final_text += "\n**" + line[:-1] + "**\n\n"

                else:
                    final_text += line.replace('\n', ' ') + '\n'

            text = P(stylename=self.styles["Text"], text=final_text)
            self.odtdoc.text.addElement(text)

        print("Everything went well.")

    def title_or_subtitle_changement(self, page):
        changed = False
        if self.writing_section["title"] != page["title"]:
            # Write the title in the odt file
            text = H(outlinelevel=2, stylename=self.styles["Title"], text=page["title"])
            self.odtdoc.text.addElement(text)

            # Keep up to date the current title
            self.writing_section["title"] = page["title"]
            changed = True

        if self.writing_section["subtitle"] != page["subtitle"]:
            # Write the title in the odt file
            text = H(outlinelevel=3, stylename=self.styles["Subtitle"], text=page["title"])
            self.odtdoc.text.addElement(text)

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
            self.odtdoc.text.addElement(text)

    def close(self):
        self.odtdoc.save(self.output_name + ".odt")
        self.file.close()

if __name__ == '__main__':
    argv = sys.argv
    pdf_path = "input/linux.pdf"
    output_name = "output/AutoCours - Linux"
    rePDFer = RePDFer(pdf_path, output_name)
    rePDFer.main()
    rePDFer.close()