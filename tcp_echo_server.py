import socket
import threading
import time
from typing import Tuple

HOST = '127.0.0.1'
PORT = 0       # 0 means that the OS will assign a free port
BACKLOG = 50
RECV_BUF = 4096


def handle_client(conn: socket.socket, addr: Tuple[str, int], conn_establish_ms: float) -> None:
    """
    Handles one client connection.

    Reads all data until the client closes the connection.
    Sends back a response with a first line indicating the connection
    establishing time in milliseconds, followed by the original bytes.
    """
    try:
        chunks = []
        while True:
            data = conn.recv(RECV_BUF)
            if not data:
                break
            chunks.append(data)

        if chunks:
            payload = b''.join(chunks)
            header = f'CONN_MS:{conn_establish_ms:.3f}\n'.encode('ascii')
            response = header + payload
            conn.sendall(response)
    finally:
        conn.close()


def serve(stop_event: threading.Event, host: str = HOST, port: int = PORT) -> None:
    """
    Starts a TCP echo server.

    For each accepted connection, the time spent in accept() is measured
    as the connection establishing time and later reported to the client.
    The loop ends when stop_event is set.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(BACKLOG)

        actual_host, actual_port = s.getsockname()
        print(f'TCP echo server listening on {actual_host}:{actual_port}')
        print('Start the TCP client with that port. Press Enter here to stop the server.')

        while not stop_event.is_set():
            try:
                s.settimeout(1.0)
                start = time.perf_counter()
                conn, addr = s.accept()
                end = time.perf_counter()
            except socket.timeout:
                continue
            except OSError:
                break

            conn_establish_ms = (end - start) * 1000.0
            t = threading.Thread(
                target=handle_client,
                args=(conn, addr, conn_establish_ms),
                daemon=True
            )
            t.start()

        print('TCP server shutting down.')


if __name__ == '__main__':
    stop_event = threading.Event()
    server_thread = threading.Thread(target=serve, args=(stop_event,), daemon=True)
    server_thread.start()

    try:
        input()
    finally:
        stop_event.set()
        server_thread.join()
