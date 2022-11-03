from __future__ import print_function

import time
from sr.robot import *

"""


"""


a_th = 2.0
""" float: Threshold for the control of the orientation"""

d_th = 0.4
""" float: Threshold for the control of the linear distance"""
gold_th = 0.6 # Threshold for gold, slightly more.

R = Robot()
""" instance of the class Robot"""

displaced_tokens = {
    'silver': [],
    'gold': []
} # Dictionary of already displaced gold and silver tokens.

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
    Function to find the closest silver token
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
    About the function
    """
    if flag:
        distance_obj, rot_obj, token_code, token_color = find_token_silver()
        distance_threshold = d_th
    else:
        distance_obj, rot_obj, token_code, token_color = find_token_gold()
        distance_threshold = gold_th
    
    if token_code == -1:
        # If no token is found, turn.
        print("No", token_color, "seen. Searching...")
        turn(10, 0.3)
    elif len(displaced_tokens['silver']) == 6 and len(displaced_tokens['gold']) == 6:
        turn(100, 2)
        print("Job is done, sir.")
        exit()
    elif token_code in displaced_tokens['silver'] and token_code in displaced_tokens['gold']:
        print("Already moved token:", token_code, "- Searching the next", token_color, "...")
        turn(10, 0.3)
    elif flag and token_code in displaced_tokens['silver']:
        print("Already moved silver token:", token_code, "- Searching the next", token_color, "...")
        turn(10, 0.3)
    elif not flag and token_code in displaced_tokens['gold']:
        print("Already moved gold token:", token_code, "- Searching the next", token_color, "...")
        turn(10, 0.3)
    else:
        print("Unmoved", token_color, ":", token_code, "| distance = ", distance_obj, "| orientation = ", rot_obj)
        if distance_obj < distance_threshold:
            global engage
            if engage:
                if R.grab():
                    displaced_tokens['silver'].append(token_code)
            else:
                if R.release():
                    displaced_tokens['gold'].append(token_code)
                    drive(-15, 1)
                    print('Backing up gracefully.')
            engage = not engage
        if rot_obj > a_th:
            turn(10, 0.1)
        elif rot_obj < -a_th:
            turn(-10, 0.1)
        elif -a_th <= rot_obj <= a_th:
            drive(50, 0.2)

while(1):
    search_and_drive(engage)