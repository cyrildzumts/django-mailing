=====
mailing
=====

Mailing is a Django app that add support for sending mail of all kind. 
Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "mailling" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'mailing',
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('mailing/', include('mailing.urls')),

3. Run `python manage.py migrate` to create the mailings models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a new mail campaign (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/mailing/ to access the planed mailing campaign