import math
import csv
import re
import numpy as np
import pandas as pd

def read_data(csv_path):
    data = []
    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            merged_string = ''.join(row)
            match = re.findall(r'\((.*?)\)',merged_string)
            if match:
                row_data = []
                for item in match:
                    val = item.split(',')
                    for i in range(len(val)):
                        val[i] = float(val[i])
                        row_data.append(val[i])
                data.append(row_data)   
        #print(data)             
    return data

def simpson(array):
    unint_of_time = 1 #can change it
    new_array = [] 
    for i in range(1,len(array),2):
        temp_row = []
        for j in range(0,len(array[0]),1):
            temp = round(((array[i][j]) ** 2) * unint_of_time,3)
            temp_row.append(temp)
        new_array.append(temp_row)
    return new_array


def main():
    csv_path = 'period_value.csv'
    array = read_data(csv_path)
    #read
    array = simpson(array) #first integral
    #print(array)
    array = simpson(array) #second integral
    #print(array)
    x_displacement,y_displacement,z_displacement,x_angle_displacement,y_angle_displacement,z_angle_displacement = 0,0,0,0,0,0
    for i in range(0,len(array),1):
        x_displacement += array[i][0]
        y_displacement += array[i][1]
        z_displacement += array[i][2]
        x_angle_displacement += array[i][3]
        y_angle_displacement += array[i][4]
        z_angle_displacement += array[i][5]

    distance = math.sqrt(x_displacement ** 2 + y_displacement ** 2 + z_displacement ** 2 )
    print("distance",distance)
    angle = [[x_angle_displacement,0,0],
             [0,y_angle_displacement,0],
             [0,0,z_angle_displacement]]
    print("angle",angle)
    return 0



if __name__ == '__main__':
    main()
