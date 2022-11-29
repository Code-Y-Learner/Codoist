from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, PasswordField, SelectField, HiddenField
from wtforms.fields.html5 import DateField, DateTimeField
from wtforms.validators import DataRequired, URL, EqualTo
from flask_ckeditor import CKEditorField


##WTForm
class ModifyCompleteForm(FlaskForm):
    usercode = HiddenField(validators=[DataRequired()])
    title = HiddenField(validators=[DataRequired()])
    complete1 = SubmitField("O")#,choices=[('O', 'O'), ('△', '△'), ('X', 'X')]
    complete2 = SubmitField("△")
    complete3 = SubmitField("X")

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    confirm_password = PasswordField("Password_confirm",validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login!")


class DateForm(FlaskForm):
    date = DateField('')
    all_periods = SubmitField('All_periods')
    submit = SubmitField("OK")

class ModifyDeadlineForm(FlaskForm):
    usercode = HiddenField(validators=[DataRequired()])
    title = HiddenField(validators=[DataRequired()])
    deadline = DateField('')
    daily = SubmitField('Make it Daily work')
    submit2 = SubmitField("OK")

class AddForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()] )
    deadline = DateField('')
    complete = SelectField(choices=[('O', 'O'), ('△', '△'), ('X', 'X')], validators=[DataRequired()])
    submit3 = SubmitField("Add Todolist")