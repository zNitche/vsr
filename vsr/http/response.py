from vsr.http.consts import HTTPConsts


class Response:
    def __init__(self, status_code: int = 200,
                 content_type: str = HTTPConsts.CONTENT_TYPE_JSON,
                 payload: str | bytes = None):
        self.__headers: dict[str, ...] = {}
        self.status_code: int = status_code
        self.content_type: str = content_type

        self.payload: str | bytes | None = payload

    def get_content_length(self) -> int:
        return len(self.payload) if self.payload else 0

    def get_headers_string(self,
                           include_http_in_header: bool = True,
                           include_content_length: bool = True) -> str:
        header_rows = [f"HTTP/1.0 {self.status_code}"] if include_http_in_header else []

        if include_content_length:
            self.add_header(HTTPConsts.CONTENT_LENGTH, self.get_content_length())

        self.add_header(HTTPConsts.CONTENT_TYPE, self.content_type)

        for header, value in self.__headers.items():
            header_rows.append(f"{header}: {value}")

        header_string = "\r\n".join(header_rows)

        return f"{header_string}\r\n\r\n"

    @property
    def headers(self):
        return self.__headers.copy()

    def add_header(self, name: str, value: str | int):
        if name is not None:
            normalized_name = name.upper()

            if normalized_name not in self.__headers.keys():
                self.__headers[normalized_name] = value

    def get_body(self) -> str | bytes:
        return self.payload if self.payload else ""

    def get_response_string(self,
                            include_http_in_header: bool = True,
                            terminate: bool = False) -> str | bytes:

        headers = self.get_headers_string(include_http_in_header=include_http_in_header)
        body = self.get_body()

        response_string = headers.encode() + body if type(body) == bytes else f"{headers}{body}"
        suffix = b"\r\n" if type(body) == bytes else "\r\n"

        return response_string if not terminate else response_string + suffix
