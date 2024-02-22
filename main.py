import os

from Model.BaseServer import BaseServer


class MinimalistWebServer(BaseServer):

    def __init__(self, host="127.0.0.1", port=8080) -> None:
        super().__init__(host, port)

    def listen_forever(self) -> None:
        """

        Method to accept incoming connections and handle them.

        We use an infinite loop with nested try except blocks.

        On the last iteration of the loop, we close the connection with the client.

        We receive 1024 bytes data streams, which can be set to more.

        decode() and encode() are used to convert bytes to string and string to bytes, respectively.

        """

        try:
            base_dir = os.path.dirname(__file__)
            project_folder = ""
            # Accept incoming connections
            while True:
                client_socket, client_address = self.server_socket.accept()

                try:
                    # Receive data from the client
                    request = client_socket.recv(1024)  # size of the buffer in bytes

                    # Parse the request
                    stream = request.decode()
                    parsed_stream = self.parse_http_request(stream)

                    path = parsed_stream["path"]

                    log = (
                        f"{client_address[0]} {parsed_stream['method'].upper()} {path}"
                    )
                    # Log request infos
                    print(log)

                    if path == "/":
                        # Default response with welcome.html
                        client_socket.sendall(self.response.encode())

                    else:
                        # Serve static file

                        url_to_path = path.replace("/", self.sep)[
                            1:
                        ]  # getting rid of first /

                        if not path.startswith("/static"):
                            # Serve index.html
                            index_path = os.path.join(
                                base_dir, url_to_path, "index.html"
                            )
                            project_folder = url_to_path

                            self.serve_static_file(client_socket, index_path)
                        else:
                            # Add project folder to path
                            file_path = os.path.join(
                                base_dir, project_folder, url_to_path
                            )
                            self.serve_static_file(client_socket, file_path)

                finally:
                    # Close the client socket
                    client_socket.close()

        # Gracefully catch KeyboardInterrupt exception
        except KeyboardInterrupt:
            print("Server shutting down...")
            # Gracefully shutting down server socket
            self.server_socket.close()


if __name__ == "__main__":
    server = MinimalistWebServer()

    server.listen_forever()
