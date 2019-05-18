import logging

from EmoPy.src.fermodel import FERModel
from emotion_detector.const import target_emotions


model = FERModel(target_emotions)


def detect_emotion(image_path=''):
    try:
        return model.predict(image_path)
    except Exception as e:
        logging.error('Emotion detection failed! Error: {}'.format(e))
        return None

