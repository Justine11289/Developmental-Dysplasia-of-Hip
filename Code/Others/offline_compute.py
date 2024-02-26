import math
import csv
import numpy as np

pre_vx,pre_vy,pre_vz,pre_px,pre_py,pre_pz,pre_time = 0,0,0,0,0,0,0
total_distance = 0

# Find position
def compute(time,ax,ay,az,x_degree,y_degree,z_degree):
    global pre_vx,pre_vy,pre_vz,pre_px,pre_py,pre_pz,pre_time,total_distance
    #compute 
    deltaTime = time - pre_time
    # Distant : dx = v*t + 1/2*a*t^2 
    dx = (pre_vx * deltaTime) + (0.5 * ax * deltaTime * deltaTime) 
    dy = (pre_vy * deltaTime) + (0.5 * ay * deltaTime * deltaTime)
    dz = (pre_vz * deltaTime) + (0.5 * (az - 1) * deltaTime * deltaTime)
    # velocity : v2 = v1 + at
    vx = pre_vx + (ax * deltaTime)
    vy = pre_vy + (ay * deltaTime)
    vz = pre_vz + (az * deltaTime)
    # position : p2 = p1 + dinstant
    px = pre_px + dx
    py = pre_py + dy
    pz = pre_pz + dz
    # update
    pre_time = time
    pre_px = px
    pre_py = py
    pre_pz = pz
    pre_vx = vx
    pre_vy = vy
    pre_vz = vz
    total_distance += math.sqrt(dx ** 2 + dy ** 2 + dz ** 2 )
    return px,py,pz

def STD(data):
    threshold = 2
    mask = []
    filtered_data = [list(map(float,d[1:7])) for d in data]
    mean = np.mean(filtered_data, axis=0)
    std_devs = np.std(filtered_data, axis=0)
    for i,row in enumerate(filtered_data):
        std_range = np.all(np.abs(row - mean) <= threshold * std_devs)
        if std_range:
            mask.append(i)
    filtered_data = [data[i] for i in mask]
    return filtered_data

def write_file(data,csv_file):
    with open(csv_file, mode = 'a+',newline='' ) as file:
        writer = csv.writer(file)
        writer.writerow(data)

def main():
    csv_path = "result.csv"
    data = []
    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)
    filtered_data = STD(data)
    time,ax,ay,az,x_degree,y_degree,z_degree = filtered_data[0:7]
    px,py,pz = compute(time,ax,ay,az,x_degree,y_degree,z_degree)
    for row in filtered_data:
        write_file(row[0:7],"offline.csv")


if __name__ == '__main__':
    main()




