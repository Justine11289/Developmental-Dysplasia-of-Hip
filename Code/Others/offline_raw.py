import math
import csv
import re
import numpy as np
import pandas as pd
from scipy.signal import medfilt

pre_vx,pre_vy,pre_vz,pre_px,pre_py,pre_pz,pre_time = 0,0,0,0,0,0,0
total_distance = 0

# Read Arduino data
def read_data(csv_path):
    # Select (x,y,z)(anglex,angley,anglez)(time) data
    data = []
    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            merged_string = ''.join(row)
            match = re.findall(r'\((.*?)\)',merged_string)
            if len(match) == 3:
                row_data = []
                for item in match:
                    val = item.split(',')
                    for i in range(len(val)):
                        if(len(val) == 1):
                            val[i] = float(val[i])/1000
                        else:
                            val[i] = float(val[i])
                        row_data.append(val[i])
                data.append(row_data)

    # Select real data
        start = 0
        for i in range(1,len(data)):
            if(data[i-1][6] > data[i][6]):
                start = i
        data = data[start:]           
    return data

# Find position
def post(ax,ay,az,x_degree,y_degree,z_degree,time):
    global pre_vx,pre_vy,pre_vz,pre_px,pre_py,pre_pz,pre_time,total_distance
    #compute 
    deltaTime = time - pre_time
    #Distant : dx = v*t + 1/2*a*t^2 
    dx = (pre_vx * deltaTime) + (0.5 * ax * deltaTime * deltaTime) 
    dy = (pre_vy * deltaTime) + (0.5 * ay * deltaTime * deltaTime)
    dz = (pre_vz * deltaTime) + (0.5 * (az - 1) * deltaTime * deltaTime)
    #velocity : v2 = v1 + at
    vx = pre_vx + (ax * deltaTime)
    vy = pre_vy + (ay * deltaTime)
    vz = pre_vz + (az * deltaTime)
    #position : p2 = p1 + dinstant
    px = pre_px + dx
    py = pre_py + dy
    pz = pre_pz + dz
    #update
    pre_time = time
    pre_px = px
    pre_py = py
    pre_pz = pz
    pre_vx = vx
    pre_vy = vy
    pre_vz = vz
    total_distance += math.sqrt(dx ** 2 + dy ** 2 + dz ** 2 )
    return px,py,pz,time



def main():
    csv_path = 'period_value.csv'
    data = read_data(csv_path)

    # Standard deviation
    data_array = np.array(data)
    std = (np.std(data_array,axis=0)) * 5
    exceeded_rows = np.all((data_array > std) | (data_array < -std), axis=0)
    exceeded_indices = np.where(exceeded_rows)[0]
    mask = np.ones(len(data_array),dtype=bool)
    mask[exceeded_indices] = False
    data_filtered = data_array[mask]

    # Filtered
    window_size = 5
    data_smoothed = medfilt(data_filtered,kernel_size=window_size)
    data_smoothed_list = data_smoothed.tolist()
    

    # Acceleration
    acceleration = data_smoothed_list
    with open('acceleration5.csv', 'w+') as af:
        writeA = csv.writer(af)
        for row in acceleration:
           writeA.writerow(row)

    # Position
    position = []
    for i in range(len(acceleration)):
        ax,ay,az,x_degree,y_degree,z_degree,time = acceleration[i]
        x,y,z,time = post(ax,ay,az,x_degree,y_degree,z_degree,time)
        position.append([x,y,z,time])

    with open('position.csv', 'w+') as pf:
        writeP = csv.writer(pf)
        for row in position:
           writeP.writerow(row)

    # Total Distance
    print("Total distance:",total_distance)
    return 0


if __name__ == '__main__':
    main()
