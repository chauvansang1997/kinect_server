import configparser
import math
import os
from queue import Queue

import numpy as np


class Configure:
    def __init__(self):
        self.config = configparser.ConfigParser()
        if os.path.exists('config_kinect.ini') is False:
            self.config['server.com'] = {}
            top_secret = self.config['server.com']
            top_secret['min_depth'] = self.min_depth
            top_secret['server_ip'] = "127.0.0.1"
            top_secret['area'] = '30'
            top_secret['max_depth'] = '0'
            top_secret['kernel'] = '0'
            top_secret['kinect_id'] = '0'
            top_secret['port'] = '8080'
            top_secret['grid_size_x'] = '1'
            top_secret['grid_size_y'] = '1'
            top_secret['kinect_id'] = '0'
            with open('config_kinect.ini', 'w') as configfile:
                self.config.write(configfile)
        else:
            self.config.read('config_kinect.ini')
            self.min_depth = self.config['server.com']['min_depth']
            self.area = self.config['server.com']['area']
            self.max_depth = self.config['server.com']['max_depth']
            self.kernel = self.config['server.com']['kernel']
            self.port = int(self.config['server.com']['port'])
            self.config_recv_port = int(self.config['server.com']['config_recv_port'])
            self.config_send_port = int(self.config['server.com']['config_send_port'])

            self.config_detect_port = int(self.config['server.com']['config_detect_port'])
            self.grid_size_list_x = self.config['server.com']['grid_size_list_x']
            self.grid_size_list_y = self.config['server.com']['grid_size_list_y']
            self.config_manage_config_port = int(self.config['server.com']['config_manage_config_port'])
            self.data_port = int(self.config['server.com']['data_port'])
            self.grid_size_list_x = self.grid_size_list_x.split(' ')
            self.grid_size_list_y = self.grid_size_list_y.split(' ')
            self.grid_size_list_y = [int(numeric_string) for numeric_string in self.grid_size_list_y]
            self.grid_size_list_x = [int(numeric_string) for numeric_string in self.grid_size_list_x]
            self.default_grid_size_x = int(self.config['server.com']['default_grid_size_x'])
            self.default_grid_size_y = int(self.config['server.com']['default_grid_size_y'])

        self.width = 512
        self.height = 424
        self.clients = []
        self.mesh_clients = []
        self.grid_size_list = []
        self.grid_size_list_x = []
        self.grid_size_list_y = []
        self.grid_transforms = []
        self.queues = []
        self.mesh_queues = []
        self.mesh_transforms = []
        try:
            self.first_depth = np.loadtxt("./configure/first_depth.txt", dtype=np.float32)
        except Exception as e:
            print(e)
            self.first_depth = None

        self.reset = False
        self.mesh_reset = False

    def write(self):
        if os.path.exists('config_kinect.ini') is False:
            self.config['server.com'] = {}
            top_secret = self.config['server.com']
            top_secret['min_depth'] = self.min_depth
            top_secret['server_ip'] = self.server_ip
            top_secret['area'] = self.area
            top_secret['max_depth'] = self.max_depth
            top_secret['kernel'] = self.kernel
            top_secret['port'] = str(self.port)
            top_secret['kinect_id'] = self.kinect_id
            top_secret['config_recv_port'] = str(self.config_recv_port)
            top_secret['config_recv_ip'] = self.config_recv_ip
            top_secret['config_send_port'] = str(self.config_send_port)
            top_secret['config_send_ip'] = self.config_send_ip
            top_secret['server_ip'] = self.server_ip

            with open('config_kinect.ini', 'w') as configfile:
                self.config.write(configfile)

    def write_grid_size_client(self, client, grid_size):
        try:
            old_grid_size = np.loadtxt("./configure/grid_size_{0}_{1}.txt".
                                       format(client[0], str(client[1])),
                                       dtype=np.int32)
            old_grid_size = old_grid_size.tolist()
            if old_grid_size[0] != grid_size[0] or old_grid_size[1] != grid_size[1]:
                self.save_grid_size(client, grid_size)
        except Exception as e:
            print(e)
            self.save_grid_size(client, grid_size)

    def save_grid_size(self, client, grid_size):
        try:
            np.savetxt("./configure/grid_size_{0}_{1}.txt".
                       format(client[0], str(client[1])), np.asarray(grid_size))
            number_point_x = grid_size[0] + 1
            number_point_y = grid_size[1] + 1
            grid_transform_client = []
            for i in range(0, number_point_x * number_point_y):
                x = (i % number_point_x) * (self.width / grid_size[0])
                y = math.trunc(math.trunc(i / number_point_x) % number_point_y) * \
                    (self.height / grid_size[1])
                grid_transform_client.append([x, y])
            grid_transform_client = np.asarray(grid_transform_client)
            np.savetxt("./configure/grid_transform_{0}_{1}.txt".
                       format(client[0], client[1]),
                       grid_transform_client)

            for i in range(0, len(self.clients)):
                if self.clients[i] == client:
                    self.grid_size_list[i] = np.asarray(grid_size)
                    self.grid_transforms[i] = grid_transform_client
                    self.reset = True
                    break

        except Exception as e:
            print(e)

    def write_transform_client(self, client, grid_transform_client):
        try:
            np.savetxt("./configure/grid_transform_{0}_{1}.txt".
                       format(client[0], client[1]),
                       np.asarray(grid_transform_client))
            print('save grid_transform success')
            for i in range(0, len(self.clients)):
                if self.clients[i] == client:
                    print('reload config')
                    self.grid_transforms[i] = grid_transform_client
                    self.reset = True
                    break
        except Exception as e:
            print(e)

    def write_mesh_transform_client(self, client, mesh_transform_client):
        try:
            np.savetxt("./mesh_configure/mesh_transform_{0}_{1}.txt".
                       format(client[0], client[1]),
                       np.asarray(mesh_transform_client))
            print('save mesh_transform success')
            for i in range(0, len(self.mesh_clients)):
                if self.mesh_clients[i] == client:
                    print('reload mesh config')
                    self.mesh_transforms[i] = mesh_transform_client
                    break
        except Exception as e:
            print(e)

    def get_mesh_client_config(self, client):
        try:
            mesh_transform_client = np.loadtxt("./mesh_configure/mesh_transform_{0}_{1}.txt".
                                               format(client[0], str(client[1])),
                                               dtype=np.int32)
            return mesh_transform_client
        except Exception as e:
            print(e)
            mesh_transform_client = np.float32([[0, 0], [512, 0], [0, 424], [512, 424]])
            np.savetxt("./mesh_configure/mesh_transform_{0}_{1}.txt".
                       format(client[0], str(client[1])), mesh_transform_client)
            return mesh_transform_client

    def get_client_config(self, client):
        try:
            grid_transform = np.loadtxt("./configure/grid_transform_{0}_{1}.txt".
                                        format(client[0], str(client[1])),
                                        dtype=np.float32)
            size = np.loadtxt("./configure/grid_size_{0}_{1}.txt".
                              format(client[0], str(client[1])),
                              dtype=np.int32)
            return grid_transform, size
        except Exception as e:
            print(e)
            number_point_x = self.default_grid_size_x + 1
            number_point_y = self.default_grid_size_y + 1
            grid_transform_client = []
            for i in range(0, number_point_x * number_point_y):
                x = (i % number_point_x) * (self.width / self.default_grid_size_x)
                y = math.trunc(math.trunc(i / number_point_x) % number_point_y) * \
                    (self.height / self.default_grid_size_y)
                grid_transform_client.append([x, y])
            grid_transform_client = np.asarray(grid_transform_client)
            np.savetxt("./configure/grid_transform_{0}_{1}.txt".
                       format(client[0], client[1]),
                       grid_transform_client)

            grid_size = [self.default_grid_size_x,
                         self.default_grid_size_y]
            np.savetxt("./configure/grid_size_{0}_{1}.txt".
                       format(client[0], str(client[1])), np.asarray(grid_size))

            return grid_transform_client, np.asarray(grid_size)

    def load_mesh_config(self, client):
        if client not in self.mesh_clients:
            try:
                mesh_transform_client = np.loadtxt("./mesh_configure/transform_{0}_{1}.txt".
                                                   format(client[0], str(client[1])),
                                                   dtype=np.float32)
                self.mesh_transforms.append(mesh_transform_client)
            except Exception as e:
                print(e)
                mesh_transform_client = np.float32([[0, 0], [512, 0], [0, 424], [512, 424]])
                np.savetxt("./mesh_configure/mesh_transform_{0}_{1}.txt".
                           format(client[0], str(client[1])), mesh_transform_client)
                self.mesh_transforms.append(mesh_transform_client)
            self.mesh_queues.append(Queue())
            self.mesh_clients.append(client)
            self.mesh_reset = True

    def load_client_config(self, client):
        if client not in self.clients:

            try:
                grid_transform_client = np.loadtxt("./configure/grid_transform_{0}_{1}.txt".
                                                   format(client[0], str(client[1])),
                                                   dtype=np.float32)
                self.grid_transforms.append(grid_transform_client)
                grid_size = np.loadtxt("./configure/grid_size_{0}_{1}.txt".
                                       format(client[0], str(client[1])),
                                       dtype=np.int32)
                self.grid_size_list.append(grid_size.tolist())

            except Exception as e:
                print(e)
                number_point_x = self.default_grid_size_x + 1
                number_point_y = self.default_grid_size_y + 1
                grid_transform_client = []
                for i in range(0, number_point_x * number_point_y):
                    x = (i % number_point_x) * (self.width / self.default_grid_size_x)
                    y = math.trunc(math.trunc(i / number_point_x) % number_point_y) * \
                        (self.height / self.default_grid_size_y)
                    grid_transform_client.append([x, y])
                grid_transform_client = np.asarray(grid_transform_client)
                self.grid_transforms.append(grid_transform_client)

                np.savetxt("./configure/grid_transform_{0}_{1}.txt".
                           format(client[0], client[1]),
                           grid_transform_client)

                grid_size = [self.default_grid_size_x,
                             self.default_grid_size_y]
                self.grid_size_list.append(np.asarray(grid_size))
                np.savetxt("./configure/grid_size_{0}_{1}.txt".
                           format(client[0], str(client[1])), np.asarray(grid_size))

            self.queues.append(Queue())
            self.clients.append(client)
            self.reset = True
            print('load client success' + str(client[1]))
