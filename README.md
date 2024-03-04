# Automated Modem AT commands testing

Test Modem AT commands using SSH protocol or serial communication

## Python version

Use Python 3.10 or newer version

## Required Python libraries

```bash
pip install paramiko pyserial colorama
```

## Installation

Download the projet to the local computer:

```bash
git clone https://github.com/bensuk/at_testing.git
```

## Configuration

Before running program, you need to set up a configuration file. Edit existing *configuration.json* file and save it.

### Email

Sends email messages about testing results

```json
"smtp":
{
  "port": 465,
  "smtp_server": "smtp.gmail.com",
  "sender_email": "sender",
  "password": "password",
  "receiver_email": "receiver"
}
```

`port` - SMTP server's port\
`smtp_server` - the address of the SMTP server\
`sender_email` - email address from which the message will be sent\
`password` - authentication password for the SMTP server\
`receiver_email - the receiver which will receive email messages about testing results`

### FTP

Sends the testing report to the FTP server

```json
"ftp_server":
{
  "hostname": "host",
  "port": 21,
  "username": "username",
  "password": "password"
}
```

`hostname` - FTP server address\
`port` - FTP server port\
`username` - username to login to the FTP server\
`password` - password to login to the FTP server

### AT commands

Define the device, modem, connection type and which commands to test. You can define multiple devices.

```json
"devices_commands":
[
  {
    "device": "RUT955",
    "modem": "EC25",
    "connection": ["ssh", "serial"],
    "commands":
    [
      {"command": "ATI", "arguments": [], "expected_code": "OK", "max_response_time": 300},
      {"command": "AT&V", "arguments": [], "expected_code": "OK", "max_response_time": 300},
      {"command": "ATF", "arguments": [], "expected_code": "ERROR", "max_response_time": 300},
      {"command": "AT+CSQ", "arguments": [], "expected_code": "OK", "max_response_time": 300},
      {"command": "ATF", "arguments": [], "expected_code": "OK", "max_response_time": 300},
      {"command": "AT+CMGF=1", "arguments": [], "expected_code": "OK", "max_response_time": 300},
      {"command": "AT+CMGS=\"phone_number\"", "arguments": ["message text!"], "expected_code": "OK", "max_response_time": 3000}
    ],
    "modem_port": "/dev/ttyUSB4"
  }
]
```

`device` - The name of the device that should be tested\
`modem` - Device's modem model\
`connection` - how to connect to the router. Supported `serial` and `ssh` connection types.\
`commands` - command which you want to test\
`modem_port` - the port to which the device itself connects to the modem to communicate. For modems such as the Teltonika TRM series, this field is not required.

---
**command**

`command` - AT command to test\
`arguments` - Arguments for the AT command, if required\
`expected_code` - expected code command should return\
`max_response_time` - wait for response in milliseconds

## Usage

Make sure that the *configuration.json* file is configured. 

### SSH

Make sure that you can connect to device via SSH.

Run application:
```bash
python3 main.py -c ssh -dev <device> -host <host> -u <user> -p <password>
```

**device** - name of the device you are connecting to\
**host** - hostname for SSH connection\
**user** - username for SSH connection\
**password** - password for SSH connection

Example:
```bash
python3 main.py -c ssh -dev rutx11 -host 192.168.1.1 -u root -p password
```

### Serial

Connect the device to the computer and find out which port the device is connected to. You can find out the port by running `$ sudo dmesg | grep -i usb` in a terminal window.

For serial communication, you would need the run the application with the root root privileges:

```bash
sudo -E python3 main.py -c serial -dev <device> -host <device port> -u <user> -p <password> -rate <Baud Rate>
```
**device** - name of the device you are connecting to\
**host** - the port of the device that is connected to computer\
**user** - username to login to the device. Not required for modems like Teltonika TRM series\
**password** - password for login to the device. Not required for modems like Teltonika TRM series\
**Baud Rate** - Baud Rate for serial communication

Example with login information:
```bash
sudo -E python3 main.py -c serial -dev rut955 -host /dev/ttyUSB4 -rate 115200 -u root -p password
```

Example without login information:
```bash
sudo -E python3 main.py -c serial -dev trm240 -host /dev/ttyUSB3 -rate 115200
```

## Output of the running application
![](https://github.com/bensuk/at_testing/blob/main/output.gif?raw=true)
