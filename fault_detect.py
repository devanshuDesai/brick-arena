""" Fault detection for Supply Air Flow

Tests whether the air flow (Actual Sup Flow) responds to changes in the room's air flow setpoint
(Actual Sup Flow SP). 

This can be achieved by calling the check_if_consistent function which takes as input a 
dictionary of room: setpoint pairs. It actuates on the given rooms to the specified setpoint
and observes whether the Actual Sup Flow responds accordingly. It then returns a dictionary of
results from each room in the form 
{
    'rm-xxxx': [setpoint, actual, percentage, [true | false]]
}
with true for success and false for failure.

NOTE: This process will typically take between 5 to 10 minutes (worst case even up to ~15 min) due
    the building_depot refresh rate. Also, this script can be modified to check other types of 
    sensors by changing the ACTUATE_SENSOR and OBSERVE_SENSOR as desired. 
"""

import sys
import arrow
import time
import pandas as pd
from datetime import timedelta
from building_depot import DataService
from pprint import pprint

TRYLIMIT = 2 # number of times to attempt actuation on room
ACTUATE_SENSOR = 'Actual Sup Flow SP' # sensor to actuate on
OBSERVE_SENSOR = 'Actual Supply Flow' # sensor to check for correct response to change in ACTUATE_SENSOR
MARGIN_OF_ERROR = 0.95 # minimum (actual/setpoint) value that is considered successful
WAIT_TIME = 5 # maximum time in minutes between actuate and observe times to determine that room is successful or failed

PT = 'US/Pacific'

bd_username = "genie_controller@ucsd.edu"
bd_api_key = "313b0b78-7981-45ee-81d4-0fbe87963110"
dataservice_url = "https://bd-datas1.ucsd.edu"
ds = DataService(dataservice_url, bd_api_key, bd_username)

uuids = {} # hold sensor uuids for each room
time_actuated = {} # records when each room was actuated

# types of sensors being observed
templates = {
    OBSERVE_SENSOR,
    ACTUATE_SENSOR,
}

time_format = 'YYYY-MM-DD HH:mm:ss'

# preparation of the experiment to obtain the sensor list
def obtain_uuid_list(room_list):
    data = {}
    for room in list(room_list.keys()):
        print(f"Obtaining uuids for {room}")
        query = {
            'room': room
        }
        resp = ds.list_sensors(query)
        data = {sensor['template']: sensor['uuid'] for sensor in resp['sensors'] if sensor['template'] in templates}
        uuids[room] = data

# perform setpoints actuate/relinquish
def actuate(rooms_dict, relinquish=False):
    records = {} # store the posted data pair (as a dict for consistence) of each room
    successfully_actuated = {} # mark if succesfully actuated for each room
    count = 0 # record how many rounds of {actuation + validation} has been done
    failed_write = [] # track rooms with that fail actuation

    if relinquish:
        print("Begin relinquish...")
    else:
        print("Begin actuation...")
    while count < TRYLIMIT:
        print(f'ROUND {count}')
        # attempt to actuate on each room
        for room, value in rooms_dict.items():
            # skip the actuated rooms during retry rounds
            if count != 0 and successfully_actuated[room]:
                continue
            # try to obtain the sensor uuid for that room
            try:
                sensor_uuid = uuids[room][ACTUATE_SENSOR]
            except KeyError:
                print(f'{room} does not have sensor point for {ACTUATE_SENSOR}, skipped.')
                continue
            # set value to -1 in relinquish mode
            if relinquish == True:
                value = -1
            
            current_time = arrow.now()
            formatted_time = current_time.format(time_format)
            print(f'Change {room}\'s sensor value to {value} at {formatted_time}...')
            # make record history
            records[room] = {str(formatted_time): value}
            successfully_actuated[room] = False 

            try:
                time.sleep(3) # sleep for some time per each actuation to avoid congestion on the bd server
                res = ds.put_timeseries_datapoints(sensor_uuid, 'PresentValue', [{str(current_time): value}] )
                time_actuated[room] = current_time
                if room in failed_write:
                    failed_write.remove(room)
            except:
                print(f"{room}: Failed to post timeseries data {value} to sensor")
                failed_write.append(room)

        init_time = arrow.now()
        # check for changes in ACTUATE_SENSOR for up to 7 minutes
        while arrow.now() - init_time < timedelta(minutes=7):
            # check for every 30 seconds
            time.sleep(15)
            for room, value in rooms_dict.items():
                # skip this room if it's already succesfully actuated
                try:
                    if successfully_actuated[room] is True:
                        continue
                except KeyError:
                    print(f'{room} does not have sensor point for {ACTUATE_SENSOR}, skipped.')
                    continue
                # skip this room if it's never written
                if room in failed_write:
                    continue
                # get the sensor uuid of this room
                try:
                    sensor_uuid = uuids[room][ACTUATE_SENSOR]
                except KeyError:
                    print(f'{room} does not have sensor point for {ACTUATE_SENSOR}, skipped.')
                    continue
                # get the current timeseries datapoint
                try: 
                    new = ds.get_latest_timeseries_datapoint(sensor_uuid, 'PresentValue')
                except:
                    print(f'Failed to get latest datapoint for {sensor_uuid}')
                    continue
                new_data = list(new['timeseries'][0].items()) # a list of sensor data dictionary
                old_data = list(records[room].items())
                new_time = arrow.get(new_data[0][0]).format(time_format)
                new_value = new_data[0][1]
                old_time = arrow.get(old_data[0][0]).format(time_format)
                old_value = old_data[0][1]
                # check if the actuation is done (value the same and newer timestamp)
                if (not relinquish) and (new_value == old_value) and (new_time > old_time):
                    successfully_actuated[room] = True
                    print(f'{room} has been actuated! (old | new): {old_value} | {new_value}')
                # check if the relinquish is done (value larger than old_value (-1) and value not
                # equal to the previously posted value and has newer timestamp)
                elif (relinquish) and (new_value > old_value) and (new_time > old_time):
                    successfully_actuated[room] = True
                    print(f'{room} has been relinquished! (old | new): {old_value} | {new_value}')
                else:
                    print(f'{room} (old | new): {old_value} | {new_value}')
    
            # quit the process if all sensors are successfully actuated
            if list(successfully_actuated.values()).count(True) == len(successfully_actuated):
                print('All actuation done!')
                return

        for room, actuated in successfully_actuated.items():
            if not actuated:
                action = "relinquished" if relinquish else "actuated"
                print(f"{room}'s sensor failed {action} in Round {count}.")

        # not all successful, add counter
        count += 1

    # for rooms that fail actuation all rounds
    for room, actuated in successfully_actuated.items():
        if not actuated:
            action = "relinquished" if relinquish else "actuated"
            print(f"WARNING: {room}'s sensor failed {action}.")

