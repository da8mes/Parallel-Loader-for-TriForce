# Reshape H5 files into N events per file
# Author: W. Wei, M. Zhang
# python stack.py <Path1> <Path2> <events_per_output_file>
# Path1 is a file search string, such as <Path>/Pi0*.h5
# Path2 is output files, with names <Path2>_0.h5 etc.

import h5py as h5
import numpy as np
import sys, glob
import pdb

input_files = glob.glob(sys.argv[1])
output_path = sys.argv[2]
events_per_output_file = int(sys.argv[3])

output_file_counter = 0 # how many files we've written
output_data = {} # data to be written out

for input_file in input_files:

    # get info about input file
    input_file = h5.File(input_file,'r')
    print("file")
    input_file_n_events = input_file['ECAL'].shape[0]
    input_file_keys = list(input_file.keys())

    # append info to output file
    for key in input_file_keys:
        input_data = input_file[key][:]
        if key not in output_data.keys():
            output_data[key] = input_data
        else:
            output_data[key] = np.concatenate([output_data[key], input_data])
    # if we have enough events, write output files
    while output_data['ECAL'].shape[0] >= events_per_output_file:
        output_file = h5.File(output_path + "_" + str(output_file_counter) + ".h5" , 'w')
        for key in output_data.keys():
            new_shape = list(output_data[key].shape)
            new_shape[0] = 10
#             print(new_shape)
            output_file.create_dataset(key, data=output_data[key][:events_per_output_file], compression="gzip", compression_opts=1, chunks=tuple(new_shape)) 
            output_data[key] = output_data[key][events_per_output_file:]
#             print(output_data['ECAL'].shape[0])
        output_file.close()
        output_file_counter += 1

    # go to the next file
    input_file.close()

if (output_data['ECAL'].shape[0] > 0):
    print(output_data['ECAL'].shape[0], " events remaining, not written.")
    