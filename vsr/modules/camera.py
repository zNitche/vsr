class Camera:
    def __init__(self, name: str, address: str):
        self.name = name
        self.address = address

        self.stream_buffer = b''
