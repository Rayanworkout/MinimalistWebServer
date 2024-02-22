import os
from BaseServer.BaseServer import BaseServer
from BaseServer.logger import logger


class MinimalistWebServer(BaseServer):

    def __init__(self, host="127.0.0.1", port=8080) -> None:
        super().__init__(host, port)

    def listen_forever(self) -> None:
        """

        Method to accept incoming connections and handle them.

        We use an infinite loop with nested try except blocks.

        On the last iteration of the loop, we close the connection with the client.

        """

        try:
            logger.info("Starting server")
            base_dir = os.path.dirname(__file__)

            # Accept incoming connections
            while True:
                client_socket, client_address = self.server_socket.accept()

                try:
                    self.dispatch_request(client_socket, client_address, base_dir)

                except Exception as e:
                    logger.error(f"An error occured while handling the request: {e}")
                    print(f"An error occured while handling the request: {e}")

                finally:
                    # Close the client socket
                    client_socket.close()

        # Gracefully catch KeyboardInterrupt exception
        except KeyboardInterrupt:
            print("Server shutting down...")
            logger.info("Gracefully shutting down server")
            # Gracefully shutting down server socket
            self.server_socket.close()


if __name__ == "__main__":
    server = MinimalistWebServer(port=8000)
    server.listen_forever()
