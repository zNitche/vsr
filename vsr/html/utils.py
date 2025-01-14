import socket


def load_request_header_from_socket(sock: socket.socket) -> str:
    request_header_string = ""

    while True:
        request_line = socket.SocketIO(sock, mode="rb").readline()
        request_line = request_line.decode()

        if request_line == "\r\n" or not request_line:
            break

        request_header_string += request_line

    return request_header_string

def url_encode(value: str | int | None) -> str | None:
    # currently only spaces are supported
    if value is None:
        return value

    return value.replace(" ", "%20")
