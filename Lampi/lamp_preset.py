import json
import time
import copy
import colorsys
import pigpio

PWM_FREQUENCY = 1000
PWM_RANGE = 1000

RED_GPIO = 19
GREEN_GPIO = 26
BLUE_GPIO = 13

RGBs = [RED_GPIO, GREEN_GPIO, BLUE_GPIO]

PRESET_FOLDER_DIRECTORY = './presets/'
PRESETS = [
    PRESET_FOLDER_DIRECTORY + "preset" + str(1),
    PRESET_FOLDER_DIRECTORY + "preset" + str(2),
    PRESET_FOLDER_DIRECTORY + "preset" + str(3),
]

class LampDriver(object):
    def __init__(self):
        self.pi = pigpio.pi()
        for g in RGBs:
            self.pi.set_PWM_frequency(g, PWM_FREQUENCY)
            self.pi.set_PWM_range(g, PWM_RANGE)
            self.pi.set_PWM_dutycycle(g, 0)

    def set_lamp_state(self, hue, saturation, brightness, is_on):
        rgb = [0.0, 0.0, 0.0]

        if is_on:
            rgb = list(colorsys.hsv_to_rgb(hue, saturation, 1.0))
            for c in range(len(rgb)):
                rgb[c] = rgb[c] * brightness

        for i in range(len(RGBs)):
            self.pi.set_PWM_dutycycle(RGBs[i], rgb[i] * PWM_RANGE)


class LampPreset:

    def __init__(self):
        self.lamp_driver = LampDriver()
        self.stop = False

    def get_preset(self, index):
        with open(PRESETS[index] + ".json") as f:
            preset = json.load(f)

        return preset

    def play_preset(self, preset_number):
        self.stop = False

        while True:
            preset = self.get_preset(preset_number)

            for init, fin in zip(preset['stateList'], preset['stateList'][1:]):
                time.sleep(init['waitTime'])

                if init['smooth']:
                    self.smooth(init['state'], fin['state'], init['transitionTime'])
                else:
                    time.sleep(init['transitionTime'])

                last = fin

            time.sleep(last['waitTime'])
            if self.stop or not preset['loop']:
                self.stop = False
                break

    def stop_preset(self):
        self.stop = True

    def smooth(self, init, fin, duration):

        prev = self.round_state(init)
        delta = 0.001 / duration
        step, mult = self.find_step(delta, init, fin)
        start_time = time.time()
        while not init == fin:

            current = time.time()
            elapsed_time = current - start_time

            step, m = self.find_step(delta, init, fin)

            for k, v in step.items():
                if v > 0:
                    init[k] = min(init[k] + v, fin[k])
                else:
                    init[k] = max(init[k] + v, fin[k])

#            if elapsed_time > duration:
#                init = fin

            time.sleep(0.001)
            end = time.time()
            delta = (end - current) / duration / 1000 * mult

            curr = self.round_state(copy.deepcopy(init))
            if not prev == curr:
                prev = curr
                self.lamp_driver.set_lamp_state(curr['h'], curr['s'], curr['b'], True)
                print(curr)

        print('Finished iterating in:', str(round(float(elapsed_time),2)), 'seconds')

    def round_state(self, state):
        for k, v in state.items():
            state[k] = round(v, 2)

        return state

    def find_step(self, base_step, init, fin):
        step = {
            'h': fin['h'] - init['h'],
            's': fin['s'] - init['s'],
            'b': fin['b'] - init['b']
        }

        base_value = None
        base_key = None
        for k, v in step.items():
            if abs(v) and (base_value is None or abs(v) < abs(base_value)):
                base_value = v
                base_key = k
        step[base_key] = base_step

        for k, v in step.items():
            if v == 0:
                step[k] = 0
            elif not k == base_key:
                step[k] = v / base_value * base_step

        return step, base_value * 1000

    # def run(self):
    #     self.play_preset()



# if __name__ == "__main__":
#     LampPreset().run()
