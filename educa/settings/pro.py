from .base import*

DEBUG=False

ADMINS = (
    ('Bosa', 'bbosalj@gmail.com'),
)

#Debug is false and a view raises an exception, all info will be sent by email to the people
#listed in the ADMINS setting.
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.postgresql_psycopg2',
        'NAME':'education',
        'USER':'admin',
        'PASSWORD':'admin5194',
        'HOST':'localhost',
        'PORT':'5432'
    }
}