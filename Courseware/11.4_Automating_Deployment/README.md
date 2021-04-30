# Automating Deployment

Everytime we change our `hi` package, there are several things we need to do. We need to increment the version number, create the package, and finally upload it to our package repo. Let's script these so we don't have to run the commands each time. Our package and deployment script will act as living documentation of the process we need to follow each time the package is updated, so future maintainers of your project don't need to start from scratch.


### Incrementing version number

First let's get our auto-versioning set up. We'll use a python module called [bumpv2ersion](https://pypi.python.org/pypi/bumpv2ersion/) to accomplish this. Remote into your EC2 instance and install:

```bash
cloud$ sudo pip3 install bump2version
```

FWIW, the original `bumpversion` package has not been maintained, so another team forked it and renamed it.  Fortunately, `bump2version` can be invoked as `bumpversion` or `bump2version` interchangeably.

Now we'll make a configuration file for bump2version. Create and edit a file called **~/connected-devices/Lampi/pkg/.bumpversion.cfg** with the following contents:

```
[bumpversion]
current_version = 0.1
commit = False
tag = False
parse = (?P<major>\d+)\.(?P<minor>\d+)
serialize = {major}.{minor}

[bumpversion:file:hi/DEBIAN/control]
search = Version: {current_version}
replace = Version: {new_version}

[bumpversion:file:hi/opt/hi/__VERSION__]
search = {current_version}
replace = {new_version}
```

Save and exit your editor. Let's do a dry run and make sure our script is working when we bump the minor part of the version number:

```bash
cloud$ cd ~/connected-devices/Lampi/pkg/
cloud$ bumpversion minor --dry-run --verbose
```

**NOTE: if you receive a `bumpversion.WorkingDirectoryIsDirtyException` error, because you have uncommitted changes in Git, append the `--allow-dirty` command-line option.**

You should see the control file getting it's version number changed to **0.2**:

```
Asserting files hi/DEBIAN/control contain the version string:
Found 'Version: 0.1' in hi/DEBIAN/control at line 5: Version: 0.1
Would change file hi/DEBIAN/control:
--- a/hi/DEBIAN/control
+++ b/hi/DEBIAN/control
@@ -3,6 +3,6 @@
 Maintainer: Gary Johnson
 Depends: python, python-dev, python-pip
 Priority: optional
-Version: 0.1
+Version: 0.2
 Description: Hello, Deb!
 Section: misc
```

Now let's write a script to run this, as well as our package and deployment. Create a new file called **~/connected-devices/Lampi/pkg/deploy\_new\_version.sh** with the following contents. Don't forget to replace {{REPO\_SHORT\_NAME}}:

```bash
#!/bin/bash

cd ~/connected-devices/Lampi/pkg/
bumpversion minor
dpkg-deb --build hi
reprepro -b ~/connected-devices/Web/reprepro/ubuntu/ includedeb {{REPO_SHORT_NAME}} hi.deb
```

Note that these are all commands we've run earlier, just collected in a single script for easy reuse. Save and exit your editor. Mark the script as executable:

```bash
cloud$ cd ~/connected-devices/Lampi/pkg/
cloud$ chmod a+x deploy_new_version.sh
```

Let's change our app before we deploy a new version. Edit **~/connected-devices/Lampi/pkg/hi/opt/hi/hi**:

```bash
#!/usr/bin/env python

import os

version = 'Unknown'
version_path = os.path.join(os.path.dirname(__file__), '__VERSION__')
with open(version_path, 'r') as version_file:
  version = version_file.read()

print('Hello Updated Deb! Version {}'.format(version))
```

Save, quit, and run our script:

```bash
cloud$ ./deploy_new_version.sh
```

**NOTE:** as your deployment script becomes more sophisticated (e.g., for the assignment) you might need to use `sudo` - most sudo implementations change the `$HOME` shell variable to `/root` which might result in your GPG keys not being found.

You'll be prompted for your password to upload to your package server. Enter that in, and then run ls on the `hi` package. 

```bash
cloud$ reprepro -b ~/connected-devices/Web/reprepro/ubuntu/ ls hi 
```

You should see a new version:

```
hi | 0.2 | my_repo | armhf, armel
```

Finally, log into your lamp, update and install `hi`, and run the script. You should see the new output:

```bash
lamp$ sudo apt-get update
lamp$ sudo apt-get install hi
lamp$ /opt/hi/hi

Hello, Updated Deb! Version 0.2
```

Now we have a build process we can reuse every time the code changes with minimal effort.

Next up: [11.5 Assignment](../11.5_Assignment/README.md)

&copy; 2015-2021 LeanDog, Inc. and Nick Barendt
