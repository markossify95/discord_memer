import dlib
from PIL import Image
from meme_generator import const
from imutils import face_utils
import numpy as np

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(const.model_path)

# resize to a max_width to keep gif size small
max_width = const.MAX_WIDTH


def generate_image(emotion='', image_path=''):
    # open our image, convert to rgba
    img = Image.open(image_path).convert('RGBA')

    # two images we'll need, for eyes and text based on emotion
    if emotion == 'anger':
        deal = Image.open(const.angry_template2_image_path)
        text = Image.open(const.angry_template2_text_path)
    else:
        deal = Image.open(const.happy_template1_image_path)
        text = Image.open(const.happy_template1_text_path)

    if img.size[0] > max_width:
        scaled_height = int(max_width * img.size[1] / img.size[0])
        img.thumbnail((max_width, scaled_height))

    img_gray = np.array(img.convert('L'))  # need grayscale for dlib face detection

    rects = detector(img_gray, 0)

    if len(rects) == 0:
        print("No faces found")
        return img

    faces = []

    for rect in rects:
        face = {}
        # print(rect.top(), rect.right(), rect.bottom(), rect.left())
        shades_width = rect.right() - rect.left()

        # predictor used to detect orientation in place where current face is
        shape = predictor(img_gray, rect)
        shape = face_utils.shape_to_np(shape)
        left_eye = shape[36:42]
        right_eye = shape[42:48]

        # compute the center of mass for each eye
        left_eye_center = left_eye.mean(axis=0).astype("int")
        right_eye_center = right_eye.mean(axis=0).astype("int")

        # compute the angle between the eye centroids
        d_y = left_eye_center[1] - right_eye_center[1]
        d_x = left_eye_center[0] - right_eye_center[0]
        angle = np.rad2deg(np.arctan2(d_y, d_x))

        # resize glasses to fit face width
        current_deal = deal.resize(
            (shades_width, int(shades_width * deal.size[1] / deal.size[0])),
            resample=Image.LANCZOS
        )
        # rotate and flip to fit eye centers
        current_deal = current_deal.rotate(angle, expand=True)
        current_deal = current_deal.transpose(Image.FLIP_TOP_BOTTOM)

        # add the scaled image to a list, shift the final position to the
        # left of the leftmost eye
        face['eyes_image'] = current_deal
        left_eye_x = left_eye[0, 0] - shades_width // 4
        left_eye_y = left_eye[0, 1] - shades_width // 6
        face['final_pos'] = (left_eye_x, left_eye_y)
        faces.append(face)

    draw_img = img.convert('RGBA')  # returns copy of original image
    for face in faces:
        draw_img.paste(face['eyes_image'], face['final_pos'], face['eyes_image'])
        draw_img.paste(text, (75, draw_img.height - 72), text)

    return draw_img
