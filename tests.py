import requests
import time
import threading

from MinimalistServer import MinimalistWebServer
from BaseServer.BaseServer import BaseServer

# HOST AND PORT


def test_default_port_number_is_correct():
    server = MinimalistWebServer()
    assert server.PORT == 8080


def test_default_host_is_correct():
    server = MinimalistWebServer()
    assert server.HOST == "127.0.0.1"


def test_custom_port_is_taken():
    server = MinimalistWebServer(port=8081)
    assert server.PORT == 8081


def test_custom_host_is_taken():
    server = MinimalistWebServer(
        host="0.0.0.0", port=8081  # Using different port to avoid conflict
    )
    assert server.HOST == "0.0.0.0"


# RESPONSES

def test_default_response_is_correct():
    server = MinimalistWebServer()

    server_thread = threading.Thread(target=server.listen_forever)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(1)
    # Fetch the default response
    response = requests.get("http://127.0.0.1:8080")
    assert response.status_code == 200

    # Stop the server
    server.stop()
    server_thread.join(timeout=2)

