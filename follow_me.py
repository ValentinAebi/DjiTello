import cv2
import winsound
from djitellopy import Tello
from numpy import sqrt, sign
from pynput.keyboard import Listener, Key

import vision

land_cmd_given = False


def print_battery_level():
    print(f"Battery: {tello.get_battery()}%")


def clamp(x, min_, max_):
    assert min_ <= max_
    return min_ if x <= min_ else max_ if x >= max_ else x


def main_keyboard_listener_func(key):
    global land_cmd_given
    if key == Key.delete:
        winsound.Beep(440, 800)
        tello.takeoff()
    elif key == Key.esc:
        land_cmd_given = True
        tello.land()
    elif key == Key.print_screen:
        tello.emergency()


if __name__ == '__main__':

    tello = Tello()
    tello.connect()
    print_battery_level()

    tello.streamon()

    main_keyboard_listener = Listener(on_press=main_keyboard_listener_func)
    main_keyboard_listener.start()

    frame_read = tello.get_frame_read()

    try:
        while not land_cmd_given:
            frame = frame_read.frame
            frame_height, frame_width = frame.shape[:2]
            frame = cv2.resize(frame, dsize=(int(frame_width), int(frame_height)))
            process_image_ret = vision.process_image(frame)
            if process_image_ret is None:
                tello.send_rc_control(0, 0, 0, 0)
            else:
                (px, py), size, frame = process_image_ret
                print("size:", size)
                thr = 10 if py < 0.3 else -10 if py > 0.3 else 0
                yaw = int(sqrt(abs(px)) * sign(px) * 100)
                forward = int(clamp(-0.42 * size + 34, 0, 25))
                tello.send_rc_control(0, forward, thr, yaw)
            cv2.imshow("Tello", frame)
            cv2.waitKey(1000 // 5)
    finally:
        if not land_cmd_given:
            tello.land()
        print_battery_level()
        tello.streamoff()
        main_keyboard_listener.stop()
        main_keyboard_listener.join()
        cv2.destroyAllWindows()
