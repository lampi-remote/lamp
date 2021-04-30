# Assignment - Load Testing

In this scenario, you are about to release LAMPI to the world. But first, you need to understand how much load the LAMPI webpage can handle.

You will be load testing two of your internet-exposed endpoints on EC2 -- your NGINX/Django-based website, and your MQTT message broker. Your goal is to discover and record the largest kind of concurrent user load that your server can reliably handle.  Then, for HTTP only, you will attempt to increase the load capacity of your system.

**NOTE:** test HTTP and MQTT separately (do not load both systems at the same time).  For a real-life production scenario, we would likely run HTTP and MQTT services on different servers.

Your Locust files, etc. should be stored in **connected-devices/loadtesting/** directory in your repository.

## Generating Fake Users and Devices

To create users and devices to load test with, a new Django command has been added in the repository **loadtestingdata**. 

When invoked:

```bash
$cloud ~/connected-devices/Web/lampisite
$cloud ./manage.py loadtestingdata
```

It will create 10,000 Users, each with one LAMPI device associated with their account.  (this might run for a few minutes as our SQLite database is pretty slow)

Note: you can run this script multiple times without issue (it is idempotent) - it will create any missing users/devices when it is run.

The User accounts have:

* a username of the form `user_<dddddd>` where "d" is an integer 0-9
* a password which is the reverse of the username (use the Python `somestring[::-1]` idiom to efficiently reverse the string)

So, for example:

* a username of `user_000000`
* a password of `000000_resu`

User accounts go from `user_000000` to `user_009999`

The Fake LAMPI devices have Device IDs starting at 1E:00:00:00:00:00 or "1e0000000000" (0x1E happens to be a "Locally Managed" MAC Address range so we can use those values withour fear of interacting with an actual device).

Each User has one LAMPI device, corresponding to their ordinal number:

* user "user\_000000" is associated with Device "1e0000000000"
* user "user\_000233" is associated with Device "1e00000000e9" (233 decimal is 0xe9)

## HTTP

For the assignment, you will construct a Locust TaskSet in **connected-devices/loadtesting/locustfile.py** with the following characteristics:

* log in with a random fake user account and password
* delay between 0.5 seconds and 10 seconds between tasks
* execute tasks that:
    * GET `/` with a weight of 100
    * GET `/lampi` with a weight of 80
    * GET `/lampi/device/<device_id>` with a weight of 75

With the default configuration (Ansible, NGINX, UWSGI, AWS `m5.large` instance) you will:

* Establish a baseline
    * Generate a small load against your Django site and verify that there are no failures or exceptions reported in the Locust Web UI
    * Increase the load until you see failures, then decrease the load until there are no failures
    * Do this until you feel comfortable that you have identified a __maximum load for your system *without error*__.


* Break your server! Increase load until you experience failures
    * After breaking your server, continue to decrease load until zero failure rate
    * "Hone in" on your maximum load by continuing to increase / decrease load in smaller and smaller increments

* Using sar, generate a report of cpu, disk, and network access at three points
     * With minimal load
     * At maximum load before failure
     * During load causing failure

Then, investigate how you might increase your systems load capacity, through online searches, experiments, etc.  Please attempt one more of these, and capture the data showing an improvement.

Note:  for all HTTP tests stick with a Locust Hatch Rate of 10 Users/Second.

A portion of the assignment grade will be based on how much you are able to increase your systems capacity above the nominal performance.  You are limited to serving your entire application from one `m5.large` instance, running both your website and the MQTT Broker, and maintaining the existing functionality of the system.

The data, reports, and any images should be captured in a new file **connected-devices/loadtesting/http-results.md** explaining the tests, the results, and what changes you made.  Your write up should include at least two paragraphs.

## MQTT

Build an interaction model for LAMPI devices publishing messages to the EC2 mosquitto broker (e.g., in the `/devices/<device_id>/` topic hierarchy) that covers frequency of user interactions and MQTT messages (only model upstream, from LAMPI device to EC2 Mosquitto).  

Document your interaction model for LAMPI with text, tables, etc. as needed, in a new file **connected-devices/loadtesting/mqtt-model.md**.  Use your engineering judgement on messages and message frequency and explain your rationale.

Using your model, build an MQTT Locust TaskSet **connected-devices/loadtesting/mqtt-locustfile.py** that publishes messages as the model describes (with appropriate QoS, Retain, etc.), assuming worst-case behaviors (e.g., all users interacting with their LAMPI touchscreens simultaneously).  Your MQTT Locust test should randomly choose a Fake Device ID for each session (equivalent to using a Fake User to test HTTP).

For this load testing, we are not simulating the MQTT Bridge directly, but instead directly generating the messages on the topics that the MQTT Bridge would be publishing to.  We are only testing the rate at which clients can publish messages to the broker (not the broker's ability to deliver those messages to subscribed clients).

Run your MQTT Locust Load Test.

* Choose performance metrics to measure (Messages/sec , CPU utilization, Memory...)
    * Establish baselines for expected performance metrics during normal use
    * Generate a small load against your MQTT broker with your MQTT Locust Task Set and observe performance metrics over time.
    * Increase and decrease the load and observe performance metrics again.
    * Do this until you feel comfortable with an average performance (i.e. messages/sec) of how many connected LAMPIs you can support, given your model.

* Attempt to break your server! Increase load until your performance is abnormally low compared to your baseline.
    * If you break your server, continue to decrease load until working close to your expected performance again.
    * "Hone in" on your maximum load by continuing to increase / decrease load in smaller and smaller increments

* Using sar, generate a report of cpu, disk, and network access at three points
    * With minimal load
    * At maximum load before failure
    * During load causing failure
* While running those tests collect the following reports for analysis
    * Log broker health using the built-in monitoring endpoints ( $SYS/# ), pipe output to a file.
    * Choose a few key metrics to report on that are important (and note those that are not).

The data, reports, and any images should be captured in a new file **connected-devices/loadtesting/mqtt-results.md** explaining the tests and the results.  Your write up should include at least two paragraphs.

## Demo

Be prepared to demo load testing both HTTP and MQTT in class.

Note: to avoid extra charges, you can (and should) "Stop" your load testing EC2 Instance(s), and then "Start" them before class.

## What to Turn in

You need to turn in the following:

1. A short (a few sentences) write up from each member of the pair summarizing what they learned completing the assignment, and one thing that surprised them (good, bad, or just surprising).  This should in **connected-devices/writeup.md** in [Markdown](https://daringfireball.net/projects/markdown/) format.  You can find a template file in **connected-devices/template\_writeup.md**
2. A Git Pull Request
3. A short video demonstrating the required behaviors emailed to the instructor and TA.  The video should be named **[assignment 3]_[LAST_NAME_1]\_[LAST_NAME_2].[video format]**.  So, for this assignment, if your pair's last names are "Smith" and "Jones" and you record a .MOV, you would email a file named ```2_smith_jones.mov``` to the instructor.
4. A live demo at the beginning of the next class - **be prepared!**

&copy; 2015-2021 LeanDog, Inc. and Nick Barendt
