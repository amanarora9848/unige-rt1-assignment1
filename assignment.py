from __future__ import print_function

import time
from sr.robot import *

"""
This is the code for Assignment 1 for the Research Track 1 course, Semester 1 (LM) at UniGe.
It contains the logic to drive the robot around and deliver the "silver" boxes to the "gold" stations.
"""

a_th = 2.0
""" float: Threshold for the control of the orientation """

silver_th = 0.4
gold_th = 0.6 # Threshold for gold, slightly more.
""" float: Thresholds for the control of the linear distance to a silver or gold token """


R = Robot()
""" Instance of the class Robot"""

displaced_tokens = {
    'silver': [],
    'gold': []
}
"""
dict: keys depicting the token color, with values of 'list' type, 
containing the token codes which have been dealt with
"""

engage = True # starting with silver who uses this flag first, and then is given to gold


def drive(speed, seconds):
    """
    Function for setting a linear velocity
    
    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def turn(speed, seconds):
    """
    Function for setting an angular velocity
    
    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def find_token_silver():
    """
    Function to find the closest silver token

    Returns: distance (float): distance to closest silver token (-1 if no silver token detected)
             orientation (float): orientation of robot wrt token (-1 if no silver token detected)
             token code (int): silver token code (-1 if no silver token detected)
             token color (string): retrieve the color of the token ("none" if no silver token detected)
    """
    dist = 100
    current_token_code = 0
    for token in R.see():
        if token.dist < dist and token.info.marker_type == 'silver-token':
            dist = token.dist
            rot_y = token.rot_y
            current_token_code = token.info.code
    if dist == 100:
	    return -1, -1, -1, "none"
    else:
   	    return dist, rot_y, current_token_code, MARKER_TOKEN_SILVER

def find_token_gold():
    """
    Function to find the closest gold token

    Returns: distance (float): distance to closest gold token (-1 if no gold token detected)
             orientation (float): orientation of robot wrt token (-1 if no gold token detected)
             token code (int): gold token code (-1 if no gold token detected)
             token color (string): retrieve the color of the token ("none" if no gold token detected)
    """
    dist = 100
    current_token_code = 0
    for token in R.see():
        if token.dist < dist and token.info.marker_type == 'gold-token':
            dist = token.dist
            rot_y = token.rot_y
            current_token_code = token.info.code
    if dist == 100:
        return -1, -1, -1, "none"
    else:
        return dist, rot_y, current_token_code, MARKER_TOKEN_GOLD

def search_and_drive(flag):
    """
    The brain and actuators of the robot.
    This function drives the robot in the direction of closest silver token,
    grabs it, then drives toward closest gold token and releases the silver token. Repeats the same.

    Args: 
        flag (bool): to keep track of whether we are searching for silver or gold token
    """
    # if looking for silver token, set parameters
    if flag:
        distance_obj, rot_obj, token_code, token_color = find_token_silver()
        distance_threshold = silver_th
    # if looking for gold token, set parameters
    else:
        distance_obj, rot_obj, token_code, token_color = find_token_gold()
        distance_threshold = gold_th
    
    # If no token is found, turn and continue search
    if token_code == -1:
        print("No", token_color, "seen. Searching...")
        turn(10, 0.3)
    # If all tokens have been dealt with (if task is complete), rejoice and exit
    elif len(displaced_tokens['silver']) == 6 and len(displaced_tokens['gold']) == 6:
        turn(100, 2)
        print("Job is done, sir.")
        exit()
    # Check if the given token is already there in both gold and silver keys of displaced_token dict
    # This is useful because there may be tokens with same code but different colors
    elif token_code in displaced_tokens['silver'] and token_code in displaced_tokens['gold']:
        print("Already moved token:", token_code, "- Searching the next", token_color, "...")
        turn(10, 0.3)
    # If silver token already displaced, don't touch it again, continue search
    elif flag and token_code in displaced_tokens['silver']:
        print("Already moved silver token:", token_code, "- Searching the next", token_color, "...")
        turn(10, 0.3)
    # If gold token already displaced, don't touch it again, continue search
    elif not flag and token_code in displaced_tokens['gold']:
        print("Already moved gold token:", token_code, "- Searching the next", token_color, "...")
        turn(10, 0.3)
    else:
        print("Unmoved", token_color, ":", token_code, "| distance = ", distance_obj, "| orientation = ", rot_obj)
        # if robot is really close and ready to grab (or release) the token
        if distance_obj < distance_threshold:
            global engage
            # if searching for silver token and it's close (upto silver_th - threshold for silver), grab it
            if engage:
                if R.grab():
                    displaced_tokens['silver'].append(token_code)
            # if searching for gold token and it's close (upto gold_th - threshold for gold), release the grabbed silver token
            else:
                if R.release():
                    displaced_tokens['gold'].append(token_code)
                    drive(-15, 1)
                    print('Backing up gracefully.')
            # flip the engage flag upon grabbing or releasing of silver token
            engage = not engage
        # Drive robot towards the token
        if rot_obj > a_th:
            turn(10, 0.1)
        elif rot_obj < -a_th:
            turn(-10, 0.1)
        elif -a_th <= rot_obj <= a_th:
            drive(50, 0.2)

while(1):
    # Commence operation
    search_and_drive(engage)