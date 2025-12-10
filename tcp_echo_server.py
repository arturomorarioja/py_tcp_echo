import socket
import threading
from typing import Tuple

HOST = '127.0.0.1'
PORT = 0       # 0 means that the OS will assign a free port
BACKLOG = 50
RECV_BUF = 4096


def handle_client(conn: socket.socket, addr: Tuple[str, int]) -> None:
    """
    Handles one client connection. Echoes back any bytes received until EOF.
    Connection is closed by the client or when no data is received.
    """
    try:
        while True:
            data = conn.recv(RECV_BUF)
            if not data:
                break
            conn.sendall(data)
    finally:
        conn.close()


def serve(stop_event: threading.Event, host: str = HOST, port: int = PORT) -> None:
    """
    Starts a multi-threaded TCP echo server.
    The OS chooses a free port if port is 0.
    The loop ends when stop_event is set. Closing the listening socket
    unblocks accept.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(BACKLOG)

        actual_host, actual_port = s.getsockname()
        print(f'Echo server listening on {actual_host}:{actual_port}')
        print('Start the client with that port. Press Enter here to stop the server.')

        # Store listening socket on the event for possible external access if needed
        # (not strictly necessary for this exercise).
        while not stop_event.is_set():
            try:
                s.settimeout(1.0)
                conn, addr = s.accept()
            except socket.timeout:
                continue
            except OSError:
                # Socket closed while waiting in accept
                break

            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()

        # Exiting the with-block closes the listening socket
        print('Server shutting down.')


if __name__ == '__main__':
    stop_event = threading.Event()
    server_thread = threading.Thread(target=serve, args=(stop_event,), daemon=True)
    server_thread.start()

    try:
        input()    # Waits until the user presses Enter
    finally:
        stop_event.set()
        server_thread.join()
