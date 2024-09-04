#!/usr/bin/env python3

import argparse
import csv
import subprocess
import sys
import tempfile

parser = argparse.ArgumentParser(description='Convert Postbank account statement pdf files to a single csv file.')
parser.add_argument('pdf_files', metavar='pdf_file', type=argparse.FileType('r'), nargs='+', help='pdf files to convert')
args = parser.parse_args()

year_str = ["Jan", "Feb", "März", "Apr", "May", "Juni", "Juli", "Aug", "Sep", "Okt", "Nov", "Dez"]
description_ledger_key = {
    "000000009802": 2250,
    "masjid al-falah": 2250,
    "masjid al falah": 2250,

    "schmidt hausverwaltu": 6310,
    "vattenfall": 6325,
    "telefonica": 6805,
    "ionos": 6810,
    "zakat": 2253,
    "prs": 2253,
    "kantin": 10000,
    "kan- tin": 10000,
}
skr_dic = {
    2250: "Dauerauftrag Spenden",
    2251: "Spenden",
    2252: "Spenden von Untermiete",
    2253: "Spendeaktionen Religiöse",
    2254: "Spendeaktionen Humanitäre",

    3700: "IHK",
    3730: "Amt",

    6800: "Porto",
    6805: "Telefon",
    6810: "Telefax und Internetkosten",
    6325: "Gas, Strom, Wasser",
    6310: "Miete",
    6420: "Beitrage",
    6855: "Zinsen",

    10000: "Kantin Jumat",
}


def main():
    statements = []

    for file in args.pdf_files:
        print(file.name)
        statement = parse_statements_from_file(str(file.name))
        write_statements_as_csv(file.name, statement)



def parse_statements_from_file(pdf_filename):
    txt_filename = next(tempfile._get_candidate_names()) + ".txt"

    bashCommand = f"pdftotext -layout -x 70 -y 100 -W 500 -H 700 {pdf_filename} {txt_filename}"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    with open(txt_filename, 'r') as f:
        filecontent = f.read()

    in_toprow_area = False
    in_statement_area = False
    in_statement = False
    last_line_token = []
    statements = []
    statement = {}

    for line in filecontent.splitlines():
        line_token = [token.strip() for token in line.split()]
        #print(line_token)

        if line_token == ['Buchung/Wert', 'Vorgang/Buchungsinformation', 'Soll', 'Haben']:
            in_toprow_area = False
            in_statement_area = True
            last_line_token = line_token
            continue

        if line_token[:4] == ['Auszug', 'Jahr', 'Seite', 'von']:
            in_toprow_area = True
            in_statement_area = False
            continue

        if line_token == ['Kontonummer', 'BLZ', 'Summe', 'Zahlungseingänge']:
            in_statement_area = False
            break

        if in_toprow_area:
            file_number = int(line_token[0])
            file_year = int(line_token[1])
            in_toprow_area = False

        if in_statement_area:
            #print(line_token)
            if line_token and not last_line_token: # if non empty and last one was empty
                in_statement = True
                statement = {}
                statement_first_line = True

            if not line_token:
                in_statement = False
                if statement: # if dict not empty
                    statements.append(statement)
                    #print("new statement written", statement)
                    statement = {}

            if in_statement:
                if statement_first_line:
                    try:
                        value = float(''.join(line_token[-2:]).replace('.', '').replace(',', '.'))
                        if value < 0:
                            statement['soll'] = value
                            statement['einnahme'] = ""
                            statement['ausgabe'] = "x"
                        else:
                            statement['haben'] = value
                            statement['einnahme'] = "x"
                            statement['ausgabe'] = ""
                    except ValueError:
                        in_statement = False
                        continue
                    date_day, date_month = line_token[0].split('/')[0][:-1].split('.')
                    if file_number == 1 and date_month not in ['12', '01']:
                        Exception(f"There is a statement from something else than Dec or Jan in the first document of {file_year}!")
                    elif file_number == 1 and date_month == '12':
                        date_year = file_year - 1
                    else:
                        date_year = file_year

                    data_type = ' '.join(line_token[1:-2])
                    month = int(date_month)
                    statement['lz'] = year_str[month-1]
                    statement['datum'] = f"{str(date_day)}.{month}.{date_year}"
                    statement['steuer'] = 1
                    statement['bemerkung'] = ""
                    statement_first_line = False
                else:
                    statement['bemerkung'] += ' '.join(line_token)
                    statement['bemerkung'] += ' '

                ledger_id = get_ledger_id(description_ledger_key, statement['bemerkung'])
                statement['kategorien'] = "-"
                statement['sachkonten'] = ledger_id

                if ledger_id in skr_dic:
                    statement['kategorien'] = skr_dic[ledger_id]

        last_line_token = line_token

    bashCommand = f"rm {txt_filename}"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    return statements

def get_ledger_id(description_ledger_key, description):
    ledger_id = 0

    for key, value in description_ledger_key.items():
        if key in description.lower():
            ledger_id = value

    return ledger_id
    

def write_statements_as_csv(filename, statements):
    with open(filename+'.csv', 'w', newline='') as csvfile:
        fieldnames = ['lz', 'datum', 'soll', 'haben', 'steuer', 'sachkonten', 'kategorien', 'einnahme', 'ausgabe', 'bemerkung']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for statement in statements:
            writer.writerow(statement)


if __name__ == "__main__":
    main()
