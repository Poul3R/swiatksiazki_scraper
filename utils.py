from datetime import datetime
import multiprocessing
import smtplib

def log_to_file(log: str):
    with open('logs.txt', 'a') as logs_file:
        logs_file.write(str(datetime.now()) + " | " + log + "\n")


def get_computer_info():
    cores_amount = multiprocessing.cpu_count()

    # name, cores, rams, network speed

def send_email():
    msmtObj = smtplib.SMTP('')