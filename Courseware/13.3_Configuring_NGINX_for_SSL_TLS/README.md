# Serving Django from NGINX

Next we need to secure our web client, and switch from HTTP to HTTPS.

## Troubleshooting

If you have trouble with the configuration, you can observe the NGINX logs:

```bash
sudo tail /var/log/nginx/error.log
```

or

```bash
sudo tail -f /var/log/nginx/error.log
```

to see updates to the log as they are appended to the file in real time.

Most errors at this point are likely to be configuration-based, so double-check those **.conf** files!

## Configure TLS

First we are going to open up a port for testing. Navigate to **console.aws.amazon.com**, click on **EC2**, click on **Security Groups**, and add an inbound rule to allow access to TCP port **443**, the standard port for HTTPS. While you're in there, remove access to port 8080 and any other unneeded ports. At this point, we're done with unencrypted HTTP (a real prooduction site would probably allow limited HTTP connections to port 80, with an automatic redirect to HTTPS on port 443).

Navigate to your NGINX sites-available directory and edit **lampisite.conf**. Change the listen port to 443 and add the needed settings for ssl:

```
# configuration of the server
server {

    # the port your site will be served on
    listen 443 ssl;
    ssl_certificate /home/ubuntu/ssl_keys/lampi_server.crt;
    ssl_certificate_key /home/ubuntu/ssl_keys/lampi_server.key;
    ssl_protocols TLSv1.2;

    # the domain name it will serve for
    server_name ec2-52-20-29-213.compute-1.amazonaws.com; # CHANGE to match your machine's FQDN
    charset     utf-8;
```

Install the Certificates and Private Keys in the directories specified.

**NOTE:** just as we would never deploy production code in a user home directory, we would never store cryptographic keys, certificates, etc. there.  Doing so simplifies the class work, though.

Restart uWSGI again and restart NGINX:

```bash
cloud$ sudo supervisorctl restart uwsgi
cloud$ sudo service nginx restart
```

Now on your host machine navigate to `https://{server_fqdn}` (note the **https**) to see the default page. You should be notified in some way that the page isn't trusted, or the certificate isn't verified, or something along these lines. Bypass this warning if possible to see your Django page.

We got those warnings because we are acting as our own Certificate Authority, the certs we sign are not trusted by default. There are many CAs that are trusted by default on modern systems (of which VeriSign is an example). For basic needs like serving web pages, most of the time you'll find yourself buying a cert from one of those CAs. For specialized needs such as the communication between devices such as our LAMPIs and the server, acting as a Certificate Authority provides some additional control that may be desired or needed.

Let's configure our browsers to trust our CA on our computer so we can connect to the website without any errors or warnings.
 
You'll need to install our CA Root Certificate as a trusted root:

- [Windows](http://www.thewindowsclub.com/manage-trusted-root-certificates-windows)
- [OSX Add certficates to Keychain](https://support.apple.com/kb/PH25443?locale=en_US&viewlocale=en_US) and [OSX Change Trust Settings](https://support.apple.com/guide/keychain-access/change-the-trust-settings-of-a-certificate-kyca11871/mac)
- [FireFox Specific](https://support.mozilla.org/en-US/kb/setting-certificate-authorities-firefox)
- For \*nix systems, search for instructions related to the browser and distribution you are using.

> **COMPATIBILITY:** There seems to be a FireFox issue with Secure Web Sockets and MQTT WebSockets - if you run into issues with FireFox where the page loads, but the LAMPI UI Screen is not connecting to the Mosquitto Broker Websockets interface, please see [this](https://support.mozilla.org/en-US/questions/1324001)

Navigate back to `https://{server_fqdn}`. It should load with no certificate warnings / trust issues. 

**NOTE: It is important to have this working, as websockets will not work at all unless the certificate is trusted by your browser.**

Next up: go to [13.4 Assignment](../13.4_Assignment/README.md)

&copy; 2015-2021 LeanDog, Inc. and Nick Barendt
