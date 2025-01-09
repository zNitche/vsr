import socket
import selectors


class Server:
    def __init__(self,
                 address: str = "0.0.0.0",
                 port: int = 8989,
                 poll_interval: float = 0.5,
                 timeout: int = 5):

        self.address = address
        self.port = port

        self.timeout = timeout
        self.poll_interval = poll_interval

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__selector = selectors.PollSelector

        self.requested_shutdown = False

    def __setup_socket(self):
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.settimeout(self.timeout)

        self.__socket.bind((self.address, self.port))
        self.__socket.listen()

        print(f"Server listening on {self.address}:{self.port}")

    def __handle_request(self, conn: socket.socket, addr: str):
        try:
            while True:
                data = conn.recv(4056)

                if not data:
                    break

                print(f"got data: {data}")

        except Exception as e:
            print(e)
            print(f"error while processing connection, addr: {addr}")

        finally:
            conn.close()
            print(f"closed connection with: {addr}")

    def __mainloop(self):
        with self.__selector() as selector:
            selector.register(self.__socket, selectors.EVENT_READ)

            while not self.requested_shutdown:
                ready = selector.select(self.poll_interval)

                if ready:
                    try:
                        conn, addr = self.__socket.accept()
                        print(f"connection from {addr}")

                        self.__handle_request(conn, addr)
                    except:
                        print("error while handling connection")

    def run(self):
        self.__setup_socket()
        self.__mainloop()

    def stop(self):
        self.requested_shutdown = True

        self.__socket.shutdown(socket.SHUT_RDWR)
        self.__socket.close()

        print(f"server has been stopped successfully")
