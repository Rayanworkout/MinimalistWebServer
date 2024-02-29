import requests
import time
import pytest
import threading

from minimalist_server import MinimalistWebServer
from BaseServer.base_server import BaseServer


@pytest.fixture(scope="module")
def web_server():
    """Fixture to start and stop the server for the tests.
    Same as a setUp and teardown method in unittest."""
    server = MinimalistWebServer()

    server_thread = threading.Thread(target=server.listen_forever)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(1)

    yield server

    server.stop()
    server_thread.join(timeout=2)


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


def test_default_response_is_correct(web_server):
    # Fetch the default response
    response = requests.get("http://127.0.0.1:8080")
    assert response.status_code == 200


def test_404_is_returned_on_bad_url(web_server):
    response = requests.get("http://127.0.0.1:8080/not_existing_path")
    assert response.status_code == 404


def test_405_is_returned_on_bad_method(web_server):
    response = requests.post("http://127.0.0.1:8080")
    assert response.status_code == 405


def test_default_page_content_is_correct(web_server):
    response = requests.get("http://127.0.0.1:8080")
    assert "A Minimalist Web Server" in response.text


# BaseServer


def test_non_int_port_raises_error():
    with pytest.raises(ValueError):
        BaseServer(port="non_int", host="127.0.0.1")


def test_non_string_host_raises_error():
    with pytest.raises(ValueError):
        BaseServer(port=8080, host=123)


def test_host_is_not_valid_ip_raises_error():
    with pytest.raises(ValueError):
        BaseServer(port=8080, host="not_valid_ip")


def test_port_out_of_range_raises_error():
    with pytest.raises(ValueError):
        BaseServer(port=70000, host="127.0.0.1")
