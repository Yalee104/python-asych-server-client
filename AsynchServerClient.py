# AsynchServerClient Class using Python 3.8

import socket
import threading
import select
from typing import final
from abc import abstractmethod


class AsynchServer(threading.Thread):

    serverSocket = None
    socketList = []
    socketSendMsgList = []

    def __init__(self, cbfunc):
        self.func = cbfunc
        threading.Thread.__init__(self)

    def start_server(self, port):
        if not self.serverSocket:
            self.serverSocket = socket.create_server(("",port))
            self.socketList.append(self.serverSocket)
            self.start()

    def get_all_connected_client(self):
        return self.socketList

    def send_message_to_client(self, client_socket, message):
        socket_msg = {client_socket:message}
        self.socketSendMsgList.append(socket_msg)

    @abstractmethod
    def message_received_from_client(self, client_socket, rcvmsg):
        print("Should implement messagereceivedfromclient if function callback is not provided")

    def wait_for_done(self):
        if self.is_alive():
            self.join()

    @final
    def run(self):
        while True:
            try:
                ready_to_read_list, ready_to_write_list, in_error_list = \
                    select.select(self.socketList, self.socketList, [], 5)
            except select.error:
                self.serverSocket.shutdown(2)  # 0 = done receiving, 1 = done sending, 2 = both
                self.serverSocket.close()
                # connection error event here, maybe reconnect
                print("connection error")
                break
            if len(ready_to_read_list) > 0:
                try:
                    for socketReadyToRead in ready_to_read_list:
                        if socketReadyToRead is self.serverSocket: # socketReadyToRead.fileno() == self.serverSocket.fileno():
                            acceptedconn, acceptedaddr = self.serverSocket.accept()
                            self.socketList.append(acceptedconn)
                            print("Connection accepted from client ", acceptedaddr)
                            print("Socket List: ", self.socketList)
                        else:
                            recv = socketReadyToRead.recv(2048)
                            if not recv:
                                print("Client Connection most likely lost")
                                self.socketList.remove(socketReadyToRead)
                            else:
                                # print("Server received from client:", recv, "  Type=", type(recv))
                                # Report the received message from client to callback function
                                if not callable(self.func):
                                    self.message_received_from_client(socketReadyToRead, recv)
                                else:
                                    self.func(socketReadyToRead, recv)

                except (ConnectionResetError, ConnectionAbortedError) as e:
                    print("Client connection dropped/aborted", type(e), e)
                    self.socketList.remove(socketReadyToRead)

            if len(ready_to_write_list) > 0:
                try:
                    for socketReadyToWrite in ready_to_write_list:
                        found_at_index = 0
                        search_found = False
                        for index in range(len(self.socketSendMsgList)):
                            for key in self.socketSendMsgList[index]:
                                if key is socketReadyToWrite:
                                    search_found = True
                                    found_at_index = index
                                    break
                            if search_found:
                                break
                        if search_found:
                            # print("ReadyToWrite Found index: ", found_at_index)
                            socket_msg = self.socketSendMsgList.pop(found_at_index)
                            if socket_msg[socketReadyToWrite]:
                                print("Server Send:", socket_msg[socketReadyToWrite])
                                socketReadyToWrite.send(socket_msg[socketReadyToWrite])

                except (ConnectionResetError, ConnectionAbortedError) as e:
                    print("Client connection dropped/aborted", type(e), e)
                    self.socketList.remove(socketReadyToWrite)

            if in_error_list:
                print(in_error_list)

        self.serverSocket.close()
        self.serverSocket = None


class AsynchClient(threading.Thread):

    autoRetryConnection = False
    serverName = None
    serverPort = None
    clientSocket = None
    sendMsgList = []

    def __init__(self, cbfunc=None):
        self.func = cbfunc
        threading.Thread.__init__(self)

    def auto_retry_on_disconnect(self, on_off):
        self.autoRetryConnection = on_off

    def connect_to_server_by_name(self, name, port):
        # We only allow one connection
        if self.clientSocket:
            return False

        self.serverName = name
        self.serverPort = port

        msg = "getaddrinfo returns an empty list"
        serverlist = socket.getaddrinfo(name, port)
        for serverInfo in serverlist:
            af, socktype, proto, canonname, sa = serverInfo
            try:
                self.clientSocket = socket.socket(af, socktype, proto)
                self.clientSocket.connect(sa)
            except socket.error:
                # print(str(socket.error) + " " + msg)
                if self.clientSocket:
                    self.clientSocket.close()
                self.clientSocket = None
                continue
            break
        if not self.clientSocket:
            print("Unable to find and connect to ", name, port)
            return False
        else:
            if not self.is_alive():
                self.start()
            return True

    def send_message_to_server(self, message):
        self.sendMsgList.append(message)

    @abstractmethod
    def message_received_from_server(self, rcvmsg):
        print("Should implement MessageReceivedFromServer if function callback is not provided")

    def wait_for_done(self):
        if self.is_alive():
            self.join()

    @final
    def socket_data_process_blocking(self):

        if not self.clientSocket:
            return

        while True:
            try:
                ready_to_read_list, ready_to_write_list, in_error_list = \
                    select.select([self.clientSocket,], [self.clientSocket,], [], 5)
            except select.error:
                self.clientSocket.shutdown(2)  # 0 = done receiving, 1 = done sending, 2 = both
                self.clientSocket.close()
                # connection error event here, maybe reconnect
                print("connection error")
                break
            if len(ready_to_read_list) > 0:
                try:
                    recv = self.clientSocket.recv(2048)
                    if not recv:
                        print("Server Connection most likely lost")
                        break
                    else:
                        # print("Client received from Server:", recv, "  Type=", type(recv))
                        # Report the received message from client to callback function or call MessageReceivedFromServer
                        if not callable(self.func):
                            self.message_received_from_server(recv)
                        else:
                            self.func(recv)

                except (ConnectionResetError, ConnectionAbortedError) as e:
                    print("Server connection dropped/aborted", type(e), e)
                    break

            if len(ready_to_write_list) > 0:
                try:
                    if len(self.sendMsgList):
                        socket_msg = self.sendMsgList.pop(0)
                        if socket_msg:
                            print("Client Send:", socket_msg)
                            self.clientSocket.send(socket_msg)

                except (ConnectionResetError, ConnectionAbortedError) as e:
                    print("Server connection dropped/aborted", type(e), e)
                    break

            if in_error_list:
                print(in_error_list)

        self.clientSocket.close()
        self.clientSocket = None

    @final
    def run(self):
        while True:
            self.socket_data_process_blocking()
            if self.autoRetryConnection:
                self.connect_to_server_by_name(self.serverName, self.serverPort)
            else:
                break
