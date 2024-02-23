import csv
from time import localtime, strftime

def create_csv_file(device_name, modem_manufacturer, modem_model):
    file_name = device_name.upper() + '_' + strftime('%Y-%m-%d %H:%M:%S', localtime()) + '.csv'

    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(['manufacturer', modem_manufacturer])
        writer.writerow(['model', modem_model])
        writer.writerow('')

    return file_name

def create_header(file, fields):
    with open(file, 'a', newline='') as csvfile:
        fieldnames = fields
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

def add_row(file, fields, dict):
    with open(file, 'a', newline='') as csvfile:
        fieldnames = fields
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writerow(dict)