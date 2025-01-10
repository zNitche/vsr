class Response:
    def __init__(self, status_code: int = 200,
                 content_type: str = "application/json",
                 payload: str = None):
        self.__headers: dict[str, ...] = {}
        self.status_code: int = status_code
        self.content_type: str = content_type

        self.payload: str | None = payload

    def get_content_length(self) -> int:
        return len(self.payload) if self.payload else 0

    def get_headers_string(self) -> str:
        header_rows = [f"HTTP/1.0 {self.status_code}"]

        for header, value in self.__headers.items():
            header_rows.append(f"{header}: {value}")

        self.add_header("CONTENT-TYPE", self.content_type)

        header_string = "\r\n".join(header_rows)

        return header_string

    @property
    def headers(self):
        return self.__headers.copy()

    def add_header(self, name: str, value: str | int):
        if name is not None:
            normalized_name = name.upper()

            if normalized_name not in self.__headers.keys():
                self.__headers[normalized_name] = value

    def get_body(self) -> str:
        return self.payload if self.payload else ""

    def get_response_string(self) -> str:
        headers = self.get_headers_string()
        body = self.get_body()

        return f"{headers}\r\n\r\n{body}"
