import fnmatch
import serial
import csv
import re

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
    compute = False
    pre_time,pre_vx,pre_vy,pre_vz,pre_px,pre_py,pre_pz = 0,0,0,0,0,0,0
    write_value = []
    csv_file = "result.csv"
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
                    pattern = r'\d+\.\d+|\d+'
                    result = re.findall(pattern,data)
                    result = [float(num) for num in result]
                    if len(result) == 7 :
                        time,ax,ay,az,x_degree,y_degree,z_degree = result[0:7]
                        print(result)
                        '''
                        print('time:',time)
                        print('x:',x)
                        print('y:',y)
                        print('z:',z)
                        print('x_degree:',x_degree)
                        print('y_degree:',y_degree)
                        print('z_degree:',z_degree)
                        '''
            
                    #print(time,x,y,z,x_degree,y_degree,z_degree) #check
                    #print(result) #check

                    #compute 
                    deltaTime = (time - pre_time)/1000.0 #sec
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


                    #write into CSV
                    write_value[0:7] = time,px,py,pz,x_degree,y_degree,z_degree
                    row = csv.writer(file)
                    for i in range(7):
                        row.writerow(write_value)


                    #update
                    pre_time = time
                    pre_px = px
                    pre_py = py
                    pre_pz = pz
                    pre_vx = vx
                    pre_vy = vy
                    pre_vz = vz


                if data.strip() == "Done!":
                    compute = True
                    print("start computing!")
            

        
    
if __name__ == '__main__':
    main()
