import socket
import selectors
import threading
from vsr import Camera
from vsr.core.modules.stream_handler import StreamHandler


class Broadcaster:
    def __init__(self,
                 address: str = "0.0.0.0",
                 port: int = 9000,
                 poll_interval: float = 0.1,
                 timeout: int = 5):

        self.address = address
        self.port = port

        self.timeout = timeout
        self.poll_interval = poll_interval

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__selector = selectors.PollSelector

        self.requested_shutdown = False

        self.__cameras: list[Camera] = []
        self.__camera_threads: list[threading.Thread] = []

    def __mainloop(self):
        with self.__selector() as selector:
            selector.register(self.__socket, selectors.EVENT_READ)

            while not self.requested_shutdown:
                ready = selector.select(self.poll_interval)

                if ready:
                    try:
                        conn, addr = self.__socket.accept()
                        print(f"connection from {addr}")

                    except Exception as e:
                        print(f"error while handling connection: {str(e)}")

    def run(self):
        self.__setup_socket()
        self.__mainloop()

    def stop(self):
        self.requested_shutdown = True

        self.__socket.shutdown(socket.SHUT_RDWR)
        self.__socket.close()
