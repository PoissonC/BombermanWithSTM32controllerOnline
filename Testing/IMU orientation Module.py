import pygame
from pygame.locals import *

import socket
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import json

host = '192.168.247.86'
port = 80

verticies = (
    (1, -2, -1), # 0
    (1, 2, -1), # 1
    (-1, 2, -1), # 2
    (-1, -2, -1), # 3
    (1, -2, 1),  # 4
    (1, 2, 1),  # 5
    (-1, -2, 1), # 6
    (-1, 2, 1)  # 7
    )

edges = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7)
    )

pitch_surfaces = (
    (0,1,5,4),
    (2,7,6,3)
    )
roll_surfaces = (
    (2,7,5,1),
    (3,6,4,0)
    )
yaw_surfaces = (
    (6,4,5,7),
    (2,3,0,1)
    )


def Cube():
    glBegin(GL_QUADS)
    for surface in roll_surfaces:
        glColor3fv((1,0,0))
        for vertex in surface:
            glVertex3fv(verticies[vertex])

    for surface in pitch_surfaces:
        glColor3fv((0,1,0))
        for vertex in surface:
            glVertex3fv(verticies[vertex])

    glEnd()

    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(verticies[vertex])
    glEnd()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            pygame.init()
            display = (800,600)
            pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

            gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

            glTranslatef(0.0,0.0, -10)
            # glTranslatef(0.0,-10, 0)
            glRotatef(-90, 1, 0, 0)
            glRotatef(-90, 0, 0, 1)
            curr_roll = 0
            curr_pitch = 0
            curr_yaw = 0
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                data= conn.recv(1024).decode('utf-8')
                print("Received from socket server:", data)
                if (data.count('{') != 1):
                # Incomplete data are received.
                    continue
                obj = json.loads(data)
		
                Roll = np.arctan2(obj['x'], obj['z']) * 180 / np.pi
                Pitch = np.arctan2(obj['y'],np.sqrt(np.square(obj['x'])+np.square(obj['z']))) * 180 / np.pi
                glRotatef(Roll - curr_roll, 1, 0, 0)
                curr_roll = Roll

                glRotatef(Pitch - curr_pitch, 0, 1, 0)
                curr_pitch = Pitch

                #glRotatef(obj['z'] - curr_yaw, 0, 0, 1)
                #curr_yaw = obj['z']


                glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
                Cube()
                pygame.display.flip()
                pygame.time.wait(40)


main()
