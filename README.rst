========================
Team and repository tags
========================

.. image:: http://governance.openstack.org/badges/deb-congress.svg
    :target: http://governance.openstack.org/reference/tags/index.html

.. Change things from this point on

.. include:: aliases.rst

.. _readme:

======================================
Congress Introduction and Installation
======================================

1. What is Congress
===================

Congress is an open policy framework for the cloud.  With Congress, a
cloud operator can declare, monitor, enforce, and audit "policy" in a
heterogeneous cloud environment.  Congress gets inputs from a cloud's
various cloud services; for example in OpenStack, Congress fetches
information about VMs from Nova, and network state from Neutron, etc.
Congress then feeds input data from those services into its policy engine
where Congress verifies that the cloud's actual state abides by the cloud
operator's policies.  Congress is designed to work with **any policy** and
**any cloud service**.

2. Why is Policy Important
==========================

The cloud is a collection of autonomous
services that constantly change the state of the cloud, and it can be
challenging for the cloud operator to know whether the cloud is even
configured correctly.  For example,

* The services are often independent from each other and do not
  support transactional consistency across services, so a cloud
  management system can change one service (create a VM) without also
  making a necessary change to another service (attach the VM to a
  network).  This can lead to incorrect behavior.

* Other times, we have seen a cloud operator allocate cloud resources
  and then forget to clean them up when the resources are no longer in
  use, effectively leaving garbage around the system and wasting
  resources.

* The desired cloud state can also change over time.  For example, if
  a security vulnerability is discovered in Linux version X, then all
  machines with version X that were ok in the past are now in an
  undesirable state.  A version number policy would detect all the
  machines in that undesirable state.  This is a trivial example, but
  the more complex the policy, the more helpful a policy system
  becomes.

Congress's job is to help people manage that plethora of state across
all cloud services with a succinct policy language.

3. Using Congress
=================

Setting up Congress involves writing policies and configuring Congress
to fetch input data from the cloud services.  The cloud operator
writes policy in the Congress policy language, which receives input
from the cloud services in the form of tables.  The language itself
resembles datalog.  For more detail about the policy language and data
format see :ref:`Policy <policy>`.

To add a service as an input data source, the cloud operator configures a Congress
"driver," and the driver queries the service.  Congress already
has drivers for several types of service, but if a cloud operator
needs to use an unsupported service, she can write a new driver
without much effort and probably contribute the driver to the
Congress project so that no one else needs to write the same driver.

Finally, when using Congress, the cloud operator must choose what
Congress should do with the policy it has been given:

* **monitoring**: detect violations of policy and provide a list of those violations
* **proactive enforcement**: prevent violations before they happen (functionality that requires
  other services to consult with Congress before making changes)
* **reactive enforcement**: correct violations after they happen (a manual process that
  Congress tries to simplify)

In the future, Congress
will also help the cloud operator audit policy (analyze the history
of policy and policy violations).

Congress is free software and is licensed with Apache.

* Free software: Apache license

4. Installing Congress
======================

There are 2 ways to install Congress.

* As part of DevStack.  Get Congress running alongside other OpenStack services like Nova
  and Neutron, all on a single machine.  This is a great way to try out Congress for the
  first time.

* Separate install.  Get Congress running alongside an existing OpenStack
  deployment

4.1 Devstack-install
--------------------
For integrating Congress with DevStack:

1. Download DevStack

.. code-block:: console

    $ git clone https://git.openstack.org/openstack-dev/devstack.git
    $ cd devstack

2. Configure DevStack to use Congress and any other service you want.  To do that, modify
   the ``local.conf`` file (inside the DevStack directory).  Here is what
   our file looks like:

.. code-block:: console

    [[local|localrc]]

    enable_plugin congress http://git.openstack.org/openstack/congress
    enable_plugin ceilometer http://git.openstack.org/openstack/ceilometer
    enable_service h-eng h-api h-api-cfn h-api-cw
    disable_service n-net
    enable_service neutron
    enable_service q-svc
    enable_service q-agt
    enable_service q-dhcp
    enable_service q-l3
    enable_service q-meta
    enable_service s-proxy s-object s-container s-account

