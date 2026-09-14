import socket

server = ('127.0.0.1', 9000)

s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s1.settimeout(2)
s1.connect(server)
print('C1 recv1', repr(s1.recv(4096).decode()))
s1.sendall(b'NAME|Alice\n')
print('C1 recv2', repr(s1.recv(4096).decode()))

s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.settimeout(2)
s2.connect(server)
print('C2 recv1', repr(s2.recv(4096).decode()))
s2.sendall(b'NAME|Bob\n')
print('C2 recv2', repr(s2.recv(4096).decode()))

print('C1 match', repr(s1.recv(4096).decode()))
print('C2 match', repr(s2.recv(4096).decode()))

s1.close()
s2.close()
