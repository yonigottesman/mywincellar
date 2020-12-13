from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User


from flask_wtf.file import FileField

    
class WineForm(FlaskForm):
    description = TextAreaField('Description', validators=[
        DataRequired(), Length(min=1, max=140)])
    rating = SelectField('Rating',choices=[1,2,3,4,5])
    image = FileField('Image')
    submit = SubmitField('Add')
    
class EditWineForm(WineForm):
    submit = SubmitField('Edit')
    delete = SubmitField('Delete',render_kw={'class':'btn-danger'})
    image = FileField('Replace Image')
    delete_image = BooleanField('Delete Image')
    