3. Run ``stack.sh``.  The default configuration expects the passwords to be 'password'
   without the quotes

.. code-block:: console

    $ ./stack.sh


4.2 Separate install
--------------------
Install the following software, if you haven't already.

* python 2.7: https://www.python.org/download/releases/2.7/

* pip: https://pip.pypa.io/en/latest/installing.html

* java: http://java.com  (any reasonably current version should work)
  On Ubuntu:   console apt-get install default-jre

* Additionally

.. code-block:: console

  $ sudo apt-get install git gcc python-dev libxml2 libxslt1-dev libzip-dev mysql-server python-mysqldb build-essential libssl-dev libffi-dev

Clone Congress

.. code-block:: console

  $ git clone https://github.com/openstack/congress.git
  $ cd congress

Install requirements

.. code-block:: console

 $ sudo pip install .

Install Source code

.. code-block:: console

  $ sudo python setup.py install

Configure Congress  (Assume you put config files in /etc/congress)

.. code-block:: console

  $ sudo mkdir -p /etc/congress
  $ sudo mkdir -p /etc/congress/snapshot
  $ sudo cp etc/api-paste.ini /etc/congress
  $ sudo cp etc/policy.json /etc/congress
  $ sudo touch /etc/congress/congress.conf


Add drivers in /etc/congress/congress.conf [DEFAULT] section:

.. code-block:: text

  drivers = congress.datasources.neutronv2_driver.NeutronV2Driver,congress.datasources.glancev2_driver.GlanceV2Driver,congress.datasources.nova_driver.NovaDriver,congress.datasources.keystone_driver.KeystoneDriver,congress.datasources.ceilometer_driver.CeilometerDriver,congress.datasources.cinder_driver.CinderDriver,congress.datasources.swift_driver.SwiftDriver,congress.datasources.plexxi_driver.PlexxiDriver,congress.datasources.vCenter_driver.VCenterDriver,congress.datasources.murano_driver.MuranoDriver,congress.datasources.ironic_driver.IronicDriver


Modify [keystone_authtoken] and [database] according to your environment.

For setting Congress with "noauth":
Add the following line to [DEFAULT] section in /etc/congress/congress.conf

.. code-block:: text

    auth_strategy = noauth

Also, might want to delete/comment [keystone_authtoken] section in
 /etc/congress/congress.conf

To use RabbitMQ with Congress,
Set the transport_url in [DEFAULT] section in /etc/congress/congress.conf according to your setup.

.. code-block:: text

    transport_url = rabbit://$RABBIT_USERID:$RABBIT_PASSWORD@$RABBIT_HOST:5672

A bare-bones congress.conf is as follows (adapt MySQL root password):

.. code-block:: text

  [DEFAULT]
  drivers = congress.datasources.neutronv2_driver.NeutronV2Driver,congress.datasources.glancev2_driver.GlanceV2Driver,congress.datasources.nova_driver.NovaDriver,congress.datasources.keystone_driver.KeystoneDriver,congress.datasources.ceilometer_driver.CeilometerDriver,congress.datasources.cinder_driver.CinderDriver,congress.datasources.swift_driver.SwiftDriver,congress.datasources.plexxi_driver.PlexxiDriver,congress.datasources.vCenter_driver.VCenterDriver,congress.datasources.murano_driver.MuranoDriver,congress.datasources.ironic_driver.IronicDriver
  auth_strategy = noauth
  [database]
  connection = mysql+pymysql://root:password@127.0.0.1/congress?charset=utf8

For a detailed sample, please follow README-congress.conf.txt

Create database

.. code-block:: console

  $ mysql -u root -p
  $ mysql> CREATE DATABASE congress;
  $ mysql> GRANT ALL PRIVILEGES ON congress.* TO 'congress'@'localhost' IDENTIFIED BY 'CONGRESS_DBPASS';
  $ mysql> GRANT ALL PRIVILEGES ON congress.* TO 'congress'@'%' IDENTIFIED BY 'CONGRESS_DBPASS';


Configure congress.conf with db information.

Push down schema

.. code-block:: console

  $ sudo congress-db-manage --config-file /etc/congress/congress.conf upgrade head

