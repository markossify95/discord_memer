import asyncio

START_WORD = 'START '


class SOFClientProtocol(asyncio.Protocol):
    def __init__(self, id, loop):
        self.id = id
        self.img_bin = b''
        self._loop = loop
        self.future_img = self._generate_future()

    def  _generate_future(self):
        return self._loop.create_future()

    def connection_made(self, transport):
        init_msg = "{}{}".format(START_WORD, self.id)
        transport.write(init_msg.encode())
        print('ID sent!')

    def send_image(self, transport, img_bin):
        transport.write(img_bin)
        transport.write_eof()
        print("image sent")

    def data_received(self, data):
        self.img_bin += data

    def eof_received(self):
        self.future_img.set_result(self.img_bin)
        return False

    def get_processed_image(self):
        return self.future_img

    def connection_lost(self, exc):
        print('The server closed the connection')
