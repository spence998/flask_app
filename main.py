from flask import (Flask,
                   render_template,
                   url_for,
                   send_from_directory)

from flask_uploads import UploadSet, configure_uploads

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
import pyttsx3
import pickle
from detecto.core import Model
from detecto import utils

from pathlib import Path
import playsound
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = "consumerlending"
app.config["UPLOADED_PHOTOS_DEST"] = 'uploads'

model = Model.load(r"C:\dev\projects\repos\flask_app\model\recycle.pth", ["recycle"])

# def serve_model(image):
#     image = utils.read_image("images/IMG_0094.JPG")
#     model = pickle.load()
#
#     predictions = model.predict(image)
#     # predictions format: (labels, boxes, scores)
#     labels, boxes, scores = predictions
#     # [‘alien’, ‘bat’, ‘bat’]
#     print(labels)
#     print(boxes)
#     # tensor([0.9952, 0.9837, 0.5153])
#     print(scores)
#     visualize.show_labeled_image(image, boxes, labels)
#     return True

photos = UploadSet('photos', tuple("png jpg jpeg mp4".split()))
configure_uploads(app, photos)

class UploadForm(FlaskForm):
    photo = FileField(
        validators=[
            FileAllowed(photos, "Only images are allowed"),
            FileRequired('File field should not be empty')
        ]
    )
    submit = SubmitField("Test item")


def play_soundfile(soundfile):
    """
    Function to convert text to speech
    :param text: text
    :param gender: gender
    :return: None
    """
    playsound.playsound(soundfile)


@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(
        app.config["UPLOADED_PHOTOS_DEST"],
        filename
    )

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    form = UploadForm()
    recyclable = False
    frames_p = Path('./uploads/frames')
    upload_p = Path('./uploads')
    print("BEFORE IF STATEMENT SUBMIT")
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = url_for("get_file", filename=filename)


        video = r"C:\dev\projects\repos\flask_app\uploads\{}".format(filename)
        utils.split_video(video,  step_size=5, output_folder=r"C:\dev\projects\repos\flask_app\uploads\frames")
        print("please work")

        try:
            for frame in list(frames_p.glob("**/frame*")):
                image = utils.read_image(str(frame))
                labels, boxes, scores = model.predict(image)
                print(f"in loop: {scores}")
                if any(scores > 0.6):
                    recyclable = True
                    break
        finally:
            for frame in list(frames_p.glob("**/frame*")):
                os.remove(frame)
            for vid in list(upload_p.glob("**/*.mp4")):
                os.remove(vid)


        #Change file_url to where the image detected is

        if recyclable:
            play_soundfile(r"C:\dev\projects\repos\flask_app\sounds\yes_recycle_david.mp3")
            return render_template('recyclable.html', form2=form, file_url=file_url)
        else:
            play_soundfile(r"C:\dev\projects\repos\flask_app\sounds\not_recyclable_david.mp3")
            return render_template('nonrecyclable.html', form2=form, file_url=file_url)
    else:
        file_url = None

    return render_template('home.html', form2=form, file_url=file_url)



if __name__=="__main__":
    app.run(debug=True)
