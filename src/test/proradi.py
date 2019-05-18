import dlib
from PIL import Image

from imutils import face_utils
import numpy as np


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

# resize to a max_width to keep gif size small
max_width = 500

# open our image, convert to rgba
img = Image.open('data/image1.jpg').convert('RGBA')

# two images we'll need, glasses and deal with it text
# deal = Image.open("templates/deals.png")
# text = Image.open('templates/text.png')
deal = Image.open("templates/eyes.png")
text = Image.open('templates/triggered.png')

if img.size[0] > max_width:
    scaled_height = int(max_width * img.size[1] / img.size[0])
    img.thumbnail((max_width, scaled_height))

img_gray = np.array(img.convert('L'))  # need grayscale for dlib face detection

rects = detector(img_gray, 0)

if len(rects) == 0:
    print("No faces found, exiting.")
    exit()

faces = []

for rect in rects:
    face = {}
    print(rect.top(), rect.right(), rect.bottom(), rect.left())
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
    dY = left_eye_center[1] - right_eye_center[1]
    dX = left_eye_center[0] - right_eye_center[0]
    angle = np.rad2deg(np.arctan2(dY, dX))

    # resize glasses to fit face width
    current_deal = deal.resize((shades_width, int(shades_width * deal.size[1] / deal.size[0])),
                               resample=Image.LANCZOS)
    # rotate and flip to fit eye centers
    current_deal = current_deal.rotate(angle, expand=True)
    current_deal = current_deal.transpose(Image.FLIP_TOP_BOTTOM)

    # add the scaled image to a list, shift the final position to the
    # left of the leftmost eye
    face['glasses_image'] = current_deal
    left_eye_x = left_eye[0, 0] - shades_width // 4
    left_eye_y = left_eye[0, 1] - shades_width // 6
    face['final_pos'] = (left_eye_x, left_eye_y)
    faces.append(face)

draw_img = img.convert('RGBA')  # returns copy of original image
for face in faces:
    draw_img.paste(face['glasses_image'], face['final_pos'], face['glasses_image'])
    draw_img.paste(text, (75, draw_img.height - 72), text)
draw_img.show()
