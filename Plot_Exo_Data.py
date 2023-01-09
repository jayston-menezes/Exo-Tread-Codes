import matplotlib.pyplot as plt
import pandas as pd
import os
import argparse

def print_options(is_vnmc_included_pf, is_vnmc_included_nf, additional_exo_data_pf, additional_exo_data_nf):

    columns_dict = {'1': [['accel_x', 'accel_y', 'accel_z'], (3, 1), 'Acceleration Data'],
                    '2': [['gyro_x', 'gyro_y', 'gyro_z'], (3, 1), 'Gyro Data'],
                    '3': [['motor_angle', 'motor_velocity', 'motor_current'], (3, 1), 'Motor Data'],
                    '4': [['ankle_angle', 'ankle_velocity', 'ankle_torque_from_current'], (3, 1), 'Ankle Data'],
                    '5': [['did_heel_strike', 'gait_phase', 'did_toe_off', 'stride_duration'], (2, 2), 'Gait Data'],
                    '6': [['commanded_current', 'commanded_position', 'commanded_torque'], (3, 1), 'Commanded Data'],
                    '7': [['slack', 'temperature'], (2, 1), 'Slack and Exo Temperature Data']
                    }

    if is_vnmc_included_nf and is_vnmc_included_pf: vnmc_string = 'Past Data & New Data'
    if is_vnmc_included_pf: vnmc_string = 'Past Data Only'
    if is_vnmc_included_nf: vnmc_string = 'New Data Only'

    if additional_exo_data_nf and additional_exo_data_pf: add_exo_data_string = 'Past Data & New Data'
    if additional_exo_data_pf: add_exo_data_string = 'Past Data Only'
    if additional_exo_data_nf: add_exo_data_string = 'New Data Only'

    print_string, count, options_list = '' , 0, list()
    for keys in columns_dict:
        count = count + 1
        print_string = print_string + str(count) + ': ' + columns_dict[keys][2] + '\n'

    if is_vnmc_included_pf or is_vnmc_included_nf:
        count = count + 1
        columns_dict[str(count)] = list([['vnmc_torque', 'mtu_force', 'length_CE', 'velocity_CE', 'muscle_stimulation', 'ankle_angle'], (3,2), 'VNMC Data'])
        print_string = print_string + str(count) + ': ' + columns_dict[str(count)][2] + ' (' + vnmc_string + ')' + '\n'

    if additional_exo_data_pf or additional_exo_data_nf:
        count = count + 1
        columns_dict[str(count)] = list([['commanded_voltage', 'commanded_motor_impedance', 'controller', 'control_state'], (2,2), 'Additional Exo Data'])
        print_string = print_string + str(count) + ': ' + columns_dict[str(count)][2] + ' (' + add_exo_data_string + ')' + '\n'

    print(print_string)

    return columns_dict, count

def get_control_states(data, length_1, length_2):

    new_data = data.iloc[length_1: length_2]
    new_data.index = range(len(new_data))
    start_stamps, end_stamps, control_state_stamps, store_control_state = list(), list(), list(), None

    for i in range(len(new_data)):
        if store_control_state is None:
            store_control_state = new_data['control_state'][i]
            start_stamps.append(new_data['loop_time'][i])
            control_state_stamps.append(new_data['control_state'][i])
        if store_control_state != new_data['control_state'][i]:
            store_control_state = new_data['control_state'][i]
            start_stamps.append(new_data['loop_time'][i])
            control_state_stamps.append(new_data['control_state'][i])
            end_stamps.append(new_data['loop_time'][i - 1])
        if i == len(new_data) - 1:
            end_stamps.append(new_data['loop_time'][i - 1])

    return start_stamps, end_stamps, control_state_stamps


def get_len_from_seconds(length_1, length_2, new_data_file):
    length_list = list()
    for i in [length_1, length_2]:
        for j in range(len(new_data_file)):
            if float(new_data_file['loop_time'][j]) >= float(i):
                length_list.append(j)
                break
            else:
                pass
    length_1 = length_list[0]
    length_2 = length_list[1]

    return length_1, length_2


def get_data_from_input(input_from_user, new_data_file, past_data_file):
    list_of_input = input_from_user.split()
    try:
        if len(list_of_input) == 1:
            choice_of_plot = str(input_from_user)
            length_1 = 0
            length_2 = new_data_file['loop_time'].iloc[-1]
        elif len(list_of_input) == 2:
            choice_of_plot = str(list_of_input[0])
            length_1 = 0
            length_2 = float(list_of_input[1])
        elif len(list_of_input) == 3:
            choice_of_plot = str(list_of_input[0])
            length_1 = float(list_of_input[1])
            length_2 = float(list_of_input[2])
        elif not list_of_input:
            choice_of_plot, length_1, length_2 = '', None, None
            return length_1, length_2, choice_of_plot
        else:
            choice_of_plot, length_1, length_2 = 'a', None, None
            return length_1, length_2, choice_of_plot
    except:
        print('\nInput not recognized. Please enter float and integers only.')
        return

    length_1, length_2 = get_len_from_seconds(length_1, length_2, new_data_file)

    return length_1, length_2, int(choice_of_plot)


