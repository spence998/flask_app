from flask import (Flask,
                   render_template,
                   url_for,
                   send_from_directory)

from flask_uploads import UploadSet, IMAGES, configure_uploads

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
import pyttsx3

app = Flask(__name__)
app.config['SECRET_KEY'] = "consumerlending"
app.config["UPLOADED_PHOTOS_DEST"] = 'uploads'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

class UploadForm(FlaskForm):
    photo = FileField(
        validators=[
            FileAllowed(photos, "Only images are allowed"),
            FileRequired('File field should not be empty')
        ]
    )
    submit = SubmitField("Test item")


def text_to_speech(text):
    """
    Function to convert text to speech
    :param text: text
    :param gender: gender
    :return: None
    """
    engine = pyttsx3.init()
    engine.setProperty('rate', 125)
    engine.setProperty('volume', 0.8)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()

@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(
        app.config["UPLOADED_PHOTOS_DEST"],
        filename
    )

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    form = UploadForm()

    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = url_for("get_file", filename=filename)

        #Test out the model here
        model_result = False

        if model_result:
            text = 'The item is recyclable'
            text_to_speech(text)
            return render_template('recyclable.html', form2=form, file_url=file_url)
        else:
            text = 'The item is not recyclable'
            text_to_speech(text)
            return render_template('nonrecyclable.html', form2=form, file_url=file_url)
    else:
        file_url=None

    return render_template('home.html', form2=form, file_url=file_url)



if __name__=="__main__":
    app.run(debug=True)