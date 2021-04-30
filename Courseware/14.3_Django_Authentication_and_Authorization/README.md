# Django Authentication and Authorization (ACL)

Our HTTP Backend for the Mosquitto Auth Plugin will use information we have about the devices, and [Django's User Authentication and Authorization system](https://docs.djangoproject.com/en/2.1/topics/auth/).

## Authentication

Our LAMPI devices use SSL/TLS Certificates to authenticate, but we do not have any authentication in place yet.

As a refresher, we support the following MQTT listeners:

| Port | Address | Protocol | SSL/TLS? | Authentication |
| ---- | ------- | -------- | -------- | -------------- |
| 1883 | 127.0.0.1 |  mqtt  | NO       | Username/Password |
| 8883 | 0.0.0.0 | mqtt     | YES      | SSL/TLS Certificate |
| 50002 | 0.0.0.0 | websockets/mqtt | YES | Username/Password |

We need to impose Username/Password Authentication on port 1883 for local connections (e.g., `mqtt-daemon` and related Django Device Association code), and on Websockets.

### Non-Websocket Clients

For non-websockets clients, we will authenticate against Django's User model.  See [authenticate](https://docs.djangoproject.com/en/2.1/topics/auth/default/#django.contrib.auth.authenticate).

### WebSockets Clients

Django relies on the **Session** contribution to manage authenticated sessions for a user.   When a user is authenticated a cookie is set with a long, random character string that can identify a user on the backend.   This session has a life expectency and can be used to fetch a user when it is active (Django middleware takes care of most of this for you, so you have not had to deal with it directly so far).

We can use this to authenticate over websockets, without the need to pass the user's username or password in the HTTP/websockets requests (which would be annonying and kludgey).

The Django view and **lampi.js** files in the repository have been updated to pass:

* 'device\_id' as the username
* Djange 'session\_key' as the password

We will be able to look this User object up within the Django auth infrastructure using the Session object's session\_id to perform **acl** or **auth** requests.

Here is a function to get a Django User object given a session\_key:

```python
def get_user_from_session_key(session_key):
    session = Session.objects.get(session_key=session_key)
    uid = session.get_decoded().get('_auth_user_id')
    return User.objects.get(pk=uid)
```

## Authorization (ACL)

Devices need to be able to Read/Write to their relevant MQTT Topics (and only theirs).

Django users connected on port 1883 (e.g., `mqtt-daemon`) will generally need to have full-access (all devices).  That's equivalent to a _superuser_ so we can us the Django `is_superuser` property of the Django User class to grant those users full access (but note that we want to do that check in the `/acl` view not in the `/superuser` view, since the latter is just provided the username and no password.

Django users connected on port 50002 (websockets/mqtt protected with a server SSL/TLS Certificate) should only have access to Read/Write relevant topics related to the devices they "own" (associated with).  

Given a Django User object, this snippet will iterate through all LAMPIs owned by that user:

```python
for lamp in user.lamp_set.all():
    device_id = lamp.device_id
    print(device_id)
```

There's an asymmetric relationship between the access controls for MQTT topics for Users and their devices bridges.  For a topic like `"/devices/b827eb08451e/lamp/set_config"` the User (say, via websockets/mqtt) needs to be able to Write (Publish) to the topic, but the device bridge needs to Read (Subscribe) from the topic.  **This is *mirror-image* access control critically important to understand.**

Continue to [14.4 Assignment](../14.4_Assignment/README.md)

&copy; 2015-2021 LeanDog, Inc. and Nick Barendt
