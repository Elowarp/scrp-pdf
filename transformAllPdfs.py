import os


def iterate(pathdir = "pdfs", root='pdfs'):
    for root, dirs, files in os.walk(pathdir):
        for file in files:
            print("Execution de "+file)
            os.system(f"python main.py {root}/{file} -o {root.split('/')[-1]}-{file[:-4]} -p 3")

if __name__ == "__main__":
    iterate()