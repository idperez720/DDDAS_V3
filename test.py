import socket, time
import numpy as np

def send_motors_commands(speeds, robot_message, sckt):
    # speeds must be an array of shape (2, 1)
    msg = robot_message.copy()
    msg[4], msg[3] = map_speed(speeds[0, 0])
    msg[6], msg[5] = map_speed(speeds[1, 0])
    msg = ''.join(msg)
    msg = bytes.fromhex(msg)
    sckt.sendall(msg)

def map_speed(value):
    value = np.clip(value, -1000, 1000)
    value = abs(value) if value >= 0 else 65536 + value # 2**16 = 65536 (Two's complement)
    speed = '000' + hex(int(value))[2:]
    speed = speed[::-1]
    speed = speed[:4][::-1]
    return speed[0:2], speed[2:4] # MSB, LSB

def map_stepper_count(count, count_prev):
    th = 1000
    delta = count - count_prev
    if(abs(delta) >= th):
        alpha = np.maximum(count, count_prev)
        beta = np.minimum(count, count_prev)
        delta = -(65535 - alpha + beta)*np.sign(delta)
    return delta

sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sckt.connect(('192.168.0.63', 1000))

id = '80'
flags_req = '02'
flags_set = '00'
motor_left_LSB = '00'
motor_left_MSB = '00'
motor_right_LSB = '00'
motor_right_MSB = '00'
leds_state = '00'
leds_rgb = '00'*12
sound = '00'
robot_message = [id, flags_req, flags_set,
                 motor_left_LSB, motor_left_MSB,
                 motor_right_LSB, motor_right_MSB,
                 leds_state, leds_rgb, sound]

msg = ''.join(robot_message)
msg = bytes.fromhex(msg)
sckt.sendall(msg)

try:
    send_motors_commands(np.array([100, 100]).reshape(2, 1), robot_message, sckt)
    k = 0
    while(True):
        data = sckt.recv(256)
        if(len(data) == 104):
            lsl, msl, lsr, msr = data[79], data[80], data[81], data[82]
            right = lsr + msr*256
            left = lsl + msl*256
            if(k == 0):
                r_count_prev, l_count_prev = right, left
            r_delta = map_stepper_count(right, r_count_prev)
            l_delta = map_stepper_count(left, l_count_prev)

            r_count_prev = right
            l_count_prev = left

            print(r_delta, l_delta, right, left)
            k += 1

except KeyboardInterrupt:
    pass


send_motors_commands(np.array([0, 0]).reshape(2, 1), robot_message, sckt)
time.sleep(1)
sckt.close()
