from typing import NamedTuple, Mapping
from socket import socket


class Request(NamedTuple):
    protocol: str
    method: str
    path: str
    headers: Mapping[str, str]

    error_response = """HTTP/1.1 500 SERVER ERROR\r\nContent-Type: application/json\r\n\r\n{'status': 500, 'message': 'internal server error'}"""

    @classmethod
    def from_socket(cls: type, request: "Request", client_socket) -> "Request":
        """Read and parse the request from a socket object.

        We extract individually method, path and then other parameters

        Raises:
          ValueError: When the request cannot be parsed.
        """

        try:
            fields: list = request.split("\r\n")
            # Extract method, protocol and path
            main_infos = fields[0].split(" ")
            method: str = main_infos[0].strip()
            path: str = main_infos[1].strip().lower()
            protocol: str = main_infos[2].strip()

            fields = fields[1:]
            headers = {}

            for field in fields:
                if field:
                    key, value = field.split(":", 1)  # 1 is maxsplit

                    # Fill output dict with request data
                    headers[key.strip().lower()] = value.strip().lower()

            # return headers
            return cls(method=method, path=path, protocol=protocol, headers=headers)

        except (Exception, ValueError) as e:
            print(
                f"An error occured: {e} Could not parse the following request:\n\n{request}"
            )
            client_socket.sendall(cls.bad_request_response.encode())