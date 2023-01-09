import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os

my_parser = argparse.ArgumentParser(prog='Mean & Standard Deviation Plotting Code',
                                         description='Code to be Impelemented on VNMC Data',
                                         epilog='Enjoy the program! :)')
my_parser.add_argument('-sa', '--speed_angle', action='store', type=str, required=True, default=None)
args = my_parser.parse_args()

# os.chdir(args.directory_name)
os.chdir("All_Data")
ls_filenames, new_list = os.listdir(), list()

for filename_iter in ls_filenames:
    # if 'CONFIG.csv' in filename_iter or 'RIGHT.csv' in filename_iter or 'LEFT.csv' in filename_iter or args.speed_angle in filename_iter:
    if args.speed_angle in filename_iter:
        new_list.append('_'.join(filename_iter.split('_')[:-1]))

new_list = set(new_list)
# os.chdir("../")
subject_mean = dict()
count = 0

for csv_filename in new_list:
    count += 1
    # os.chdir(args.directory_name)
    subject_num = 'Subject ' + str(count)
    print(csv_filename)
    try:
        temp_str = str(csv_filename) + '_RIGHT.csv'
        data_og_right = pd.read_csv(str(csv_filename) + '_RIGHT.csv')
        column_names = list(data_og_right.columns)
        for i in ['state_time', 'loop_time', 'did_heel_strike', 'did_toe_off', 'gait_phase','gen_var1', 'gen_var2',
                  'gen_var3', 'controller', 'control_state','gen_var4', 'gen_var1', 'status_mn', 'status_ex', 'status_re',
                  'temperature', 'heel_fsr', 'toe_fsr', 'did_slip']:
            try: column_names.remove(i)
            except: pass
        data_og_right =  data_og_right.loc[(data_og_right['loop_time'] >= 50) & (data_og_right['loop_time'] <= 110)]
        data_og_right.index = list(range(len(data_og_right)))
        temp_str = str(csv_filename) + '_LEFT.csv'
        data_og_left = pd.read_csv(str(csv_filename) + '_LEFT.csv')
        data_og_left = data_og_left.loc[(data_og_left['loop_time'] >= 50) & (data_og_left['loop_time'] <= 110)]
        data_og_left.index = list(range(len(data_og_left)))
        df_list = [data_og_right, data_og_left]
    except:
        raise ValueError(temp_str + ' cannot be read. Please check the file.')

    # os.chdir("../")
    # os.mkdir("Plots for " + str(args.speed_angle))
    # os.chdir("Plots for " + str(args.speed_angle))


    loop_time_list_left, loop_time_list_right = list(), list()

    get_indices_ls = [loop_time_list_left, loop_time_list_right]
    for iter_data_file in range(len(df_list)):
        for get_index in range(len(df_list[iter_data_file])):
            if int(df_list[iter_data_file]['did_heel_strike'][get_index]) == 1:
                get_indices_ls[iter_data_file].append(get_index)

    left_col_names_dicts, right_col_names_dicts = dict(), dict()

    dicts_right_left = [right_col_names_dicts, left_col_names_dicts]

    for iter_dict in dicts_right_left:
        for col_names in column_names:
            iter_dict[str(col_names)] = dict()

    data = df_list.copy()

    for iter_val in range(len(data)):
        loop_time_list = get_indices_ls[iter_val]
        index = iter_val
        iter_data_file = data[iter_val]
        for get_index in range(len(loop_time_list)):
            if (get_index + 1 != len(loop_time_list)):
                for iter_dict in range(len(dicts_right_left[index])):
                    dicts_right_left[index][column_names[iter_dict]]['Gait Cycle ' + str(get_index + 1)] = \
                        iter_data_file.loc[loop_time_list[get_index]:loop_time_list[get_index+1], column_names[iter_dict]]
                    dicts_right_left[index][column_names[iter_dict]]['Gait Cycle ' + str(get_index + 1)].index = \
                        list(range(1, len(dicts_right_left[index][column_names[iter_dict]]['Gait Cycle ' + str(get_index + 1)])+1))

    for iter_dict_rl in dicts_right_left:
        for iter_dict in iter_dict_rl:
            iter_dict_rl[iter_dict] = pd.DataFrame.from_dict(iter_dict_rl[iter_dict])

    for iter_dict_rl in dicts_right_left:
        for iter_dict in iter_dict_rl:
            iter_dict_rl[iter_dict][subject_num + 'Mean'] = iter_dict_rl[iter_dict].mean(axis=1)
            # iter_dict_rl[iter_dict][subject_num + 'Standard Deviation'] = iter_dict_rl[iter_dict].std(axis=1)
            # iter_dict_rl[iter_dict][subject_num + 'Mean + Standard Deviation'] = iter_dict_rl[iter_dict]['Mean'] + iter_dict_rl[iter_dict]['Standard Deviation']
            # iter_dict_rl[iter_dict][subject_num + 'Mean - Standard Deviation'] = iter_dict_rl[iter_dict]['Mean'] - iter_dict_rl[iter_dict]['Standard Deviation']

    # for iter_dict_rl in dicts_right_left:
    #     for iter_dict in iter_dict_rl:
    #         iter_df = iter_dict_rl[iter_dict]
    #         max_val_list, min_val_list = list(), list()
    #         for i in range(len(iter_df)):
    #             list_row = list()
    #             for j in range(len(iter_df.columns)-4):
    #                 error = iter_df['Mean'][i+1] - iter_df['Gait Cycle ' + str(j + 1)][i+1]
    #                 list_row.append(error)
    #             max_val_list.append(max(list_row))
    #             min_val_list.append(min(list_row))
    #         iter_df['Max Error'] = max_val_list
    #         iter_df['Min Error'] = min_val_list

