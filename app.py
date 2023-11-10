import socket

HOST = "127.0.0.1"  
PORT = 1500 

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print('Server listening on port '+str(PORT))
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        flag = '220 (vsFTPd 3.0.3)\n'
        conn.sendall(flag.encode("utf-8"))
        while True:
            data = conn.recv(1024)
            if not data:
                break
            if 'USER' in str(data):
                conn.sendall(''.encode('utf-8'))
            elif 'PASS' in str(data):
                conn.sendall('530 Login incorrect.\n'.encode('utf-8'))
            else:
                conn.sendall('530 Please login with USER and PASS.\n'.encode('utf-8'))