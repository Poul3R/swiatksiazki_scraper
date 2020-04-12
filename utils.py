from datetime import datetime
import smtplib
import config
import os

def log_to_file(log: str):
    with open('logs.txt', 'a') as logs_file:
        logs_file.write(str(datetime.now()) + " | " + log + "\n")


def get_computer_info():
    computer_name = os.environ['COMPUTERNAME']
    cores_amount = os.environ['NUMBER_OF_PROCESSORS']
    os_system = os.environ['OS']

    return cores_amount, computer_name, os_system


def send_email():
    smtpObj = smtplib.SMTP(config.email['smtp'], config.email['port'])
    print(str(smtpObj.ehlo()))

    smtpObj.starttls()

    smtpObj.login(config.email['email_from'], config.email['password'])

    smtpObj.sendmail(config.email['email_from'], config.email['email_to'], 'Subject: So long.\nTest message from scraper')

    smtpObj.close()

get_computer_info()

email_body = """
Subject: Świat Książki Scraper \n
Computer specification:


"""