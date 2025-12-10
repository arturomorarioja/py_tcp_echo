import socket
import sys
import time

HOST = '127.0.0.1'
RECV_BUF = 4096


def parse_response(data: bytes, original_message: bytes) -> tuple[float, bytes]:
    """
    Parses the server response.

    Expected format:
        b'CONN_MS:<float>\\n' + original_message

    Returns:
        (connection_establish_ms, echoed_payload)
    """
    newline_index = data.find(b'\n')
    if newline_index == -1 or not data.startswith(b'CONN_MS:'):
        return 0.0, data

    header = data[:newline_index].decode('ascii', errors='replace')
    payload = data[newline_index + 1:]

    try:
        _, value_str = header.split(':', 1)
        conn_establish_ms = float(value_str)
    except ValueError:
        conn_establish_ms = 0.0

    return conn_establish_ms, payload


def run_client(host: str, port: int, message: bytes) -> None:
    """
    Connects to the TCP echo server, sends the message, measures the round-trip
    time (RTT) until the server closes the connection, then parses the server
    reported connection establishing time and prints all metrics.
    """
    to_send = message
    chunks = []

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
        except OSError:
            print(f'Error: could not connect to {host}:{port}.')
            print('Ensure that the TCP server is running and that the port number is correct.')
            sys.exit(1)

        start = time.perf_counter()
        s.sendall(to_send)

        # Important: signal that no more data will be sent.
        # This allows the server recv() loop to reach EOF and reply.
        s.shutdown(socket.SHUT_WR)

        while True:
            chunk = s.recv(RECV_BUF)
            if not chunk:
                break
            chunks.append(chunk)

        end = time.perf_counter()

    rtt_ms = (end - start) * 1000.0
    raw_response = b''.join(chunks)
    conn_ms, echoed_payload = parse_response(raw_response, to_send)
    total_ms = rtt_ms + conn_ms

    print('Sent bytes                 :', len(to_send))
    print('Received bytes             :', len(raw_response))
    print('Payload match              :', echoed_payload == to_send)
    print('Client RTT (send→receive)  : {:.3f} ms'.format(rtt_ms))
    print('Server connection time     : {:.3f} ms'.format(conn_ms))
    print('Approx. total time         : {:.3f} ms'.format(total_ms))
    print('Echoed data:\n', echoed_payload.decode('utf-8', errors='replace'))


def parse_args() -> tuple[int, bytes]:
    """
    Parses CLI arguments.
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
    run_client(HOST, port, message)
