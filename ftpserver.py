import sys
import socket
import selectors
import types

host = "0.0.0.0"  
port = 1500 

sel = selectors.DefaultSelector()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)
    flag = '220 (vsFTPd 2.3.4)\n'
    conn.sendall(flag.encode("utf-8"))

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            #sent = sock.send(data.outb)
            tosend = ''
            if 'USER' in str(data.outb):
                tosend = ''.encode('utf-8')
            elif 'PASS' in str(data.outb):
                tosend = '530 Login incorrect.\n'.encode('utf-8')
            else:
                tosend = '530 Please login with USER and PASS.\n'.encode('utf-8')
            sent = sock.send(tosend)
            #print(sent)
            data.outb = tosend[sent:]
            #print(data.outb)

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()