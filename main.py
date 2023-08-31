import sys
from threading import Thread

import cv2
import pygame
import winsound
from djitellopy import Tello
from pynput.keyboard import Key, Listener

stream = True
takeoff = False
land_or_emergency = False

# TODO try reimplementing using pygame events


def refresh_rc_signals():
    pygame.event.pump()


def print_battery_level():
    print(f"Battery: {tello.get_battery()}%")


def handle_key_pressed(key):
    global land_or_emergency, takeoff
    if key == Key.space:
        land_or_emergency = True
    elif key == Key.ctrl_l:
        takeoff = True
    elif key == Key.backspace:
        tello.emergency()
        land_or_emergency = True


def stream_video():
    global stream
    while stream:
        img = tello.get_frame_read().frame
        img = cv2.resize(img, (1080, 720))
        cv2.imshow("Tello", img)
        cv2.waitKey(1)
    tello.streamoff()


if __name__ == '__main__':

    pygame.init()

    rc = pygame.joystick.Joystick(0)
    rc.init()


    def axis(n: int):
        raw = int(rc.get_axis(n) * 100)
        threshold = 15
        if abs(raw) < threshold:
            return 0
        elif raw > 0:
            return raw - threshold
        else:
            return raw + threshold


    def throttle():
        return -axis(1)


    def yaw():
        return axis(0)


    def pitch():
        return -axis(5)


    def roll():
        return axis(2)


    tello = Tello()
    tello.connect()
    print_battery_level()

    tello.streamon()
    video_thread = Thread(target=stream_video)
    video_thread.start()

    keyboard_listener = Listener(on_press=handle_key_pressed)
    keyboard_listener.start()

    while not takeoff:
        pass

    tello.takeoff()
    winsound.Beep(500, 1000)
    print("takeoff completed", file=sys.stderr)

    try:
        while not land_or_emergency:
            refresh_rc_signals()
            tello.send_rc_control(roll(), pitch(), throttle(), yaw())
    finally:
        if tello.is_flying:
            tello.land()
        print_battery_level()
        stream = False
        pygame.quit()
        keyboard_listener.stop()
        video_thread.join()
