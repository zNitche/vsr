import hashlib
import socket
import json
from vsr.utils import communication


class Packet:
    def __init__(self, content: dict[str, any]):
        self.content = content

    @staticmethod
    def from_socket(conn: socket.socket):
        size_buff = communication.receive(conn=conn, length=4)
        size = communication.int_from_bytes(size_buff)

        if size == 0:
            return None

        packet_data = communication.receive(conn, size)
        return Packet.from_bytes(packet_data)

    @staticmethod
    def from_bytes(buff: bytes):
        buff_size = len(buff)

        hash_length = 32

        if buff_size <= hash_length:
            raise Exception(f"packet buff size too small, expected ath least 32 bytes, got {buff_size}")

        body_size = buff_size - hash_length
        body = buff[:body_size]

        packet_checksum = buff[body_size:].decode()
        body_checksum = hashlib.md5(body).hexdigest()

        if not body_checksum == packet_checksum:
            raise Exception(f"packet checksum missmatch, expected: '{packet_checksum}' got '{body_checksum}'")

        return Packet(content=json.loads(body.decode()))

    def dump(self) -> bytes:
        body_buff = json.dumps(self.content).encode()

        checksum = hashlib.md5(body_buff).hexdigest().encode()

        content = body_buff + checksum
        size = communication.int_to_bytes(len(content))

        return size + content

    def __str__(self):
        return json.dumps(self.content)
