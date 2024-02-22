import mimetypes
import os
import socket
import time

from .logger import logger


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

    def __init__(self, host, port) -> None:

        # Define the host and port
        self.HOST: str = host
        self.PORT: int = port
        self.project_folder = ""
        self.sep = os.sep

        current_dir = os.path.dirname(__file__)
        default_html_path = os.path.join(current_dir, "welcome.html")

        try:
            # Read the content of the HTML file
            with open(default_html_path) as file:
                html_content = file.read()

            # Define the response with HTML content
            self.response = (
                f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{html_content}"""
            )

        except (FileNotFoundError, PermissionError, IOError) as e:
            print(
                "Error: The default HTML file does not exist or is not accessible, falling back to default response."
            )
            self.response = f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Could not open default HTML file, check your terminal<br><br>{e}</h1></body></html>"""

        except Exception as e:
            print(f"An unexpected error occurred while opening default HTML file: {e}")
            self.response = f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Could not open default HTML file, check your terminal<br>{e}</h1></body></html>"""

        # Init the socket server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the host and port
        self.server_socket.bind((self.HOST, self.PORT))

        # Listen for incoming connections
        self.server_socket.listen(10)  # Allow up to 10 queued connections
        print(f"\n> Server listening on http://{self.HOST}:{self.PORT}")

    @staticmethod
    def parse_http_request(request: str) -> dict:
        """
        Method to parse the incoming request body

        We extract individually method, path and then other parameters

        """

        try:
            fields: list = request.split("\r\n")
            # Extract method, protocol and path
            main_infos = fields[0].split(" ")
            method: str = main_infos[0].strip()
            path: str = main_infos[1].strip().lower()
            protocol: str = main_infos[2].strip()

            fields = fields[1:]
            output = {"method": method, "path": path, "protocol": protocol}

            for field in fields:
                if field:
                    key, value = field.split(":", 1)  # 1 is maxsplit

                    # Fill output dict with request data
                    output[key.strip().lower()] = value.strip().lower()

            return output

        except Exception as e:
            print(
                f"An error occured: {e} Could not parse the following request:\n\n{request}"
            )

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
            response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\n404 Not Found"
            client_socket.sendall(response.encode())
            return 404

    def dispatch_request(self, client_socket, client_address, base_dir):

        # Receive data from the client
        request = client_socket.recv(1024)  # size of the buffer in bytes
        # Parse the request
        stream = request.decode()
        parsed_stream = self.parse_http_request(stream)

        path = parsed_stream["path"]
        protocol = parsed_stream["protocol"]
        request_method = parsed_stream["method"].upper()

        if request_method == "GET":
            status_code = self.handle_get_request(path, client_socket, base_dir)
        else:
            status_code = 400
            bad_request_response = """HTTP/1.1 400 BAD REQUEST\r\nContent-Type: application/json\r\n\r\n{'status': 400, 'message': 'wrong request method'}"""

            client_socket.sendall(bad_request_response.encode())

        readable_time = time.strftime("%T")
        log = f'{client_address[0]} - - [{readable_time}] "{request_method} {path} {protocol}" {status_code}'
        # Log request infos
        logger.info(log)
        print(log)

    def handle_get_request(self, path, client_socket, base_dir):
        if path == "/":
            # Default response with welcome.html
            client_socket.sendall(self.response.encode())

        else:
            # Serve static file

            url_to_path = path.replace("/", self.sep)[1:]  # getting rid of first /

            if not path.startswith("/static"):
                # Serve index.html
                index_path = os.path.join(base_dir, url_to_path, "index.html")
                self.project_folder = url_to_path

                status_code = self.serve_static_file(client_socket, index_path)

            else:
                # Add project folder to path
                file_path = os.path.join(base_dir, self.project_folder, url_to_path)
                status_code = self.serve_static_file(client_socket, file_path)

            return status_code
