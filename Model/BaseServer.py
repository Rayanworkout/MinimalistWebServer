import mimetypes
import os
import socket


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

        self.sep = os.sep

        current_dir = os.path.dirname(__file__)
        default_html_path = os.path.join(current_dir, "welcome.html")

        try:
            # Read the content of the HTML file
            with open(default_html_path, "r") as file:
                html_content = file.read()

            # Define the response with HTML content
            self.response = (
                f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{html_content}"""
            )

        except (FileNotFoundError, PermissionError, IOError) as e:
            print(
                "Error: The default HTML file does not exist, falling back to default response."
            )
            self.response = f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Could not open default HTML file, check your terminal<br><br>{e}</h1></body></html>"""

        except Exception as e:
            print(
                f"An unexpected error occurred while opening default HTML file: {e}\nFalling back to default response."
            )
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
            # Extract method and path
            method: str = fields[0].split(" ")[0].strip().lower()
            path: str = fields[0].split(" ")[1].strip().lower()

            fields = fields[1:]
            output = {"method": method, "path": path}

            for field in fields:
                if field:
                    key, value = field.split(":", 1)  # 1 is maxsplit
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
        else:
            response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\n404 Not Found"
            client_socket.sendall(response.encode())
