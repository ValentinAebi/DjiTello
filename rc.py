import sys
from threading import Thread

import cv2
import pygame
import winsound
from djitellopy import Tello
from pynput.keyboard import Key, Listener

stream = True
land_or_emergency = False

# This script converts the commands of a joystick (intended to be an RC controller connected to the computer) into
# channel values that are sent to the Tello.

# WARNING: The scripts in this repo do not guarantee that the Tello drone behaves safely during their execution.
# WARNING: Depending on the joystick/controller, the mapping of the RC channels may need to be updated.


def refresh_rc_signals():
    pygame.event.pump()


def print_battery_level():
    print(f"Battery: {tello.get_battery()}%")


def main_keyboard_listener_func(key):
    global land_or_emergency
    if key == Key.esc:
        land_or_emergency = True
    elif key == Key.print_screen:
        tello.emergency()
        land_or_emergency = True


def stream_video():
    frame_read = tello.get_frame_read()
    global stream
    while stream:
        img = frame_read.frame
        img = cv2.resize(img, (1080, 720))
        cv2.imshow("Tello", img)
        cv2.waitKey(1000//30)
    tello.streamoff()


def fly():
    try:
        while not land_or_emergency:
            refresh_rc_signals()
            tello.send_rc_control(roll(), pitch(), throttle(), yaw())
    finally:
        if tello.is_flying:
            tello.land()
        print_battery_level()
        main_keyboard_listener.stop()
        takeoff_keyboard_listener.stop()


def takeoff_keyboard_listener_func(key):
    if key == Key.delete:
        tello.takeoff()
        winsound.Beep(500, 1000)
        print("takeoff completed", file=sys.stderr)
        fly()


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

    main_keyboard_listener = Listener(on_press=main_keyboard_listener_func)
    main_keyboard_listener.start()

    takeoff_keyboard_listener = Listener(on_press=takeoff_keyboard_listener_func)
    takeoff_keyboard_listener.start()

    takeoff_keyboard_listener.join()
    main_keyboard_listener.join()
    stream = False
    video_thread.join()
    pygame.quit()
