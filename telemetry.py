import threading
import os
import eel
import pickle
import socket
import select
from threading import Thread
import time
from time import sleep
from enum import Enum
import random

class OS(Enum):
    LINUX = 0
    WINDOWS = 1


CURRENT_OS = OS.LINUX
if os.name == "nt":
    CURRENT_OS=OS.WINDOWS


class Wind:
    speed = 0
    direction = 0

    def __init__(self, speed, direction):
        self.speed = speed
        self.direction = direction


class NodeStates:
    airmar_reader = 0
    battery_monitor = 0
    control_system = 0
    network_comms = 0
    pwm_controller = 0
    serial_rc_receiver = 0
    trim_tab_comms = 0


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
    node_states = NodeStates()


# Set web files folder
eel.init('web')


@eel.expose                         # Expose this function to Javascript
def say_hello_py(x):
    print('Hello from %s' % x)


class UI:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    current_node_states = NodeStates()
    connection_timeout = 1.0

    def __init__(self):
        # create server socket
        if CURRENT_OS == OS.LINUX:
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        elif CURRENT_OS == OS.WINDOWS:
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("0.0.0.0", 1111))  # Bind to a specific address and port
        self.server_socket.listen(1)
        self.server_socket.setblocking(0)
        self.server_socket.settimeout(0.2)

    def connect_to_sailbot(self):
        # Create a socket client
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if CURRENT_OS == OS.LINUX:
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        elif CURRENT_OS == OS.WINDOWS:
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # print("Creating connection")
        ip = socket.gethostbyname("sailbot.netbird.cloud")
        print("Sailbot ip is " + str(ip))
        connected = False
        while not connected:
            try:
                client_socket.connect((ip, 1111))  # Connect to the server
                connected = True
            except:
                print("Connection failed, retrying...")
                sleep(self.connection_timeout)

        # Receive and deserialize data from the server
        # received_data_bytes = client_socket.recv(1024)
        # received_data=""
        # if len(received_data_bytes) > 0:
        #     try:
        #         received_data = pickle.loads(received_data_bytes)
        #     except EOFError:
        #         print("Unexpected EOF in data- why does this happen?")
        # else:
        #     print("Recieved data is empty?")
        # print("Got data")
        # Close the client socket
        #client_socket.close()

        # Process the received data
        # print("Received Data:")
        # for data in received_data:
        #     print(data)

        return client_socket

    def update_boat_state(self, new_state: BoatState):

        # update node states
        new_nodes_status = new_state.node_states
        if new_nodes_status.network_comms != self.current_node_states.network_comms:
            eel.NetworkCommsUp() if new_nodes_status.network_comms == 1 else eel.NetworkCommsDown()
        if new_nodes_status.airmar_reader != self.current_node_states.airmar_reader:
            eel.AirmarReaderUp() if new_nodes_status.airmar_reader == 1 else eel.AirmarReaderDown()
        if new_nodes_status.battery_monitor != self.current_node_states.battery_monitor:
            eel.BatteryMonitorUp() if new_nodes_status.battery_monitor == 1 else eel.BatteryMonitorDown()
        if new_nodes_status.control_system != self.current_node_states.control_system:
            eel.ControlSystemUp() if new_nodes_status.control_system == 1 else eel.ControlSystemDown()
        if new_nodes_status.pwm_controller != self.current_node_states.pwm_controller:
            eel.PWMControllerUp() if new_nodes_status.pwm_controller == 1 else eel.PWMControllerDown()
        if new_nodes_status.trim_tab_comms != self.current_node_states.trim_tab_comms:
            eel.TrimTabCommsUp() if new_nodes_status.trim_tab_comms == 1 else eel.TrimTabCommsDown()
        self.current_node_states = new_nodes_status

        #update boat info
        eel.updateHeading(new_state.current_heading)
        eel.updateBoatSpeed(new_state.speed_kmh)
        eel.updateApparentWind(new_state.apparent_wind)
        eel.updateTrueWind(new_state.true_wind)


    def sailbot_comms(self):
        client_socket = self.connect_to_sailbot()
        client_socket.setblocking(0)
        client_socket.settimeout(0.2)
        print("Receiving data")
        last_data_time = time.time()
        received_data_bytes=[]
        while True:
            if time.time() - last_data_time > self.connection_timeout:
                print("Connection to sailbot timed out, reconnecting...")
                client_socket = self.connect_to_sailbot()
            try:
                received_data_bytes = client_socket.recv(1024)
            except:
                pass
            if len(received_data_bytes) > 0:
                received_data = pickle.loads(received_data_bytes)
                last_data_time = time.time()
                print(received_data.latitude)


    def test_ui(self):
        i = 0
        while True:
            eel.NetworkCommsUp()
            if (i % 2 == 0):
                eel.DrawLines([[51.508, -0.11, 51.503, -0.06]])
                eel.updateBoatPosition(51.504, -0.08)
            else:
                eel.DrawLines([[51.508, -0.12, 51.503, -0.07]])
                eel.updateBoatPosition(51.505, -0.09)
            i += 1

            eel.updateHeading(random.randrange(0, 360, 1))
            eel.updateBoatSpeed(random.randrange(0, 20, 1))
            eel.updateApparentWind(random.randrange(0, 360, 1))
            eel.updateTrueWind(random.randrange(0, 360, 1))
            sleep(1)

def main():
    ui = UI()
    comms_thread = threading.Thread(target=ui.sailbot_comms, daemon=True)
    comms_thread.start()
    #ui_update_thread = threading.Thread(target=ui.test_ui, daemon=True)
    #ui_update_thread.start()
    say_hello_py('Python World!')
    eel.say_hello_js('Python World!')  # Call a Javascript function
    if CURRENT_OS == OS.WINDOWS:
        eel.start('telemetry.html', mode='custom', cmdline_args=['node_modules/electron/dist/electron.exe', '.'])
    elif CURRENT_OS == OS.LINUX:
        eel.start('telemetry.html', mode='custom', cmdline_args=['node_modules/electron/dist/electron', '.'])

if __name__ == "__main__":
    main()