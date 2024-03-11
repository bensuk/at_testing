import paramiko
from time import sleep
import re

def connect(hostname, username, password, timeout = 1):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

    ssh_client.connect(
        hostname=hostname,
        username=username,
        password=password,
        timeout=timeout
    )
    return ssh_client

client = connect('192.168.8.119', 'root', 'Admin123')

channel = client.invoke_shell()
#tikrinu ar galiu jau siusti kita komanda

read_size = 1024

expr = bytes(f'^root@RUT955:.+# $', 'utf-8')

command = bytes('socat /dev/tty,raw,echo=0,escape=0x03 /dev/ttyUSB4,raw,setsid,sane,echo=0,nonblock ; stty sane\r', 'utf-8')


sleep(1)
channel.sendall(command)
sleep(.1)
channel.sendall('at\r')
sleep(.1)
channel.sendall(b'\x03\r')

channel.recv




#root@RUT955:~# socat /dev/tty,raw,echo=0,escape=0x03 /dev/ttyUSB4,raw,setsid,san\r\r\ne,echo=0,nonblock ; stty sane\r\nat\n\n\nOK\n\n

# channel.sendall(command)
# channel.sendall(b'\x03\r')
last_line = b''
done = False
while not done:
    data = last_line + channel.recv(read_size)
    data = data.split(b'\n')

    for i, line in enumerate(data):
        if line[-2:] == b'\r\r' and len(data) > i+1:
            data[i] = line[:-2] + data[i+1]
            line = data[i]
            del data[i+1]

        print(line)
        last_line = data[-1]

        if re.search(expr, line):
            done = True





