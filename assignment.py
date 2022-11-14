from __future__ import print_function

import time
from sr.robot import *

"""
This is the code for Assignment 1 for the Research Track 1 course, Semester 1 (LM) at UniGe.
It contains the logic to drive the robot around and deliver the "silver" boxes to the "gold" stations.
"""

a_th = 2.0
""" float: Threshold for the control of the orientation """

silver_th = 0.403
gold_th = 0.61
""" float: Thresholds for the control of the linear distance to a silver or gold token """

R = Robot()
""" Instance of the class Robot """

# Starting with silver who uses this flag first, and then is given to gold.
engage = True

total_tokens = 12 # Total number of tokens (should be even for this task)

# Preference for dynamic or static speed settings for the robot
want_dynamic_speed = True

displaced_tokens = {
    'silver': [],
    'gold': []
}
""" dict: keys depicting the token color, with values of 'list' type, 
containing the token codes which have been dealt with
"""

# Flags for clean print statements - make each set of statements to be displayed once per activity.
not_seen_flag = done_flag = already_seen_flag = unmoved_flag = moveback_flag = False


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


def locate_token(flag):
    """
    Function to find the closest silver or gold token, based on the passed control flag

    Args: flag(bool): If True, it is silver. If False, it is gold

    Returns: distance (float): distance to closest token (-1 if no token detected)
             orientation (float): orientation of robot wrt token (-1 if no token detected)
             token code (int): gold token code (-1 if no token detected)
             token color (string): retrieve the color of the token ("token" if no token detected)
             distance_threshold(float): respective threshold for closest distance, wrt token color (-1 if no token detected)
    """
    dist = 100
    current_token_code = 0

    # If required token is silver.
    if flag:
        distance_threshold = silver_th
        color = MARKER_TOKEN_SILVER
    # If required token is gold.
    else:
        distance_threshold = gold_th
        color = MARKER_TOKEN_GOLD

    for token in R.see():
        if token.dist < dist and token.info.marker_type == color:
            dist = token.dist
            rot_y = token.rot_y
            current_token_code = token.info.code
            token_color = token.info.marker_type

    if dist == 100:
        token_info_dict = {
            'distance_obj': -1,
            'rot_obj': -1,
            'token_code': -1,
            'token_color': "token",
            'distance_threshold': -1
        }
    else:
        token_info_dict = {
            'distance_obj': dist,
            'rot_obj': rot_y,
            'token_code': current_token_code,
            'token_color': token_color,
            'distance_threshold': distance_threshold
        }
    return token_info_dict


def drive_to_deliver(distance, orientation):
    """
    Function to drive robot towards the token.
    Args: distance(float): Distance to the respective token.
          orientation(float): Orientation of robot w.r.t. token.
    """
    # Drive robot towards the token
    if not want_dynamic_speed:
        if orientation > a_th:
            turn(15, 0.04)
        elif orientation < -a_th:
            turn(-15, 0.04)
        elif orientation <= abs(a_th):
            drive(100, 0.05)
    elif want_dynamic_speed:
        if orientation > a_th or orientation < -a_th:
            turn(orientation/(0.01*85), 0.005)
        elif orientation <= abs(a_th):
            drive((distance * 70)/(0.05), 0.05)  # Dynamic linear speed setting


def continue_search(token_color, orientation, token_search_condition, token_code='0'):
    """
    Function to rotate robot and make it keep searching for the next token.
    Args: token_color(string): Silver or Gold token
          orientation(float): Orientation of robot w.r.t. token.
          token_search_condition(int): 1 for no token found case, while 2 when spotted token is already arranged.
          token_code(int): Token code of the token in observation.
    """
    global not_seen_flag, already_seen_flag
    if token_search_condition == 1:
        if not not_seen_flag:
            print("No", token_color, "seen. Searching...")
            print("-" * 78)
        not_seen_flag = True
        if not want_dynamic_speed:
            turn(20, 0.03)
        elif want_dynamic_speed:
            turn(abs(orientation)/0.001*8, 0.001)
    if token_search_condition == 2:
        if not already_seen_flag:
            print("Already moved token:", token_code,
                  "- Searching the next", token_color, "...")
            print("-" * 78)
        already_seen_flag = True
        if not want_dynamic_speed:
            turn(20, 0.03)
        elif want_dynamic_speed:
            turn(abs(orientation)/0.001*8, 0.001)