subjects_dict_mean_rl = {'Right': dict(), 'Left':dict()}
subjects_dict_std_dev_rl = {'Right': dict(), 'Left':dict()}
filename_strs = ['Right', 'Left']
temp = 0
for iter_dict_rl in dicts_right_left:
    temp = temp + 1
    for iter_dict in iter_dict_rl:
        temp_df = pd.DataFrame()
        for subject_iter in range(1, len(new_list)+1):
            temp_df[str(subject_iter) + 'Mean'] = iter_dict_rl[iter_dict][str(subject_iter) + 'Mean']
        subjects_dict_mean_rl[filename_strs[temp-1]][iter_dict] = temp_df.mean(axis=1)
        subjects_dict_std_dev_rl[filename_strs[temp - 1]][iter_dict] = temp_df.std(axis=1)

# subjects_dict = pd.DataFrame.from_dict(subjects_dict)
os.chdir("../")
os.mkdir("Plots for " + str(args.speed_angle))
os.chdir("Plots for " + str(args.speed_angle))

temp = 0
for right_left in subjects_dict_mean_rl:
    # temp = temp + 1
    # count = 0
    for iter_dict in subjects_dict_mean_rl[right_left]:
        iter_df = subjects_dict_mean_rl[right_left][iter_dict]
        x = list(np.arange(0, 100, 100/len(iter_df)))
        mean_add_std = subjects_dict_mean_rl[right_left][iter_dict] + subjects_dict_std_dev_rl[right_left][iter_dict]
        mean_sub_std = subjects_dict_mean_rl[right_left][iter_dict] - subjects_dict_std_dev_rl[right_left][iter_dict]
        try:
            plt.plot(x, iter_df, 'b-', label=str(iter_dict))
            plt.fill_between(x, mean_sub_std, mean_add_std, color='b', alpha=0.2)
        except:
            # print(len(x), len(iter_df['Mean']))
            # print(str(csv_filename))
            try:
                plt.plot(x, iter_df['Mean'][:len(x)], 'b-', label=str(iter_dict))
                plt.fill_between(x, mean_sub_std[:len(x)], mean_add_std[:len(x)], color='b', alpha=0.2)
            except:
                plt.plot(x[:len(iter_df['Mean'])], iter_df['Mean'], 'b-', label=str(iter_dict))
                plt.fill_between(x[:len(iter_df['Mean'])], mean_sub_std, mean_add_std, color='b', alpha=0.2)
            # print(len(x), len(iter_df))
            # print(x, iter_dict, iter_df)
            # quit()
        # plt.fill_between(x, iter_df['Mean - Standard Deviation'], iter_df['Mean + Standard Deviation'], color='b', alpha=0.2)
        plt.title(str(iter_dict) + ' vs. Gait Cycle')
        plt.ylabel(str(iter_dict))
        plt.xlabel("Gait Cycle")
        # plt.figure(figsize=(4, 4))
        plt.legend()
        # plt.show()
        # plt.savefig(str(csv_filename) + '_' + str(iter_dict) + filename_strs[temp-1] + '_plot.png')
        plt.savefig(str(iter_dict) + filename_strs[temp-1] + '_plot.png')
        plt.close()
        # csv_filename[-6:]

print('Done!!!')
os.chdir("../")
