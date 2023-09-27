import threading
import os
import eel
import pickle
import socket
import select
from threading import Thread
import time
from time import sleep

conntection_timeout = 1.0

class Wind:
    speed = 0
    direction = 0

    def __init__(self, speed, direction):
        self.speed = speed
        self.direction = direction


class BoatState:
    latitude = 0
    latitude_direction = ""
    longitude = 0
    longitude_direction = ""
    current_heading = 0
    magnetic_deviation = 0
    magnetic_deviation_direction = ""
    magnetic_variation = 0
    magnetic_variation_direction = 0
    track_degrees_true = 0
    track_degrees_magnetic = 0
    speed_knots = 0
    speed_kmh = 0
    rate_of_turn = 0
    outside_temp = 0
    atmospheric_pressure = 0
    true_wind = Wind(0, 0)
    apparent_wind = Wind(0, 0)
    pitch = 0
    roll = 0


# Set web files folder
eel.init('web')


@eel.expose                         # Expose this function to Javascript
def say_hello_py(x):
    print('Hello from %s' % x)

#create server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
server_socket.bind(("0.0.0.0", 1111))  # Bind to a specific address and port
server_socket.listen(1)
server_socket.setblocking(0)
server_socket.settimeout(0.2)


def connect_to_sailbot():
    # Create a socket client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    # print("Creating connection")
    ip = socket.gethostbyname("sailbot.netbird.cloud")
    print("Sailbot ip is "+str(ip))
    connected = False
    while not connected:
        try:
            client_socket.connect((ip, 1111))  # Connect to the server
            connected = True
        except:
            print("Connection failed, retrying...")
            sleep(conntection_timeout)

    # Receive and deserialize data from the server
    received_data_bytes = client_socket.recv(1024)
    if len(received_data_bytes)>0:
        try:
            received_data = pickle.loads(received_data_bytes)
        except EOFError:
            print("Unexpected EOF in data- why does this happen?")
    # print("Got data")
    # Close the client socket
    client_socket.close()

    # Process the received data
    # print("Received Data:")
    for data in received_data:
        print(data)

def recieve_data():
    print("Receiving data")
    last_data_time = time.time()
    while True:
        print("Time since last: ")
        print(time.time()-last_data_time)
        if time.time()-last_data_time>conntection_timeout:
            print("Connection to sailbot timed out, reconnecting...")
            connect_to_sailbot()
        print("Before select")
        read_sockets, write_sockets, error_sockets = select.select([server_socket], [], [], 0.2)
        print("after select")
        for sock in read_sockets:
            print("Before accept")
            this_client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")
            this_client_socket.setblocking(0)
            this_client_socket.settimeout(0.2)
            # Receive and deserialize data from the server
            print("Before recv")
            received_data_bytes = this_client_socket.recv(1024)
            print("after recv")
            if len(received_data_bytes)>0:
                received_data = pickle.loads(received_data_bytes)
                print(received_data.latitude)
            # Close the client socket
            last_data_time = time.time()
            this_client_socket.close()


def sailbot_comms():
    connect_to_sailbot()
    receive_thread = Thread(target=recieve_data, daemon=True)
    receive_thread.start()


def main():
    comms_thread = threading.Thread(target=sailbot_comms, daemon=True)
    comms_thread.start()
    say_hello_py('Python World!')
    eel.say_hello_js('Python World!')  # Call a Javascript function
    if os.name == "nt":
        eel.start('telemetry.html', mode='custom', cmdline_args=['node_modules/electron/dist/electron.exe', '.'])
    else:
        eel.start('telemetry.html', mode='custom', cmdline_args=['node_modules/electron/dist/electron', '.'])


if __name__ == "__main__":
    main()