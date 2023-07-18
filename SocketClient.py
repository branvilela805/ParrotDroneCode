import socket

def getData(cs):
    cs.send("get data".encode())
    data = cs.recv(1024).decode()  # receive response
    print('Received from server: ' + data)  # show in terminal
    

def client_program():
    # host = socket.gethostname()  # as both code is running on same pc
    host = "10.247.5.44"
    port = 9123  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    # message = input(" -> ")  # take input

    while True:
        message = input()
        # client_socket.send(message.encode())  # send message
        if message == "y":
            getData(client_socket)

        # message = input(" -> ")  # again take input

    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()