Set up Congress accounts
  Use your OpenStack RC file to set and export required environment variables:
  OS_USERNAME, OS_PASSWORD, OS_PROJECT_NAME, OS_TENANT_NAME, OS_AUTH_URL.

  (Adapt parameters according to your environment)

.. code-block:: console

  $ ADMIN_ROLE=$(openstack role list | awk "/ admin / { print \$2 }")
  $ SERVICE_TENANT=$(openstack project list | awk "/ admin / { print \$2 }")
  $ CONGRESS_USER=$(openstack user create --password password --project admin --email "congress@example.com" congress | awk "/ id / {print \$4 }")
  $ openstack role add $ADMIN_ROLE --user $CONGRESS_USER --project  $SERVICE_TENANT
  $ CONGRESS_SERVICE=$(openstack service create congress --name "policy" --description "Congress Service" | awk "/ id / { print \$4 }")
  $ openstack endpoint create $CONGRESS_SERVICE --region RegionOne --publicurl http://127.0.0.1:1789/  --adminurl http://127.0.0.1:1789/ --internalurl http://127.0.0.1:1789/

Start Congress
  The default behavior is to start the Congress API, Policy Engine, and
  Datasource in a single node. For HAHT deployment options, please see the
  :ref:`HA Overview <ha_overview>` document.

.. code-block:: console

  $ sudo /usr/local/bin/congress-server --debug

Configure datasource drivers
  First make sure you have the Congress client (project python-congressclient)
  installed. Run this command for every service that Congress will poll for
  data. Please note that the service name $SERVICE should match the ID of the
  datasource driver, e.g. "neutronv2" for Neutron and "glancev2" for Glance;
  $OS_USERNAME, $OS_TENANT_NAME, $OS_PASSWORD and $SERVICE_HOST are used to
  configure the realted datasource driver so that congress knows how to
  talk with the service.

.. code-block:: console

  $ openstack congress datasource create $SERVICE "$SERVICE" --config username=$OS_USERNAME --config tenant_name=$OS_TENANT_NAME --config password=$OS_PASSWORD --config auth_url=http://$SERVICE_HOST:5000/v2.0


Install test harness

.. code-block:: console

  $ sudo pip install 'tox<1.7'

Run unit tests

.. code-block:: console

  $ tox -epy27

Read the HTML documentation
  Install python-sphinx and the oslosphinx extension if missing.

.. code-block:: console

  $ sudo pip install sphinx
  $ sudo pip install oslosphinx

  Build the docs

.. code-block:: console

  $ make docs

  Open doc/html/index.html in a browser

4.3 Debugging unit tests
------------------------

In order to break into the debugger from a unit test we need to insert
a breaking point to the code:

.. code-block:: python

  import pdb; pdb.set_trace()

Then run ``tox`` with the debug environment as one of the following::

  tox -e debug
  tox -e debug test_file_name.TestClass.test_name

For more information see the `oslotest documentation
<http://docs.openstack.org/developer/oslotest/features.html#debugging-with-oslo-debug-helper>`_.

4.4 Upgrade
-----------

Here are the instructions for upgrading to a new release of the
Congress server.

1. Stop the Congress server.

2. Update the Congress git repo

.. code-block:: console

  $ cd /path/to/congress
  $ git fetch origin

3. Checkout the release you are interested in, say Mitaka.  Note that this
step will not succeed if you have any uncommitted changes in the repo.

.. code-block:: console

  $ git checkout origin/stable/mitaka


If you have changes committed locally that are not merged into the public
repository, you now need to cherry-pick those changes onto the new
branch.

4. Install dependencies

.. code-block:: console

 $ sudo pip install

5. Install source code

.. code-block:: console

  $ sudo python setup.py install

6. Migrate the database schema

.. code-block:: console

  $ sudo congress-db-manage --config-file /etc/congress/congress.conf upgrade head

7. (optional) Check if the configuration options you are currently using are
   still supported and whether there are any new configuration options you
   would like to use.  To see the current list of configuration options,
   use the following command, which will create a sample configuration file
   in ``etc/congress.conf.sample`` for you to examine.

.. code-block:: console

   $ tox -egenconfig

8. Restart Congress, e.g.

.. code-block:: console

  $ sudo /usr/local/bin/congress-server --debug
