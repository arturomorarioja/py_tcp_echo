import socket
import sys

HOST = '127.0.0.1'
RECV_BUF = 4096


def run_client(host: str, port: int, message: bytes) -> None:
    """
    Connects to the echo server, sends the message, then reads until the same
    number of bytes has been received back.
    """
    to_send = message
    expected = len(to_send)
    received = 0
    chunks = []

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(to_send)

        while received < expected:
            chunk = s.recv(RECV_BUF)
            if not chunk:
                break
            chunks.append(chunk)
            received += len(chunk)

    echoed = b''.join(chunks)

    print('Sent bytes   :', expected)
    print('Received bytes:', len(echoed))
    print('Payload match:', echoed == message)
    print('Echoed data:\n', echoed.decode('utf-8', errors='replace'))


def parse_args() -> tuple[int, bytes]:
    """
    Parses and validates CLI arguments.
    Usage: python tcp_echo_client.py <port> <message>
    """
    if len(sys.argv) < 3:
        print('Usage: python tcp_echo_client.py <port> <message>')
        sys.exit(1)

    try:
        port = int(sys.argv[1])
    except ValueError:
        print('Port must be an integer.')
        sys.exit(1)

    if not (1 <= port <= 65535):
        print('Port must be between 1 and 65535.')
        sys.exit(1)

    message_str = ' '.join(sys.argv[2:])
    message_bytes = message_str.encode('utf-8')

    return port, message_bytes


if __name__ == '__main__':
    port, message = parse_args()
    try:
        run_client(HOST, port, message)
    except (ConnectionRefusedError, TimeoutError):
        print(f'Error: could not connect to {HOST}:{port}.')
        print('Ensure that the echo server is running and that the port number is correct.')
        sys.exit(1)
    except OSError as exc:
        print(f'Network error while communicating with {HOST}:{port}: {exc}')
        sys.exit(1)
