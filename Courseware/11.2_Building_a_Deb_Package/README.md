# Building a Deb Package

Before we expose our package repo to the internet, let's build and upload a [debian package](https://www.debian.org/doc/manuals/debian-faq/ch-pkg_basics.en.html) to our repository and make sure everything is working okay.

### Create folder structure

First we need an executable to package. We're going to make a package called "hi" that contains an executable also called "hi". Let's make a directory to build our deb package in:

```bash
cloud$ mkdir -p ~/connected-devices/Lampi/pkg/hi/{DEBIAN,opt/hi}
cloud$ cd ~/connected-devices/Lampi/pkg/hi/
```

Viewed in `tree` (you can install it through apt-get if you want), this folder structure should look like so:

```
pkg
├── hi
│   ├── DEBIAN
│   └── opt
│       └── hi
```

The **~/connected-devices/Lampi/pkg/hi** is the directory that holds everything we want to package. 

* **DEBIAN** is a special folder that contains all the configuration & metadata for the debian package
* Everything else in **~/connected-devices/Lampi/pkg/hi** will be installed in the root of the system. So **~/connected-devices/Lampi/pkg/hi/opt/hi** will install into **/opt/hi** on the system in which it is installed. If we wanted to install some supervisor scripts with our package, we could make a **~/connected-devices/Lampi/pkg/hi/etc/supervisor/conf.d/** directory and files in it would install into **/etc/supervisor/conf.d**, for example.


### Create an Executable

Now let's build an executable to package. When the package is installed, we want the executable to be installed in **/opt/hi/** so create it as **~/connected-devices/Lampi/pkg/hi/opt/hi/hi**

> If you're wondering why we're putting this executable in /opt/, refer here for more info on the folder structure of a Linux system: [http://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch03s13.html](http://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch03s13.html)

```python
#!/usr/bin/env python3

import os

version = 'Unknown'
version_path = os.path.join(os.path.dirname(__file__), '__VERSION__')
with open(version_path, 'r') as version_file:
  version = version_file.read()

print('Hello Deb! Version {}'.format(version))
```

Let's create a file to hold the version of our program. Create **~/connected-devices/Lampi/pkg/hi/opt/hi/\_\_VERSION\_\_** with the following contents (no whitespace, no newline):

```
0.1
```

Save and close both files, mark hi as executable, then run it:

```bash
cloud$ cd ~/connected-devices/Lampi/pkg/hi/opt/hi/
cloud$ sudo chmod a+x hi
cloud$ ./hi

Hello Deb! Version 0.1
```

### Create package metadata

Now let's build a [control file](http://packaging.ubuntu.com/html/debian-dir-overview.html#the-control-file) to describe our package. 

Create a file at **~/connected-devices/Lampi/pkg/hi/DEBIAN/control**, replacing {{YOUR_NAME}} with your name:

```
Package: hi
Architecture: all
Maintainer: {{YOUR_NAME}}
Depends: python3, python3-dev, python3-pip
Priority: optional
Version: 0.1
Description: Hello, Deb!
Section: misc
```

Note that these metadata files are whitespace sensitive and do not allow additional empty lines so be careful while editing.

Finally, we need to fix file ownership and make root the owner of the entire directory structure. The permissions of the files in this directory will travel with the package, so if we don't do this the files will be installed with incorrect ownership.

```bash
cloud$ sudo chown -R root:root ~/connected-devices/Lampi/pkg/hi/
```

Note that after you do this, further edits to files in this directory will require `sudo`.

This should be all we need to build our deb package, so let's go:

```bash
cloud$ cd ~/connected-devices/Lampi/pkg/
cloud$ dpkg-deb --build hi
```

You should now have a **hi.deb** in **~/connected-devices/Lampi/pkg/**. Let's upload this to our package repo on the same machine. Note that we use **-b** to provide the path to the repo. Note also that you need to replace {{REPO_SHORT_NAME}} with whatever you specified in the previous section for a short name:

```bash
cloud$ reprepro -b ~/connected-devices/Web/reprepro/ubuntu/ includedeb {{REPO_SHORT_NAME}} hi.deb
```

You will be prompted for the passphrase you made when you generated your key in the previous section.

Once that is done, ask the package repo to list all packages for `hi`. You should get a single listing for the 0.1 version of hi you just uploaded:

```bash
reprepro -b ~/connected-devices/Web//reprepro/ubuntu/ ls hi

hi | 0.1 | gary | armhf, armel
```

Okay! Now we need to expose the package repo to the internet so we can install the package on a machine using the repo.

Next up: [11.3 Serve Package Repo Online](../11.3_Serve_Package_Repo_Online/README.md)

&copy; 2015-2021 LeanDog, Inc. and Nick Barendt
