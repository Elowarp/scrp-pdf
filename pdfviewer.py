'''
 Nom : Elowan
 Email : elowanh@yahoo.com
 Création : 11-02-2023 18:46:40
 Dernière modification : 11-02-2023 22:35:28
'''

# Importing required modules
from tkinter import *
from PIL import Image,ImageTk
from pdf2image import convert_from_path

class PDFViewer(Frame):
    def __init__(self, pdf_file, defaultSize=(128*7,96*7), zoom=2):
        super().__init__()
        self.pdf_file = pdf_file
        self.defaultSize = defaultSize
        self.zoomedSize = (defaultSize[0]*zoom, defaultSize[1]*zoom)
        self.zoom = zoom

        # Creating the main window
        self.initUi()

    def initUi(self):
        # Setting size of the window
        self.pack(fill=BOTH, expand=1)

        # Creating the frame for PDF Viewer
        self.pdf_frame = Frame(self).pack(fill=BOTH)

        # Adding text widget for inserting images
        self.pdf = Text(self.pdf_frame,bg="grey")

        # Paking the text widget
        self.pdf.pack(fill=BOTH,expand=1)

        # Here the PDF is converted to list of images
        self.pages = convert_from_path(self.pdf_file, size=self.zoomedSize)

        # Empty list for storing images
        self.photos = []

        # Storing the converted images into list
        for i in range(len(self.pages)):
            self.photos.append(ImageTk.PhotoImage(self.pages[i]))
        
        self.canvas = Canvas(self, width=self.zoomedSize[0], height=self.zoomedSize[1])

    def displayPageWithInformations(self, indexPage, informations, callback):
        # Displaying the page
        img = self.canvas.create_image(0, 0,anchor=NW,image=self.photos[indexPage])
        
        i=0
        # For each element, we create a rectangle around it and bind it to a callback
        # The callback will be called when the user click on the rectangle
        for elmt in informations:
            x1,y1,x2,y2 = elmt.bbox
            
            # We need to zoom the coordinates to fit the image
            # (because the original image is around 128x96 which is too small)
            x1*=self.zoom
            y1*=self.zoom
            x2*=self.zoom
            y2*=self.zoom

            # Coordinates are inverted in the image
            y1= self.zoomedSize[1]-y1
            y2= self.zoomedSize[1]-y2

            # Creating the rectangle and tag it with the index of the element in the list
            rec = self.canvas.create_rectangle(x1,y1,x2,y2,activefill='black',tags=[i])

            # Binding the rectangle to the callback
            self.canvas.tag_bind(rec, "<Button-1>", callback)
            i+=1

        self.canvas.pack(fill=BOTH, expand=1)


if __name__ == "__main__":
    # Creating object of PDFViewer class
    size = (128*7,96*7)

    root = Tk()
    viewer = PDFViewer("pilesfiles.pdf")
    root.geometry("{}x{}".format(size[0],size[1]))
    viewer.displayPageWithInformations(50, [])

    root.mainloop()
