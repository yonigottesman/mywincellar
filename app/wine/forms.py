from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import (BooleanField, PasswordField, SelectField, StringField,
                     SubmitField, TextAreaField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                ValidationError)

from app.models import User


class WineForm(FlaskForm):
    description = TextAreaField(
        'Description', validators=[DataRequired(),
                                   Length(min=1, max=140)])
    rating = SelectField('Rating', choices=[1, 2, 3, 4, 5])
    image = FileField('Image')
    submit = SubmitField('Add')


class EditWineForm(WineForm):
    submit = SubmitField('Edit')
    delete = SubmitField('Delete', render_kw={'class': 'btn-danger'})
    image = FileField('Replace Image')
    delete_image = BooleanField('Delete Image')
