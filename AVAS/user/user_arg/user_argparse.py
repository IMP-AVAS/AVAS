import argparse
import os
import sys



from api import  plot_dataset, plot_cavity_voltage, plot_phase, change_particle_number,\
                plot_phase_advance, plot_cavity_syn_phase

def main_argparse():
    # 创建主解析器
    parser = argparse.ArgumentParser(description="AVAS")


    # 创建子解析器
    subparsers = parser.add_subparsers(dest="function", help="Available commands")


    # 功能
    subparsers_simulation = subparsers.add_parser("simulation", help="simulation")
    subparsers_simulation.add_argument('-pp', "--projectpath", type=str, help="simulation")

    # 功能
    subparsers_scan = subparsers.add_parser("scan", help="scan")
    subparsers_scan.add_argument('-pp', "--projectpath", type=str, help="scan")

    # 功能
    subparsers_scan = subparsers.add_parser("changeNum", help="chang particle number")
    subparsers_scan.add_argument('-ip', "--infile_path", type=str, help="Path to the entry file")
    subparsers_scan.add_argument('-op', "--outfile_path", type=str, help="Path to the export file")
    subparsers_scan.add_argument('-r', "--ratio", type=int, help="multiple of particle number expansion")

    # 功能
    # subparsers_draw = subparsers.add_parser("draw_dataset", help="draw")
    # subparsers_draw.add_argument('-dp', "--dataset_path", type=str, help="scan")
    # subparsers_draw.add_argument('-num', "--num", type=int, help="scan")
    # subparsers_draw.add_argument('-m', "--BaseMassInMeV", type=float, help="scan")
    # subparsers_draw.add_argument('-freq', "--frequency", type=float, help="scan")

    # 功能
    subparsers_draw = subparsers.add_parser("plot", help="plot")
    subparsers_draw.add_argument('-pn', "--picture_name", type=str, choices=['loss', 'emittance_x', 'emittance_y', 'emittance_z', 'rms_x', 'rms_y', 'rms_xy', 'max_x', 'max_y', 'max_xy',
            'longitudinal_phase', 'energy', 'beta_x', 'beta_y', 'beta_z', 'beta_xyz', 'cavity_voltage', 'phase', 'phase_advance', 'syn_phase'],
                                 help="name of picture ")
    subparsers_simulation.add_argument('-pp', "--projectpath", type=str, help="simulation")
    subparsers_draw.add_argument('-fp', "--file_path",  nargs='+', type=str, help="path of file")
    subparsers_draw.add_argument('-m', "--mass", type=float, help="mass of particle")
    subparsers_draw.add_argument('-freq', "--frequency", type=float, help="frequency of beam")
    subparsers_draw.add_argument('-ckr', "--cavity_ke_ratio", nargs='+',  type=str, help="ratio of actual cavity voltage to ke")
    subparsers_draw.add_argument('-ot', "--out_type", type=str, help="Type control")


    # 解析命令行参数
    args = parser.parse_args()

    # 根据命令调用相应的功能和处理参数

    if args.function == "simulation":
        AVAS_simulation(args.projectpath)

    elif args.function == "scan":
        print("Calling Function 2 with param:", args.projectpath)

    elif args.function == "changeNP":
        change_particle_number(args.infile_path, args.outfile_path, args.ratio)


    elif args.function == "plot":
        dataset_list = ['loss', 'emittance_x', 'emittance_y', 'emittance_z', 'rms_x', 'rms_y', 'rms_xy', 'max_x', 'max_y', 'max_xy',
        'longitudinal_phase', 'energy', 'beta_x', 'beta_y', 'beta_z',  'beta_xyz']

        if args.picture_name in dataset_list:
            plot_dataset(args.pp, args.picture_name)

        elif args.picture_name == 'cavity_voltage':
            tmp_r = {}
            for i in range(0, len(args.cavity_ke_ratio), 2):
                tmp_r[args.cavity_ke_ratio[i]] = float(args.cavity_ke_ratio[i+1])

            plot_cavity_voltage(args.pp, tmp_r)

        elif args.picture_name == 'syn_phase':
            plot_cavity_syn_phase(args.pp)

        elif args.picture_name == 'phase':
            plot_phase(args.file_path)

        elif args.picture_name == 'phase_advance':
            plot_phase_advance(args.pp, args.out_type)

    else:
        print("No valid command provided")

if __name__ =="__main__":
    main_argparse()
