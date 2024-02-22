import socket


class BaseServer:
     def __init__(self, host="127.0.0.1", port=8080) -> None:
        """
        Initialize the web server class.

        We create a TCP socket listening for the initial
        client connexion through IPv4.

        Then we bind our socket to our host:port to be able to receive incoming
        connections on this address.

        After binding, we use server_socket.listen() to prepare the server to accept
        connections.

        """

        # Define the host and port
        self.HOST: str = host
        self.PORT: int = port

        self.ok = """HTTP/1.1  200 OK\r\nContent-Type: application/json\r\n\r\n{"status": 200}"""

        try:
            # Read the content of the HTML file
            with open("welcome.html", "r") as file:
                self.html_content = file.read()

            # Define the response with HTML content
            self.response = f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{self.html_content}"""

        except (FileNotFoundError, PermissionError, IOError):
            print(
                "Error: The default HTML file does not exist, falling back to default response."
            )
            self.response = """HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Hello, world!</h1></body></html>"""

        except Exception as e:
            print(
                f"An unexpected error occurred while opening default HTML file: {e}\nFalling back to default response."
            )
            self.response = """HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Hello, world!</h1></body></html>"""

        # Init the socket server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the host and port
        self.server_socket.bind((self.HOST, self.PORT))

        # Listen for incoming connections
        self.server_socket.listen(10)  # Allow up to 10 queued connections
        print(f"\nServer listening on http://{self.HOST}:{self.PORT}")
