from ftplib import FTP, all_errors
import pathlib

def login_to_ftp(host, user, password, port):
    _timeout = 5

    ftp = FTP()
    ftp.connect(host, port, _timeout)
    ftp.login(user, password)

    return ftp

def send_report(host, user, password, port, upload_file : pathlib.Path):
    try:
        ftp = login_to_ftp(host, user, password, port)

        with open(upload_file, 'rb') as file:
            ftp.storbinary(f'STOR {upload_file.name}', file)

        ftp.quit()
    except all_errors as err:
        print(f'Could not send report to the FTP server: {err}')