from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
# from wtforms.validators import Required


class LoginForm(FlaskForm):
    # username = StringField("username", validators=[Required()])
    # password = PasswordField("password", validators=[Required()])
    username = StringField("username")
    password = PasswordField("password")
    remember_me = BooleanField("remember_me", default=False)
    submit = SubmitField()