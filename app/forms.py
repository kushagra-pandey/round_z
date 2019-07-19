from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DecimalField, FloatField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo, Length
from app.models import User, Startup

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterStartupForm(FlaskForm):
    name = StringField('Startup Name', validators=[DataRequired()])
    description=TextAreaField('Description', validators=[Length(min=0, max=140)])
    validation = StringField('Validation Code', validators=[DataRequired()])
    logo = FileField('Logo', validators=[FileRequired(),
        FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Submit')
    def validate_name(self, name):
        test = Startup.query.filter_by(name=name.data).first()
        if test is not None:
            raise ValidationError('Please use a different startup name.')
    def validate_validation(self, validation):
        if validation.data != "1234":
            raise ValidationError('Incorrect Validation Pin.')
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
class EditStartupForm(FlaskForm):
    name = StringField('Startup Name', validators=[DataRequired()])
    description=TextAreaField('Description', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')
    def __init__(self, original_username, *args, **kwargs):
        super(EditStartupForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
    def validate_name(self, name):
        if name.data != self.original_username:
            test = Startup.query.filter_by(name=name.data).first()
            if test is not None:
                raise ValidationError('Please use a different startup name.')
class InvestForm(FlaskForm):
    name = StringField('Startup Name', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    submit = SubmitField('Next')
    def validate_name(self, name):
        test = Startup.query.filter_by(name=name.data).first()
        if test is None:
            raise ValidationError('This startup name does not exist. Please try a different name.')
    def validate_amount(self, amount):
        if amount.data <= 0:
            raise ValidationError('Please enter a positive amount.')
