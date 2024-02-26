import fnmatch
import serial
import csv
import re
import numpy as np

pre_time,pre_vx,pre_vy,pre_vz,pre_px,pre_py,pre_pz = 0,0,0,0,0,0,0
pre_ax = 0
start = False

def auto_detect_serial_unix(preferred_list=['*']):
    '''try to auto-detect serial ports on win32'''
    import glob
    glist = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    ret = []

    # try preferred ones first
    for d in glist:
        for preferred in preferred_list:
            if fnmatch.fnmatch(d, preferred):
                ret.append(d)
    if len(ret) > 0:
        return ret
    # now the rest
    for d in glist:
        ret.append(d)
    return ret

def check(data):
    global start
    stripped_data = data.strip()
    if stripped_data == "Done!":
        start = True
    print(data)
    return

def compute(time,ax,ay,az,x_degree,y_degree,z_degree):
    write_value = []
    global pre_time,pre_vx,pre_vy,pre_vz,pre_px,pre_py,pre_pz,pre_ax
    deltaTime = time - pre_time
    # Distant : dx = v*t + 1/2*a*t^2 
    dx = (pre_vx * deltaTime) + (0.5 * ax * deltaTime * deltaTime) 
    dy = (pre_vy * deltaTime) + (0.5 * ay * deltaTime * deltaTime)
    dz = (pre_vz * deltaTime) + (0.5 * (az - 1) * deltaTime * deltaTime)
    # Velocity : v2 = v1 + at
    vx = pre_vx + (ax * deltaTime)
    vy = pre_vy + (ay * deltaTime)
    vz = pre_vz + ((az-1) * deltaTime)
    # Position : p2 = p1 + dinstant
    px = pre_px + dx
    py = pre_py + dy
    pz = pre_pz + dz
    # Update
    pre_time = time
    pre_px = px
    pre_py = py
    pre_pz = pz
    pre_vx = vx
    pre_vy = vy
    pre_vz = vz 
    pre_ax = ax
    write_value[0:4] = time,ax,vx,px
    return

# Standard deviation
def STD(data):
    threshold = 2
    mask = []
    filtered_data = [d[1:7] for d in data]
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
    available_ports = auto_detect_serial_unix()
    port = serial.Serial(available_ports[0], baudrate= 115200,timeout=0.1)
    port.flushInput()
    ## baudrate is transfering ratio
    ## timeout is to set a read timeout value in seconds
    global start
    count_data_num = 1 
    count_for_stop = 0   
    tmp_value = []
    
    while(count_for_stop<1000):
            rawdata = port.readline()
            data = rawdata.decode()
            if start == False:
                check(data)
            else:
                pattern = r'-?\d+\.\d+|-?\d+'
                result = re.findall(pattern,data)
                result = [float(num) for num in result]
                if len(result) == 7:
                    tmp_value.append(result)
                    count_data_num += 1
                    print(result[0:7])
                    write_file(result[0:7],"result.csv")
                    if count_data_num % 20 == 0:
                        filtered_data = STD(tmp_value)
                        for row in filtered_data:
                            write_file(row[0:7],"filter20.csv")
                        tmp_value = []
                        for row in filtered_data:
                            time,ax,ay,az,x_degree,y_degree,z_degree = row[0:7]
                            time = time/1000.0
                            compute(time,ax,ay,az,x_degree,y_degree,z_degree)
                    count_for_stop += 1 
    start = False

    port.close()            
    return 0

                
if __name__ == '__main__':
    main()
