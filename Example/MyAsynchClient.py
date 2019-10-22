import AsynchServerClient


def server_msg_callback(msg):
    print("Message From Server = ", msg)


def main_example_with_callback():
    C = AsynchServerClient.AsynchClient(server_msg_callback)
    C.auto_retry_on_disconnect(True)
    if C.connect_to_server_by_name("localhost", 8001):
        while True:
            WhatToSend = input("Send To Client: ")
            C.send_message_to_server(WhatToSend.encode('utf-8'))


class MyAsynchClient(AsynchServerClient.AsynchClient):

    def __init__(self):
        super().__init__(self)
        self.auto_retry_on_disconnect(True)
        self.connect_to_server_by_name("localhost", 8001)

    def message_received_from_server(self, rcvmsg):
        print("Message From Server = ", rcvmsg)


def main_example_with_subclass():
    C = MyAsynchClient()
    while True:
        whattosend = input("Send To Client: ")
        C.send_message_to_server(whattosend.encode('utf-8'))


if "__main__" == __name__:

    main_example_with_callback()
    # main_example_with_subclass()
