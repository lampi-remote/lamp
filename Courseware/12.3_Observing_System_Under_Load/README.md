# Observing the System Under Load

### Installing sysstat

We will use [sysstat](https://github.com/sysstat/sysstat) to collect information about our system for retrieval later. Let's install it on the machine under load, your EC2 instance that is hosting Django and your MQTT broker:

```bash
cloud$ sudo apt-get install -y sysstat
```

systat contains a lot of different tools, but there are three we will focus on:

* `sadc`, `sa1`, `sa2` collects info on system activity
* `sar` prints collected data, formatted for stdout
* `sadf` outputs collected data in other formats (XML, CSV, etc)


### Capturing Historical Data

We want `sa1` to run on startup. It installs some init.d scripts by default, but they are disabled. To enable them, edit **/etc/default/sysstat** with superuser privileges. Change ENABLED from false to true:

```
ENABLED="true"
```

Save the file. Now let's see how often data is collected. Again with `sudo` open up the cron job at **/etc/cron.d/sysstat**.

```bash
# Activity reports every 10 minutes everyday
5-55/10 * * * * root command -v debian-sa1 > /dev/null && debian-sa1 1 1

# Additional run at 23:59 to rotate the statistics file
59 23 * * * root command -v debian-sa1 > /dev/null && debian-sa1 60 2
```

So, by default, sysstat uses `sa1` to capture data every 10 minutes, and creates a new capture file every day. Go ahead and `sudo reboot` so the configuration change can take effect.

Log back into the EC2 instance. Let's list log output:

```bash
cloud$ ls -la /var/log/sysstat
```

You should see an entry for today named **sa[n]**, where *n* is the current date (e.g., sa16 for November 16th).

```
-rw-r--r--  1 root root   243056 Nov 16 16:40 sa16
```

Let's use `sar` to observe that file. First let's view CPU usage. Replace the file name with the latest one in your log folder:

```bash
sar -u -f /var/log/sysstat/sa16
```

*-u* is for CPU usage, *-f [file]* is to provide a log file to read. You should see all captured output for the day (you may need to let the system run for a while since it only captures every 10 minutes):

```
01:35:01 PM     CPU     %user     %nice   %system   %iowait    %steal     %idle
01:45:01 PM     all      0.03      0.00      0.02      0.00      0.03     99.92
01:55:01 PM     all      0.02      0.00      0.02      0.00      0.03     99.93
02:05:01 PM     all      0.02      0.00      0.01      0.00      0.03     99.94
02:15:01 PM     all      0.02      0.00      0.02      0.00      0.04     99.92
02:25:01 PM     all      0.01      0.00      0.01      0.00      0.04     99.94
02:35:01 PM     all      0.02      0.00      0.01      0.00      0.03     99.93
02:45:01 PM     all      0.03      0.00      0.01      0.00      0.03     99.92
02:55:01 PM     all      0.03      0.00      0.02      0.00      0.04     99.91
03:05:01 PM     all      0.04      0.00      0.02      0.00      0.03     99.91
03:15:01 PM     all      0.04      0.00      0.03      0.00      0.05     99.88
03:25:01 PM     all      0.03      0.00      0.01      0.00      0.03     99.93
03:35:01 PM     all      0.04      0.00      0.01      0.00      0.05     99.90
03:45:01 PM     all      0.03      0.00      0.01      0.00      0.03     99.92
03:55:01 PM     all      0.04      0.00      0.02      0.01      0.03     99.91
04:05:01 PM     all      0.02      0.00      0.02      0.00      0.04     99.92
04:15:01 PM     all      0.02      0.00      0.01      0.00      0.04     99.93
04:25:01 PM     all      0.12      0.00      0.03      0.02      0.05     99.79
04:35:01 PM     all      0.01      0.00      0.01      0.00      0.03     99.95
Average:        all      0.03      0.01      0.02      0.01      0.04     99.90

04:40:52 PM       LINUX RESTART
```

Now let's view memory usage for the day, using *-r* instead of *-u*:

```bash
sar -r -f /var/log/sysstat/sa16
```

You should see stats on memory usage:

```
01:35:01 PM kbmemfree kbmemused  %memused kbbuffers  kbcached  kbcommit   %commit  kbactive   kbinact   kbdirty
01:45:01 PM    286080    730212     71.85    112880    254760    435936     42.89    465444    192676         0
01:55:01 PM    286112    730180     71.85    112896    254764    435936     42.89    465468    192676         0
02:05:01 PM    285980    730312     71.86    112904    254764    435936     42.89    465516    192648         4
02:15:01 PM    285960    730332     71.86    112932    254772    435936     42.89    465536    192664         0
02:25:01 PM    285988    730304     71.86    112948    254780    435936     42.89    465588    192648         4
02:35:01 PM    285988    730304     71.86    112964    254780    435936     42.89    465600    192648         0
02:45:01 PM    285856    730436     71.87    112984    254784    435936     42.89    465648    192628         0
02:55:01 PM    285856    730436     71.87    112996    254792    435936     42.89    465680    192620         0
03:05:01 PM    285732    730560     71.88    113004    254796    435936     42.89    465700    192612         0
03:15:01 PM    285700    730592     71.89    113012    254800    435936     42.89    465724    192604         0
03:25:01 PM    285708    730584     71.89    113036    254800    435936     42.89    465756    192600         0
03:35:01 PM    285700    730592     71.89    113056    254804    435936     42.89    465780    192604         0
03:45:01 PM    285740    730552     71.88    113072    254804    435936     42.89    465788    192620         0
03:55:01 PM    285576    730716     71.90    113160    254820    435936     42.89    465920    192632         0
04:05:01 PM    285448    730844     71.91    113180    254820    435936     42.89    465936    192640         0
04:15:01 PM    285460    730832     71.91    113212    254828    435936     42.89    465944    192672         0
04:25:01 PM    273220    743072     73.12    113548    258100    445852     43.87    476628    193096         0
04:35:01 PM    277492    738800     72.70    113572    258088    441840     43.48    472668    193064         0
Average:       373624    642668     63.24    103490    182433    437202     43.02    418159    158613         1

04:40:52 PM       LINUX RESTART
```

You can also combine flags to output multiple stats at once. This will display memory and CPU usage:

```bash
cloud$ sar -ur -f /var/log/sysstat/sa16
```

### Displaying Current Stats

We can also use `sar` to display current system info, which is better for frequently updating stats. This is what you will use to observe your system during load testing.

Let's observe memory and CPU usage every second, for 60 seconds:

```bash
cloud$ sar -ur 1 60
```

You should see output occur every second for a minute.

To see all the things that `sar` can display, [refer to the documentation](http://sebastien.godard.pagesperso-orange.fr/man_sar.html) (yes, the page's style is a little dated looking).

Next up: [12.4 Assignment](../12.4_Assignment/README.md)

&copy; 2015-2021 LeanDog, Inc. and Nick Barendt
