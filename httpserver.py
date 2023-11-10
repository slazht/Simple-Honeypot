import sys
import socket
import selectors
import types

host = "0.0.0.0"  
port = 1600 

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
    #flag = '220 (vsFTPd 2.3.4)\n'
    #conn.sendall(flag.encode("utf-8"))

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
            tosend = """HTTP/1.1 200 OK
Date: Fri, 10 Nov 2023 14:31:51 GMT
Content-Type: text/html
Transfer-Encoding: chunked
Connection: close
Server: nginx 1.1
Last-Modified: Friday, 10-Nov-2023 14:31:51 GMT
Cache-Control: private, no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0, s-maxage=0
cf-edge-cache: no-cache

551
<html>
<head></head></html>\n""".encode('utf-8')
            
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