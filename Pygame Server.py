#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import socket
import select

import json

HEADER_LENGTH = 10

IP = '192.168.1.189'
PORT = 1235

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
#server_socket.bind((socket.gethostname(), PORT))
server_socket.listen()
# List of sockets for select.select()
sockets_list = [server_socket]
# List of connected clients - socket as a key, user header and name as data
clients = {}
player_coords = {}
#print(f'Listening for connections on {IP}:{PORT}...')
print(f'Listening for connections on {socket.gethostname()}:{PORT}...')

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())

        # Return an object of message header and message data
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False
    
def prepare_message(message_data):
    try:
        message_encoded = message_data.encode('utf-8')
        message_header = f"{len(message_encoded):<{HEADER_LENGTH}}".encode('utf-8')

        return message_header + message_encoded

    except:
        return False
    
def prepare_message(message):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())

        # Return an object of message header and message data
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    if read_sockets:
        print(read_sockets)
    # Iterate over notified sockets
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:

            # Accept new connection
            # That gives us new socket - client socket, connected to this given client only, it's unique for that client
            # The other returned object is ip/port set
            client_socket, client_address = server_socket.accept()

            # Client should send his name right away, receive it
            user = receive_message(client_socket)
            # If False - client disconnected before he sent his name
            if user is False:
                continue

            # Add accepted socket to select.select() list
            sockets_list.append(client_socket)

            # Also save username and username header
            clients[client_socket] = user

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

        # Else existing socket is sending a message
        else:

            message = receive_message(notified_socket)

            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                sockets_list.remove(notified_socket)
                del player_coords[clients[notified_socket]['data'].decode("utf-8")]
                del clients[notified_socket]
                continue

            # Get user by notified socket, so we will know who sent the message
            user = clients[notified_socket]
            
            player_coords[user['data'].decode("utf-8")] = json.loads(message["data"].decode("utf-8"))
            message_data = json.dumps(player_coords).encode('utf-8')
            message_header = f"{len(message_data):<{HEADER_LENGTH}}".encode('utf-8')

            # print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
            # Iterate over connected clients and broadcast message
            for client_socket in clients:
                client_socket.send(message_header + message_data)

    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del player_coords[clients[notified_socket]['data'].decode("utf-8")]
        del clients[notified_socket]
        


# In[6]:


user['data'].decode("utf-8")


# In[ ]:




