
import AsynchServerClient

S = None

def ClientMsgCallback(clientSocket, msg):
    global S
    EchoMsg = str("Echo Back: " + msg.decode('utf-8'))
    S.SendMessageToClient(clientSocket, EchoMsg.encode('utf-8'))

def main():
    global S

    S = AsynchServerClient.AsynchServer(ClientMsgCallback)
    S.StartServer(8001)
    S.WaitForDone()

if "__main__" == __name__:
    main()
