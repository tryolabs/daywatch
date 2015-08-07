*****
Setup
*****

DayWatch uses Vagrant to provide an isolated, virtual machine for development
and Ansible for orchestration of both development and production servers. This
provides a completely reproducible environment for all developers, and allows
testing of everything all the way up to deployment on local virtual servers.

Getting Started
===============

Setup
-----

Vagrant version 2 can probably be installed without a problem from your
operating system's package manager, however, Ansible should probably be
installed with pip. For the latter, we recommend creating a virtual environment
using virtualenvwrapper to isolate the Ansible version.

After you have Vagrant and Ansible, do the following to spin up and provision
the VM:

::

   vagrant up
   cd daywatch/deploy
   ansible-galaxy install bobbyrenwick.pip

Finally, this command will provision the virtual machine:

::

   ./run.sh configure

Configuration
-------------

When provisioning is done, you have to create an admin user:

::

   vagrant ssh
   ./manage.py createsuperuser

You'll then have to answer some questions. For testing, you'll probably want
something like :code:`admin` and :code:`admin` for the password.

Now navigate to :code:`localhost:8080`. Sign in with your super user account,
and you're in.

If you click around the panels you'll find there's not much to do, since your
user has no permissions. To give yourself access, navigate to the Django admin,
go to :code:`Users`, click on the :code:`admin` user, and scroll to the bottom
of the page. You will find settings for user permissions:

.. image:: img/user-permissions.png

These allow you to control who can access the different aspects of functionality
and which countries they have access to.

Deploying to Production
=======================

Ansible's :code:`hosts.txt` looks like this:

::

  vagrant         ansible_ssh_host=192.168.45.10 ansible_ssh_user=vagrant

  [enabled]
  vagrant

To add a new host -- say, for a production server -- add a line under
Vagrant. For instance:

::

   prod            ansible_ssh_host=my-ec2-instance.compute.amazonaws.com ansible_ssh_user=ubuntu

Then, add :code:`prod` under :code:`enabled` to execute all deployment actions
on the :code:`prod` server.
