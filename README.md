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

#### Note:
The robot might (in rare cases) appear stopped, but actually it be turning in opposite directions very fast and could take a couple of moments until it reorients itself correctly and finds the token. In such cases, please patiently wait for it to move fast again, it will.

## The Exercise
-----------------------------

To run the scripts in the simulator, use `run.py`, passing to it the file names.

```shell
$ python run.py assigment.py
```

![Short video of task in action](rt1prj1.gif)

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

### Variables and "switches"

The code has following variables which control different aspects of the overall execution, as stated in the comments:
```python
a_th = 2.0
""" float: Threshold for the control of the orientation """

silver_th = 0.40 # Threshold distance for silver (nearest distance to approach before action).
gold_th = 0.62  # Threshold for gold, slightly more.
""" float: Thresholds for the control of the linear distance to a silver or gold token """

engage = True # Starting with silver who uses this flag first, and then is given to gold.

total_tokens = 12 # Total number of tokens (should be evenfor this task)

want_dynamic_speed = True # Preference for dynamic or static speed settings for the robot

not_seen_flag = done_flag = already_seen_flag = unmoved_flag = moveback_flag = False
```
The variables `silver_th` and `gold_th` control the minimum distance of approach to respective token, and gold has a higher value, unsurprisingly, because the silver token has to be released in front of the gold token without pushing it. Variable `a_th` defines the same thing, just for the orientation of the robot w.r.t token.

The toggle `engage` toggles everything concerning with the silver/gold token. Functions taking this flag gather information and execute instructions of search, grab and release based on this flag. `engage` being True is silver, and opposite is gold.

`total_tokens` is a variable which holds the number of tokens in the environment, and the code takes this into account and stops when all tokens have been arranged. This is kept for a possible future improvement wherein we can take input from user or other source regarding number of elements (even).

`want_dynamic_speed` is an option that the user can choose to keep True (if they want smoother motion of robot, the robot drive and turn speeds vary with variations in the distance or orientation from the token being searched), or want the speeds to be static i.e. False.

Finally, variables `not_seen_flag` to `moveback_flag` are used to control the printing procedures (for appropriate print statements and printing them once per condition).

### Functions and Procedures

```
Following functions are used to drive the robot around and perform the task requested.

1. PROCEDURE drive: Function for setting a linear velocity
2. PROCEDURE turn : Function for setting an angular velocity
3. FUNCTION locate_token : Function to find the closest silver or gold token, based on the passed control flag. Returns a dictionary "token_information" with keys as follows - distance, orientation, token_code, token_color, distance_threshold.
4. PROCEDURE drive_to_deliver : Function to drive robot towards the token.
5. PROCEDURE continue_search : Function to rotate robot and make it keep searching for the next token.
6. PROCEDURE grab_release : Function to grab the nearest seen silver token and release it near the nearest seen gold token.
7. PROCEDURE end_task : Function for the robot to stop the task and end program execution after completion.
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

<!-- #### FUNCTION: Search required coloured robot and retrieve its parameters

```c
SELECTOR //BOOLEAN type, True means wanted token is silver, while False means wanted token is gold.

function LOCATE_TOKEN(SELECTOR)
    set dist to 100 //Maximum distance after which token not detected

    if SELECTOR
        set distance_threshold to distance_threshold_for_silver
        set color to silver-token
    else:
        set distance_threshold to distance_threshold_for_gold
        set color to gold-token
    endif

    foreach TOKEN in observed_tokens
        if observed_distance < dist AND observed_token_color is color
            set dist to observed_distance
            set orientation to observed_orientation
            set token_code to observed_token_code
            set token_code to observed_token_color
        endif
    endfor

    if dist is not updated
        return default values
    else:
        return dist, orientation, token_code, "silver-token", distance_threshold
``` -->

### PROCEDURE: Arrange all silver-gold tokens in pairs.

```js
SELECTOR //BOOLEAN, True means wanted token is silver, False means wanted token is gold
SILVER_ARRANGED //set of silver tokens already dealt with
GOLD_ARRANGED //set of gold tokens already dealt with

procedure MAIN()

    token_information ← LOCATE_TOKEN(SELECTOR)

    if no token detected
        KEEP SEARCHING
    
    else if all tokens arranged
        END EXECUTION

    else if token observed has required color and has already been arranged
        KEEP SEARCHING
    
    else
        if token_information[distance] < token_information[distance_threshold]
            if SELECTOR is True
                GRAB TOKEN
                add token to SILVER_ARRANGED
            else
                RELEASE TOKEN
                ADD token to GOLD_ARRANGED
                DRIVE_ROBOT backwards
            endif
            invert SELECTOR
        endif

        //maneuver robot to wanted token
        if token_information[orientation] > orientation_threshold:
            TURN_ROBOT right
        else if token_information[orientation] < -orientation_threshold:
            TURN_ROBOT left
        else if token_information[orientation] <= |orientation_threshold|
            DRIVE_ROBOT forward
        endif
    
    endif
```


### Possible Improvements

- For the case of a silver obstacle in the path of the robot while it has already grabbed a silver token, logic to go around it instead of colliding with it can be written.

- User input to set the driving and turning speed of the robot can be accepted and integrated into the code.

- The movement of the robot can be made smoother by calculating appropriate gain for accuracy and adding (or reducing) small amount of "power" on every iteration upto a desired value, instead of setting it to desired value, and the execution time can be reduced. However, this method was observed to be a little prone to errors, so skipped for now.

- There could be more precision in how close to the gold token does the robot drop the silver token.

- The current code logic could be made even simpler.

[sr-api]: https://studentrobotics.org/docs/programming/sr/
