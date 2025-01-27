import socket
import selectors
import threading
from vsr import Camera
from vsr.core.modules.stream_handler import StreamHandler


class Relay:
    def __init__(self,
                 address: str = "0.0.0.0",
                 port: int = 8989,
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

    def __setup_socket(self):
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.settimeout(self.timeout)

        self.__socket.bind((self.address, self.port))
        self.__socket.listen()

        print(f"Server listening on {self.address}:{self.port}")

    def add_camera(self, camera: Camera):
        if camera.name in [cam.name for cam in self.__cameras]:
            raise Exception(f"camera with name {camera.name} already exists")

        self.__cameras.append(camera)

    def __get_camera_for_address(self, address: tuple[str, int]):
        for camera in self.__cameras:
            if camera.address == address[0]:
                return camera

        return None

    def __handle_request(self, conn: socket.socket, addr: tuple[str, int]):
        cur_thread = threading.current_thread()

        try:
            camera = self.__get_camera_for_address(addr)

            if camera is None:
                raise Exception(f"camera hasn't been found for {addr}")

            stream_handler = StreamHandler(connection=conn, camera=camera)
            stream_handler.process()

        except Exception as e:
            print(f"error while processing connection, addr: {addr}, thread: {cur_thread.name}: {str(e)}")

        finally:
            conn.close()

            self.__camera_threads.remove(cur_thread)
            print(f"closed connection with: {addr}, thread: {cur_thread.name} / {cur_thread.native_id}")

    def __mainloop(self):
        with self.__selector() as selector:
            selector.register(self.__socket, selectors.EVENT_READ)

            while not self.requested_shutdown:
                ready = selector.select(self.poll_interval)

                if ready:
                    try:
                        conn, addr = self.__socket.accept()
                        print(f"connection from {addr}")

                        thread = threading.Thread(target=self.__handle_request, args=(conn, addr))
                        print(f"starting request handler: {thread.name}")

                        self.__camera_threads.append(thread)
                        thread.start()

                    except Exception as e:
                        print(f"error while handling connection: {str(e)}")

    def run(self):
        self.__setup_socket()
        self.__mainloop()

    def stop(self):
        self.requested_shutdown = True

        self.__socket.shutdown(socket.SHUT_RDWR)
        self.__socket.close()

        for thread in self.__camera_threads:
            thread.join()

        print(f"server has been stopped successfully")
