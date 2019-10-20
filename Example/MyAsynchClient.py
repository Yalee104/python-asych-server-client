import AsynchServerClient

C = None

def ServerMsgCallback(msg):
    print("Message From Server = ", msg)

if "__main__" == __name__:
    C = AsynchServerClient.AsynchClient(ServerMsgCallback)
    if C.ConnectToServerByName("localhost", 8001) == True:
        while True:
            WhatToSend = input("Send To Client: ")
            C.SendMessageToServer(WhatToSend.encode('utf-8'))
    C.WaitForDone()
