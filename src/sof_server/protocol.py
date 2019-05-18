import asyncio

from emotion_detector import detector
from meme_generator import generator

START_WORD = 'START '
FILES_DIR = '../files/'


def process(file_name):
    # detect emotion
    image_path = "{}{}".format(FILES_DIR, file_name)
    detected_emotion = detector.detect_emotion(image_path=image_path)
    # create meme
    img = generator.generate_image(emotion=detected_emotion, image_path=image_path)
    out_name = "processed_" + file_name

    out_path = "{}{}".format(FILES_DIR, out_name)
    img.save(out_path, "PNG")
    return out_path


class SOFServerProtocol(asyncio.Protocol):
    def __init__(self):
        self.transport = None
        self.file_name = None

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        if not self.file_name and data.decode().startswith(START_WORD):
            self.file_name = data.decode().lstrip(START_WORD)
            print('file name arrived: {}'.format(self.file_name))
            return

        print('start writing data!')
        with open('{}{}'.format(FILES_DIR, self.file_name), 'ab') as f:
            f.write(data)

    def eof_received(self):
        print("Start processing image...")
        out_path = process(self.file_name)

        with open(out_path, "rb") as f:
            self.transport.write(f.read())
            self.transport.write_eof()
            self.transport.close()

        return False

    def connection_lost(self, exc):
        print("CONN LOST!!!")
        return False
