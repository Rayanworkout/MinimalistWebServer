import mimetypes
import os
import socket
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

    """

    # Responses
    BAD_REQUEST_RESPONSE = """HTTP/1.1 400 BAD REQUEST\r\nContent-Type: application/json\r\n\r\n{'status': 400, 'message': 'wrong request method'}""".encode()
    NOT_FOUND_RESPONSE = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\n404 Not Found".encode()

    def __init__(self, host, port) -> None:

        # Define the host and port
        self.HOST: str = host
        self.PORT: int = port
        self.sep = os.sep

        current_dir = os.path.dirname(__file__)
        default_html_path = os.path.join(current_dir, "default.html")

        # Check if port is an int
        try:
            self.PORT = int(self.PORT)
        except ValueError:
            raise ValueError("Port number must be an integer")

        try:
            # Read the content of the HTML file
            with open(default_html_path) as file:
                html_content = file.read()

            # Define the response with HTML content
            self.response = (
                f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{html_content}"""
            )

        except Exception as e:
            message = f"Error: The default HTML file does not exist or is not accessible, falling back to default response. \n\n{e}"

            print(message)
            logger.warning(message.replace("\n", ""))

            self.response = f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Could not open default HTML file, check your terminal<br><br>{e}</h1></body></html>"""

        try:
            # Init the socket server
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Allow reusing the same address
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Bind the socket to the host and port
            self.server_socket.bind((self.HOST, self.PORT))

            # Listen for incoming connections
            self.server_socket.listen(10)  # Allow up to 10 queued connections
            print(f"\n> Server listening on http://{self.HOST}:{self.PORT}")
        except OSError as e:
            print(f"Could not launch server: {e}")

    @staticmethod
    def serve_static_file(client_socket, file_path: str) -> None:

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
            client_socket.sendall(BaseServer.NOT_FOUND_RESPONSE)
            return 404

    def dispatch_request(self, client_socket, client_address):

        # Receive data from the client
        request = client_socket.recv(1024)  # size of the buffer in bytes
        # Parse the request
        stream = request.decode()
        parsed_stream = Request.from_socket(stream, client_socket)

        path = parsed_stream.path
        protocol = parsed_stream.protocol
        request_method = parsed_stream.method.upper()

        if request_method == "GET":
            status_code = self.handle_get_request(path, client_socket)
        else:
            status_code = 400

            client_socket.sendall(BaseServer.BAD_REQUEST_RESPONSE)

        readable_time = time.strftime("%T")
        log = f'{client_address[0]} - - [{readable_time}] "{request_method} {path} {protocol}" {status_code}'
        # Log request infos
        logger.info(log)
        print(log)

    def handle_get_request(self, path, client_socket):
        if path == "/":
            # Default response with welcome.html
            client_socket.sendall(self.response.encode())
            status_code = 200

        else:
            # Serve static file
            url_to_path = path.replace("/", self.sep)[1:]  # getting rid of first /

            status_code = self.serve_static_file(client_socket, url_to_path)

        return status_code
