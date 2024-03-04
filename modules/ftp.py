from ftplib import FTP
import pathlib

def send_report(host, user, password, port, upload_file : pathlib.Path):
    try:
        _timeout = 5

        ftp = FTP()
        ftp.connect(host, port, _timeout)
        ftp.login(user, password)

        with open(upload_file, 'rb') as file:
            ftp.storbinary(f'STOR {upload_file.name}', file)

        ftp.quit()
    except Exception:
        print('Could not send report to the FTP server')