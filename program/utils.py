from datetime import datetime
import smtplib
from program import config
import os


def log_to_file(log: str):
    with open('logs.txt', 'a') as logs_file:
        logs_file.write(str(datetime.now()) + " | " + log + "\n")

        logs_file.close()


def get_logs_from_file():
    with open('logs.txt', 'r') as logs_file:
        logs = logs_file.read()

        logs_file.close()
        return logs


def get_computer_info():
    try:
        cores_amount = os.environ['NUMBER_OF_PROCESSORS']
        os_system = os.environ['OS']

        return cores_amount, os_system
    except BaseException as error:
        log_to_file(str(error))
        return


def get_email_content():
    cores_amount, os_system = get_computer_info()
    email_body = """
    Subject: Świat Książki - Scraper\n
        Computer specification:
        coses amount: %s
        os: %s
    ----------------------------------
    \n
    """ % (cores_amount, os_system)

    email_body += get_logs_from_file()

    return email_body


def send_log_email():
    try:
        smtpObj = smtplib.SMTP(config.email['smtp'], config.email['port'])

        smtpObj.starttls()

        smtpObj.login(config.email['email_from'], config.email['password'])

        smtpObj.sendmail(config.email['email_from'], config.email['email_to'], get_email_content().encode("utf8"))

        smtpObj.close()
    except BaseException as error:
        log_to_file(str(error))


def turn_computer_off():
    os.system('shutdown -s -t 15')
