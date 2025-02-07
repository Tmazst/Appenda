from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField, TextAreaField,BooleanField, SelectField,DateField, URLField,RadioField,IntegerField,TelField
from wtforms.validators import DataRequired,Length,Email, EqualTo, ValidationError,Optional
from flask_login import current_user
from flask_wtf.file import FileField , FileAllowed
# from wtforms.fields.html5 import DateField,DateTimeField


class Register(FlaskForm):

    name = StringField('name', validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('email', validators=[DataRequired(),Email()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8, max=64)])
    confirm = PasswordField('confirm', validators=[DataRequired(),EqualTo('password'), Length(min=8, max=64)])
    

    submit = SubmitField('Create Account!')

    def validate_email(self,email):
        from app import db, User,app

        # with db.init_app(app):
        user_email = User.query.filter_by(email = self.email.data).first()
        if user_email:
            return ValidationError(f"Email already registered in this platform")

class AccountForm(FlaskForm):
    contacts = TelField('Contact(s)', validators=[Optional()])
    gender =  RadioField('Gender',choices=[("Male", "Male"),("Female", "Female")], validators=[Optional()])
    town = StringField('Your Town (Optional)', validators=[Optional()])
    region = SelectField('Region (Optional)', validators=[Optional()],choices=[("Manzini", "Manzini"),("Hhohho", "Hhohho"),
        ("Shiselweni", "Shiselweni"),("Lobombo", "Lobombo")])
    address = StringField('Phy. Address (Optional)', validators=[Optional()])
    
    # zip_code = StringField('Zip Code / Postal Code', validators=[Length(min=0, max=64)])
    # address = StringField('Physical Address', validators=[DataRequired(), Length(min=8, max=100)])
    image = FileField('Profile Image', validators=[FileAllowed(['jpg','png'])])

    submit = SubmitField('Update')


class ImagesForm(FlaskForm):

    name = StringField('Image Name*', validators=[DataRequired()])
    alias = StringField('siSwati Name(s) or Other', validators=[DataRequired()])
    image = FileField('Upload Image*', validators=[DataRequired()], render_kw={"accept": "image/png,image/jpeg,image/gif,image/bmp"})
    description = TextAreaField('Describe Image', validators=[Optional()])
    image_category = SelectField('Category*',choices=[
        ("Nature", "Nature"),
        ("Mountains", "Mountains"),
        ("Vegetation", "Vegetation"),
        ("Sunsets", "Sunsets"),
        ("Flowers", "Flowers"),
        ("Seascapes", "Seascapes"),
        ("Cities", "Cities"),
        ("Abstract", "Abstract"),
        ("Rivers", "Rivers"),
        ("Wildlife", "Wildlife"),
        ("Beaches", "Beaches"),
        ("Forests", "Forests"),
        ("Spring Water", "Spring Water"),
        ("Deserts", "Deserts"),
        ("Space", "Space"),
        ("Landscapes", "Landscapes"),
        ("Cultural", "Cultural"),
        ("Underwater", "Underwater"),
        ("People", "People"),
        ("Community", "Community"),
        ("Festival", "Festival"),
        ("Road", "Road"),
        ("Infrastructure", "Infrastructure"),
        ("Communications & Media", "Communications & Media"),
        ("Finance", "Finance"),
        ("Health", "Health"),
        ("Educational", "Educational"),
        ("Entertainment", "Entertainment"),
        ("Travel & Entertainment", "Travel & Entertainment"),
        ("Lifestyle", "Lifestyle"),
        ("Media", "Media"),
        ("Food", "Food"),
        ("Insurance", "Insurance"),
        ("Fast Food", "Fast Food"),
        ("Techonology", "Techonology"),
        ("Training & Skills", "Training & Skills"),
        ("Faith", "Faith"),
        ("Business", "Business"),
        ("Weather", "Weather"),
        ("Sports & Re-Creational", "Sports & Re-Creational"),
        ("Betting & Casino", "Betting & Casino"),
        ("Natural Resources", "Natural Resources"),
        ("Energy", "Energy"),
        ("Savings", "Savings"),
        ("Loans", "Loans"),
        ("News", "News"),
        ("Music", "Music"),
        ("Shopping", "Shopping"),
        ("Productivity", "Productivity"),
        ("Utilities", "Utilities"),
        ("Games", "Games")
    ], validators=[DataRequired()])
    publish=BooleanField("Publish Image",default=True)
    submit=SubmitField('submit')

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

    def validate_image(self, image):
        if image.data:
            # Get the file extension
            filename = image.data.filename
            if not '.' in filename or filename.rsplit('.', 1)[1].lower() not in self.ALLOWED_EXTENSIONS:
                raise ValidationError('File type is not allowed. Please upload a PNG, JPG, JPEG, GIF, or BMP file.')


class SendEmailForm(FlaskForm):

    app_name = StringField('App Name', validators=[Length(max=120)])
    emails = StringField('Emails', validators=[Length(max=120)])
    submit = SubmitField('submit')


class EditAppInfoForm(FlaskForm):

    app_name = StringField('App Name', validators=[Length(max=120)])
    app_code = IntegerField('App Code(Check it in Your Email)', validators=[Length(max=120)])
    submit = SubmitField('submit')


class EntertainerUserForm(FlaskForm):
    company_name = StringField('Company Name', validators=[Length(max=120)])
    company_address = StringField('Company Address', validators=[Length(max=120)])
    payment_options = StringField('Payment Options', validators=[Length(max=100)])
    submit = SubmitField('Submit')


class Login(FlaskForm):
    email = StringField('email', validators=[DataRequired(),Email()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8, max=64)])
    submit = SubmitField('Login')


class Contact_Form(FlaskForm):

    name = StringField('name')
    email = StringField('email', validators=[DataRequired(),Email()])
    subject = StringField("subject")
    message = TextAreaField("Message",validators=[Length(min=8, max=2000)])
    submit = SubmitField("Send")


class Reset(FlaskForm):

    old_password = PasswordField('old password', validators=[DataRequired(), Length(min=8, max=64)])
    new_password = PasswordField('new password', validators=[DataRequired(), Length(min=8, max=64)])
    confirm_password = PasswordField('confirm password', validators=[DataRequired(), EqualTo('new password'), Length(min=8, max=64)])

    reset = SubmitField('Reset')


class Reset_Request(FlaskForm):

    email = StringField('email', validators=[DataRequired(), Email()])
    reset = SubmitField('Submit')

    # def validate_email(self,email):
    #     user = user.query.filter_by