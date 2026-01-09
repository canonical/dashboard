# Dashboard

A Django-based database-driven web application, to track the progress of projects against a set of criteria to measure quality and progress.

![A sample dashboard](screenshots/dashboard.png)

This repo contains the source code of the application. [Run the application from source](./dashboard#readme)

This repo also contains the source code of a Kubernetes charm for operating the application as part of a Juju deployment. To learn about Juju and charms, see https://juju.is/docs.

> [!IMPORTANT]
> To use the dashboard charm in a real Juju deployment, see [TODO: docs on Charmhub] instead of this repo.
> This repo is the right place to look if you'd like to test the charm, customise it for your own purposes, or contribute to development!

In this README:

  - **[Deploy the dashboard on your machine](#deploy-the-dashboard-on-your-machine)**
    - [Prepare your environment](#prepare-your-environment)
    - [Create a container image for the application](#create-a-container-image-for-the-application)
    - [Create a charm](#create-a-charm)
    - [Deploy the dashboard charm](#deploy-the-dashboard-charm)
    - [Configure the dashboard](#configure-the-dashboard)
    - [Deploy a PostgreSQL charm](#deploy-a-postgresql-charm)
    - [Wait for the charms to finish deploying](#wait-for-the-charms-to-finish-deploying)
    - [Integrate the dashboard with PostgreSQL](#integrate-the-dashboard-with-postgresql)
    - [Check the status of the dashboard](#check-the-status-of-the-dashboard)
    - [Open the dashboard in your browser](#open-the-dashboard-in-your-browser)
    - [Explore further](#explore-further)
  - **[Simulate a production deployment](#simulate-a-production-deployment)** (work in progress)

## Deploy the dashboard on your machine

### Prepare your environment

 1. Follow the "Set things up" instructions in [Write your first Kubernetes charm for a Django app](https://canonical-charmcraft.readthedocs-hosted.com/en/latest/tutorial/kubernetes-charm-django/). These instructions will guide you through installing the required tools.

    You can stop following the setup instructions after you've installed Juju and bootstrapped a development controller.

    At this point, you should have a shell session inside a Multipass virtual machine called `charm-dev`. Continue using your `charm-dev` shell session until you're ready to [open the dashboard in your browser](#open-the-dashboard-in-your-browser).

 2. Clone this repo:

    ```
    cd
    git clone https://github.com/canonical/dashboard.git
    cd ~/dashboard
    ```

 3. Create a "model" in Juju:

    ``` { name=create-model }
    juju add-model web-k8s
    ```

    You can think of the model as a unified workspace for the dashboard application and related applications, including a PostgreSQL database.

    After creating the model, you should see the following output:

    > ```
    > Added 'web-k8s' model on microk8s/localhost with credential 'microk8s' for user 'admin'
    > ```

 4. Check the architecture of your machine:

    ``` { name=check-architecture }
    dpkg --print-architecture
    ```

    If the output is not `amd64`, you'll need to adjust some of the commands in this README. For example, if the output is `arm64`, you'll need to replace `amd64` by `arm64`.

 5. Configure the Juju model to match the architecture of your machine:

    ``` { name=configure-model }
    juju set-model-constraints -m web-k8s arch=amd64  # remember to replace amd64 if needed!
    ```

### Create a container image for the application

``` { name=create-image }
cd ~/dashboard
rockcraft pack
```

The application will run in a Kubernetes cluster, so we need a container image for the application. The `rockcraft` command uses [Rockcraft](https://documentation.ubuntu.com/rockcraft/en/latest/) to create a "rock" image that is compliant with the [Open Container Initiative](https://opencontainers.org/) format.

Creating the container image might take several minutes, so this is a good point to take a break. When you return, you should see the following output:

> ```
> Packed dashboard_0.47_amd64.rock
> ```

### Create a charm

``` { name=create-charm }
cd ~/dashboard/charm
charmcraft pack
```

In essence, the charm is a Python wrapper for the dashboard application. It's also common to call charms "operators". The dashboard charm receives information from Juju about related applications (in our case, a PostgreSQL database) and how we'd like the dashboard to be configured, then acts appropriately in the dashboard application's container.

Creating the charm might take several minutes, so this is another good point to take a break. When you return, you should see the following output:

> ```
> Packed dashboard_ubuntu-22.04-amd64.charm
> ```

### Deploy the dashboard charm

``` { name=deploy-dashboard }
cd ~/dashboard
rockcraft.skopeo --insecure-policy copy --dest-tls-verify=false \
  oci-archive:dashboard_0.47_amd64.rock \
  docker://localhost:32000/dashboard:0.47
juju deploy ./charm/dashboard_ubuntu-22.04-amd64.charm \
  --resource django-app-image=localhost:32000/dashboard:0.47
```

The `rockcraft.skopeo` command makes the container image available to Juju.

Deploying the charm adds it to our Juju model. At a high level, this does the following:

  - Enables the dashboard application to discover related applications, including a PostgreSQL database.

  - Runs the container image that we created for the dashboard application. There's no database yet, so this won't actually start the dashboard's web server. The charm will automatically start the web server when we integrate the dashboard with a database.

After deploying the charm, you should see the following output:

> ```
> Located local charm "dashboard", revision 0
> Deploying "dashboard" from local charm "dashboard", revision 0 on ubuntu@22.04/stable
> ```

### Configure the dashboard

``` { name=configure-dashboard }
juju config dashboard django-allowed-hosts='*'
```

This command tells Juju which configuration values to use when the charm starts the dashboard's web server. We're using `django-allowed-hosts='*'` to make it easier to access the dashboard for testing; you wouldn't use this value in a production deployment.

### Deploy a PostgreSQL charm

``` { name=deploy-postgres }
juju deploy postgresql-k8s --trust
```

### Wait for the charms to finish deploying

``` { name=watch-status }
juju status --watch 1s
```

This command displays a status report that updates every second.

Deploying the charms might take several minutes. Wait until the status of the `dashboard` app is "blocked" and the status of `postgresql-k8s` app is "active":

> ```
> Model    Controller      Cloud/Region        Version  SLA          Timestamp
> web-k8s  dev-controller  microk8s/localhost  3.6.4    unsupported  11:00:00+08:00
>
> App             Version  Status   Scale  Charm           Channel    Rev  Address         Exposed  Message
> dashboard                blocked      1  dashboard                    0  10.162.183.219  no       missing integrations: postgresql
> postgresql-k8s  14.15    active       1  postgresql-k8s  14/stable  495  10.162.183.145  no
>
> Unit               Workload  Agent  Address      Ports  Message
> dashboard/0*       blocked   idle   10.1.179.60         missing integrations: postgresql
> postgresql-k8s/0*  active    idle   10.1.179.5          Primary
> ```

To exit the status report, press <kbd>Ctrl</kbd> + <kbd>C</kbd>.

### Integrate the dashboard with PostgreSQL

``` { name=integrate-charms }
juju integrate dashboard postgresql-k8s
```

When you run this command, the dashboard charm does the following:

  - Receives information from Juju about the PostgreSQL database, including its location on the network, username, and password.

  - Connects to the dashboard application's container and starts the dashboard's web server, with the database information in environment variables. The dashboard charm also sets environment variables for the configuration values that we specified in [Configure the dashboard](#configure-the-dashboard).

This enables the dashboard's web server to directly interact with the database.

### Check the status of the dashboard

  ``` { name=check-dashboard-status }
  juju status dashboard
  ```

  You should see the following output:

  > ```
  > Model    Controller      Cloud/Region        Version  SLA          Timestamp
  > web-k8s  dev-controller  microk8s/localhost  3.6.4    unsupported  11:02:00+08:00
  >
  > App        Version  Status  Scale  Charm      Channel  Rev  Address         Exposed  Message
  > dashboard           active      1  dashboard             0  10.162.183.219  no
  >
  > Unit          Workload  Agent  Address      Ports  Message
  > dashboard/0*  active    idle   10.1.179.60
  > ```

### Open the dashboard in your browser

 1. Grab the address of the `dashboard/0` unit from Juju's status report. In our example in [Check the status of the dashboard](#check-the-status-of-the-dashboard), the address is `10.1.179.60`.

 3. Open a terminal on your machine. You'll complete the rest of this section outside your `charm-dev` virtual machine.

 3. Display information about your `charm-dev` virtual machine:

    ```
    multipass info charm-dev
    ```

    You should see the following output:

    > ```
    > Name:           charm-dev
    > State:          Running
    > Snapshots:      0
    > IPv4:           10.35.173.143
    >                 10.1.179.0
    > (more lines)
    > ```

 4. Grab the first IPv4 address listed. This is the address of your `charm-dev` virtual machine. In our example, the address is `10.35.173.143`.

 5. Make it possible to access the dashboard application's container:

    ```
    sudo ip route add 10.1.179.0/24 via 10.35.173.143  # remember to replace the addresses!
    ```

      - Replace `10.1.179` by the first three numbers in the address from step 1.
      - Replace `10.35.173.143` by the address from step 4.

 6. Open `http://<unit>:8000` in your browser, where `<unit>` is the address from step 1. In our example, that would be `http://10.1.179.60:8000`.

You should see the dashboard in your browser. Congratulations!

### Explore further

  - To load the sample data that comes with the dashboard, run the following command inside your `charm-dev` virtual machine:

    ``` { name=load-sample-data }
    juju run dashboard/0 load-sample-data
    ```

    This uses a Juju "action" to run [manage.py](./dashboard/manage.py) inside the dashboard application's container. For technical details, see [TODO: doc in progress].

  - To inspect the configuration of the dashboard's web server, run the following commands inside your `charm-dev` virtual machine:

    ``` {name=inspect-server }
    # For convenience later, install yq to help display YAML:
    which yq > /dev/null 2>&1
    if [ $? -ne 0 ]; then sudo snap install yq; fi
    # Ask the Pebble service manager to tell us whether the web server is active:
    juju ssh --container django-app dashboard/0 pebble services django
    # Ask the Pebble service manager to tell us which environment variables were set:
    pebble_yaml="$(juju ssh --container django-app dashboard/0 pebble plan)"
    echo -e "\nEnvironment variables:"
    echo "$pebble_yaml" | yq '.services.django.environment'
    ```

## Simulate a production deployment

Work in progress. Aspects to cover:
- Integrating ingress
- How to disable debug mode and still have the application work
- Probably more...
