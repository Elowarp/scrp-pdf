'''
 Nom : Elowan
 Création : 07-03-2023 12:50:30
 Dernière modification : 09-03-2023 10:56:57
'''
from mdutils.mdutils import MdUtils

class MarkdownModule:
    def __init__(self, output_filename):
        self.output_filename = output_filename  

        self.mdFile = MdUtils(file_name=self.output_filename, title="AutoCours")
        self.write_template()

        self.writing_section = {
            "title": "",
            "subtitle": "",
            "section": "",
        }

    def write_template(self):
        with open("template.md", "r", encoding="utf-8") as file:
            text = file.read()
            self.mdFile.write(text=text)
            

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

            # If there is an image
            if page["images"] != []:
                for image in page["images"]:
                    self.mdFile.write("<p align='center'><img src='/images/" + image + "'/></p>")
                    pass

            for definition in page["definitions"]:
                if "Figure" in definition:
                    self.mdFile.new_paragraph(text='_' + definition.strip() + '_')
                else:
                    self.mdFile.new_paragraph(text='!!! quote "Définition"\n    ' + definition)

            if final_text != "":
                self.mdFile.new_paragraph(text=final_text)

            final_text = ""
            for line in page["texts"]:
                # If it's something you have to know by heart
                if "♥" in line:
                    final_text += "\n**" + line[:-1] + "**\n\n"

                else:
                    final_text += line.replace('\n', '  ') + '\n'  # 2 espace a la fin d'une ligne permet de faire un saut de ligne sans nouveau paragraphe en md

            self.add_paragraph(text=final_text)

        print("Everything went well.")

    def add_header(self, level, text):
        if text != "": self.mdFile.new_header(level=level, title=text, add_table_of_contents="n")
    
    def add_paragraph(self, text):
        if text != "": self.mdFile.new_paragraph(text=text)

    def title_or_subtitle_changement(self, page):
        changed = False
        if self.writing_section["title"] != page["title"]:
            # Write the title in the odt file
            self.add_header(level=2, text=page["title"])

            # Keep up to date the current title
            self.writing_section["title"] = page["title"]
            changed = True

        if self.writing_section["subtitle"] != page["subtitle"]:
            # Write the title in the odt file
            self.add_header(level=3, text=page["title"])

            # Keep up to date the current subtitle
            self.writing_section["subtitle"] = page["subtitle"]
            changed = True
        
        return changed

    def section_changement(self, page):
        if self.writing_section["section"] != page["section"]:
            # Keep up to date the current section
            self.writing_section["section"] = page["section"]
            
            # Write the title in the odt file
            self.add_header(level=4, text=page["section"])


    def close(self):
        self.mdFile.create_md_file()