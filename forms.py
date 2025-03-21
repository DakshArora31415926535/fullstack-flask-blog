from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class RegisterForm(FlaskForm):
    name=StringField(label="Enter your name",validators=[DataRequired()])
    password=StringField(label="Enter a password")
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    name=StringField(label="Enter your name",validators=[DataRequired()])
    password = StringField(label="Enter your password")
    submit = SubmitField("Login")


class CommentForm(FlaskForm):
    comment=CKEditorField(label="Comment",validators=[DataRequired()])
    submit = SubmitField("Post")
