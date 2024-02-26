import fnmatch
import serial
import csv
import re
import math
from datetime import datetime

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


def main():
    available_ports = auto_detect_serial_unix()
    port = serial.Serial(available_ports[0], baudrate= 115200,timeout=0.1)
    ## baudrate is transfering ratio
    ## timeout is to set a read timeout value in seconds
    count_for_stop = 0
    compute = False
    pre_time,pre_vx,pre_vy,pre_vz,pre_px,pre_py,pre_pz = 0,0,0,0,0,0,0
    min_time,max_time=9999999,-1
    count_data_num = 0
    pre_ax = 0
    write_value = []
    now = datetime.now()
    hour = str(now.hour)
    minute = str(now.minute)
    csv_file = "result" + hour + minute + ".csv"
    

    with open(csv_file, mode = 'w+',newline='' ) as file:
        while(True):
            #print(compute) #check
            rawdata = port.readline()
            data = rawdata.decode()
            if data.strip() == "MPU9250 is connected":
                compute = False
                #print('check')
                print(data)
            if data.strip() == "MPU9250 dose is connected":
                compute = False
                #print('check')
                print(data)
            if data.strip() == "Position you MPU9250 flat and don't move it - calibrating...":
                compute = False
                #print('check')
                print(data)
        
            if compute == True:
                pattern = r'-?\d+\.\d+|-?\d+'
                result = re.findall(pattern,data)
                result = [float(num) for num in result]
                if len(result) == 7 :
                    time,ax,ay,az,x_degree,y_degree,z_degree = result[0:7]
                    count_data_num += 1
                    print(result)
                
                #print(time,x,y,z,x_degree,y_degree,z_degree) #check
                #print(result) #check
                

                #count time
                if time < min_time:
                    min_time = time
                if time > max_time:
                    max_time = time


                #compute 
                deltaTime = (time - pre_time)/1000.0 #sec
                #Distant : dx = v*t + 1/2*a*t^2 
                dx = (pre_vx * deltaTime) + (0.5 * ax * deltaTime * deltaTime) 
                dy = (pre_vy * deltaTime) + (0.5 * ay * deltaTime * deltaTime)
                dz = (pre_vz * deltaTime) + (0.5 * (az - 1) * deltaTime * deltaTime)
                #velocity : v2 = v1 + at
                vx = pre_vx + (ax * deltaTime)
                vy = pre_vy + (ay * deltaTime)
                vz = pre_vz + ((az-1) * deltaTime)
                #position : p2 = p1 + dinstant
                px = pre_px + dx
                py = pre_py + dy
                pz = pre_pz + dz


                #write into CSV
                #write_value[0:7] = time,px,py,pz,x_degree,y_degree,z_degree #write position data
                #write_value[0:7] = time,ax,ay,az,x_degree,y_degree,z_degree #write raw data
                write_value[0:7] = time,ax,vx,px,x_degree,y_degree,z_degree
                row = csv.writer(file)
                row.writerow(write_value)
                
                '''
                print(count_for_v_calibrating)
                if pre_vx == vx and pre_vy == vy and pre_vz == vz:
                    count_for_v_calibrating += 1
                if count_for_v_calibrating == 10:
                    vx,vy,vz = 0,0,0
                    count_for_v_calibrating = 0 
                '''

                #update
                pre_time = time
                pre_px = px
                pre_py = py
                pre_pz = pz
                pre_vx = vx
                pre_vy = vy
                pre_vz = vz
                print(px,py,pz)
                

                if pre_ax == ax:
                    count_for_stop += 1
                pre_ax = ax


            if data.strip() == "Done!":
                compute = True
                print("start computing!")

            #print('count_for_stop: ',count_for_stop)
            if count_for_stop == 3000:
                print("STOP!")
                port.write(b'STOP\n')
                port.close()
                dis = math.sqrt(px ** 2 + py ** 2 + pz ** 2)
                total_time = (max_time - min_time) / 1000
                print('total_data_num:',count_data_num)
                print('time(s):',total_time)
                print('p_x:(m)',px)
                print('distant(m):',dis)
                return 0

                
if __name__ == '__main__':
    main()
