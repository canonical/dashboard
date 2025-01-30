=========
Dashboard
=========

A Django-based database-driven web application, to track progress of projects against a set of criteria to determine quality or development.

Launch a development version of the application
===============================================

Installation
--------------

::
    git clone ...
    cd dashboard
    python -m venv .venv
    source ./venv/bin/activate
    pip install -r requirements.txt


Database setup
~~~~~~~~~~~~~~~~~

Create the database tables

::
    ./manage.py migrate

For convenience some data, including an admin user (*test*, password *test*), are provided in ``initial_data.yaml``, and can be loaded with::

    ./manage.py loaddata initial_data.yaml


Launch the site
~~~~~~~~~~~~~~~

    ./manage.py runserver    

Login in to the admin http://localhost:8000/admin or explore the dashboard.

Nearly every cell in the dashboard is a link to the relevant admin view.
