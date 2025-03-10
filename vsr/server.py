import socket
import selectors

#TMP
from vsr.http.consts import HTTPConsts
from vsr.http.response import Response


class Server:
    def __init__(self,
                 address: str = "0.0.0.0",
                 port: int = 8989,
                 poll_interval: float = 0.1,
                 timeout: int = 5,
                 broadcast: bool = False,
                 broadcaster: None = None):

        self.address = address
        self.port = port

        self.timeout = timeout
        self.poll_interval = poll_interval

        # temp solution
        self.broadcast = broadcast
        self.broadcaster: Server = broadcaster

        self.broadcast_buff = b""

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
            if not self.broadcast:
                while True:
                    # 128kB
                    data = conn.recv(131072)

                    if not data:
                        break

                    # print(f"got data: {len(data)}")
                    self.broadcast_buff = data

            else:
                prev_buff = b""

                response = Response()
                response.add_header(HTTPConsts.CONTENT_TYPE,
                                    HTTPConsts.CONTENT_TYPE_MULTIPART_MIXED_REPLACE.format(boundary="frame"))

                header_str = response.get_headers_string(include_content_length=False)
                conn.sendall(header_str.encode())

                while True:
                    buff = self.broadcaster.broadcast_buff

                    if prev_buff != buff and len(buff) > 0:
                        res = Response(content_type=HTTPConsts.CONTENT_JPEG, payload=buff)

                        res_buff = res.get_response_string(include_http_in_header=False, terminate=True)
                        res_buff = b"--frame\r\n" + res_buff

                        # print(res_buff)

                        conn.sendall(res_buff)
                        prev_buff = buff

                        print(f"send data: {len(buff)}")

        except Exception as e:
            print(f"error while processing connection, addr: {addr}")
            print(e)

        finally:
            if not self.broadcast:
                self.broadcast_buff = b""

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
