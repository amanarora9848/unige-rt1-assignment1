#!/usr/bin/env python

import os
import time
from multiprocessing import Pool
import subprocess
import threading
import csv
import argparse

# Command line arguments
parser = argparse.ArgumentParser(description="Run the simulation batches with specified repititions, and calculate various metrics associated with the simulation of the game.")
parser.add_argument('-b', '--batches', type=int, help="Number of batches to run the simulation for.")
parser.add_argument('-r', '--reps', type=int, help="Number of repititions of sim per batch.")
parser.add_argument('-m', '--metrics_interval', type=int, help="Number of batches after which to calculate metrics.")

args = parser.parse_args()

lock = threading.Lock()

def empty_csv(filename):
    if os.path.exists(filename):
        os.remove(filename)

def run_sim():
    subprocess.call(["python", "run.py", "assignment.py"])

def calc_metrics(num_rows):
    if os.path.exists("execution_times.csv"):
        with open("execution_times.csv", "r") as f:
            reader = csv.reader(f)
            all_runs = [row for row in reader if row]
            
            # Get the last num_rows from all_runs, excluding the title row
            recent_exec_times = all_runs[-num_rows:] if len(all_runs) > 1 else []
    # Get all successful runs (with values not equal to 90 or 100)
    successful_runs = [row for row in recent_exec_times if float(row[0]) not in {90, 100, 110}]

    # Calculate the failed runs (total rows - length of successful runs)
    failed_runs = len(recent_exec_times) - len(successful_runs)

    # Calculate the mean
    mean_exec_time = None
    if successful_runs:
        mean_exec_time = sum(float(row[0]) for row in successful_runs) / len(successful_runs)
    
    # Calculate the standard deviation
    std_dev = None
    if successful_runs:
        std_dev = (sum((float(row[0]) - mean_exec_time)**2 for row in successful_runs) / len(successful_runs))**0.5
    
    # Metrics for all batches
    metrics = [len(recent_exec_times), failed_runs, mean_exec_time, std_dev]

    # Check if metrics.csv file exists
    if os.path.exists("metrics.csv"):
        with open("metrics.csv", "a") as f:
            writer = csv.writer(f)
            writer.writerow(metrics)
    else:
        with open("metrics.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Total runs", "Failed runs", "Mean Successful runs", "Standard Deviation"])
            writer.writerow(metrics)
    

def main():

    if not args.batches or not args.reps or not args.metrics_interval:
        parser.print_help()
        return
    
    num_reps = args.reps
    num_batches = args.batches
    m = args.metrics_interval
    metrics_interval = m
    threads = []

    empty_csv("metrics.csv")
    empty_csv("execution_times.csv")

    for batch in range(num_batches):
        
        for _ in range(num_reps):
            t = threading.Thread(target=run_sim)
            t.start()
            threads.append(t)

        # Wait for all threads to finish
        for t in threads:
            t.join()
        
        # After every `m` batches, calculate metrics
        if (batch + 1) % metrics_interval == 0:
            calc_metrics(metrics_interval * num_reps)
        
        threads = [] # Reset threads for next batch


if __name__ == "__main__":
    main()
