import os
from bs4 import BeautifulSoup
import urllib.request
import requests

chunk_size = 2000

# Mets tout les pdf du site dans le dossier ./pdfs/...

def explore(anchor):
    with urllib.request.urlopen('https://nussbaumcpge.be/public_html/Sup/MP2I/'+anchor) as response:
        webpage = response.read()
        soup = BeautifulSoup(webpage, 'html.parser')
        print("\n"+anchor[:-4] +
              "---------------------------------------------------")
        if not os.path.isdir("pdfs/"+anchor[:-4]):
            os.makedirs("pdfs/"+anchor[:-4])
        for pdf in (soup.find_all("div", {"class": "column1"})[0].find_all('a')):
            pdflink = pdf.get('href', '/')
            url = 'https://nussbaumcpge.be/public_html/Sup/MP2I/'+pdflink
            print(url)
            r = requests.get(url, stream=True)

            with open("pdfs/"+anchor[:-4]+"/"+pdflink, 'wb') as fd:
                for chunk in r.iter_content(chunk_size):
                    fd.write(chunk)


def main():
    with urllib.request.urlopen('https://nussbaumcpge.be/public_html/Sup/MP2I/index.php') as response:
        webpage = response.read()
        soup = BeautifulSoup(webpage, 'html.parser')
        if not os.path.isdir("pdfs"):
            os.makedirs("pdfs")

        for anchor in soup.find("ul", {"id": "onglets"}).find_all('a'):
            try:
                onglet = anchor.get('href', '/')
                if onglet == "index.php":
                    continue
                explore(onglet)
            except urllib.error.HTTPError:
                print("404 Not Found")


if __name__ == "__main__":
    main()
