#!/usr/bin/env python

import struct, sys, threading, time

from pymavlink import mavutil
from pymavlink.dialects.v10 import gtri_uav

gtri_xml_path="/home/michael/uav-arobs/gtri-uav/uav_resources/uav-messages/mavlink_message_definitions/v1.0/gtri_uav.xml"

UAV_SUBNET="192.168.90.255"
DEFAULT_UAV_PORT=14550

#TODO: need targets based on UAVID
uav_ids = [2,4]
ids_to_remove = []
uav_params = {}
target_component = 1
param_provider = "A/P" #ATMY or A/P
done_checking = False
previous_rcv_time = time.time()

mavutil.set_dialect("gtri_uav")

master = mavutil.mavlink_connection(
    "udpin:" + UAV_SUBNET + ":" + str(DEFAULT_UAV_PORT), dialect="gtri_uav")
    #"udpbcast:" + UAV_SUBNET + ":" + str(DEFAULT_UAV_PORT), dialect="gtri_uav")

out = mavutil.mavlink_connection(
    "udpbcast:" + UAV_SUBNET + ":" + str(DEFAULT_UAV_PORT), dialect="gtri_uav")

def uint_to_float(val_int):
    s = struct.pack(">I", val_int)
    return float(struct.unpack(">f", s)[0])

def uint_to_int(val_int):
    s = struct.pack(">I", val_int)
    return struct.unpack(">i", s)[0]

def to_uint(val):
    if type(val) == float:
        s = struct.pack(">f", val)
    elif type(val) == int:
        s = struct.pack(">i", val)
    elif type(val) == bool:
        s = struct.pack(">b", val)

    return struct.unpack(">I", s)[0]

def isclose(a, b, rel_tol=1e-02):
    #return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)))
    val = abs(abs(a)-abs(b))
    #print ("diff: %f" % val)
    return val >= rel_tol

def verify_these_params_for_all_uavs(blessed_param_file):
    global uav_ids, uav_params, out, param_provider, done_checking, previous_rcv_time

    params_to_check = {}

    with open(blessed_param_file, 'r') as f:
        for line in f:
            tokens = line.split()
            if len(tokens) > 1:
                params_to_check[tokens[0]] = tokens[1]

    #clear and initialize dictionaries of each uav's parameter list
    uav_params = {}
    for next_uav_id in uav_ids:
        uav_params[next_uav_id] = {}

        ##get all parameters from the autopilot into gtri-uav:
        #out.mav.param_get_all_send(255, next_uav_id, param_provider, 1826605139)
        #wait for parameters to arrive on the autopilot:
        #print("Waiting for params to arrive at autonomy for uav %d" % next_uav_id)
        #time.sleep(15)
        
    #get parameters from all robots
    for next_uav_id in uav_ids:
        previous_rcv_time = time.time()

        print("Getting local copy of params for uav %d" % next_uav_id)
        success = True
        while (len(uav_params[next_uav_id]) < len(params_to_check) 
                and success == True):
            
            #print " %d %d " % (len(uav_params[next_uav_id]), len(params_to_check))
            for param in params_to_check:
                if param in uav_params[next_uav_id]:
                    continue #already got it

                #print param
                out.mav.param_get_by_name_send(255, next_uav_id,
                    param_provider, param)
                #print "Asking for %s from %d" % (param, next_uav_id)
                #don't deluge them :)
                time.sleep(0.01)
            
            if time.time() - previous_rcv_time > 6:
                print "Timed out trying to get params for UAV %d" % next_uav_id
                ids_to_remove.append(next_uav_id) 
                success = False

            #wait a bit between sets of asks
            time.sleep(2)

        if (success):
            print "Got all %d params for UAV %d" % (len(uav_params[next_uav_id]), next_uav_id)
       
    if len(ids_to_remove) > 0:
        for next_id in ids_to_remove:
            uav_params.pop(next_id, None)
            uav_ids.remove(next_id)

    #now verify the lists of parameters
    for next_uav_id in uav_ids:
        print "ID: %d" % next_uav_id
        for param in sorted(params_to_check):
            try:
                if (isclose(float(uav_params[next_uav_id][param]),
                        float(params_to_check[param]))):
                    print "%s, expected %s != UAV %d set to %s" % (param, \
                            params_to_check[param], next_uav_id, \
                            uav_params[next_uav_id][param])
            except:
                print "Excpetion with param %s on uav %d " % (param, next_uav_id)

    done_checking = True

def message_handler_thr():
    global previous_rcv_time
    while True:
        m = master.recv_msg()
        if m is None:
            continue

        if m.get_type() == "PARAM_DESCRIPTION":
            #print "saw a param description message!"
            #print m.sender_id
            #print m.name
            #print m.value
            #print m.total
            #print m.valid
            if m.sender_id in uav_params:
                uav_params[m.sender_id][m.name] = uint_to_float(m.value)
                previous_rcv_time = time.time()
                #print "%s %f" % (m.name, uint_to_float(m.value))
        #if m.get_type() == "PARAM_HASHES":
        #    print "saw a param hashes message"
        #    print "%d %d %s %d %d" % (m.sender_id, m.target_system, m.provider_name, m.names_hash, m.full_hash)

        #time.sleep(0.1)
t = threading.Thread(target=message_handler_thr, name="message_handler_thr")
t.daemon = True
t.start()

#TODO: un-hardcode this
verify_these_params_for_all_uavs("/home/michael/devel/incantations/paramChecker/s1000_cuas.parm")

while done_checking == False:
    time.sleep(1)
