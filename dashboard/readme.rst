=========
Dashboard
=========


Launch a development version of the application
===============================================


Installation
--------------

::

    git clone git@github.com:canonical/dashboard.git
    cd dashboard
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt


Database setup
~~~~~~~~~~~~~~~~~

Create the database tables

::

    ./manage.py migrate

For convenience some data are provided in ``initial_data.yaml``, and can be loaded with::

    ./manage.py loaddata initial_data.yaml


Launch the site
~~~~~~~~~~~~~~~

::

    ./manage.py runserver

Login in to the admin http://localhost:8000/admin (use admin user *test*, password *test*, if you loaded the provided initial data) or explore the dashboard.

Nearly every cell in the dashboard is a link to the relevant admin view. The most interesting admin view is for *Projects*, for example http://localhost:8000/admin/projects/project/2/change/.


Automated tests
===============

Some automated tests are included and can be executed by running ``pytest`` (while in the root directory, with the virtual environment activated).
