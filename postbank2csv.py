#!/usr/bin/env python3

import argparse
import csv
import subprocess
import sys
import tempfile
import config

parser = argparse.ArgumentParser(description='Convert Postbank account statement pdf files to a single csv file.')
parser.add_argument('pdf_files', metavar='pdf_file', type=argparse.FileType('r'), nargs='+', help='pdf files to convert')
args = parser.parse_args()


def main():
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
            iban = f"{line_token[4]}{line_token[5]}{line_token[6]}{line_token[7]}{line_token[8]}{line_token[9]}"
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
                    statement = {}

            if in_statement:
                if statement_first_line:
                    try:
                        value = float(''.join(line_token[-2:]).replace('.', '').replace(',', '.'))
                        if value < 0:
                            statement['soll'] = str(value).replace('.', ',')
                            statement['einnahme'] = ""
                            statement['ausgabe'] = "x"
                        else:
                            statement['haben'] = str(value).replace('.', ',')
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
                    statement['lz'] = config.year_str[month-1]
                    statement['datum'] = f"{str(date_day)}.{month}.{date_year}"
                    statement['steuer'] = 1
                    statement['desc'] = ""
                    statement_first_line = False
                else:
                    statement['desc'] += ' '.join(line_token)
                    statement['desc'] += ' '

                statement['kategorien'] = "-"
                statement['sachkonten'] = 0
                statement["bemerkung"] = "---"

                if iban == config.iban_prs and statement['einnahme'] != '':
                    set_static_ledger_from_iban(2253, "PRS", statement)
                else:
                    set_ledger_information(statement)

        last_line_token = line_token

    bashCommand = f"rm {txt_filename}"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    return statements

def set_ledger_information(statement):
    description = statement["desc"].lower()

    for key, data in config.skr_dic.items():
        for keyword in config.get_keys(data):
            if keyword in description:
                statement["sachkonten"] = key
                statement["kategorien"] = data["category"]
                statement["bemerkung"] = config.get_description(description, data["description"])
                break
    

def write_statements_as_csv(filename, statements):
    csv_filename = filename
    if ".pdf" in filename:
        csv_filename = filename.replace("pdf", "csv")

    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['lz', 'datum', 'soll', 'haben', 'steuer', 'sachkonten', 'kategorien', 'einnahme', 'ausgabe', 'bemerkung', 'desc']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for statement in statements:
            writer.writerow(statement)

def set_static_ledger_from_iban(ledger, description, statement):
    ledger_info = config.skr_dic[ledger]

    statement["sachkonten"] = ledger
    statement["kategorien"] = ledger_info["category"]
    statement["bemerkung"] = description

if __name__ == "__main__":
    main()
