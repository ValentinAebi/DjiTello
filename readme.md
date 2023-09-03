## Python scripts for the Tello drone

**⚠️ The scripts in this repo do not guarantee that the Tello drone behaves safely during their execution ⚠️**

These scripts have been tested with the [djitellopy 2.5.0 library](https://github.com/damiafuentes/DJITelloPy),
Python 3.8, and a basic Tello (non-EDU). The drone uses its visual sensors to keep its position (built-in feature,
not depending on the Python scripts), so it needs a good luminosity in order to work correctly. The drone is not responsive during takeoff.

### Keys
 - Delete -> Takeoff
 - Esc -> Land
 - PrtSc -> Emergency (immediately stop the motors)
