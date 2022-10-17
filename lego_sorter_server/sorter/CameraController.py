import logging
from socket import socket, AF_INET, SOCK_DGRAM


class CameraController:

    def __init__(self, device_IP = ""):
        self.PORT = 50052
        self.device_IP = device_IP

    def setIP(self, device_IP):
        self.device_IP = device_IP

    def send_image_order(self):
        if self.device_IP is not None and self.device_IP != "":
            sock = socket(AF_INET, SOCK_DGRAM)  # UDP Socket
            logging.info(f"[LegoSorterServiceLW] Sending image order to client {self.device_IP}.")
            sock.sendto(bytes("IMAGE_ORDER", 'utf-8'), (self.device_IP, self.PORT))