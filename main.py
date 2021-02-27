import socket
import socketserver
import threading

client_addr = []
client_socket = []


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    ip = ""
    port = 0
    timeOut = 100

    def setup(self):
        self.ip = self.client_address[0].strip()
        self.port = self.client_address[1]
        self.request.settimeout(self.timeOut)
        print(self.ip + ":" + str(self.port) + " Connected to server！")
        client_addr.append(self.client_address)
        client_socket.append(self.request)

    def handle(self):
        while True:  # while循环
            try:
                data = str(self.request.recv(1024), 'ascii')
            except socket.timeout:
                print(self.ip + ":" + str(self.port) + " Timeout! Closing...")
                break
            except ConnectionResetError:
                print(self.ip + ":" + str(self.port) + " Socket Reset. Closing...")
                break
            except ConnectionAbortedError:
                print(self.ip + ":" + str(self.port) + " Connection Aborted. Closing...")
                break

            if data:  # 判断是否接收到数据
                cur_thread = threading.current_thread()
                response = bytes("{}: {}".format(cur_thread.name, data), 'ascii')
                self.request.sendall(response)

    def finish(self):
        print(self.ip + ":" + str(self.port) + " Socket Closed!")

        client_addr.remove(self.client_address)
        client_socket.remove(self.request)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Nothing to add here, inherited everything necessary form parents."""
    """Mix-in class to handle each request in a new thread."""
    pass


if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 6688
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)

    ip, port = server.server_address
    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)

    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

    try:
        while 1:
            pass
    except KeyboardInterrupt:
        server.shutdown()
        print("Server Closed!")