def plotter(new_data_file, past_data_file, past_data_include):

    loop_choice_of_plot = True

    if 'controller' in list(past_data_file.columns): is_vnmc_included_pf = True if 'ControllerUsed.VirtualNeuromusuclarController' in set(past_data_file['controller']) else False
    else: is_vnmc_included_pf = False
    if 'controller' in list(new_data_file.columns): is_vnmc_included_nf = True if 'ControllerUsed.VirtualNeuromusuclarController' in set(new_data_file['controller']) else False
    else: is_vnmc_included_nf = False

    additional_exo_data_pf = True if ('controller' in list(past_data_file.columns) and
                                      'control_state' in list(past_data_file.columns) and
                                      'commanded_voltage' in list(past_data_file.columns) and
                                      'commanded_motor_impedance' in list(past_data_file.columns)) else False
    additional_exo_data_nf = True if ('controller' in list(new_data_file.columns) and
                                      'control_state' in list(new_data_file.columns) and
                                      'commanded_voltage' in list(new_data_file.columns) and
                                      'commanded_motor_impedance' in list(new_data_file.columns)) else False

    columns_dict, count = print_options(is_vnmc_included_pf, is_vnmc_included_nf, additional_exo_data_pf, additional_exo_data_nf)

    while loop_choice_of_plot:

        input_from_user = input('\nType Number and Range of Duration (in secs) for Plot + Enter. Press only Enter to Exit: ')

        length_1, length_2, choice_of_plot = get_data_from_input(input_from_user, new_data_file, past_data_file)

        if choice_of_plot == ' ' or choice_of_plot == '': break
        elif str(choice_of_plot) not in list(map(str, list(range(1, count+1)))):
            print('\nInput not recognized. Please enter the correct number for corresponding plot and duration in seconds.')
            continue

        past_data_loop_time = past_data_file['loop_time'][length_1:length_2]
        new_data_loop_time = new_data_file['loop_time'][length_1:length_2]

        fig, axs = plt.subplots(int(columns_dict[str(choice_of_plot)][1][0]), int(columns_dict[str(choice_of_plot)][1][1]))

        past_data_file_ls, new_data_file_ls = list(), list()

        for col_name in columns_dict[str(choice_of_plot)][0]:
            if past_data_include:
                past_data_file_ls.append(past_data_file[columns_dict[str(choice_of_plot)][0][col_name]][length_1:length_2])
            new_data_file_ls.append(new_data_file[col_name][length_1:length_2])

        plot_axs_ls = list()
        for i in range(int(columns_dict[str(choice_of_plot)][1][0])):
            for j in range(int(columns_dict[str(choice_of_plot)][1][1])):
                plot_axs_ls.append([i, j])

        for iter_var in range(len(plot_axs_ls)):
            if iter_var > len(columns_dict[str(choice_of_plot)][0])-1: break
            if int(columns_dict[str(choice_of_plot)][1][1]) != 1:
                if past_data_include:
                    axs[plot_axs_ls[iter_var][0], plot_axs_ls[iter_var][1]].plot(past_data_loop_time, past_data_file_ls[iter_var],
                                   label= 'Past ' +  ' '.join(columns_dict[str(choice_of_plot)][0][iter_var].split('_')).title(),
                                   color='gray', linewidth=5)
                axs[plot_axs_ls[iter_var][0], plot_axs_ls[iter_var][1]].plot(new_data_loop_time, new_data_file_ls[iter_var],
                               label='New ' +  ' '.join(columns_dict[str(choice_of_plot)][0][iter_var].split('_')).title(),
                               linewidth=1)
                axs[plot_axs_ls[iter_var][0], plot_axs_ls[iter_var][1]].set_title(' '.join(columns_dict[str(choice_of_plot)][0][iter_var].split('_')).title())
            else:
                if past_data_include:
                    axs[plot_axs_ls[iter_var][0]].plot(past_data_loop_time, past_data_file_ls[iter_var],
                                    label='Past ' + ' '.join(columns_dict[str(choice_of_plot)][0][iter_var].split('_')).title(),
                                    color='gray', linewidth=5)
                axs[plot_axs_ls[iter_var][0]].plot(new_data_loop_time, new_data_file_ls[iter_var],
                                label='New ' + ' '.join(columns_dict[str(choice_of_plot)][0][iter_var].split('_')).title(),
                                linewidth=1)
                axs[plot_axs_ls[iter_var][0]].set_title(' '.join(columns_dict[str(choice_of_plot)][0][iter_var].split('_')).title())

            fig.suptitle(columns_dict[str(choice_of_plot)][2] + " - Time (X-axis) vs. Data (Y-axis)")

        colors = {'ReelOutState': 'silver', 'SwingState': 'red', 'ReelInState': 'white',
                  'StanceState': 'yellow', 'StandingState': 'rgb(255, 255, 204)', 'SlipState': 'rgb(255, 255, 0)'}

        if int(columns_dict[str(choice_of_plot)][1][1]) != 1:
            if 'control_state' in list(new_data_file.columns):
                start_stamps, end_stamps, control_state_stamps = get_control_states(new_data_file, length_1, length_2)
                for row in axs:
                    for ax in row:
                        for i in range(len(start_stamps)):
                            ax.axvspan(start_stamps[i], end_stamps[i], color=colors[str(control_state_stamps[i])[13:]],
                                       alpha=0.5)
        else:
            if 'control_state' in list(new_data_file.columns):
                start_stamps, end_stamps, control_state_stamps = get_control_states(new_data_file, length_1, length_2)
                for col in axs:
                        for i in range(len(start_stamps)):
                            col.axvspan(start_stamps[i], end_stamps[i], color=colors[str(control_state_stamps[i])[13:]],
                                       alpha=0.5)
        plt.show()
        # plt.savefig('.png')

