"""
    Nom : Elowarp
    Création : 01-03-2023 13:55:45
    Dernière modification : 01-03-2023 13:55:59
    Define all types of elements used in the project
"""
from odf.style import Style

class Object:
    def __init__(self, text, style):
        self.text = text
        self.style = style

class Title(Object):
    def __init__(self, text, hierarchy):
        """
            hierarchy(int) : the importance of the title
        """
        self.hierarchy = hierarchy
        match hierarchy:
            case 0:
                self.style = Style(name="Title", family="paragraph")
            case 1:
                self.style = Style(name="Heading 1", family="paragraph")
            case 2:
                self.style = Style(name="Heading 2", family="paragraph")
            case 3:
                self.style = Style(name="Heading 3", family="paragraph")
            case 4:
                self.style = Style(name="Heading 4", family="paragraph")
            case e:
                raise ValueError("Hierarchy must be between 0 and 4")
        
        super().__init__(text, self.style)