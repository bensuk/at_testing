import device_connection.connection as connection
import report.csv_report as csv_report
from colorama import Fore, Style
from modules import print_information, configuration, ftp, send_email

class RunConfigurationCommands:
    def __init__(self, client : connection.Connection, printer : print_information.PrintInformation, device_configuration, configuration_file):
        self._client = client
        self._printer = printer
        self._dev_conf = device_configuration
        self._conf_file = configuration_file

    def create_csv_file(self):
        self._csv_file = csv_report.create_csv_file(self._dev_conf['device'], self._client.get_modem_manufacturer(), self._dev_conf['modem'])

    def create_csv_header(self):
        self.create_csv_file()

        self._fields = ['command', 'expected_code', 'result_code', 'passed']
        csv_report.create_header(self._csv_file, self._fields)

    def run_commands(self, print_on_same_line = False):
        self._commands = self._dev_conf['commands'].copy()
        self._completed_commands = 0
        self._successful_commands = 0
        self._print_on_same_line = print_on_same_line

        self.create_csv_header()
        self._print_header()
        self._client.send_many_at_commands_callback(self._dev_conf['commands'], self.process_result, False)

        self.send_report_to_ftp_server()
        self.send_email_notification()

    def process_result(self, result):
        for command in self._commands:
            if command['command'] == result['command']:
                if self._print_on_same_line and self._completed_commands > 0:
                    self._printer.jump_line(3)
                else:
                    self._printer.jump_line(2)

                if result['result_code'] == command['expected_code']:
                    self._printer.print_on_current_line(f'{result["result_code"]: ^8} | {result["command"]: <22} | {command["expected_code"]: ^8} | {"Passed": ^7}')

                    result['passed'] = True
                    self._successful_commands += 1
                else:
                    self._printer.print_on_current_line(f'{result["result_code"]: ^8} | {result["command"]: <22} | {command["expected_code"]: ^8} | {"Failed": ^7}')

                    result['passed'] = False

                del result['results']
                result['expected_code'] = command["expected_code"]
                csv_report.add_row(self._csv_file, self._fields, result)

                self._commands.remove(command)
                self._completed_commands += 1

                self._print_results()
                break

    def _print_header(self):
        header = f'Received | {"Command": <22} | Expected | Results'
        self._printer.print_on_current_line(header)
        self._printer.print_new_line(str.ljust('-', len(header), '-'))
        self._printer.print_new_line()
        self._printer.print_new_line()

    def _print_results(self):
        self._printer.print_new_line()

        if self._commands:
            self._printer.print_new_line()
            self._printer.print_new_line()
            self._printer.print_new_line()
        else:
            self._printer.print_new_line(f'End of testing. Tested {self._completed_commands} commands:')

        self._printer.print_new_line(f'Passed: {Fore.GREEN}{self._successful_commands}{Style.RESET_ALL}')
        self._printer.print_new_line(f'Failed: {Fore.RED}{self._completed_commands - self._successful_commands}{Style.RESET_ALL}')

        if self._commands:
            self._printer.jump_line(4)
        else:
            self._printer.print_new_line()
            self._printer.print_new_line()
            self._printer.jump_line()

    def send_report_to_ftp_server(self):
        ftp_configuration = configuration.get_ftp_configuration(self._conf_file)
        ftp.send_report(ftp_configuration['hostname'], ftp_configuration['username'], ftp_configuration['password'], ftp_configuration['port'], self._csv_file)

    def send_email_notification(self):
        subject = f"{self._dev_conf['device']} device completed test"
        email_message = f"""Test completed!\n\nTested commands: {self._completed_commands}
            Passed: {self._successful_commands}
            Failed: {self._completed_commands - self._successful_commands}"""
    
        email_configuration = configuration.get_email_configuration(self._conf_file)
        send_email.send_message(email_configuration, subject, email_message)