def parse_args():
    my_parser = argparse.ArgumentParser(prog='Exoboot Code',
                                        description='Run Exoboot Controllers',
                                        epilog='Enjoy the program! :)')
    my_parser.add_argument('-pf', '--past_data_files', action='store',
                           type=str, required=False, default=False)
    my_parser.add_argument('-nf', '--new_data_files', action='store',
                           type=str, required=False, default=False)
    args = my_parser.parse_args()
    return args


if __name__ == '__main__':

    args = parse_args()

    past_data_file_name = args.past_data_files
    new_data_file_name = args.new_data_files

    if past_data_file_name:
        # Using Input from User
        past_data_file_left = pd.read_csv(str(past_data_file_name)+'_LEFT.csv')
        past_data_file_right = pd.read_csv(str(past_data_file_name) + '_RIGHT.csv')
    else:
        # Using Default files
        past_data_file_left = pd.read_csv("Default_Past_Data_LEFT.csv")
        past_data_file_right = pd.read_csv("Default_Past_Data_RIGHT.csv")

    if new_data_file_name:
        # Using Input from User
        new_data_file_left = pd.read_csv('exo_data/' + str(new_data_file_name)+'_LEFT.csv')
        new_data_file_right = pd.read_csv('exo_data/' + str(new_data_file_name) + '_RIGHT.csv')
        # new_data_file_left = pd.read_csv(str(new_data_file_name) + '_LEFT.csv')
        # new_data_file_right = pd.read_csv(str(new_data_file_name) + '_RIGHT.csv')
    else:
        # Using most recent files
        file_list = os.listdir("exo_data")
        file_list.sort(reverse=True)
        new_data_file_right = pd.read_csv('exo_data/' + str(file_list[0]))
        new_data_file_left = pd.read_csv('exo_data/' + str(file_list[1]))
        # print(str(file_list[0]))

    # print(new_data_file_right, new_data_file_left)
    # print(new_data_file_left['loop_time'].index)
    # print(file_list[1])

    file_lists = [new_data_file_right, new_data_file_left]

    for iter_file in range(len(file_lists)):
        temp_list = list()
        stride_duration, last_heel_strike_timestamp = 0, 0
        for iter_var in range(len(file_lists[iter_file])):
            if file_lists[iter_file]['did_heel_strike'][iter_var] == 1:
                stride_duration = file_lists[iter_file]['loop_time'][iter_var] - last_heel_strike_timestamp
                temp_list.append(stride_duration)
                last_heel_strike_timestamp = file_lists[iter_file]['loop_time'][iter_var]
            else:
                temp_list.append(stride_duration)
        file_lists[iter_file]['stride_duration'] = temp_list

    while True:

        past_data_yes_no = input('\nDo you want to plot Past Data along with New Data [y/n]:')
        if past_data_yes_no.lower() == 'y':
            past_data_include = True
            break
        elif past_data_yes_no.lower() == 'n':
            past_data_include = False
            break
        else:
            print('\nInput not understood. Type [y/n] + Enter.')

    print('''\nInput Desired Exoboot Side Plot
0: Exit Code
1: Left Side
2: Right Side''')
    while True:
        left_or_right_or_exit = input('\nEnter Left Side or Right Side or Exit:')
        if left_or_right_or_exit == '1':
            plotter(new_data_file_left, past_data_file_left, past_data_include)
        elif left_or_right_or_exit == '2':
            plotter(new_data_file_right, past_data_file_right, past_data_include)
        elif left_or_right_or_exit == '0':
            print('\nExiting Plotting Code. Thank you!')
            break
        else:
            print('\nInput not understood. Please enter desired input.')

