import os
import sys
from pprint import pprint
import psycopg2 as pg
from dotenv import load_dotenv
import src.extracter.data_extracter as de
from tqdm import tqdm

load_dotenv()
CSV_PATH = os.getenv('CSV_PATH')

def submit_csvs():
    con = pg.connect(
        database="FinancePi",
        host="localhost",
        port="5432",
        user="postgres",
        password="Fred2001",)

    cur = con.cursor()

    for file in tqdm(os.listdir(CSV_PATH), desc="Submiting data to database\t", unit="csv"):
        with open(f"{CSV_PATH}/{file}", 'r') as fr:
            csv = fr.read()
            csv = csv.split('\n')
            for line in csv:
                if line == '':
                    continue
                line_data = line.split(',')
                cur.execute(f"select * from insert_movement('{de.Date(line_data[0], 'dd/mm/yyyy').to_sql_format()}', '{de.Date(line_data[1], 'dd/mm/yyyy').to_sql_format()}', '{remove_quotation(line_data[2])}', {line_data[3]}, {line_data[4]})")
                res = cur.fetchall()
                # pprint(line_data)
                # pprint(f"Already existed = {res[0][0]}")
                con.commit()
    con.close()

def remove_quotation(msg):
    cpy = ""
    for c in msg:
        if c != '\'' and c != '\"':
            cpy += c
    return cpy

if __name__ == '__main__':
    print(sys.argv[0])
    CSV_PATH = "../../data/csv"
    submit_csvs()