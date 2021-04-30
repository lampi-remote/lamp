# Remote Updates

Depending on the system, there are lots of different remote update techniques available.  We will be using one consistent with our system - since Raspbian is a Debian based Linux distribution, we will use the Debian package infrastructure.

You have been using Debian's system (and Ubuntu's, which is built on Debian) all semester, with the `sudo apt-get update` and `sudo apt-get install PACKAGE_NAME` to update your local package database and install a particular package, respectively.

There are two separate things going on here:

1. managing the package database (querying source repositories for their package index information) 
1. downloading and installing those packages

The packages we are referring to are [Debian packages](https://wiki.debian.org/Packaging#What_is_a_.22package.22.3F).  A Debian Package is archive files with a specific format.  The archive contents for a package include:

* metadata about the package contents, versions, etc.
* scripts to be run before installing, after installing, before removing, after removing, etc.
* the actual files (binary executables, libraries, /etc configuration files, etc.)

Debian packages that are manged by the Debian repositories are typically built from source code.

This chapter will focus on creating a [debian package](https://wiki.debian.org/RepositoryFormat) for our LAMPI software and automating the update process.  First, though, we need to create a package repository to host our packages. 

# Creating an Apt Repository

We're going to create a Debian package repository using [reprepro](https://wiki.debian.org/DebianRepository/SetupWithReprepro). We will host this on the same EC2 instance as our Django server and route it through NGINX, which is already up and running to serve our Django app.

### Creating Keys

Reprepro uses [GPG](https://www.gnupg.org) keys for security (e.g., code signing), so we'll start by making keys. GPG uses [system entropy](https://en.wikipedia.org/wiki/Entropy_%28computing%29#Linux_kernel) to generate secure keys. Unfortunately we won't have enough entropy on our EC2 server -- there's no mouse and keyboard data and not nearly enough disk activity to fill the pool (here is a good [introduction to Linux's entropy pool](https://hackaday.com/2017/11/02/what-is-entropy-and-how-do-i-get-more-of-it/)). 

So, as a workaround, we're going to use [rng-tools](https://www.gnu.org/software/hurd/user/tlecarrour/rng-tools.html) to generate entropy. Note that **this is a poor workaround** and will not produce cryptographically secure keys. In a production system we should generate entropy using a [hardware RNG](https://en.wikipedia.org/wiki/Hardware_random_number_generator) or by generating the keys on a local machine with keyboard and mouse activity and transferring them to our server.

```bash
cloud$ sudo apt-get install rng-tools
cloud$ sudo rngd -r /dev/urandom
```

Now we're going to configure options for how GPG keys are generated. 

We need to make our **~/.gnupg** directory and limit permissions:

```bash
cloud$ mkdir -p ~/.gnupg
cloud$ chmod og-rwx ~/.gnupg
```

Edit **~/.gnupg/gpg.conf** so that it contains the following:

```
personal-digest-preferences SHA256
cert-digest-algo SHA256
default-preference-list SHA512 SHA384 SHA256 SHA224 AES256 AES192 AES CAST5 ZLIB BZIP2 ZIP Uncompressed
```

Finally, generate the keys:

```bash
cloud$  gpg --full-generate-key
```

It will ask you several questions. Answer:

* Kind of key: (1) RSA and RSA
* Length: 4096
* Expiry: 0 (key does not expire, confirm)
* Enter name and email, NO COMMENT
* Enter a passphrase and confirm. You'll need to enter this passphrase when you submit a new package to the repo.

Now go ahead and list your keys:

```bash
cloud$ gpg --list-keys --keyid-format=short
```

You should get some sort of output like this:

```
-------------------------------
pub   rsa4096/3E759EB7 2019-03-25 [SCEA]
      7C7B2DBF7C7A5C688C6ED12ED367304D3E759EB7
uid         [ultimate] fname lname <you@something.com>
sub   rsa4096/8F78BAB9 2019-03-25 [SEA]
```

Write down the value for the subkey (after "sub"), specifically the value after the **rsa4096/**. In the example above, it would be **8F78BAB9**. You'll need this in a moment.

Publish the key to keyserver.ubuntu.com so we can access it later on our lamp. Replace {{SUB_KEY}} with the key value you just noted (8F78BAB9, in the example above).

```bash
gpg --keyserver keyserver.ubuntu.com --send-key {{SUB_KEY}}
```

### Create repository

Install reprepro:

```bash
cloud$ sudo apt-get install -y reprepro
```

Create a directory structure for your Debian repo, then ensure your user is the owner of the directory structure:

```bash
cloud$ sudo mkdir -p ~/connected-devices/Web/reprepro/ubuntu/{conf,dists,incoming,indices,logs,pool,project,tmp}
cloud$ cd ~/connected-devices/Web/reprepro/ubuntu/
cloud$ sudo chown -R `whoami` .
```

Now edit **~/connected-devices/Web/reprepro/ubuntu/conf/distributions** in your editor of choice. Replace the following values:

* {{FULL_NAME}} - Your full name (e.g., Jane Doe)
* {{REPO_NAME}} - Repo full name (e.g., Jane's Debian Repo)
* {{REPO_SHORT_NAME}} - Single lower case word used to refer to repository (e.g., jane)
* {{SUB_KEY}} - Key you wrote down in earlier (e.g., 8F78BAB9)

```
Origin: {{FULL_NAME}}
Label: {{REPO_NAME}}
Codename: {{REPO_SHORT_NAME}}
Architectures: armhf armel
Suite: stable
Components: main non-free contrib
Description: Local Debian repository
SignWith: {{SUB_KEY}}
```

That should be enough to run your package server, although it's not exposed to the internet yet.

Next up: [11.2 Building a Deb Package](../11.2_Building_a_Deb_Package/README.md)

&copy; 2015-2021 LeanDog, Inc. and Nick Barendt
