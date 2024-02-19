import socket

# TODO map static files by folder
# Handle POST Requests


class MinimalistWebServer:
    def __init__(self, host="127.0.0.1", port=8080) -> None:
        """
        Function to initialize the web server class.

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

    def listen_forever(self) -> None:
        """

        Method to accept incoming connections and handle them.

        We use an infinite loop with nested try except blocks.

        On the last iteration of the loop, we close the connection with the client.

        We receive 1024 bytes data streams, which can be set to more.

        decode() and encode() are used to convert bytes to string and string to bytes, respectively.

        """

        try:
            # Accept incoming connections
            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f"Connection from {client_address}")

                try:
                    # Receive data from the client
                    request = client_socket.recv(1024)  # size of the buffer in bytes

                    # Parse the request
                    stream = request.decode()
                    parsed_stream = self.parse_http_request(stream)

                    # Send the response back to the client
                    client_socket.sendall(self.response.encode())
                finally:
                    # Close the client socket
                    client_socket.close()

        # Gracefully catch KeyboardInterrupt exception
        except KeyboardInterrupt:
            print("Server shutting down...")
            # Gracefully shutting down server socket
            self.server_socket.close()

    def parse_http_request(self, request: str) -> dict:
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


if __name__ == "__main__":
    server = MinimalistWebServer()

    server.listen_forever()
