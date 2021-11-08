import os
from dotenv import load_dotenv
from tqdm import tqdm

def convert_to_text():
    load_dotenv()
    PDF_PATH = os.getenv("PDF_PATH")
    TXT_PATH = os.getenv("TXT_PATH")
    for file in tqdm(os.listdir(PDF_PATH), desc="Extracting txt from PDFs\t", unit="pdf"):
        pdf = f'\'{PDF_PATH}/{file}\''
        txt = f"{TXT_PATH}/'{file.split('.'[0])}.txt'"
        if 'EXTRATO COMBINADO' in file and txt not in os.listdir(TXT_PATH):
            command = f"pdftotext -layout '{PDF_PATH}/{file}' {TXT_PATH}/'{file.split('.')[0]}.txt'"
            result = os.system(command)
            if result != 0:
                print(f"Error on '{command}'")

if __name__ == '__main__':
    convert_to_text()
