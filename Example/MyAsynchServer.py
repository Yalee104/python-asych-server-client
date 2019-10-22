
import AsynchServerClient

S = None


def client_msg_callback(client_socket, msg):
    global S
    echomsg = str("Echo Back: " + msg.decode('utf-8'))
    S.send_message_to_client(client_socket, echomsg.encode('utf-8'))


def main_example_with_callback():
    global S
    S = AsynchServerClient.AsynchServer(client_msg_callback)
    S.start_server(8001)
    S.wait_for_done()


class MyAsynchServer(AsynchServerClient.AsynchServer):

    def __init__(self):
        super().__init__(self)
        self.start_server(8001)

    def message_received_from_client(self, client_socket, rcvmsg):
        echomsg = str("Echo Back: " + rcvmsg.decode('utf-8'))
        self.send_message_to_client(client_socket, echomsg.encode('utf-8'))
        print("Message From Server = ", rcvmsg)


def main_example_with_subclass():

    S = MyAsynchServer()
    S.wait_for_done()


if "__main__" == __name__:

    main_example_with_callback()
    # main_example_with_subclass()