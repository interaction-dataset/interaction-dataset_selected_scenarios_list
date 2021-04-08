#!/usr/bin/env python

import numpy as np
import argparse

from utils import dataset_reader
from utils import dataset_types
from utils import dict_utils

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, help="Path to the track file", nargs="?")
    args = parser.parse_args()

    if args.filename is None:
        raise IOError("You must specify a filename. Type --help for help.")

    track_dictionary = dataset_reader.read_tracks(args.filename)

    print("Found " + str(len(track_dictionary)) + " object tracks.")

    ################################################################################################
    ################################################################################################

    ### Input parameters, change these
    threshold_heading_cos_sim = -0.85; # [-1,1], <0 means closing in, >0 means getting farther away
    threshold_relative_spd    = 2; # m/s, I guess
    threshold_displacement    = 15; # m, I guess

    ################################################################################################
    ################################################################################################

    ## find first and last timestamp in the whole trackfile
    list_of_time_stamp_ms_first_for_all_vehicles  = [];
    list_of_time_stamp_ms_last_for_all_vehicles   = [];
    for i in range(0,len(track_dictionary)):
        track = dict_utils.get_value_list(track_dictionary)[i]
        list_of_time_stamp_ms_first_for_all_vehicles.append(track.time_stamp_ms_first)
        list_of_time_stamp_ms_last_for_all_vehicles.append(track.time_stamp_ms_last)
    time_stamp_ms_sweep_start = min(list_of_time_stamp_ms_first_for_all_vehicles)
    time_stamp_ms_sweep_stop = max(list_of_time_stamp_ms_last_for_all_vehicles)

    ## just init
    vehicle_id_latch = None
    other_vehicle_id_latch = None

    ## sweep over all timestamps
    for time_stamp_ms_sweep in range(time_stamp_ms_sweep_start , time_stamp_ms_sweep_stop, 100):

        ## first check which vehicles exist in the scene, make a list
        array_matching_vehicles = (time_stamp_ms_sweep >= np.asarray(list_of_time_stamp_ms_first_for_all_vehicles)) & \
                                  (time_stamp_ms_sweep <= np.asarray(list_of_time_stamp_ms_last_for_all_vehicles))
        list_online_vehicles    = array_matching_vehicles.nonzero()[0].tolist()
        
        ## then compute the probability of each vehicle ramming into another vehicle on the scene 
        ## (like a fully connected, undirected graph)
        for i, vehicle in enumerate(list_online_vehicles):
            
            list_other_vehicles = [x for j,x in enumerate(list_online_vehicles) if j!=i]
            for other_vehicle in list_other_vehicles:
                victim = dict_utils.get_value_list(track_dictionary)[vehicle].motion_states[time_stamp_ms_sweep]
                pos_victim = np.asarray( [ victim.x, victim.y ] );
                spd_victim = np.asarray( [ victim.vx, victim.vy ] );

                ## perpet as in PERPETrator 
                perpet = dict_utils.get_value_list(track_dictionary)[other_vehicle].motion_states[time_stamp_ms_sweep]
                pos_perpet = np.asarray( [ perpet.x, perpet.y ] );
                spd_perpet = np.asarray( [ perpet.vx, perpet.vy ] );
                
                displacement     = pos_perpet - pos_victim;
                displacement_mag = np.linalg.norm(displacement);
                relative_spd     = spd_perpet - spd_victim;
                relative_spd_mag = np.linalg.norm(relative_spd);
                cosine_simil     = np.dot(displacement, relative_spd)/(np.linalg.norm(displacement)*np.linalg.norm(relative_spd))
                
                ## Collision probability metric is defined very loosely here, this definitely needs to change 
                ## ideally it should be the somewhat conditioned version of the "collision index" in 
                ## N. Kaempchen, "Situation Assessment of an Autonomous Emergency Brake for Arbitrary V2V Collision Scenarios" 
                
                ## if they're accelerated towards each other, mainly longitudinal
                if cosine_simil < threshold_heading_cos_sim: 
                    ## if they're "close enough"
                    if displacement_mag < threshold_displacement:
                        ## if their relative speed is "large enough"
                        if relative_spd_mag > threshold_relative_spd:
                            if not ( (vehicle_id_latch == vehicle) and (other_vehicle_id_latch == other_vehicle) ):
                                scenario_name_from_input_path   = args.filename.split('/')[-2]
                                trackfile_name_from_input_path  = args.filename.split('/')[-1]
                                trackfile_id = trackfile_name_from_input_path[-7:-4]
                                with open('../lists/' + scenario_name_from_input_path + '_' + trackfile_name_from_input_path[0:-4] + '.csv','a') as fd:
                                    fd.write(scenario_name_from_input_path + ',' + trackfile_id + ',' + str(time_stamp_ms_sweep) + ',' + str(vehicle+1) + ',' + str(other_vehicle+1) + '\n')
                                    print('Probable longitudinal collision between vehicles:', vehicle+1, ' and ', other_vehicle+1, ', starting at time:', time_stamp_ms_sweep)
                            vehicle_id_latch = vehicle
                            other_vehicle_id_latch = other_vehicle
            
            # undirected graph, so checking for a connection only once
            list_online_vehicles.remove(vehicle)
