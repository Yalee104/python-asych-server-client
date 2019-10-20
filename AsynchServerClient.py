# Python3

import socket
import threading
import select

class AsynchServer(threading.Thread):

    serverSocket = None
    SocketList = []
    SocketSendMsgList = []

    def __init__(self, func):
        self.func = func
        threading.Thread.__init__(self)

    def StartServer(self, port):
        if not self.serverSocket:
            self.serverSocket = socket.create_server(("",port))
            self.SocketList.append(self.serverSocket)
            self.start()

    def GetAllConnectedClient(self):
        # TODO
        pass

    def SendMessageToClient(self, clientSocket, message):
        socketMsg = {clientSocket:message}
        self.SocketSendMsgList.append(socketMsg)

    def WaitForDone(self):
        if self.is_alive():
            self.join()

    def run(self):
        while True:
            try:
                ready_to_read_list, ready_to_write_list, in_error_list = \
                    select.select(self.SocketList, self.SocketList, [], 5)
            except select.error:
                self.serverSocket.shutdown(2)  # 0 = done receiving, 1 = done sending, 2 = both
                self.serverSocket.close()
                # connection error event here, maybe reconnect
                print("connection error")
                break
            if len(ready_to_read_list) > 0:
                try:
                    for socketReadyToRead in ready_to_read_list:
                        if socketReadyToRead is self.serverSocket: #socketReadyToRead.fileno() == self.serverSocket.fileno():
                            acceptedConn, acceptedAddr = self.serverSocket.accept()
                            self.SocketList.append(acceptedConn)
                            print("Connection accepted from client ", acceptedAddr)
                            print("Socket List: ", self.SocketList)
                        else:
                            recv = socketReadyToRead.recv(2048)
                            if not recv:
                                print("Client Connection most likely lost")
                                self.SocketList.remove(socketReadyToRead)
                            else:
                                #print("Server received from client:", recv, "  Type=", type(recv))
                                # Report the received message from client to callback function
                                self.func(socketReadyToRead, recv)

                except (ConnectionResetError, ConnectionAbortedError) as e:
                    print("Client connection dropped/aborted", type(e), e)
                    self.SocketList.remove(socketReadyToRead)

            if len(ready_to_write_list) > 0:
                try:
                    for socketReadyToWrite in ready_to_write_list:
                        foundAtIndex = 0
                        bSearchFound = False
                        for index in range(len(self.SocketSendMsgList)):
                            for key in self.SocketSendMsgList[index]:
                                if key is socketReadyToWrite:
                                    bSearchFound = True
                                    foundAtIndex = index
                                    break;
                            if bSearchFound:
                                break;
                        if bSearchFound:
                            #print("ReadyToWrite Found index: ", foundAtIndex)
                            SocketMsg = self.SocketSendMsgList.pop(foundAtIndex)
                            if SocketMsg[socketReadyToWrite]:
                                print("Server Send:", SocketMsg[socketReadyToWrite])
                                socketReadyToWrite.send(SocketMsg[socketReadyToWrite])

                except (ConnectionResetError, ConnectionAbortedError) as e:
                    print("Client connection dropped/aborted", type(e), e)
                    self.SocketList.remove(socketReadyToWrite)

            if in_error_list:
                print(in_error)

        self.serverSocket.close()
        self.serverSocket = None

class AsynchClient(threading.Thread):

    clientSocket = None
    SendMsgList = []

    def __init__(self, func):
        self.func = func
        threading.Thread.__init__(self)

    def ConnectToServerByName(self, Name, Port):
        # We only allow one connection
        if self.clientSocket:
            return False

        msg = "getaddrinfo returns an empty list"
        self.serverList = socket.getaddrinfo(Name, Port)
        for serverInfo in self.serverList:
            af, socktype, proto, canonname, sa = serverInfo
            try:
                self.clientSocket = socket.socket(af, socktype, proto)
                self.clientSocket.connect(sa)
            except socket.error:
                print(str(socket.error) + " " + msg)
                if self.clientSocket:
                    self.clientSocket.close()
                self.clientSocket = None
                continue
            break
        if not self.clientSocket:
            print ("Unable to find and connect to ", Name, Port)
            return False
        else:
            self.start()
            return True

    def SendMessageToServer(self, message):
        self.SendMsgList.append(message)

    def WaitForDone(self):
        if self.is_alive():
            self.join()

    def run(self):
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
                        #print("Client received from Server:", recv, "  Type=", type(recv))
                        # Report the received message from client to callback function
                        self.func(recv)

                except (ConnectionResetError, ConnectionAbortedError) as e:
                    print("Server connection dropped/aborted", type(e), e)
                    break

            if len(ready_to_write_list) > 0:
                try:
                    if len(self.SendMsgList):
                        SocketMsg = self.SendMsgList.pop(0)
                        if SocketMsg:
                            print("Client Send:", SocketMsg)
                            self.clientSocket.send(SocketMsg)

                except (ConnectionResetError, ConnectionAbortedError) as e:
                    print("Server connection dropped/aborted", type(e), e)
                    break

            if in_error_list:
                print(in_error)

        self.clientSocket.close()
        self.clientSocket = None

