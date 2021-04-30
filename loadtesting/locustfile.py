from locust import HttpLocust, TaskSet, task
import random
import resource

MAX_USER = 1000
DEVICE_ID_BASE = 0x1e0000000000

resource.setrlimit(resource.RLIMIT_NOFILE, (999999, 999999))


class UserBehavior(TaskSet):

    def on_start(self):
        self.user_num = random.randint(0, MAX_USER-1)
        self.login()

    def login(self):
        response = self.client.get("/login/?next=/")
        csrftoken = response.cookies.get('csrftoken', '')
        username = 'user_{:0>6d}'.format(self.user_num)
        password = username[::-1]

        self.client.post("/login/?next=/", {
            "csrfmiddlewaretoken": csrftoken,
            "username": username,
            "password": password})

    @task(100)
    def load_index(self):
        self.client.get("/")

    @task(80)
    def load_lampi_index(self):
        self.client.get("/lampi")

    @task(75)
    def load_device_page(self):
        self.client.get("/lampi/device/{0:x}".format(
            DEVICE_ID_BASE + self.user_num), name='/lampi/device/<device_id>')


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 10000
