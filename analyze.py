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

args = parser.parse_args()

lock = threading.Lock()

def empty_csv(filename):
    if os.path.exists(filename):
        os.remove(filename)

def run_sim():
    subprocess.call(["python", "run.py", "assignment.py"])


def calc_metrics(batch_num):
    if os.path.exists("execution_times.csv"):
        with open("execution_times.csv", "r") as f:
            reader = csv.reader(f)

            # Skip the first row (header)
            next(reader)

            all_runs = [row for row in reader]

            # Get all successful runs (with values < 45 seconds)
            successful_runs = [row for row in all_runs if float(row[0]) < 45]
            
            # Calculate the failed runs (total rows - length of successful runs)
            failed_runs = len(all_runs) - len(successful_runs)

            # Calculate the mean
            mean_exec_time = None
            if successful_runs:
                mean_exec_time = sum(float(row[0]) for row in successful_runs) / len(successful_runs)
            
            # Calculate the standard deviation
            std_dev = None
            if successful_runs:
                std_dev = (sum((float(row[0]) - mean_exec_time)**2 for row in successful_runs) / len(successful_runs))**0.5
            
            # Metrics for the batch
            metrics = [batch_num, len(all_runs), failed_runs, mean_exec_time, std_dev]

            # Check if metrics.csv file exists
            if os.path.exists("metrics.csv"):
                with open("metrics.csv", "a") as f:
                    writer = csv.writer(f)
                    writer.writerow(metrics)
            else:
                with open("metrics.csv", "w") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Batch Number", "Total runs", "Failed runs", "Mean Successful runs", "Standard Deviation"])
                    writer.writerow(metrics)


def main():

    if not args.batches or not args.reps:
        parser.print_help()
        return
    
    num_reps = args.reps
    num_batches = args.batches
    threads = []

    # empty_csv("metrics.csv")

    for batch in range(num_batches):

        # Empty the CSV file for each batch
        empty_csv("execution_times.csv")

        for _ in range(num_reps):
            t = threading.Thread(target=run_sim)
            t.start()
            threads.append(t)

        # Wait for all threads to finish
        for t in threads:
            t.join()
        
        threads = [] # Reset threads for next batch

        calc_metrics(batch+1)

if __name__ == "__main__":
    main()
