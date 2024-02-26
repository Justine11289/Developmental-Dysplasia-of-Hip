import math
import csv
import re
import numpy as np
import pandas as pd

# Read Arduino data
def read_data(csv_path):
    data = []
    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            merged_string = ''.join(row)
            match = re.findall(r'\((.*?)\)',merged_string)
            if len(match) == 2:
                row_data = []
                for item in match:
                    val = item.split(',')
                    for i in range(len(val)):
                        val[i] = float(val[i])
                        row_data.append(val[i])
                data.append(row_data)                
    return data

# Integral
def simpson(array):
    unint_of_time = 1
    new_array = []
    for i in range(1,len(array),2):
        temp_row = []
        for j in range(0,6,1):
            temp = round(((array[i][j]) ** 2) * unint_of_time,3)
            temp_row.append(temp)
        new_array.append(temp_row)
    return new_array

def main():
    csv_path = 'period_value.csv'
    ACM = read_data(csv_path)
    #delta_a = calculate_delta(ACM)
    
    with open('acceleration.csv', 'a+') as af:
        writeA = csv.writer(af)
        for row in ACM:
           writeA.writerow(row)

    velocity = simpson(ACM)
    with open('velocity.csv', 'a+') as vf:
        writeV = csv.writer(vf)
        for row in velocity:
           writeV.writerow(row)

    position = simpson(velocity)
    with open('position.csv', 'a+') as pf:
        writeP = csv.writer(pf)
        for row in position:
           writeP.writerow(row)

    x_d,y_d,z_d = 0,0,0
    for i in range(0,len(position),1):
        x_d += position[i][0]
        y_d += position[i][1]
        z_d += position[i][2]
    
    #distance = math.sqrt(x_d ** 2 + y_d ** 2 + z_d ** 2 )
    #print('distance:',distance)
    return 0


if __name__ == '__main__':
    main()
