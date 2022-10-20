from login_exception import LoginException
from settings.settings import Settings

import json
import socket
import threading
import traceback

settings = Settings()

class ChatServer:
    def __init__(self):
        self._header_size = settings.header_size
        self._identifier = 'Server > '
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.bind((settings.server_ip, settings.server_port))
        self._server.listen(settings.max_connections_accepted)
        print('[*] Chat Server Has Started')

    def mainloop(self):
        while True:
            try:
                client, address = self._server.accept()
                print(f'[*] New connection from {address[0]}')
                client_handler = threading.Thread(target=self.session, args=(client, address))
                client_handler.start()
            except KeyboardInterrupt:
                break

        self._server.close()

    def login(self, sock):
        for i in range(0,3):
            try:
                request = self.receive_msg(sock)
                login_attempt = json.loads(request)
                return login_attempt['username']
            except:
                error = traceback.format_exc()
                print(error)
                if i == 2:
                    raise LoginException('Login failed!')
                continue

    def chat(self, client, address):
        with client as sock:
            username = None
            try:
                username = self.login(sock)
            except LoginException as ex:
                username = None
            if username == None:
                print(f'[*] Failed login attempt from {address[0]}')
                print(f'[*] {address[0]} has been kicked from server')
                sock.close()
            self.send_msg(sock, msg)
            while True:
                try:
                    request = self.receive_msg(sock)
                    if request == '/q':
                        break
                    print(request)
                    msg = input(self._identifier)
                    self.send_msg(sock, f'{self._identifier }{msg}')
                except:
                    error = traceback.format_exc()
                    print(error)
                    break
            sock.close()
        print(f'[*] {address[0]} has disconnected from the server\r\n')

    def send_msg(self, sock, msg):
        msg = msg + '\r\n'
        payload = f'{len(msg):<{self._header_size}}'+msg
        sock.send(payload.encode('utf-8'))

    def receive_msg(self, sock):
        buffer = ""
        new_msg = True
        while True:
            raw_request = sock.recv(self._header_size)
            if new_msg:
                msglen = int(raw_request.decode("utf-8"))
                new_msg = False
                continue
            buffer += raw_request.decode("utf-8")
            if len(buffer) >= msglen:
                break
        return buffer.strip()



def main():
    app = ChatServer()
    app.mainloop()

if __name__ == "__main__":
    main()