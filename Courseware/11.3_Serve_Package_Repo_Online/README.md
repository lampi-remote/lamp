# Serve Package Repo Online

Let's build an nginx configuration to allow access to our package repo. Port 80 is used by more important things, so we'll serve our repo **on port 8090**.

First, open port 8090 for incoming requests at [console.aws.amazon.com](https://console.aws.amazon.com).  **DO NOT FORGET TO DO THIS!**

Next, let's build a nginx configuration in **/etc/nginx/sites-available/{{name}}-apt.conf**, replacing name with the short name of your repo. In the file, replace {{FQDN}} with the FQDN of your server (available on [console.aws.amazon.com](https://console.aws.amazon.com)).

```
server {
  listen 8090;
  server_name {{FQDN}};

  access_log /var/log/nginx/packages-access.log;
  error_log /var/log/nginx/packages-error.log;

  location / {
    root /home/ubuntu/connected-devices/Web/reprepro;
    index index.html;
  }

  location ~ /(.*)/conf {
    deny all;
  }

  location ~ /(.*)/db {
    deny all;
  }
}
```

Now the configuration is in sites-available, and we'll symlink it into sites-enabled so it will actually be run:

```bash
cloud$ cd /etc/nginx/sites-enabled
cloud$ sudo ln -s ../sites-available/{{name}}-apt.conf .
cloud$ sudo service nginx reload
```

You should be all set to access the package server externally.


## Install the package

Next we'll install the package repo on your lamp, then the package itself. 

### Install package needed for `gpg`

We need to install a packaged required to work with GPG keys:

```bash
lamp$ sudo apt-get install dirmngr
```

### Adding the Repository

Next, let's get the public key for our apt server that we sent to the keyserver in the first part of this chapter. Remote into the lamp and run the following, replacing {{SUB_KEY}} with the value you wrote down in the first part of this chapter:

```bash
lamp$ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys {{SUB_KEY}}
```

Next let's add your repo, update, then install our package. Replace {{FQDN}} with your server's FQDN and {{REPO\_SHORT\_NAME}} with the repo short name used earlier.

Create a new file **/etc/apt/sources.list.d/lampi.list** with the following contents as a superuser:

```
deb http://{{FQDN}}:8090/ubuntu/ {{REPO_SHORT_NAME}} main
```

### Update the Apt Cache Repository and Install the **hi** Package

```bash
lamp$ sudo apt-get update
lamp$ sudo apt-get install -y hi
```

Run the `hi` command. It's not on your path, so just run it directly out of **/opt/hi**:

```bash
lamp$ /opt/hi/hi

Hello, Deb! Version 0.1
```

You have just installed your custom package!  

Next up: [11.4 Automating Deployment](../11.4_Automating_Deployment/README.md)

&copy; 2015-2021 LeanDog, Inc. and Nick Barendt
