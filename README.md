# TCP Echo
TCP connection example.

It starts a TCP server on a random port. The server receives client requests with the port and a message as parameters, then it echoes the message back.

The client also shows the total time each request takes, including TCP connection-establishment.

## Usage
1. Start the server: `python tcp_echo_server.py`
    
    - It will display the random port number, e.g.: `TCP echo server listening on 127.0.0.1:20476`
2. Run the client passing as parameters the server port and the message to send to the TCP server, e.g.: `python tcp_echo_client.py 20476 Hello there!`

    - It will send the message to the TCP server and receive a response
    - It will print connection-related information, e.g.:
        ```
        Sent bytes                 : 12
        Received bytes             : 28
        Payload match              : True
        Client RTT (send→receive)  : 0.515 ms
        Server connection time     : 348.267 ms
        Approx. total time         : 348.782 ms
        Echoed data:
         Hello there!
        ```

## Tools
Python

## Author
ChatGPT 5.1, prompted by Arturo Mora-Rioja.