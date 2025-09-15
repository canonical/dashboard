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

Explore the dashboard at http://localhost:8000/ or 
login to the admin http://localhost:8000/admin (if you loaded the provided initial data, use admin user ``superuser``, password ``superuser`` or user ``driver`, password ``driver``). 

Nearly every cell in the dashboard is a link to the relevant admin view. The most interesting admin view is for *Projects*, for example http://localhost:8000/admin/projects/project/2/change/.


Automated tests
===============

Some automated tests are included and can be executed by running::
    
    make test
