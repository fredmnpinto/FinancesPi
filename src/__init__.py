import src.gmail.email
import os, tqdm
from src.pydf.pdf import convert_to_text
from src import pydf
from src.extracter.data_extracter import Extract
from src.pydb.db import submit_csvs
from dotenv import load_dotenv

load_dotenv()

def get_data():
    # Download PDFs
    src.gmail.email.download_extratos()

    # Turn pdf into txt
    if len(os.listdir("data/pdf")) > 0:
        convert_to_text()
    else:
        print("There are no pdfs for me to convert")

    # Turn txt into csv
    txt_path = os.getenv("TXT_PATH")
    csv_folder_path = os.getenv("CSV_PATH")
    for file in tqdm.tqdm(os.listdir(txt_path), desc="Extracting data from txt\t", unit="txt"):
        if file in os.listdir(os.getenv('CSV_PATH')):
            continue
        Extract(txt_path + '/' + file).save_to_csv()

    # Send data to db
    submit_csvs()