
#%% Load modules
import cv2 as cv
from urllib.request import urlopen
import socket
import sys

#%% Clear working space
get_ipython().magic('clear')
get_ipython().magic('reset -f')


#%% Capture image from camera
cv.namedWindow('Camera')
cv.moveWindow('Camera', 0, 0)
cmd_no = 0
def capture():
    global cmd_no
    cmd_no += 1
    print(str(cmd_no) + ': capture image')
    cam = urlopen('http://192.168.4.1/capture')
    img = cam.read()
    img = np.asarray(bytearray(img), dtype = 'uint8')
    img = cv.imdecode(img, cv.IMREAD_UNCHANGED)
    cv.imshow('Camera', img)
    # cv.waitKey(1)
    return img

#%% Send a command and receive a response
def cmd(sock, do, what = '', where = '', at = ''):
    global cmd_no
    cmd_no += 1
    msg = {"H":str(cmd_no)} # dictionary
    if do == 'move':
        msg["N"] = 3
        what = ' car '
        if where == 'forward':
            msg["D1"] = 3
        elif where == 'back':
            msg["D1"] = 4
        elif where == 'left':
            msg["D1"] = 1
        elif where == 'right':
            msg["D1"] = 2
        msg["D2"] = at # at is speed here
        where = where + ' '
    elif do == 'stop':
        msg.update({"N":1,"D1":0,"D2":0,"D3":1})
        what = ' car'
    elif do == 'rotate':
        msg.update({"N":5,"D1":1,"D2":at}) # at is an angle here
        what = ' ultrasonic unit'
        where = ' '
    elif do == 'measure':
        if what == 'distance':
            msg.update({"N":21,"D1":2})
        elif what == 'motion':
            msg["N"] = 6
        what = ' ' + what
    elif do == 'check':
        msg["N"] = 23
        what = ' off the ground'
    msg_json = json.dumps(msg)
    print(str(cmd_no) + ': ' + do + what + where + str(at), end = ': ')
    try:
        sock.send(msg_json.encode())
    except:
        print('Error: ', sys.exc_info()[0])
        sys.exit()
    while 1:
        res = sock.recv(1024).decode()
        if '__' in res:
            break
    try:
        res = re.search('_(.*)}', res).group(1)
    except:
        print('received: ', res)
        print('Error:', sys.exc_info()[0])
    if res == 'ok' or res == 'true':
        res = 1
    elif res == 'false':
        res = 0
    elif msg.get("N") == 6:
        res = res.split(",")
        res = [int(x)/16384 for x in res]
    else:
        res = int(res)
    print(res)
    return res
        

#%% Plot MPU data


#%% Connect to car's WiFi
ip = "192.168.4.1"
port = 100
print('Connect to {0}:{1}'.format(ip, port))
car = socket.socket()
try:
    car.connect((ip, port))
except:
    print('Error: ', sys.exc_info()[0])
    sys.exit()
print('Connected!')

#%% Read first data from socket
print('Receive from {0}:{1}'.format(ip, port))
try:
    data = car.recv(1024).decode()
except:
    print('Error: ', sys.exc_info()[0])
    sys.exit()
print('Received: ', data)

#%% Main
cmd(car, do = 'rotate', at = 90)
cmd(car, do = 'measure', what = 'distance')
cmd(car, do = 'rotate', at = 30)
cmd(car, do = 'measure', what = 'distance')
cmd(car, do = 'rotate', at = 150)
cmd(car, do = 'measure', what = 'distance')
cmd(car, do = 'rotate', at = 90)
cmd(car, do = 'measure', what = 'motion')


#%% Close socket
#car.close()
