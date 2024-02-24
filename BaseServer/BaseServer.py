import mimetypes
import os
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import time

from .logger import logger
from .Request import Request


class BaseServer:
    """

    Base Server class
    We create a TCP socket listening for the initial
    client connexion through IPv4.

    Then we bind our socket to our host:port to be able to receive incoming
    connections on this address.

    After binding, we use server_socket.listen() to prepare the server to accept
    connections.

    The server can then accept connections through MinimalistWebServer.listen_forever()

    Methods:

        dispatch_request(client_socket: socket, client_address: str) => parse request and verifies method. Calls
                                                                               handle_get_request() for GET or returns
                                                                               _METHOD_NOT_ALLOWED_RESPONSE.
                                                                               Also log request data.

        handle_get_request(client_socket: socket, path: str) => called by dispatch_request(). Serves default
                                                                       HTML file at root URL, and calls serve_static_file()
                                                                       for othe

        serve_static_file(client_socket: socket, file_path: str) => returns an encoded response containing the
                                                                           content of the file or _NOT_FOUND_RESPONSE.
    """

    # Responses
    _DEFAULT_RESPONSE = None  # computed inside __init__()
    _BAD_REQUEST_RESPONSE = """HTTP/1.1 400 BAD REQUEST\r\nContent-Type: application/json\r\n\r\n{'status': 400, 'message': 'bad request'}""".encode()
    _NOT_FOUND_RESPONSE = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\n404 Not Found".encode()
    _ERROR_RESPONSE = """HTTP/1.1 500 SERVER ERROR\r\nContent-Type: application/json\r\n\r\n{'status': 500, 'message': 'internal server error'}""".encode()
    _METHOD_NOT_ALLOWED_RESPONSE = """HTTP/1.1 405 NOT ALLOWED\r\nContent-Type: application/json\r\n\r\n{'status': 405, 'message': 'wrong request method'}""".encode()

    _SEP = os.sep

    # Cache default html content
    _DEFAULT_HTML_FILE_CONTENT = None

    _CURRENT_DIR = os.path.dirname(__file__)
    _DEFAULT_HTML_PATH = os.path.join(_CURRENT_DIR, "default.html")

    def __init__(self, host: str, port: int) -> None:

        # Define the host and port
        self.HOST = host
        self.PORT = port

        # Check if port is an int
        try:
            self.PORT = int(self.PORT)
        except ValueError:
            raise ValueError("Port number must be an integer")

        try:
            # Read the content of the HTML file if not cached
            if not BaseServer._DEFAULT_HTML_FILE_CONTENT:
                with open(BaseServer._DEFAULT_HTML_PATH) as file:
                    BaseServer._DEFAULT_HTML_FILE_CONTENT = file.read()

            # Define the response with HTML content
            BaseServer._DEFAULT_RESPONSE = f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{BaseServer._DEFAULT_HTML_FILE_CONTENT}"""

        except Exception as e:
            message = f"Error: The default HTML file does not exist or is not accessible, falling back to default response. \n\n{e}"

            print(message)
            logger.warning(message.replace("\n", ""))

            BaseServer._DEFAULT_RESPONSE = f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Could not open default HTML file, check your terminal<br><br>{e}</h1></body></html>"""

        try:
            # Init the socket server
            self.server_socket = socket(AF_INET, SOCK_STREAM)

            # Allow reusing the same address
            self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            # Bind the socket to the host and port
            self.server_socket.bind((self.HOST, self.PORT))

            # Listen for incoming connections
            self.server_socket.listen(10)  # Allow up to 10 queued connections
            print(f"\n> Server listening on http://{self.HOST}:{self.PORT}\n")
        except Exception as e:
            raise Exception(f"Could not launch server: {e}")

    @classmethod
    def dispatch_request(cls, client_socket: socket, client_address: str) -> None:

        # Receive data from the client
        request = client_socket.recv(1024)  # size of the buffer in bytes
        # Parse the request
        stream = request.decode()
        parsed_stream = Request.from_socket(stream, client_socket)

        try:
            path = parsed_stream.path
            protocol = parsed_stream.protocol
            request_method = parsed_stream.method.upper()

        except AttributeError:
            # Request is malformed or hasn't been parsed correctly
            client_socket.sendall(BaseServer._BAD_REQUEST_RESPONSE)
            client_socket.close()

        # Serving only GET requests
        if request_method != "GET":
            status_code = 405
            client_socket.sendall(BaseServer._METHOD_NOT_ALLOWED_RESPONSE)
            client_socket.close()
            return

        status_code = BaseServer.handle_get_request(client_socket, path)

        readable_time = time.strftime("%T")
        log = f'{client_address[0]} - - [{readable_time}] "{request_method} {path} {protocol}" {status_code}'
        # Log request infos
        logger.info(log)
        print(log)

    @classmethod
    def handle_get_request(cls, client_socket: socket, path: str):
        if path == "/":
            # Default response with welcome.html
            client_socket.sendall(BaseServer._DEFAULT_RESPONSE.encode())
            status_code = 200

        else:
            # Serve static file
            url_to_path = path.replace("/", BaseServer._SEP)[
                1:
            ]  # getting rid of first /

            status_code = BaseServer.serve_static_file(client_socket, url_to_path)

        return status_code

    @classmethod
    def serve_static_file(cls, client_socket: socket, file_path: str) -> int:

        # Get the file's MIME type
        content_type = mimetypes.guess_type(file_path)[0]

        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, "rb") as file:
                file_content = file.read()
                response = (
                    f"HTTP/1.1 200 OK\r\nContent-Length: {len(file_content)}\r\nContent-Type: {content_type}\r\n\r\n".encode(
                        "utf-8"
                    )
                    + file_content
                )
                client_socket.sendall(response)
                # Returning status code to be able to print it
                return 200
        else:
            client_socket.sendall(BaseServer._NOT_FOUND_RESPONSE)
            return 404
