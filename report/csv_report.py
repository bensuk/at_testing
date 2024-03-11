import csv
from time import localtime, strftime
import pathlib

def create_csv_file(device_name, modem_manufacturer, modem_model):
    # file_name = device_name.upper() + '_' + strftime('%Y-%m-%d %H:%M:%S', localtime()) + '.csv'
    #windows
    file_name = device_name.upper() + '_' + strftime('%Y-%m-%d %Hh%Mm%Ss', localtime()) + '.csv'
    path = pathlib.Path(f'report/reports/{file_name}')

    if not path.parent.exists():
        path.parent.mkdir(mode=0o775)

    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(['manufacturer', modem_manufacturer])
        writer.writerow(['model', modem_model])
        writer.writerow('')

    return path

def create_header(file, fields):
    with open(file, 'a', newline='') as csvfile:
        csv.DictWriter(csvfile, fieldnames=fields).writeheader()

def add_row(file, fields, dict):
    with open(file, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writerow(dict)