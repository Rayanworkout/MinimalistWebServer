import os
import mimetypes

from Model.BaseServer import BaseServer


class MinimalistWebServer(BaseServer):

    def __init__(self, host, port) -> None:
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
                        self.send_response(client_socket, self.response)

                    else:

                        # Serve static file

                        url_to_path = path.replace("/", os.sep)[
                            1:
                        ]  # getting read of first /
                        base_dir = os.path.dirname(__file__)

                        if not path.startswith("/static"):
                            # Serve index.html
                            index_path = os.path.join(
                                base_dir, url_to_path, "index.html"
                            )

                            self.serve_static_file(client_socket, index_path)
                        else:
                            file_path = os.path.join(base_dir, url_to_path)
                            print(file_path)
                            self.serve_static_file(client_socket, file_path)

                finally:
                    # Close the client socket
                    client_socket.close()

        # Gracefully catch KeyboardInterrupt exception
        except KeyboardInterrupt:
            print("Server shutting down...")
            # Gracefully shutting down server socket
            self.server_socket.close()

    def send_response(self, client_socket, response: str) -> None:
        client_socket.sendall(response.encode())

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

    def serve_static_file(self, client_socket, file_path: str) -> None:

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
            self.send_response(
                client_socket,
                "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\n404 Not Found",
            )


if __name__ == "__main__":
    server = MinimalistWebServer()

    server.listen_forever()
