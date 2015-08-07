# DayWatch Platform

## Getting Started

We have included a Vagrant virtual machine definition and Ansible playbooks to
create a reproducible development environment. All you need is Vagrant and
Ansible.

Vagrant version 2 can be installed without a problem from your
operating system's package manager, however, Ansible should probably be
installed with pip. For the latter, we recommend creating a virtual environment
using virtualenvwrapper to isolate the Ansible version.

After you have Vagrant and Ansible, do the following to spin up and provision
the VM:

```bash
vagrant up
cd daywatch/deploy
ansible-galaxy install bobbyrenwick.pip
./run.sh configure
```

## To-Do

Wanted:

- [ ] XLS Export
- [ ] More advanced search, for example, prices within a range, or that a
  certain field meets a certain condition. This is typical of vertical search
  engines
