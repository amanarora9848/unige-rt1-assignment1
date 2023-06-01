from __future__ import print_function

import time
from sr.robot import *
import os
import csv

a_th = 2.0 #float: Threshold for the control of the orientation
d_th = 0.4 #float: Threshold for the control of the linear distance

fin_silver = [] #record the number of silver token that is done
fin_gold = [] #record the number of gold token that is done

R = Robot() #instance of the class Robot

def forward(speed, seconds): 
    """
    This function is for moving forward
    Args:   speed (int): the speed of the wheels
	        seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def turn(speed, seconds):
    """
    This function is for turning
    Args:   speed (int): the speed of the wheels
	        seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed/2
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def find_token(color): 
    """
    This function is for fiding the closest token considering its color

    Arg:    color: true=silver false=gold

    Returns:dist (float): distance of the closest token (-1 if no token is detected)
	        rot_y (float): angle between the robot and the token (-1 if no token is detected)
    """
    dist=100
    for token in R.see():
        if color == True and token.dist < dist and token.info.marker_type is MARKER_TOKEN_SILVER: #silver and closer than previous token
            if token.info.offset in fin_silver: #ignore tokens which are already delivered
                continue
            else:
                dist=token.dist
                rot_y=token.rot_y
                num=token.info.offset #to distinguish token if it's delivered or not
        elif color == False and token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD:
            if token.info.offset in fin_gold: #ignore tokens which are already delivered
                continue
            else:
                dist=token.dist
                rot_y=token.rot_y
                num=token.info.offset #to distinguish token if it's delivered or not
    if dist==100:
        return -1, -1, -1
    else:
        return dist, rot_y, num # distance, angle, offset (next target)

def record(color, num):
    """
    This function is for record the offset of tokens which the robot has already reached

    Args:   color:  silver=true, gold=false
            num:    the number given by find_token, which indicates the offset of token
    """
    if color == True: #count silvers
        fin_silver.append(num)
        print("REACHED SILVER: "+str(fin_silver))
    elif color == False: #count golds
        fin_gold.append(num)
        print("REACHED GOLD: "+str(fin_gold))

def write_execution_times(exec_time):
    """
    Function to write the execution times to a csv file.
    Args: exec_time(float): Execution time of the program.
    """
    file_path = os.path.abspath('execution_times.csv')
    file_exists = os.path.isfile(file_path)
    with open(file_path, 'a') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Execution Time"])
        # Write the execution time for this run
        writer.writerow([exec_time])

search_time = 0

def main():
    global search_time
    print("MISSION STARTED!") 
    start_timer = time.time() 
    silver = True #look for silver at first
    while 1:
        search_time = time.time() - start_timer
        if search_time > 180:
            print("FAILSAFE TRIGGER", search_time)
            write_execution_times(90)
        dist, rot_y, num = find_token(silver) #info about closest token(silver/gold)
        if dist==-1: #when find_token couldn't find any token
            print("NO TOKEN HAS FOUND YET")
            turn(10,1)
        elif dist <d_th + 0.2: #if the robot is about to reach token, we grab/release it
            print("THERE IS")
            if silver == True:
                forward(20, 1) #go forward a little bit to grab
                print("I GOT YOU")
                R.grab() #grab silver token
                record(silver, num) #after grab it, record its number
                turn(-20, 2)
                print("DELIVER TIME!")
            elif silver == False:
                print("HERE YOU ARE!")
                R.release()
                record(silver, num)
                if len(fin_gold) == 6:
                    # forward(-20, 2)
                    # turn(+20, 1.5)
                    print("MISSION COMPLETED!")
                    end_timer = time.time()
                    print("Time: ", end_timer - start_timer)
                    write_execution_times(end_timer - start_timer)
                    # exit()
                    break
                turn(+20, 2)
            silver = not silver #switch silver/gold
        elif -a_th<= rot_y <= a_th: # if the robot is well aligned with the token, we go forward
            print("KEEP THIS WAY")
            forward(40, 0.5)
        elif rot_y < -a_th: # if the robot is not well aligned with the token, we move it on the left or on the right
            print("LEFT")
            turn(-4, 0.25)
        elif rot_y > a_th:
            print("RIGHT")
            turn(+4, 0.25)

main()
