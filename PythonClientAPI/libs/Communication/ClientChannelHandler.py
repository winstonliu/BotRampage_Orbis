import socket as s

END_OF_MESSAGE_DELIMITER = '\n'
MAX_BYTES_TO_RECEIVE = 1
STRING_ENCODING = 'utf-8'


class ClientChannelHandler():
    def __init__(self):
        self.connected = False

    def start_socket_connection(self, port_number, host_name):
        try:
            self.sock = s.socket(s.AF_INET, s.SOCK_STREAM)
            self.sock.connect((host_name, port_number))
            self.connected = True
            print("Connected")
        except s.error:
            print("Cannot connect to  {0} at port {1}. Check to see that the server is running.".format(host_name,
                                                                                                        port_number))

    def close_connection(self):
        self.sock.close()
        self.connected = False
        print("Connection closed")

    def send_message(self, message):
        self.check_socket_connection()
        try:
            # all messages are delimited by a "\n" character
            byte_encoded_message = (message + END_OF_MESSAGE_DELIMITER).encode(STRING_ENCODING)
            self.sock.sendall(byte_encoded_message)
        except s.error:
            self.close_connection()
            raise Exception("Socket failed to send. Closing socket")

    def receive_message(self):
        complete_data = ''
        received_data = ''
        self.check_socket_connection()
        while END_OF_MESSAGE_DELIMITER not in received_data:
            received_data = self.sock.recv(MAX_BYTES_TO_RECEIVE)
            received_data = received_data.decode(STRING_ENCODING)
            complete_data += received_data.strip()
        return complete_data

    def check_socket_connection(self):
        if not self.connected:
            raise Exception("Cannot send or receive message on closed socket")
