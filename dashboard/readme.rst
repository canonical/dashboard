=========
Dashboard
=========


Launch a development version of the application
===============================================


Installation
--------------

::

    git clone git@github.com:canonical/dashboard.git
    cd dashboard/dashboard
    make install

This will create a Python virtual environment in ``.venv`` and install the required dependencies.

Database setup
~~~~~~~~~~~~~~~~~

Create the database tables and initialize them with some test data 

::

    make init

The above command executes two separate steps. If you want to run them separately, you can do so with:

1. Create the database tables::

        make migrate

2. (Optional) Load data into the database. For convenience some data are provided in ``initial_data.yaml``, and can be loaded with::

        source .venv/bin/activate
        ./manage.py loaddata initial_data.yaml


Launch the site
~~~~~~~~~~~~~~~

::

    make run

Explore the dashboard at http://localhost:8000/ or log in to the admin interface at http://localhost:8000/admin. If you loaded the provided initial data, log in as one of the following users:

* ``superuser`` with password ``superuser``
* ``driver`` with password ``driver``

Nearly every cell in the dashboard is a link to the relevant admin view. The most interesting admin view is for *Projects*, for example http://localhost:8000/admin/projects/project/2/change/.


Test the application
====================

Some automated tests are included and can be executed by running::
    
    make test


Modify static files
===================

If you're contributing to the application and need to modify static files, for example the CSS files, make sure to modify the files in ``dashboard/static``.

Before you commit your changes, run::

    make collecstatic

This copies the static files to the ``staticfiles`` directory.

During local development, the files in ``dashboard/staticfiles`` aren't used, because ``DEBUG = True`` in ``dashboard/settings.py``. However, in production we have ``DEBUG = False``, which means that the files in ``dashboard/staticfiles`` are used. See the `Django docs <https://docs.djangoproject.com/en/4.2/howto/static-files/>`__.
