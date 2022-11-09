Research Track 1 - Assignment 1 (UniGe)
=======================================

## About Python Robotics Simulator
This is a simple, portable robot simulator developed by [Student Robotics](https://studentrobotics.org).
Some of the arenas and the exercises have been modified for the Research Track I course

Installation
----------------------

The simulator requires a Python 2.7 installation, the [pygame](http://pygame.org/) library, [PyPyBox2D](https://pypi.python.org/pypi/pypybox2d/2.1-r331), and [PyYAML](https://pypi.python.org/pypi/PyYAML/).

Pygame, unfortunately, can be tricky (though [not impossible](http://askubuntu.com/q/312767)) to install in virtual environments. If you are using `pip`, you might try `pip install hg+https://bitbucket.org/pygame/pygame`, or you could use your operating system's package manager. Windows users could use [Portable Python](http://portablepython.com/). PyPyBox2D and PyYAML are more forgiving, and should install just fine using `pip` or `easy_install`.

To run the project, it is recommended to create a python2 virtualenv for the project. To do so, we first need to install virtualenv pip package, and then create a python2.7 virtualenv since the simulator is based on python2.7:

```shell
$ pip install virtualenv
$ git clone https://github.com/amanarora9848/unige-rt1-assignment1.git
$ cd unige-rt1-assignment1
$ virtualenv -p /usr/bin/python2.7 .rt1project1
$ . .rt1project1/bin/activate
```

This activated the python2.7 virtualenv. To deactivate:
```shell
$ deactivate
```

Once in the venv, we can install the project requirements. Fortunately, there exists a requirements.txt file.
```shell
$ pip install -r requirements.txt
```

## Troubleshooting

When running `python run.py <file>`, you may be presented with an error: `ImportError: No module named 'robot'`. This may be due to a conflict between sr.tools and sr.robot. To resolve, symlink simulator/sr/robot to the location of sr.tools.

On Ubuntu, this can be accomplished by:
* Find the location of srtools: `pip show sr.tools`
* Get the location. In my case this was `/usr/local/lib/python2.7/dist-packages`
* Create symlink: `ln -s path/to/simulator/sr/robot /usr/local/lib/python2.7/dist-packages/sr/`

## The Exercise
-----------------------------

To run the scripts in the simulator, use `run.py`, passing to it the file names.

```shell
$ python run.py assigment.py
```

![Short video of task in action](rt1assignment1.gif)

Robot API
---------

The API for controlling a simulated robot is designed to be as similar as possible to the [SR API][sr-api].

### Motors ###

The simulated robot has two motors configured for skid steering, connected to a two-output [Motor Board](https://studentrobotics.org/docs/kit/motor_board). The left motor is connected to output `0` and the right motor to output `1`.

The Motor Board API is identical to [that of the SR API](https://studentrobotics.org/docs/programming/sr/motors/), except that motor boards cannot be addressed by serial number. So, to turn on the spot at one quarter of full power, one might write the following:

```python
R.motors[0].m0.power = 25
R.motors[0].m1.power = -25
```

### The Grabber ###

The robot is equipped with a grabber, capable of picking up a token which is in front of the robot and within 0.4 metres of the robot's centre. To pick up a token, call the `R.grab` method:

```python
success = R.grab()
```

The `R.grab` function returns `True` if a token was successfully picked up, or `False` otherwise. If the robot is already holding a token, it will throw an `AlreadyHoldingSomethingException`.

To drop the token, call the `R.release` method.

Cable-tie flails are not implemented.

### Vision ###

To help the robot find tokens and navigate, each token has markers stuck to it, as does each wall. The `R.see` method returns a list of all the markers the robot can see, as `Marker` objects. The robot can only see markers which it is facing towards.

Each `Marker` object has the following attributes:

* `info`: a `MarkerInfo` object describing the marker itself. Has the following attributes:
  * `code`: the numeric code of the marker.
  * `marker_type`: the type of object the marker is attached to (either `MARKER_TOKEN_GOLD`, `MARKER_TOKEN_SILVER` or `MARKER_ARENA`).
  * `offset`: offset of the numeric code of the marker from the lowest numbered marker of its type. For example, token number 3 has the code 43, but offset 3.
  * `size`: the size that the marker would be in the real game, for compatibility with the SR API.
* `centre`: the location of the marker in polar coordinates, as a `PolarCoord` object. Has the following attributes:
  * `length`: the distance from the centre of the robot to the object (in metres).
  * `rot_y`: rotation about the Y axis in degrees.
* `dist`: an alias for `centre.length`
* `res`: the value of the `res` parameter of `R.see`, for compatibility with the SR API.
* `rot_y`: an alias for `centre.rot_y`
* `timestamp`: the time at which the marker was seen (when `R.see` was called).

For example, the following code lists all of the markers the robot can see:

```python
markers = R.see()
print "I can see", len(markers), "markers:"

for m in markers:
    if m.info.marker_type in (MARKER_TOKEN_GOLD, MARKER_TOKEN_SILVER):
        print " - Token {0} is {1} metres away".format( m.info.offset, m.dist )
    elif m.info.marker_type == MARKER_ARENA:
        print " - Arena marker {0} is {1} metres away".format( m.info.offset, m.dist )
```

## Working and Explanation

### The main python script: assignment22.py

This file is for executing the procedure for the assignment. Given the robot, the environment and the defined parameters, the task for the robot is to pick and place each nearest silver token near the nearest golden one at a given instant of time. 

The robot starts with searching the silver token, which is defined when 'engage' control flag is True. The robot finds the nearest silver flag and moves towards it. Everytime the silver token is grabbed, the engage flag is inverted to search and move towards the nearest gold flag. Everytime the silver token is released, the engage flag is again inverted. The function definitions and logic is defined in the pseudocode below.

Once the task is finished, the robot rejoices.

### Pseudocodes for the procedures / functions for assignment22
```
PSEUDOCODE: Program to make the robot arrange all silver-gold tokens in pairs.
```
<!-- ```
Procedures to drive robot around:

procedure DRIVE(speed, time)
    left motor power ← speed
    right motor power ← speed
    sleep(time)
    left, right motor power ← 0

procedure TURN(speed, time)
    left motor power ← speed
    right motor power ← -speed
    sleep(time)
    left, right motor power ← 0
``` -->

```
Function to search required coloured robot and retrieve its parameters
SELECTOR //BOOLEAN type, True means wanted token is silver, while False means wanted token is gold.

function LOCATE_TOKEN(SELECTOR)
    set dist to 100 //Maximum distance after which token not detected
    if SELECTOR //wanted token is silver
        set distance_threshold to distance_threshold_for_silver
        foreach TOKEN in observed_tokens
            if observed_distance < dist AND observed_token_color is silver
                set dist to observed_distance
                set orientation to observed_orientation
                set token_code to observed_token_code
            endif
        endfor
        if dist = 100 //dist not updated
            return default values for no wanted token detected
        else
            RETURN dist, orientation, token_code, "silver-token", distance_threshold
        endif
    else //wanted token is gold
        set distance_threshold to distance_threshold_for_gold
        foreach TOKEN in observed_tokens
            if observed_distance < dist AND observed_token_color is gold
                set dist to observed_distance
                set orientation to observed_orientation
                set token_code to observed_token_code
            endif
        endfor
        if dist = 100 //dist not updated
            return default values for no wanted token detected
        else
            RETURN dist, orientation, token_code, "gold-token", distance_threshold
        endif
    endif
```

```
Algorithm to implement the given task: 'drive and drop':

SELECTOR //BOOLEAN, True means wanted token is silver, False means wanted token is gold
SILVER_ARRANGED //set of silver tokens already dealt with
GOLD_ARRANGED //set of gold tokens already dealt with

procedure DRIVE_AND_DROP(SELECTOR)

    distance, orientation, token_code, token_color, distance_threshold ← LOCATE_TOKEN(SELECTOR)

    if no token detected
        TURN_ROBOT //continue searching
    
    else if all tokens arranged
        DRIVE_ROBOT backward
        TURN_ROBOT for 2 rotations
        PRINT "Task Completed"
        END EXECUTION

    //Condition useful to account for duplicate token codes for different colors, both already arranged
    else if token_code in SILVER_ARRANGED AND token_code in GOLD_ARRANGED
        TURN_ROBOT //continue searching

    //If token of arranged code found and is of same color (useful in case of duplicate token codes for different colors)
    else if (SELECTOR AND token_code in SILVER_ARRANGED) OR
                (NOT SELECTOR AND token_code in GOLD_ARRANGED)
        TURN_ROBOT //continue searching
    
    else
        if distance < distance_threshold
            if SELECTOR //wanted token is silver
                GRAB_TOKEN()
                add token to SILVER_ARRANGED
            else //wanted token is gold
                RELEASE_TOKEN()
                add token to GOLD_ARRANGED
                DRIVE_ROBOT backwards
            endif
            INVERT SELECTOR
        endif

        //to maneuver robot to wanted token
        if orientation > orientation_threshold:
            TURN_ROBOT right
        else if orientation < -orientation_threshold:
            TURN_ROBOTRN left
        else if -orientation_threshold <= orientation <= orientation_threshold
            DRIVE_ROBOT forward
        endif
    
    endif
```

```
To implement the given task:

while True
    DRIVE_AND_DROP(selector)
```
### Possible Improvements

- For the case of a silver obstacle in the path of the robot while it has already grabbed a silver token, logic to go around it can be written
- User input to set the driving and turning speed of the robot can be accepted and integrated into the code
- There could be more precision in how close to the gold token does the robot drop the silver token, and if it maneuvers in a way to avoid moving the gold token at all
- The current code logic could be made even simpler

[sr-api]: https://studentrobotics.org/docs/programming/sr/
