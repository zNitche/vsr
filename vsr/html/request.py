import socket
import json
from vsr.html import utils
from vsr.html.consts import HTTPConsts


class Request:
    def __init__(self):
        self.protocol: str | None = None
        self.url: str | None = None
        self.method: list[str] | None = None
        self.content_length: int = 0
        self.content_type: str | None = None

        self.headers: dict[str, ...] = {}
        self.raw_body: str | None = None

        self.body: any = None

        self.query_params: dict[str, ...] = {}

    @staticmethod
    def from_socket(sock: socket.socket):
        try:
            request_header_string = utils.load_request_header_from_socket(sock)
            request = Request()
            request.parse_header(request_header_string)

            if request.content_length:
                request_body_string = sock.recv(request.content_length)
                request.parse_body(request_body_string.decode())

            return request

        except Exception as e:
            return None

    def parse_header(self, header_string: str):
        split_request_string = header_string.replace("\r", "").split("\n")

        if len(split_request_string) > 0:
            self.method, self.url, self.protocol = split_request_string[0].split()
            split_request_string.pop(0)

            self.headers = self.__parse_request_headers_string(split_request_string)
            self.__parse_query_params()

        self.content_length = int(self.headers[HTTPConsts.CONTENT_LENGTH]) if (HTTPConsts.CONTENT_LENGTH
                                                                               in self.headers.keys()) else 0

        self.content_type = self.headers.get(HTTPConsts.CONTENT_TYPE)

    def __parse_request_headers_string(self, split_request_string: list[str]) -> dict[str, ...]:
        request_struct = {}

        if len(split_request_string) > 0:
            for raw_row in split_request_string:
                row = raw_row.split(":")

                if len(row) == 2:
                    request_struct[row[0].upper()] = row[1].strip()

        return request_struct

    def __parse_query_params(self):
        split_url = self.url.split("?")

        if len(split_url) == 2:
            for param_string in split_url[1].split("&"):
                split_string = param_string.split("=")

                if len(split_string) == 2:
                    self.query_params[split_string[0]] = utils.url_encode(split_string[1])

    def __parse_body(self):
        # currently only application/json and text/plain are supported
        match self.content_type:
            case HTTPConsts.CONTENT_TYPE_JSON:
                return json.loads(self.raw_body)
            case HTTPConsts.CONTENT_TYPE_TEXT:
                return self.raw_body
            case _:
                return ""

    def parse_body(self, body_string: str):
        self.raw_body = body_string.replace("\r", "").replace("\n", "")
        self.body = self.__parse_body() if self.content_type else None