def grab_release(token_code):
    """
    Function to grab the nearest seen silver token and release it near the nearest seen gold token.
    Args: token-code(int): Spotted token code.
    """
    global engage, moveback_flag
    # If searching for silver token and it's close (upto silver_th i.e. silver threshold), grab it.
    if engage:
        if R.grab():
            print("Grabbed! Delivering...")
            print("-" * 78)
            # Add the token code of the silver token to displaced_tokens dict
            # so that it's not touched again
            displaced_tokens['silver'].append(token_code)
    # If searching for gold token and it's close (upto gold_th i.e. gold threshold)...
    # ...release the grabbed silver token
    else:
        if R.release():
            # Add the token code of the silver token to displaced_tokens dict
            # so that it's not searched for again
            displaced_tokens['gold'].append(token_code)
            # Move back a bit
            drive(-30, 0.85)
            if not moveback_flag:
                print("Released near nearest gold token.\nBacking up a bit, gracefully.")
                print("-" * 78)
            moveback_flag = True
            not_seen_flag = already_seen_flag = unmoved_flag = False
    # Flip the engage flag upon grabbing or releasing of silver token
    engage = not engage
    moveback_flag = False


def end_task():
    """
    Function for the robot to stop the task and end program execution after completion.
    """
    global done_flag
    # Drive backwards and rejoice.
    drive(-90, 1.0)
    turn(85, 0.8)
    turn(-85, 0.8)
    if not done_flag:
        print("Job is done.")
        print("Delivered", len(displaced_tokens['silver']), "tokens.")
        print("-" * 31, "EXECUTION ENDS", "-" * 31)
    done_flag = True
    exit()


def main():
    """
    The main function of the robot.
    This function drives the robot in the direction of closest silver token,
    grabs it, then drives toward closest gold token and releases the silver token, making pairs.
    Continues until all tokens are paired.
    """
    global unmoved_flag

    print("-" * 30, "EXECUTION BEGINS", "-" * 30)

    while 1:

        # Set the parameters to find and move towards the nearest token
        token_info_dict = locate_token(engage)

        # If no token is found, turn and continue search.
        if token_info_dict['token_code'] == -1:
            # The parameter 1 is to mark this particular case.
            continue_search(token_info_dict['token_color'], token_info_dict['rot_obj'], 1)

        # If all tokens have been dealt with (if task is complete), rejoice and exit.
        elif (len(displaced_tokens['silver']) == total_tokens/2 and
                len(displaced_tokens['gold']) == total_tokens/2):
            end_task()

        # If a [silver or gold] token has already been displaced, ignore it and continue search.
        # This is useful because there may be tokens with same code but different colors.
        elif ((engage and token_info_dict['token_code'] in displaced_tokens['silver']) or
                (not engage and token_info_dict['token_code'] in displaced_tokens['gold'])):
            # The parameter 2 is to mark this particular case.
            continue_search(token_info_dict['token_color'], token_info_dict['rot_obj'], 2, token_info_dict['token_code'])

        else:
            if not unmoved_flag:
                print("Unmoved", token_info_dict['token_color'], ":", token_info_dict['token_code'], "\ndistance = ",
                      token_info_dict['distance_obj'], "| orientation = ", token_info_dict['rot_obj'],
                      "\nRushing to grab it...")
                print("-" * 78)
            unmoved_flag = True

            # If robot is really close and ready to grab (or release) the token.
            if token_info_dict['distance_obj'] < token_info_dict['distance_threshold']:
                grab_release(token_info_dict['token_code'])

            # Drive robot towards the token
            drive_to_deliver(token_info_dict['distance_obj'], token_info_dict['rot_obj'])


# Execute
main()
