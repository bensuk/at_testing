from multiprocessing import Process, Manager
import connection
import csv_report

def run_commands(client : connection.Connection, commands, csv_file):
    results = client.send_many_at_commands(commands)
    compare_results(commands, results, csv_file)

def run_commands_multiprocessing(client : connection.Connection, commands, csv_file):
    manager = Manager()
    shared_list = manager.list()

    p1 = Process(target=client.send_many_at_commands_multiprocessing, args=(commands, shared_list))
    p2 = Process(target=compare_results, args=(commands, shared_list, csv_file))

    p1.start()
    p2.start()

    p1.join()
    if (p1.exitcode != 0):
        p2.terminate()
    else:
        p2.join()

def compare_results(commands : list, results : list, csv_file):
    fields = ['command', 'expected_code', 'result_code', 'passed', 'results']
    csv_report.create_header(csv_file, fields)

    command_count = len(commands)
    successful_count = 0

    print(f'\nrunning at commands ({command_count} commands to test)..')

    for command in commands:
        while True:
            for result in results:
                if command['command'] == result['command']:
                    if result['result_code'] == command['expected_code']:
                        print(f'[{"OK": ^5}] | {result["command"]: <22} | Expected code = Received code ("{command["expected_code"]}" = "{result["result_code"]}")')

                        dict = result.copy()
                        dict['expected_code'] = command["expected_code"]
                        dict['passed'] = True
                        csv_report.add_row(csv_file, fields, dict)

                        successful_count += 1

                    else:
                        print(f'[{"ERROR": ^5}] | {result["command"]: <22} | Expected code != Received code ("{command["expected_code"]}" != "{result["result_code"]}")')

                        dict = result.copy()
                        dict['expected_code'] = command["expected_code"]
                        dict['passed'] = False
                        csv_report.add_row(csv_file, fields, dict)
                    results.remove(result)
                    break
            else:
                continue
            break
    print(f'\nTested {command_count} commands:\n\tPassed: {successful_count}\n\tFailed: {command_count-successful_count}')