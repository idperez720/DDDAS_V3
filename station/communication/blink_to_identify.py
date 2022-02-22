import numpy as np
import socket, pickle, time, os


def main_blink_to_identify(colors, N, N_max):
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, 'ip_addresses/addresses.pickle')

    id = '80'
    flags_req = '00'
    flags_set = '00'
    motor_left_LSB = '00'
    motor_left_MSB = '00'
    motor_right_LSB = '00'
    motor_right_MSB = '00'
    leds_state = '00'
    leds_rgb = '00'*12
    sound = '00'
    message = [id, flags_req, flags_set, motor_left_LSB, motor_left_MSB, motor_right_LSB, motor_right_MSB, leds_state, leds_rgb, sound]

    def toggle_led(sckt, led_state, message=message):
        message_to_send = message.copy()
        if(led_state == 1):
            message_to_send[7] = '07'

        message_to_send = ''.join(message_to_send)
        message_to_send = bytes.fromhex(message_to_send)
        sckt.sendall(message_to_send)

    N = 6
    robots = {}
    colors = ['blue', 'purple', 'red', 'green', 'lime', 'yellow']
    for i in range(N):
        robots[colors[i]] = [i+1, 'unregistered_ip', colors[i], 'unregistered_ip']

    print('Input number of robots to identify (1-6):')
    N = input()
    N = np.clip(int(N), 1, 6)

    for i in range(N):
        print('Input the last 3 digits of the IP address to test (i.e., 192.168.0.XXX):')
        host = input()
        host = host.strip()
        host = '192.168.0.' + host

        print('Connecting to: ', host)
        sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sckt.connect((host, 1000))
        toggle_led(sckt, 1)

        print('Input the last 3 digits of the IP address to associate (i.e., 192.168.0.XXX):')
        associated = input()
        associated = '192.168.0.' + associated.strip()
        print('Associated ', host, ' to ', associated )

        print('Input the color of the lighting robot (blue, purple , red, green, lime, yellow):')
        color = input()
        color = color.strip()
        robots[color][1] = host
        robots[color][-1] = associated


        print('The ', color, ' robot (number ', robots[color][0], ') has been identified!')
        toggle_led(sckt, 0)
        time.sleep(0.5)
        sckt.close()

    print('A total of ', N, ' robots have been identified. Saving adresses...')

    with open(path, 'wb') as handle:
        pickle.dump(robots, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print('Adresses saved!')
