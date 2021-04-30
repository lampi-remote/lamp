# Assignment

The assignment is to complete the Django HTTP Backend for the Mosquitto Auth Plugin.  There are two parts: Authentication and Authorization (ACL).

By the end of this assignment, you should have a Lampi and a web client communicating with your EC2 instance using Django as the point of authority for granting access to topics to users that belong to them.

You will need a new Django application that is served by your existing Django project to manage authentication as well as ACL access, completing the views we have provided as a starting point.

## Deployment

During development, use the Django development server with:

```bash
$cloud ./manage.py runserver 0.0.0.0:8080
```

When complete, though, modify the NGINX Configuration ```/etc/nginx/sites-available/lampisite.conf``` so that your Django application is served with the current configuration (HTTPS SSL/TLS on 443, etc.), but also served with plain HTTP on port 8080 without SSL/TLS, **and** that only clients on localhost can access it (see [NGINX allow/deny](http://nginx.org/en/docs/http/ngx_http_access_module.html) _allow_ and _deny_ directives).

Also, be sure for final deployment that `mosquitto` is configured to use port 8080 for all auth plugin requests.

### Authentication

You will need to authenticate Django users with Username/password (e.g., `mqtt-daemon`) as well as Django users via websockets ('device_id' as username and Django 'session_key' as password).

You should create a new Django superuser account named `mqtt-daemon` for use by `mqtt-daemon` and the Lampi Add form, and modify the Paho code to use that username/password combination.

### ACL Validation

You will need to provide authorization (ACL) for these types of "users":

1. LAMPI device bridges (with 'username'=='clientid' of the form `b827eb08451e_broker`)
1. Django Users (which will already have been authenticated)
1. Django Users that are Django superusers (which should have all access rights)
1. Django Users via WebSockets

LAMPI device bridges should only be able to access topics related to the device itself.

Users (other than superusers) should only be able to access topics related to their devices.

Sample Topics that you need to provide appropriate access control for:

| Sample Topics |
|--------------|
| /devices/b827eb08451e/lamp/associated |
| /devices/b827eb08451e/lamp/connection/lamp_service/state |
| /devices/b827eb08451e/lamp/connection/lamp_ui/state |
| /devices/b827eb08451e/lamp/connection/lamp\_bt\_peripheral/state |
| /devices/b827eb08451e/lamp/changed |
| /devices/b827eb08451e/lamp/set_config |
| /devices/b827eb08451e/lamp/bluetooth |
| $SYS/broker/connection/b827eb08451e_broker/state |

(the device_id of 'b827eb08451e' is just for illustration purposes).

The "$SYS/broker/connection/b827eb08451e_broker/state" is a special topic that the bridge itself maintains.

The Python Paho [topic\_matches\_sub()](http://www.eclipse.org/paho/clients/python/docs/#global-helper-functions) function can be handy to test whether a topic that access is requested for matches a topic string that should be accessible to that user.  You might consider dynamically generating strings like `"/devices/{}/lamp/changed".format(device_id)`.  Or, maybe dynamically generated lists of such topic strings.

The "direction" - Write (Publish) or Read (Subscribe) is encoded in the HTTP request as  "1" for Read and "2" for Write (just a convention of the Mosquitto Auth Plugin).  There are two constants in the file already for you:

```python
ACL_SUB = "1" # READ
ACL_PUB = "2" # WRITE
```
**REMEMBER:** Device bridges require asymmetric privileges (mirror-images) if a User can Read (Subscribe) to a topic, the Device must be able to Write (publish) to that topic.  For example, "/devices/b827eb08451e/lamp/changed" is Written (published) by the device bridge, and the User needs to be able to Read (Subscribe) to that topic to get state updates, while "/devices/b827eb08451e/lamp/set_config" needs to be Written (Published) by the User, and Read (Subscribed) by the device bridge (so that it can re-publish any updates from EC2 on that topic "down" to the broker on the device.

Other than superusers, access should be as limited as feasible.  That is, if a particular user would have no legitimate reason to Read a topic, they should be denied that access (and equivalently, Write access). 

## What to Turn in

You need to turn in the following:

1. A short (a few sentences) write up from each member of the pair summarizing what they learned completing the assignment, and one thing that surprised them (good, bad, or just surprising).  This should in **connected-devices/writeup.md** in [Markdown](https://daringfireball.net/projects/markdown/) format.  You can find a template file in **connected-devices/template\_writeup.md**
2. A Git Pull Request
3. A short video demonstrating the required behaviors emailed to the instructor and TA.  The video should be named **[assignment 3]_[LAST_NAME_1]\_[LAST_NAME_2].[video format]**.  So, for this assignment, if your pair's last names are "Smith" and "Jones" and you record a .MOV, you would email a file named ```2_smith_jones.mov``` to the instructor.
4. A live demo at the beginning of the next class - **be prepared!**

&copy; 2015-2021 LeanDog, Inc. and Nick Barendt
