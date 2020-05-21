from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, Regexp, ValidationError, Length
from enums import Genre, States
from phonenumbers import parse, geocoder



# --------------------------------------------------------------------- #
# Custom Validators
# --------------------------------------------------------------------- #

# Refrences:
#    https://stackoverflow.com/questions/5205652/facebook-profile-url-regular-expression
#    https://wtforms.readthedocs.io/en/stable/crash_course.html
#    https://stackoverflow.com/questions/50327174/custom-validators-in-wtforms-using-flask

# This custom validator will allow empty strings
# the original URL() raises an error with empty strings
def my_url():
    def _my_url(form, field):
        # Will remove the URL validator in case the user tries again
        # with an empty URL
        if len(field.validators) >2:
            field.validators.pop()

        if not field.data == "":
            field.validators.append(URL())
        else:
            # This will make orm to insert default url when input string is empty
            field.data = None
    return _my_url


# This custom validator will allow empty strings
# Validates the facebook url with regex
def fb_url():
    def _fb_url(form, field):
        # Will remove the URL validator in case the user tries again
        # with an empty URL
        if len(field.validators) >2:
            field.validators.pop()

        if not field.data == "":
            field.validators.append(URL())
            field.validators.append(
                Regexp(
                       "(?:(?:http|https):\/\/)?(?:www.)?facebook.com\/(?:(?:\w)*#!\/)?(?:pages\/)?(?:[?\w\-]*\/)?(?:profile.php\?id=(?=\d.*))?([\w\-]*)?"
                      )
            )
    return _fb_url


# This Custom Validator implements 
# State Validation on Input Phone Number
def phone():
    def _phone(form, field):
        data = field.data
        if not (len(data) == 10):
            raise ValidationError
        
        phone_number = parse(data, "US")
        city, state = geocoder.description_for_number(phone_number, "en").split(', ')

        # Checks for states in enum
        if not (state in [value for choice, value in States.choices()]):
            raise ValidationError
    return _phone


# This Custom Validator implements
# Validation on Genres Enums
def my_genres():
    def _my_genres(form, field):
        enum_genres = [value for choice, value in Genre.choices()]

        # Check if every vales is in genre enum
        for item in field.data:
            if not item in enum_genres:
                raise ValidationError
    
    return _my_genres

# --------------------------------------------------------------------- #
# Forms
# --------------------------------------------------------------------- #

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), AnyOf([choice.value for choice in States])],
        choices= States.choices()
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[phone()]
    )
    genres = SelectMultipleField(
        # TODO:[COMPLETED] implement enum restriction
        'genres', validators=[DataRequired(), my_genres()],
         choices= Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', 
         validators=[fb_url()]
    )
    image_link = StringField(
        'image_link', validators=[my_url()]
    )
    website = StringField(
        'website', validators=[my_url()]
    )
    seeking_talent = BooleanField(
        'seeking_talent', default="checked"
    )
    seeking_description = StringField(
        'seeking_description', validators=[Length(max=256)]
    )



# TODO IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM
class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]
    )
    phone = StringField(
        # TODO implement validation logic for state
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        choices=[
            ('Alternative', 'Alternative'),
            ('Blues', 'Blues'),
            ('Classical', 'Classical'),
            ('Country', 'Country'),
            ('Electronic', 'Electronic'),
            ('Folk', 'Folk'),
            ('Funk', 'Funk'),
            ('Hip-Hop', 'Hip-Hop'),
            ('Heavy Metal', 'Heavy Metal'),
            ('Instrumental', 'Instrumental'),
            ('Jazz', 'Jazz'),
            ('Musical Theatre', 'Musical Theatre'),
            ('Pop', 'Pop'),
            ('Punk', 'Punk'),
            ('R&B', 'R&B'),
            ('Reggae', 'Reggae'),
            ('Rock n Roll', 'Rock n Roll'),
            ('Soul', 'Soul'),
            ('Other', 'Other'),
        ]
    )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[URL()]
    )



class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

