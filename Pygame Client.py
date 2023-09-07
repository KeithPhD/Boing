#!/usr/bin/env python
# coding: utf-8

# In[118]:


import socket
import select
import errno
import json

import pygame
import sys

import time

# Initialize Pygame
pygame.init()

# Set up display
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Moving and Jumping Square")

# Colors
white = (255, 255, 255)
blue = (0, 0, 255)
red = (255, 0, 0)

# Square properties
square_size = 50
square_x = screen_width // 2 - square_size // 2
square_y = screen_height - square_size
v_speed = 0
gravity = 0.98
x_accel = 1
x_speed = 0
x_resist = 0.1
can_jump = True
jump_old = True
font = pygame.font.Font(None, 16)
black = (0, 0, 0)
players = {}

frames = 0
get_time = time.time()
clock = pygame.time.Clock()

HEADER_LENGTH = 10

IP = '192.168.1.189'
PORT = 1235
my_username = input("Username: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
#client_socket.connect((socket.gethostname(), PORT))

# Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
client_socket.setblocking(False)

username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)
data_dict = {"x": square_x, "y": square_y, "xv": x_speed, "yv": v_speed, "keys": keys_down, "jump": can_jump}
message = json.dumps(data_dict).encode('utf-8')
message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(message_header + message)

keys_old = []

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys_down = []
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        if can_jump:
            x_speed -= x_accel
        else:
            x_speed -= x_accel / 3
        keys_down += ['a']
    if keys[pygame.K_d]:
        if can_jump:
            x_speed += x_accel
        else:
            x_speed += x_accel / 3
        keys_down += ['d']
    if can_jump:
        x_speed -= 0.2 * x_speed
    else:
        x_speed -= 0.02 * x_speed
    square_x += x_speed
    
    if keys[pygame.K_w] and can_jump:
        v_speed = 18
        square_y -= 1
        can_jump = False
    if keys[pygame.K_w]:
        keys_down += ['w']
        
    if square_x > screen_width - square_size:
        square_x = screen_width - square_size
        x_speed = x_speed * -1
    if square_x < 0:
        square_x = 0
        x_speed = x_speed * -1
    
    if square_y < screen_height - square_size:
        square_y -= v_speed
        v_speed -= gravity
    else:
        v_speed = 0
        square_y = screen_height - square_size
        can_jump = True
        
 #   for player in players:
 #       if (players[player]['x'] - square_x)**2 + (players[player]['y'] - square_y)**2 < square_size**2:
            
            #A = (players[player]['xv'] - x_speed)**2 + (players[player]['yv'] - v_speed)**2
            #B = (players[player]['xv'] - x_speed)*(players[player]['x'] - square_x) + (players[player]['yv'] - y_speed)*(players[player]['y'] - square_y)
            #C = (players[player]['x'] - square_x)**2 + (players[player]['y'] - square_y)**2
            #T = -1 * B / A / 2 - math.sqrt(square_size**2 / A + (B / A)**2 / 4 - C / A)
            

    data_dict = {"x": square_x, "y": square_y, "xv": x_speed, "yv": v_speed, "keys": keys_down, "jump": can_jump}
    message = json.dumps(data_dict)

    # If message is not empty - send it
    if message and (keys_old != keys_down or jump_old != can_jump):
        # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)
    keys_old = keys_down
    jump_old = can_jump

    screen.fill(white)
    for player in players:
        if 'jump' in players[player]:
            if 'a' in players[player]['keys']:
                if players[player]['jump']:
                    players[player]['xv'] -= x_accel
                else:
                    players[player]['xv'] -= x_accel / 3
            if 'd' in players[player]['keys']:
                if players[player]['jump']:
                    players[player]['xv'] += x_accel
                else:
                    players[player]['xv'] += x_accel / 3
            if 'w' in players[player]['keys'] and players[player]['jump']:
                players[player]['yv'] = 18
                players[player]['y'] -= 1
                players[player]['jump'] = False
            if players[player]['jump']:
                players[player]['xv'] -= 0.2 * players[player]['xv']
            else:
                players[player]['xv'] -= 0.02 * players[player]['xv']
            players[player]['x'] += players[player]['xv']

            if players[player]['x'] > screen_width - square_size:
                players[player]['x'] = screen_width - square_size
                players[player]['xv'] = players[player]['xv'] * -1
            if players[player]['x'] < 0:
                players[player]['x'] = 0
                players[player]['xv'] = players[player]['xv'] * -1
            
            if players[player]['y'] < screen_height - square_size:
                players[player]['y'] -= players[player]['yv']
                players[player]['yv'] -= gravity
            else:
                players[player]['yv'] = 0
                players[player]['y'] = screen_height - square_size
                players[player]['jump'] = True
                
            square = pygame.Rect(int(players[player]['x']), int(players[player]['y']), 50, 50)
            pygame.draw.circle(screen, (0, 255, 0), square.center, square_size / 2)
            text = font.render(player, True, black)
            text_rect = text.get_rect(midbottom=(square.centerx, square.top))
            screen.blit(text, text_rect)
    
    if int(time.time()) > int(get_time):
        display = frames
        frames = 0
    if display:
        fps_text = font.render(str(display) + " fps", True, black)
        screen.blit(fps_text, (0, 0))
    frames += 1
    get_time = time.time()
    
    pygame.draw.circle(screen, (255, 0, 255), (square_x + square_size / 2, square_y + square_size / 2), square_size / 2, width=1)
    pygame.display.flip()
    clock.tick(60)
    
    
    try:
        while True:
            message_header = client_socket.recv(HEADER_LENGTH)
            # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
            if not len(message_header):
                print('Connection closed by the server')
                sys.exit()
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')
            screen.fill(white)
            
            players = json.loads(message)
            for player in players:
                square = pygame.Rect(int(players[player]['x']), int(players[player]['y']), 50, 50)
                pygame.draw.rect(screen, (0, 255, 0), square)
                text = font.render(player, True, black)
                text_rect = text.get_rect(midbottom=(square.centerx, square.top))
                screen.blit(text, text_rect)
            pygame.draw.circle(screen, (255, 0, 255), (square_x + square_size / 2, square_y + square_size / 2), square_size / 2, width=1)
            pygame.display.flip()
            #clock.tick(60)
        
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        # We just did not receive anything
        continue

    except Exception as e:
        # Any other exception - something happened, exit
        print('Reading error: '.format(str(e)))
        sys.exit()


# In[ ]:


# Still has name error, and other squares figgiting on update

