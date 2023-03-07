'''
 Nom : Elowan
 Création : 07-03-2023 12:50:30
 Dernière modification : 07-03-2023 13:17:47
'''
from odf.opendocument import load
from odf.style import Style
from odf.text import H, P

class LibreOfficeModule:
    def __init__(self, output_filename):
        self.output_filename = output_filename
        
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
        
        self.writing_section = {
            "title": "",
            "subtitle": "",
            "section": "",
        }

    def main(self, pages):
        """
        Write the text in a file
        :param text: text to write
        :return: None
        """
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
        self.odtdoc.save(self.output_filename + ".odt")