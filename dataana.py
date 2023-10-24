import numpy as np
import csv


with open('1.csv', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        time = row
        # data = row[1]

print(time)