# check the value of OBSERVE_SENSOR
def observe(room, value):
    actual_value = -2 # -2 represents error
    timestamp = -1
    try:
        sensor_uuid = uuids[room][OBSERVE_SENSOR]
    except KeyError:
        print(f"Unable to retrieve uuid of {OBSERVE_SENSOR} for {room}")
        return actual_value

    # get data from OBSERVE_SENSOR
    try:
        data = ds.get_latest_timeseries_datapoint(sensor_uuid, 'PresentValue')
        data_list = list(data['timeseries'][0].items())
        actual_value = data_list[0][1]
        timestamp = arrow.get(data_list[0][0]).to(PT)
    except:
        print("Failed")
        return actual_value

    print(f"{room} (SP | Actual): {value} | {actual_value} at {timestamp.format(time_format)}")
    return actual_value


def check_if_consistent(rooms_dict):
    # actuate on each room in dictionary
    obtain_uuid_list(rooms_dict)
    print("Actuate...")
    actuate(rooms_dict)
    
    sensor_data = {} # hold value of OBSERVE_SENSOR
    finished = [] # holds successful_rooms

    print("Observe...")
    init_time = arrow.now()
    while arrow.now() - init_time <= timedelta(minutes=WAIT_TIME):
        time.sleep(15)
        for room, value in rooms_dict.items():
            if room in finished:
                continue

            # get OBSERVE_SENSOR value
            actual_value = observe(room, value)

            # classify whether room failed or not based on OBSERVE_SENSOR value
            if actual_value == -2:
                result = "No value" # happens when there is error retrieving sensor data
                finished.append(room)
            elif actual_value == 0: # to avoid division by 0
                result = False
            elif (actual_value / value) >= MARGIN_OF_ERROR:
                result = True
                finished.append(room)
            else:
                result = False
            # info for each room will be in the form: [setpoint, actual_value, percentage, true/false (success/failure)]
            sensor_data[room] = [value, actual_value, f'{100 * actual_value/value:.2f}', result]

        if len(sensor_data) == len(finished):
            break

    pprint(sensor_data)
    print('Relinquishing...')
    actuate(rooms_dict, relinquish=True)
    return sensor_data

    # returns values as a DataFrame
    # return pd.DataFrame.from_dict(sensor_data, orient='index', columns=columns_list) 
    # columns_list = ['date', 'time', 'SP', 'Actual', 'Result'] # columns for dataframe

if __name__ == "__main__":
    # only works for checking individual rooms
    if len(sys.argv) != 3:
        print("Invalid arguments\nUsage: python fault_detect.py room_num setpoint")
    else:
        check_if_consistent({sys.argv[1], sys.argv[2]})

# example usage:
#
# rooms_dict = {
#     "rm-2126": 540,
#     "rm-1231": 650,
#     "rm-2136": 215,
#     "rm-3130": 540
# }

# check_if_consistent(rooms_dict)