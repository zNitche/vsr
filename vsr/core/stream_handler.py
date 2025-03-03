import socket
import threading
import selectors
import time
from vsr.modules.camera import Camera
from vsr.logger import Logger


class StreamHandler:
    def __init__(self,
                 connection: socket.socket,
                 camera: Camera,
                 timeout: int = 5,
                 poll_interval: float = 0.5):

        self.__camera = camera

        self.__selector = selectors.PollSelector

        self.__thread = threading.current_thread()
        self.__connection = connection

        self.__poll_interval = poll_interval
        self.__timeout = timeout

        self.requested_shutdown = False

        self.__logger = Logger.for_thread(logger_name="stream_handler_logger",
                                          thread_uid=self.__thread.native_id)

    def process(self):
        self.__logger.info("init")
        self.__connection_loop()

        try:
            self.__connection.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            print(str(e))

    def __connection_loop(self):
        last_action_time = time.time()

        with self.__selector() as selector:
            selector.register(self.__connection, selectors.EVENT_READ)

            while self.__connection and not self.requested_shutdown:
                ready = selector.select(self.__poll_interval)
                current_loop_time = time.time()

                if ready:
                    try:
                        data = self.__connection.recv(131072)

                        if data:
                            self.__camera.stream_buffer = data

                    except:
                        print("Error while loading data")

                    last_action_time = time.time()

                if current_loop_time - last_action_time >= self.__timeout:
                    break
