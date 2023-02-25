import random

import pygame as pg
import pygame.midi
import unicodedata
from pyautogui import press, typewrite, hotkey


class Action:
    def __init__(self, string: str = None, timestamp: int = None, special: bool = None):
        self.string = string
        self.timestamp = timestamp
        self.special = special

        if string is None:
            self.string = ""
        if timestamp is None:
            self.timestamp = 0
        if special is None:
            self.special = False

    def clear(self):
        self.string = ""
        self.timestamp = 0
        self.special = False

    def is_empty(self):
        return self.string == "" and self.timestamp == 0

    def get_weird(self):
        new_string = ""

        for c in self.string:
            random_caps = random.choice([True, False])

            if random_caps:
                new_string += c.capitalize()
            else:
                new_string += c.lower()

        return new_string

    def run(self):
        if self.special:
            if self.string == "<space>":
                typewrite(" ")
            else:
                hotkey('alt', 'ctrl', unicodedata.normalize('NFD', self.string).encode('ascii', 'ignore').decode('utf-8'))
            return

        if CAPS is True:
            typewrite(self.string.capitalize())
        elif CAPS is False:
            typewrite(self.string.lower())
        else:
            typewrite(self.get_weird())

    def __str__(self):
        return f"{self.string}, {self.timestamp}"


next_actions = []
CAPS = False


def handle(event):
    # keys
    if 48 <= event.data1 <= 72 and event.data2 > 0:
        # 48 -> a (97)
        next_actions.append(Action(chr(event.data1 + 49), event.timestamp))

    # special keys
    charmap = {
        4: "ą",  # upper
        5: "ę",
        6: "ó",
        7: "ś",
        0: "z",  # lower
        1: "ż",
        2: "    ",
        3: "<space>"
    }
    if 0 <= event.data1 <= 7 and event.status == 192:
        if charmap[event.data1] == "z":
            special = False
        else:
            special = True

        next_actions.append(Action(charmap[event.data1], event.timestamp, special=special))

    # caps lock
    if event.status == 176 and event.data1 == 1:
        global CAPS
        if event.data2 == 0:
            CAPS = False
        elif event.data2 == 127:
            CAPS = True
        else:
            CAPS = "weird"


def main(device_id=None):
    pg.init()
    pg.fastevent.init()
    event_get = pg.fastevent.get
    event_post = pg.fastevent.post
    pygame.midi.init()

    if device_id is None:
        input_id = pygame.midi.get_default_input_id()
    else:
        input_id = device_id

    print("using input_id :%s:" % input_id)
    i = pygame.midi.Input(input_id)

    pg.display.set_mode((1, 1))

    going = True
    while going:
        # combinations
        comb_map = {
            "mqt": "obserwuj",      # nuty C1 E G
            "mpt": "inatorskiego",  # nuty C1 D# G
            "qty": "na",            # nuty E1 G C2
            "osx": "tiktoku",       # nuty D1 F# H

            "aeh": "no hej co tam",  # C0 DUR
        }

        if len(next_actions) >= 3:
            curr_time = next_actions[-1].timestamp

            near_1 = abs(curr_time - next_actions[-2].timestamp) < 500
            near_2 = abs(curr_time - next_actions[-3].timestamp) < 500

            A = next_actions[-1].string
            B = next_actions[-2].string
            C = next_actions[-3].string

            if near_1 and near_2:
                comb = "".join([A, B, C])

                for c, res in comb_map.items():
                    if len(comb) == 3 and c[0] in comb and c[1] in comb and c[2] in comb:
                        del next_actions[-3:]  # delete last 3
                        next_actions.append(Action(res, curr_time))

        # evaluate next_action
        if len(next_actions) > 0 and (abs(pygame.time.get_ticks() - next_actions[-1].timestamp) > 500) and (not next_actions[-1].is_empty()):
            print(next_actions[-1], len(next_actions))
            next_actions[-1].run()
            next_actions.pop()

        events = event_get()
        for e in events:
            if e.type in [pg.QUIT]:
                going = False
            if e.type in [pg.KEYDOWN]:
                going = False
            if e.type in [pygame.midi.MIDIIN]:
                # print(e)
                handle(e)

        if i.poll():
            midi_events = i.read(10)
            midi_evs = pygame.midi.midis2events(midi_events, i.device_id)

            for m_e in midi_evs:
                event_post(m_e)

    del i
    pygame.midi.quit()


if __name__ == "__main__":
    main()
