import socket


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

        # Define the response
        self.response = """HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Hello, world!</h1></body></html>"""

        # Init the socket server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the host and port
        self.server_socket.bind((self.HOST, self.PORT))

        # Listen for incoming connections
        self.server_socket.listen()
        print(f"Server listening on {self.HOST}:{self.PORT} ...")

    def listen_forever(self) -> None:
        try:
            # Accept incoming connections
            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f"Connection from {client_address}")
                try:
                    # Receive data from the client
                    request = client_socket.recv(1024)
                    print(f"Received request:\n{request.decode()}")
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


server = MinimalistWebServer()

server.listen_forever()
