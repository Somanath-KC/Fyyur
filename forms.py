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



# TODO:[COMPLETED] IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM
class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=States.choices()
    )
    phone = StringField(
        # TODO:[COMPLETED] implement validation logic for state
        'phone', validators=[phone()]
    )
    image_link = StringField(
        'image_link', validators=[my_url()]
    )
    genres = SelectMultipleField(
        # TODO;[COMPLETED] implement enum restriction
        'genres', validators=[DataRequired(), my_genres()],
        choices= Genre.choices()
    )
    facebook_link = StringField(
        # TODO:[COMPLETED] implement enum restriction
        'facebook_link', validators=[fb_url()]
    )
    website = StringField(
        'website', validators=[my_url()]
    )
    seeking_venue = BooleanField(
        'seeking_venue', default="checked"
    )
    seeking_description = StringField(
        'seeking_description', validators=[Length(max=256)]
    )



class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    datetime = DateTimeField(
        'datetime',
        validators=[DataRequired()],
        default= datetime.today()
    )

