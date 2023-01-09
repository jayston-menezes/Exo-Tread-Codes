import numpy as np
import pandas as pd
import Mat_File_Reader
from scipy.interpolate import interp1d
import argparse

my_parser = argparse.ArgumentParser(prog='Matlab & Csv Processing Code',
                                        description='Sync Treadmill & Exoboot Data',
                                        epilog='Enjoy the program! :)')
my_parser.add_argument('-csv', '--csv_filename', action='store', type=str, required=False, default=False)
my_parser.add_argument('-mat', '--mat_filename', action='store', type=str, required=False, default=False)
args = my_parser.parse_args()

try:
    temp_str = str(args.csv_filename) + '_RIGHT.csv'
    df_right = pd.read_csv('exo_data/'+ str(args.csv_filename) + '_RIGHT.csv')
    temp_str = str(args.csv_filename) + '_LEFT.csv'
    df_left = pd.read_csv('exo_data/' + str(args.csv_filename) + '_LEFT.csv')
    temp_str = str(args.mat_filename) + '.mat'
    file_name = str(args.mat_filename) +'.mat'
    df_list = [df_right, df_left]
except:
    raise ValueError(temp_str + ' cannot be read. Please check the file.')

start_timestamp_dict = {}

for df in [[df_list[0], 'Right Sync Timestamp'], [df_list[1], 'Left Sync Timestamp']]:
    side_timestamp = df[1]
    for i in range(len(df[0]['sync'])):
        if df[0]['sync'][i] == 0:
            start_timestamp_dict[side_timestamp] = [df[0]['loop_time'][i], side_timestamp]
            break
        else:
            pass

for start_timestamp in start_timestamp_dict:
    if start_timestamp == 'Right Sync Timestamp':
        time_data_1200_right_ls = list(np.arange(start_timestamp_dict[start_timestamp][0], df_right['loop_time'].iloc[-1], 1/1200))
        time_data_1200_right_ls.append(df_right['loop_time'].iloc[-1])
    else:
        time_data_1200_left_ls = list(np.arange(start_timestamp_dict[start_timestamp][0], df_left['loop_time'].iloc[-1], 1/1200))
        time_data_1200_left_ls.append(df_left['loop_time'].iloc[-1])

for confirm_timestamp in start_timestamp_dict:
    if confirm_timestamp[0]:
        print(str(confirm_timestamp) + ' found!\n')
    else:
        raise ValueError(str(confirm_timestamp) + 'not found. Quitting Program!')

print('Reading .mat file and acquiring data....\n')
filtered_force_data_right_x, filtered_force_data_right_y, filtered_force_data_right_z, filtered_force_data_left_x, filtered_force_data_left_y, filtered_force_data_left_z = Mat_File_Reader.load_mat_file_and_filter_data(file_name)

print('Creating Linear Interpolation Functions....\n')
interpolation_func_r_fx = interp1d(time_data_1200_right_ls, filtered_force_data_right_x[0:len(time_data_1200_right_ls)], 'cubic')
interpolation_func_r_fy = interp1d(time_data_1200_right_ls, filtered_force_data_right_y[0:len(time_data_1200_right_ls)], 'cubic')
interpolation_func_r_fz = interp1d(time_data_1200_right_ls, filtered_force_data_right_z[0:len(time_data_1200_right_ls)], 'cubic')
interpolation_func_l_fx = interp1d(time_data_1200_left_ls, filtered_force_data_left_x[0:len(time_data_1200_left_ls)], 'cubic')
interpolation_func_l_fy = interp1d(time_data_1200_left_ls, filtered_force_data_left_y[0:len(time_data_1200_left_ls)], 'cubic')
interpolation_func_l_fz = interp1d(time_data_1200_left_ls, filtered_force_data_left_z[0:len(time_data_1200_left_ls)], 'cubic')

interpolation_functions = [[interpolation_func_r_fx, interpolation_func_r_fy, interpolation_func_r_fz],
                           [interpolation_func_l_fx, interpolation_func_l_fy, interpolation_func_l_fz]]
new_columns_name = [['Treadmill Force X', 'Treadmill Force Y', 'Treadmill Force Z'],
                    ['Treadmill Force X', 'Treadmill Force Y', 'Treadmill Force Z']]

print('Interpolating based on Time Data....\n')

start_timestamp_ls = ['Right Sync Timestamp', 'Left Sync Timestamp']
for df_iter in range(len(df_list)):
    df = df_list[df_iter]
    for x_y_z in range(len(interpolation_functions[df_iter])):
        temp_list = list()
        sync_timestamp_reached = False
        for iter_var in range(len(df)):
            if df['sync'][iter_var] == 0:
                sync_timestamp_reached=True
            if sync_timestamp_reached:
                temp_list.append(interpolation_functions[df_iter][x_y_z](df['loop_time'][iter_var]))
            else:
                temp_list.append(0)
        df[new_columns_name[df_iter][x_y_z]] = temp_list

print('Creating .csv files....\n')

df_right.to_csv('Right_Exoboot_Post_Processed_Data.csv', index=False)
df_left.to_csv('Left_Exoboot_Post_Processed_Data.csv', index=False)

print('Done!')







