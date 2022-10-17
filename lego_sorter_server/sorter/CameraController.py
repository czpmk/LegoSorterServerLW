import logging
from socket import socket, AF_INET, SOCK_DGRAM


class CameraController:

    def __init__(self):
        self.deviceIP: str = ""
        self.PORT = 50052

    @staticmethod
    def send_image_order(self):
        if self.deviceIP is not None and self.deviceIP != "":
            sock = socket(AF_INET, SOCK_DGRAM)  # UDP Socket
            logging.info(f"[LegoSorterServiceLW] Sending image order to client {self.deviceIP}.")
            sock.sendto(bytes("IMAGE_ORDER", 'utf-8'), (self.deviceIP, self.PORT))