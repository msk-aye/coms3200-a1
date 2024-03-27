import socket
import sys
import time
import threading
import os

INVALID_ARGUMENTS = "Invalid arguments provided\n"
WAITING = "[(%s)] Waiting for a connection\n"
PRINT_RECEIVED = "[%s (%s)] %s\n"
CONNECTION = "[(%s)] Get a connection from %s\n"
WELCOME = "Welcome to the channel, %s"
TERMINATED_BY_CLIENT = "[Connection terminated by the client]\n"
TERMINATED_BY_SERVER = "[Connection terminated by the server]\n"
EXIT = "exit"
EMPTY = ""

class ChatServer:

    def __init__(self):
        self.host = "127.0.0.1"
        self.client_name = None
        self.port = None
        self.socket = None
        self.conn = None

    def get_time(self):
        return time.strftime("%H:%M:%S", time.localtime())

    def read_port_number(self):
        """
        Read the port number from argument, store it to self.port.
        Exit with code 1 if invalid argument is provided.
        :return: None
        """
        if len(sys.argv) != 2:
            sys.stdout.write(INVALID_ARGUMENTS)
            os._exit(1)

        self.port = int(sys.argv[1])

    def listen_on_port(self):
        """
        Create a socket listens on the specified port.
        Store the socket object to self.socket.
        Print time and acceptance message to the stdout.
        :return: None
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        sys.stdout.write(WAITING % self.get_time())

    def recv_client_connection(self):
        """
        Accept a client connection and store the new
        accepted connection to self.conn.
        Get and store the client name in self.client_name.
        Print the get connection message to the stdout.
        Send the welcome message to the connected client.
        :return: None
        """
        self.conn, self.addr = self.socket.accept()
        self.client_name = self.conn.recv(1024).decode()
        sys.stdout.write(CONNECTION % (self.get_time(), self.client_name))
        self.conn.send((WELCOME % self.client_name).encode())

    def _receive_and_print_message(self):
        """
        Use a while loop to receive TCP packets from the client and print
        messages to stdout.
        If the message is "exit", print "[Connection Terminated by the client]"
        to stdout. Then close the socket and exit with code 0.
        :return: None
        """
        while True:
            message = self.conn.recv(1024).decode()

            if message == EXIT or not message:
                sys.stdout.write(TERMINATED_BY_CLIENT)
                sys.stdout.flush()
                self.conn.close()
                os._exit(0)

            sys.stdout.write(PRINT_RECEIVED %
                             (self.client_name, self.get_time(), message))

    def receive_and_print_message(self):
        """
        Multithreading
        :return: None
        """
        threading.Thread(target=self._receive_and_print_message).start()

    def send_message(self):
        """
        Use a while loop to get message from stdin and send out the message
        back to the client.
        If the message is "exit", print "[Connection Terminated by the client]"
        to the stdout. Then close the socket and exit with code 0.
        :return: None
        """
        while True:
            message = input()

            if message == EMPTY:
                continue

            self.conn.send(message.encode())

            if message == EXIT:
                sys.stdout.write(TERMINATED_BY_SERVER)
                self.conn.close()
                sys.stdout.flush()
                os._exit(0)

    def run_chat_server(self):
        """
        Run the chat server that receives and sends messages to the client
        :return: None
        """
        self.read_port_number()
        self.listen_on_port()
        self.recv_client_connection()
        self.receive_and_print_message()
        self.send_message()


if __name__ == '__main__':
    chat_server = ChatServer()
    chat_server.run_chat_server()