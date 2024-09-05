#!/usr/bin/env python3

import csv
import sys
import chardet
import argparse
import config

parser = argparse.ArgumentParser(description="Convert paypal CSV files.")
parser.add_argument('files', metavar='F', type=str, nargs='+', help='CSV files to be read')
args = parser.parse_args()

def main():    
    for file in args.files:
        print(file)
        write_statements_as_csv(file)

def write_statements_as_csv(file_path):
    encoding = detect_encoding(file_path)
    statements = read_csv_to_dict(file_path, encoding)

    with open("generated_"+file_path, 'w', newline='') as csvfile:
        fieldnames = ['lz', 'datum', 'soll', 'haben', 'steuer', 'sachkonten', 'kategorien', 'einnahme', 'ausgabe', 'bemerkung', 'desc']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for statement in statements:
            writer.writerow(statement)

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def read_csv_to_dict(file_path, encoding):
    statements = []
    
    with open(file_path, mode='r', newline='', encoding=encoding) as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter='\t')
        
        for row in csvreader:
            data_dict = {}
            data_dict['steuer'] = 1
            data_dict["desc"] = ""
            data_dict['kategorien'] = "-"
            data_dict['sachkonten'] = 0
            data_dict["bemerkung"] = "-"
            for header, value in row.items():
                #extract data from date
                if header == "Date":
                    day, month, year = value.split("/")
                    data_dict["lz"] = config.year_str[int(month)-1]
                    data_dict["datum"] = str(value).replace("/", ".")

                #extract data from value
                if header == "Net":
                    tmp_value = float(value.replace('.', '').replace(',', '.'))
                    if tmp_value< 0:
                        data_dict['soll'] = value
                        data_dict['einnahme'] = ""
                        data_dict['ausgabe'] = "x"
                    else:
                        data_dict['haben'] = value
                        data_dict['einnahme'] = "x"
                        data_dict['ausgabe'] = ""

                #extract data from recipient email 
                if header == "From Email Address":
                    data_dict["desc"] += f"From: {value} "
                if header == "To Email Address":
                    data_dict["desc"] += f"To: {value} "
                if header == "Note":
                    data_dict["desc"] += "Note: " + value
                    description = data_dict["desc"].lower()

                    if not data_dict['ausgabe']:
                        for key, data in config.skr_dic.items():
                            keys = config.get_keys(data)
                            for keyword in keys:
                                if keyword in description:
                                    data_dict["sachkonten"] = key
                                    data_dict["kategorien"] = data["category"]
                                    data_dict["bemerkung"] = config.get_description(description, data["description"])
            statements.append(data_dict)
    
    return statements

if __name__ == "__main__":
    main()