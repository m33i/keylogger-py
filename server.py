import socket

host = socket.gethostname()
port = 1337
s = socket.socket()
s.bind((host,port))
s.listen(5)

print("Waiting for client...")
conn,addr = s.accept()
print("Connected by " + addr[0])

while True:
	data = conn.recv(1024)
	if  data:
         print(data.decode('utf-8'))