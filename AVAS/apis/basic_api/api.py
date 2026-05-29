# -- coding: utf-8 --

from core.MultiParticle import MultiParticle

from aftertreat.picture.plotdataset import PlotDataSet
from aftertreat.picture.plotphase import PlotPhase
from aftertreat.picture.plotphase2 import PlotPhase2
from aftertreat.dataanalysis.caltwiss import CalTwiss
from aftertreat.picture.plotenvbeamout import PlotEnvBeamOut

from apps.changeNp import ChangeNp
from aftertreat.picture.plotpicture import PlotCavityVoltage, PlotPhaseAdvance, PlotCavitySynPhase
from apps.matchtwiss import MatchTwiss
from apps.circlematch import CircleMatch
from aftertreat.picture.plotacc import PlotAcc
from apps.calacceptance import Acceptance
import os
from apps.basicenv import BasicEnvSim
from apps.LongAccelerator import LongAccelerator
from utils.tolattice import write_mulp_to_lattice_only_sim2
from apps.error import Errorstat, ErrorDyn, Errorstatdyn

from aftertreat.picture.ploterror import PlotErrout, PlotErr_emit_loss
from aftertreat.picture.plotdesnsity import PlotDensity, PlotDensityLevel, PlotDensityProcess

########################################################################################################################
from aftertreat.picture.plotphaseellipse import PlotPhaseEllipse
from utils.tool import format_output, generate_web_picture_param, generate_web_picture_path
from apps.diaginfo import DiagInfo
from aftertreat.dataanalysis.extodensity import ExtoDensity
from utils.inputconfig import InputConfig
from utils.change_win_to_linux import change_end_crlf
from aftertreat.picture.plotplt import PlotPlt
from aftertreat.picture.plot_edst import Plotedst
#下列为功能函数
#基础运行


# -- coding: utf-8 --

# 下列为功能函数
# 基础运行
def basic_mulp(**item):
    """
    :param project_path:
    :return:
    多粒子模拟
    """

    # else:
    project_path = item.get('project_path')

    multiparticle_obj = MultiParticle(item)

    lattice_mulp_path = os.path.join(project_path, 'InputFile', 'lattice_mulp.txt')
    lattice_path = os.path.join(project_path, 'InputFile', 'lattice.txt')
    write_mulp_to_lattice_only_sim2(lattice_mulp_path, lattice_path)

    res = multiparticle_obj.run()
    # 生成束诊文件
    # diag_item = {
    #     "project_path": project_path,
    #     "input_file": os.path.join(project_path, 'InputFile'),
    #     "output_file": os.path.join(project_path, 'OutputFile'),
    #     "diag_file_path": os.path.join(project_path, 'OutputFile', 'par_diag1.txt'),
    # }
    # obj = DiagInfo(diag_item)
    # obj.write_diag_info_to_file()
    #
    item = {"projectPath": project_path, }
    input_info = InputConfig()
    input_info = input_info.create_from_file(item)
    input_info = input_info["data"]["inputParams"]
    if input_info.get("pchistogram_start") == 1 and input_info.get("pchistogram_grid") > 0:
        # 生成密度文件
        exdata_path = os.path.join(project_path, "OutputFile", "PCHistogram.dat")

        dataset_path = os.path.join(project_path, "OutputFile", "DataSet.txt")
        target_density_path = os.path.join(project_path, "OutputFile", f"density_par.dat")

        density_obj = ExtoDensity(exdata_path, dataset_path, target_density_path)
        density_obj.generate_density_file_onestep(1)

    print('模拟结束')
    return True


# 粒子数扩充
def change_particle_number(infile_path, outfile_path, ratio):
    """
    :param infile_path: 输入
    :param outfile_path: 输出
    :param ratio: 扩大的比例
    :return:
    扩充经粒子数
    """
    v = ChangeNp(infile_path, outfile_path, ratio)
    v.run()
    return None


def match_twiss(project_path, use_lattice_initial_value=0):
    """
    twiss参数匹配
    :param project_path:
    :param use_lattice_initial_value:
    :return:
    """
    v = MatchTwiss(project_path)
    res = v.match_twiss(r"lattice_env.txt", use_lattice_initial_value)
    print('匹配结束')

    return res


def circle_match(project_path):
    """
    周期匹配
    :param project_path:
    :return:
    """
    v = CircleMatch(project_path)
    res = v.circle_match(r"lattice_env.txt")
    print('匹配结束')
    return res


def err_dyn(**item):
    """
    p跑动态误差, 静态误差将被注释掉
    :param project_path:
    :return:
    """
    default_item = {
        "project_path": None,
        "seed": 50,
        "if_normal": 1,
        "field_path": None,
        "if_generate_density_file": 1
    }
    default_item.update(item)
    v = ErrorDyn(default_item)
    res = v.run()
    print('动态误差结束')

    return res


def err_stat(**item):
    """
    :param project_path:
    :return:
    根据是否有adjust命令判断是否需要优化
    """
    default_item = {
        "project_path": None,
        "seed": 50,
        "if_normal": 1,
        "field_path": None,
        "if_generate_density_file": 1
    }
    default_item.update(item)
    v = Errorstat(default_item)
    v.run()


def err_stat_dyn(**item):
    """

    :param project_path:
    :return:
    动态误差和静态误差一起跑，
    """
    default_item = {
        "project_path": None,
        "seed": 50,
        "if_normal": 1,
        "field_path": None,
        "if_generate_density_file": 1
    }
    default_item.update(item)
    v = Errorstatdyn(default_item)
    v.run()
    return None


def basic_env(project_path, lattice):
    """

    :param project_path:
    :param lattice:
    :return:
    基础包络模拟
    """
    obj = BasicEnvSim(project_path, lattice)
    res = obj.run()
    return res


def longdistance(project_path, kind):
    obj = LongAccelerator(project_path, kind)
    obj.run()
    return None


def cal_acceptance(project_path, kind):
    obj = Acceptance(project_path)
    emit, norm_emit, x_min, xx_min = obj.cal_accptance(kind)
    return emit, norm_emit, x_min, xx_min


def plot_acc(project_path, kind):
    obj = PlotAcc(project_path)
    res = obj.run(kind)
    return res


# 下列为画图函数

# 画dataset中的数据
# def plot_dataset(project_path, picture_type, show_=1, fig=None, platform = "qt"):
#
#     """
#     :param project_path:
#     :param picture_name:
#     :param show_:
#     :return:
#     dataset文件中数据的可视化
#     """
#     dataset_path = os.path.join(project_path, "OutputFile", "dataset.txt")
#     v = PlotDataSet(dataset_path, picture_type)
#     v.get_x_y()
#     res = v.run(show_, fig)
#     return res


def plot_dataset(**item):
    # item = {project_path: , picture_type: , show_: 1, fig: None, platform: "qt", "sample_interval": 1}
    """
    :param project_path:
    :param picture_name:
    :param show_:
    :return:
    dataset文件中数据的可视化
    """
    default_item = {"projectPath": None, "pictureType": None, "show_": 0, "fig": None, "platform": "qt",
                    "sampleInterval": 1,
                    "needData": False
                    }

    default_item.update(item)

    project_path = default_item.get("projectPath")
    picture_type = default_item.get("pictureType")
    show_ = default_item.get("show_")
    fig = default_item.get("fig")
    platform = default_item.get("platform")
    sample_interval = default_item.get("sampleInterval")
    webreturn_type = default_item.get("webreturnType")
    need_data = default_item.get("needData")

    dataset_path = os.path.join(project_path, "OutputFile", "DataSet.txt")
    v = PlotDataSet(dataset_path, picture_type, sample_interval)
    v.get_x_y()

    if platform == "qt":
        output = v.run(show_, fig)

    elif platform == "web":
        # 生成文件名
        save_path = generate_web_picture_path(project_path)
        v.run(show_, fig, save_path)

        # 生成返回信息
        picture_param = {"picturePath": save_path, "pictureInfo": {}}

        if need_data is True:
            data = generate_web_picture_param(v)
            picture_param["pictureInfo"] = data

        output = format_output(**picture_param)

    return output


# 画相图
def plot_phase(dst_path, show_=1, fig = None, platform = "qt"):
    v = PlotPhase(dst_path)
    res = v.run(show_, fig)
    return res

# def plot_dst(item):
#     default_picture_type = [
#         ["x", "x1"],
#         ["y", "y1"],
#         ["phi", "w"],
#         ["z", "z1"],
#     ]
#
#     default_item = {"filePath": None, "pictureType": default_picture_type, "show_": 0, "fig": None, "platform": "qt",
#                     "sampleInterval": 1, "needData": False, "projectPath": None, "location": "out",
#                     "dst_dict": None,
#                     "twiss_dict": None}
#
#     default_item.update(item)
#     platform = default_item.get("platform")
#     project_path = default_item.get("projectPath")
#     fig = default_item.get("fig")
#     sample_interval = default_item.get("sampleInterval")
#     location = default_item.get("location")
#     show_ = default_item.get("show_")
#     picture_type = default_item.get("pictureType")
#     dst_dict = default_item.get("dst_dict")
#     twiss_dict = default_item.get("twiss_dict")
#
#
#     if platform == "qt":
#         file_path = default_item.get("filePath")
#     elif platform == "web":
#         if location == "out":
#             file_path = os.path.join(project_path, "OutputFile", default_item.get("filePath"))
#         elif location == "in":
#             file_path = os.path.join(project_path, "InputFile", default_item.get("filePath"))
#
#
#     dst_picture_item = {
#         "show_": show_,
#         "fig": fig,
#         "save_path": None,
#         "picture_type": picture_type,
#         "dst_path": file_path,
#         "dst_dict": dst_dict,
#         "twiss_dict": twiss_dict,
#     }
#
#
#     v = PlotPhase()
#
#     if platform == "qt":
#         output = v.run(dst_picture_item)
#
#     elif platform == "web":
#         try:
#             save_path = generate_web_picture_path(project_path)
#
#             dst_picture_item["save_path"] = save_path
#
#             v.run(dst_picture_item)
#             picture_param = {"picturePath": save_path}
#             output = format_output(**picture_param)
#         except Exception as e:
#             code = -1
#             msg = str(e)
#             picture_param = {"picturePath": ""}
#             output = format_output(code, msg=msg, **picture_param)
#     return output





#第二种相图画法
def plot_dst(item):
    default_item = {"dst_path": None, "picture_type": [["x", "x1"]], "show_": 0, "fig": None, "platform": "qt",
                    "sampleInterval": 1, "needData": False, "projectPath": None, "location": "out",
                    "dst_dict": None, "twiss_dict": None,
    }

    default_item.update(item)

    platform = default_item.get("platform")
    project_path = default_item.get("projectPath")
    fig = default_item.get("fig")
    sample_interval = default_item.get("sampleInterval")
    location = default_item.get("location")
    show_ = default_item.get("show_")
    dst_dict = default_item.get("dst_dict")
    twiss_dict = default_item.get("twiss_dict")
    picture_type = default_item.get("picture_type")


    if platform == "qt":
        dst_path = default_item.get("dst_path")
    elif platform == "web":
        if location == "out":
            dst_path = os.path.join(project_path, "OutputFile", default_item.get("dst_path"))
        elif location == "in":
            dst_path = os.path.join(project_path, "InputFile", default_item.get("dst_path"))

    v = PlotPhase2()

    item = {
        "show_": show_,
        "fig": fig,
        "save_path": None,
        "picture_type":picture_type,
        "dst_path": dst_path,
        "dst_dict": dst_dict,
        "twiss_dict": twiss_dict,
    }


    if platform == "qt":
        output = v.run(item)
    elif platform == "web":
        try:
            save_path = generate_web_picture_path(project_path)
            item["save_path"] = save_path
            v.run(item)

            picture_param = {"picturePath": save_path}
            output = format_output(**picture_param)
        except Exception as e:
            code = -1
            msg = str(e)
            picture_param = {"picturePath": ""}
            output = format_output(code, msg=msg, **picture_param)
    return output

def plot_edst(item):
    default_item = {"edst_path": None, "picture_type": [["x", "x1"]], "show_": 0, "fig": None, "platform": "qt",
                    "sampleInterval": 1, "needData": False, "projectPath": None, "location": "out",
                    "dst_dict": None, "twiss_dict": None,
    }

    default_item.update(item)

    platform = default_item.get("platform")
    project_path = default_item.get("projectPath")
    fig = default_item.get("fig")
    sample_interval = default_item.get("sampleInterval")
    location = default_item.get("location")
    show_ = default_item.get("show_")
    edst_dict = default_item.get("edst_dict")
    twiss_dict = default_item.get("twiss_dict")
    picture_type = default_item.get("picture_type")


    if platform == "qt":
        edst_path = default_item.get("edst_path")
    elif platform == "web":
        if location == "out":
            edst_path = os.path.join(project_path, "OutputFile", default_item.get("edst_path"))
        elif location == "in":
            edst_path = os.path.join(project_path, "InputFile", default_item.get("edst_path"))

    v = Plotedst()

    item = {
        "show_": show_,
        "fig": fig,
        "save_path": None,
        "picture_type":picture_type,
        "edst_path": edst_path,
        "edst_dict": edst_dict,
    }


    if platform == "qt":
        output = v.run(item)
    elif platform == "web":
        try:
            save_path = generate_web_picture_path(project_path)
            item["save_path"] = save_path
            v.run(item)

            picture_param = {"picturePath": save_path}
            output = format_output(**picture_param)
        except Exception as e:
            code = -1
            msg = str(e)
            picture_param = {"picturePath": ""}
            output = format_output(code, msg=msg, **picture_param)
    return output


def plot_plt(item):
    default_item = {"plt_path": None, "picture_type": [["x", "x1"]], "show_": 0, "fig": None, "platform": "qt",
                    "sampleInterval": 1, "needData": False, "project_path": None, "location": "out",
                    "dst_dict": None, "part_arr": None, "exist_particle": None,
                    "twiss_dict": None, "num": None,
    }

    default_item.update(item)

    platform = default_item.get("platform")
    project_path = default_item.get("project_path")
    plt_path = default_item.get("plt_path")
    fig = default_item.get("fig")

    sample_interval = default_item.get("sampleInterval")
    location = default_item.get("location")
    show_ = default_item.get("show_")

    dst_dict = default_item.get("dst_dict")
    part_arr = default_item.get("part_arr")
    exist_particle = default_item.get("exist_particle")

    twiss_dict = default_item.get("twiss_dict")
    picture_type = default_item.get("picture_type")
    num = default_item.get("num")

    v = PlotPlt()

    item = {
        "show_": show_,
        "fig": fig,
        "save_path": None,
        "picture_type":picture_type,
        "project_path": project_path,
        "plt_path": plt_path,
        "num": 0,

        "part_arr": part_arr,
        "exist_particle": exist_particle,
        "dst_dict": dst_dict,

        "twiss_dict": twiss_dict,
    }

    if platform == "qt":
        output = v.run(item)
    elif platform == "web":
        try:
            save_path = generate_web_picture_path(project_path)
            item["save_path"] = save_path
            v.run(item)

            picture_param = {"picturePath": save_path}
            output = format_output(**picture_param)
        except Exception as e:
            code = -1
            msg = str(e)
            picture_param = {"picturePath": ""}
            output = format_output(code, msg=msg, **picture_param)
    return output


def plot_cavity_voltage(project_path, ratio, show_=1, fig=None, platform="qt"):
    """
    :param project_path:
    :param ratio: {} 场名：比例
    :param show_:
    :return:
    腔压图
    """

    lattice_mulp_path = os.path.join(project_path, 'InputFile', 'lattice_mulp.txt')
    v = PlotCavityVoltage(lattice_mulp_path, ratio)
    v.get_x_y()
    res = v.run(show_, fig)
    return res


# def plot_cavity_syn_phase(project_path, show_=1, fig = None, platform = "qt"):
#     # item = {project_path, show_=1, fig = None, platform = "qt"}
#     """
#
#     :param project_path:
#     :param show_:
#     :return:
#     腔体同步相位图
#     """
#     v = PlotCavitySynPhase(project_path)
#     v.get_x_y()
#     res = v.run(show_, fig)
#     return res
def plot_cavity_syn_phase(**item):
    # item = {project_path, show_=1, fig = None, platform = "qt"}

    """

    :param project_path:
    :param show_:
    :return:
    腔体同步相位图
    """

    default_item = {"projectPath": None, "show_": 0, "fig": None, "platform": "qt", "needData": False}
    default_item.update(item)

    project_path = default_item.get("projectPath")
    show_ = default_item.get("show_")
    fig = default_item.get("fig")
    platform = default_item.get("platform")
    need_data = default_item.get("needData")

    lattice_mulp_path = os.path.join(project_path, 'InputFile', 'lattice_mulp.txt')
    v = PlotCavitySynPhase(lattice_mulp_path)
    v.get_x_y()

    if platform == "qt":
        output = v.run(show_, fig)

    elif platform == "web":

        # 生成文件名
        save_path = generate_web_picture_path(project_path)

        v.run(show_, fig, save_path)

        # 生成返回信息
        picture_param = {"picturePath": save_path, "pictureInfo": {}}

        if need_data is True:
            data = generate_web_picture_param(v)
            picture_param["pictureInfo"] = data

        output = format_output(**picture_param)

    return output


def plot_phase_advance(**item):
    """
    :param project_path:
    :param out_type:
    :param out_type:
    :param show_:
    :return:
    相移图
    """
    # item = {project_path, picture_type, show_ = 1, fig = None, platform = "qt"}
    default_item = {"projectPath": None, "pictureType": "period", "show_": 0, "fig": None,
                    "platform": "qt", "nnedData": False}
    default_item.update(item)

    project_path = default_item.get("projectPath")
    picture_type = default_item.get("pictureType")
    show_ = default_item.get("show_")
    fig = default_item.get("fig")
    platform = default_item.get("platform")
    need_data = default_item.get("needData")
    v = PlotPhaseAdvance(project_path, picture_type)
    v.get_x_y()

    if platform == "qt":
        output = v.run(show_, fig)
    elif platform == "web":
        # 生成文件名
        save_path = generate_web_picture_path(project_path)

        v.run(show_, fig, save_path)

        # 生成返回信息
        picture_param = {"picturePath": save_path, "pictureInfo": {}}

        if need_data is True:
            data = generate_web_picture_param(v)
            picture_param["pictureInfo"] = data

        output = format_output(**picture_param)
    return output


def plot_error_out(**item):
    """
    :param project_path:
    :param picture_name:
    :param picture_type:
    :param show_:
    :return:
    误差图
    """
    default_item = {"filePath": None,
                    "statMethod": "average",
                    "pictureType": "xy",
                    "show_": 0, "fig": None, "platform": "qt",
                    "needData": False, "projectPath": None}

    default_item.update(item)

    stat_method = default_item.get("statMethod")
    picture_type = default_item.get("pictureType")
    show_ = default_item.get("show_")
    fig = default_item.get("fig")
    platform = default_item.get("platform")
    need_data = default_item.get("needData")
    project_path = default_item.get("projectPath")
    if platform == "qt":
        file_path = default_item.get("filePath")
    elif platform == "web":
        file_path = os.path.join(project_path, 'OutputFile', default_item.get("filePath"))

    v = PlotErrout(file_path, stat_method, picture_type)
    v.get_x_y()

    if platform == "qt":
        output = v.run(show_, fig)
    elif platform == "web":
        # 生成文件名
        save_path = generate_web_picture_path(project_path)
        output = v.run(show_, fig, save_path)

        # 生成返回信息
        picture_param = {"picturePath": save_path, "pictureInfo": {}}

        if need_data is True:
            data = generate_web_picture_param(v)
            picture_param["pictureInfo"] = data

        output = format_output(**picture_param)

    return output


def plot_error_emit_loss(**item):
    """
    :param project_path:
    :param picture_name:
    :param picture_type:
    :param show_:
    :return:
    误差图
    """
    default_item = {"filePath": None, "pictureType": "par", "show_": 0, "fig": None,
                    "platform": "qt", "needData": False, "projectPath": None}
    default_item.update(item)

    picture_type = default_item.get("pictureType")
    show_ = default_item.get("show_")
    fig = default_item.get("fig")
    platform = default_item.get("platform")
    need_data = default_item.get("needData")
    project_path = default_item.get("projectPath")

    if platform == "qt":
        file_path = default_item.get("filePath")
    elif platform == "web":
        file_path = os.path.join(project_path, 'OutputFile', default_item.get("filePath"))

    v = PlotErr_emit_loss(file_path, picture_type)
    v.get_x_y()

    if platform == "qt":
        output = v.run(show_, fig)

    elif platform == "web":
        # 生成文件名
        save_path = generate_web_picture_path(project_path)
        v.run(show_, fig, save_path)

        # 生成返回信息
        picture_param = {"picturePath": save_path, "pictureInfo": {}}
        if need_data is True:
            pictureInfo = {}
            pictureInfo["labelx"] = v.xlabel
            pictureInfo["labely1"] = v.ylabel1
            pictureInfo["labely2"] = v.ylabel2

            pictureInfo["datax1"] = v.xy["ax1_x"]
            pictureInfo["datay1"] = v.xy["ax1_y"]

            pictureInfo["datax2"] = v.xy["ax2_x"]
            pictureInfo["datay2"] = v.xy["ax2_y"]

            pictureInfo["legends1"] = v.labels1
            pictureInfo["legend2"] = v.labels2

            picture_param["pictureInfo"] = pictureInfo

        output = format_output(**picture_param)
        # except Exception as e:
        #     code = -1
        #     msg = str(e)
        #     kwargs.update(pictureParam)
        #     output = format_output(code, msg=msg, **kwargs)
    return output


def plot_density(**item):
    default_item = {"filePath": None, "desnityPlane": "x", "show_": 0, "fig": None, "platform": "qt",
                    "sampleInterval": 1, "needData": False, "projectPath": None}

    default_item.update(item)

    file_path = default_item.get("filePath")
    picture_type = default_item.get("desnityPlane")
    show_ = default_item.get("show_")
    fig = default_item.get("fig")
    platform = default_item.get("platform")
    sample_interval = default_item.get("sampleInterval")
    need_data = default_item.get("needData")
    project_path = default_item.get("projectPath")

    v = PlotDensity(file_path, picture_type, sample_interval)
    v.get_x_y()

    if platform == "qt":
        output = v.run(show_, fig)
    elif platform == "web":
        save_path = generate_web_picture_path(project_path)
        output = v.run(show_, fig, save_path)

        picture_param = {"picturePath": save_path, "pictureInfo": {}}

        if need_data is True:
            pictureInfo = {}
            pictureInfo["labelx"] = v.xlabel
            pictureInfo["labely"] = v.ylabel
            pictureInfo["z_m"] = v.z_m.tolist()
            pictureInfo["y_m"] = v.y_m.tolist()
            pictureInfo["density_m"] = v.density_m.tolist()
            pictureInfo["legends"] = [None]
            picture_param["pictureInfo"] = pictureInfo

        output = format_output(**picture_param)

    return output


def plot_density_level(**item):
    default_item = {"filetath": None, "desnityPlane": "x", "show_": 0, "fig": None, "platform": "qt",
                    "sampleInterval": 1, "needData": False, "projectPath": None}

    default_item.update(item)

    file_path = default_item.get("filePath")
    picture_type = default_item.get("desnityPlane")
    show_ = default_item.get("show_")
    fig = default_item.get("fig")
    platform = default_item.get("platform")
    sample_interval = default_item.get("sampleInterval")
    need_data = default_item.get("needData")
    project_path = default_item.get("projectPath")

    v = PlotDensityLevel(file_path, picture_type, sample_interval)
    v.get_x_y()

    if platform == "qt":
        output = v.run(show_, fig)

    elif platform == "web":
        save_path = generate_web_picture_path(project_path)

        # 运行并保存图片
        v.run(show_, fig, save_path)

        # 生成返回信息
        picture_param = {"picturePath": save_path, "pictureInfo": {}}

        if need_data is True:
            data = generate_web_picture_param(v)
            picture_param["pictureInfo"] = data

        output = format_output(**picture_param)

    return output


def plot_density_process(**item):
    # density_plane = ["x", "y", "r", "z"]
    # picture_type = [
    # "centroid"
    # "emit",
    # rms_size, rms_size_max,
    # lost, maxlost, minlost,
    # ]

    default_item = {"filePath": None, "desnityPlane": "x", "pictureType": "centroid", "show_": 0, "fig": None,
                    "platform": "qt",
                    "sampleInterval": 1, "needData": False, "projectPath": None}

    default_item.update(item)

    file_path = default_item.get("filePath")
    density_plane = default_item.get("desnityPlane")
    picture_type = default_item.get("pictureType")
    show_ = default_item.get("show_")
    fig = default_item.get("fig")
    platform = default_item.get("platform")
    sample_interval = default_item.get("sampleInterval")
    need_data = default_item.get("needData")
    project_path = default_item.get("projectPath")

    v = PlotDensityProcess(file_path, density_plane, picture_type, sample_interval)
    v.get_x_y()

    if platform == "qt":
        output = v.run(show_, fig)
    elif platform == "web":
        # 生成文件名
        save_path = generate_web_picture_path(project_path)

        v.run(show_, fig, save_path)

        # 生成返回信息
        picture_param = {"picturePath": save_path, "pictureInfo": {}}

        if need_data is True:
            data = generate_web_picture_param(v)
            picture_param["pictureInfo"] = data

        output = format_output(**picture_param)

    return output

    return res


def plot_density_transport(**item):
    default_item = {"filePath": None, "desnityPlane": "x", "pictureType": "density", "show_": 0, "fig": None,
                    "platform": "qt",
                    "sampleInterval": 1, "needData": False, "projectPath": None}

    default_item.update(item)

    project_path = default_item.get("projectPath")
    platform = default_item.get("platform")
    if platform == "qt":
        file_path = default_item.get("filePath")
    elif platform == "web":
        file_path = os.path.join(project_path, 'OutputFile', default_item.get("filePath"))

    default_item["filePath"] = file_path

    picture_type = default_item.get("pictureType")
    process_type = ["centroid", "emit", "rms_size", "rms_size_max"]

    if picture_type == "density":
        res = plot_density(**default_item)

    elif picture_type == "density_level":
        res = plot_density_level(**default_item)

    elif picture_type in process_type:
        res = plot_density_process(**default_item)
    return res


def plot_phase_ellipse(parameter_item, picture_type, show_=1, fig=None, platform="qt"):
    obj = PlotPhaseEllipse()
    obj.get_x_y(picture_type, parameter_item)
    res = obj.run(show_, fig)
    return res


def plot_env_beam_out(project_path, picture_name, show_=1, fig=None):
    v = PlotEnvBeamOut(project_path)
    v.get_x_y(picture_name)
    res = v.run(show_, fig)
    return res


################################################################################`#######################################
# 下列为数据分析函数

# 计算twiss参数
def cal_twiss(dst_path):
    v = CalTwiss(dst_path)
    res = v.get_emit_xyz()
    return res


def judge_opti(res):
    sign = []
    # 判断是否需要矫正
    for i in res:
        if i[0] == 'adjust':
            sign.append('adjust')
        elif i[0].startswith('diag'):
            sign.append('diag')

    # 如果这两个都包含,
    if 'adjust' in sign and 'diag' in sign:
        return 1
    else:
        return 0


def change_file_win2linux(**item):
    path = item.get('project_path')
    beam_path = os.path.join(path, "InputFile", "beam.txt")
    input_path = os.path.join(path, "InputFile", "input.txt")
    boundary_path = os.path.join(path, "InputFile", "boundary.txt")

    change_end_crlf(beam_path)
    change_end_crlf(input_path)
    if os.path.exists(boundary_path):
        change_end_crlf(boundary_path)



def plot_dst4qt(item):
    # item = {
    #     "dst_path": ,
    #     "show_": ,
    #  }


    dst_path = item.get("dst_path")
    show_ = item.get("show_")

    plot_phase = PlotPhase(dst_path)

    plot_phase.run(show_=show_)
    return 1

if __name__ == '__main__':
    edst_path = r"C:\Users\wangh\Desktop\qx\2beam\OutputFile\outData_6.992532.edst"

    item = {
        ""
    }

    item = {
        "show_": 1,
        "fig": None,
        "save_path": None,
        "picture_type":  [["x", "x1"], ["y", "y1"], ["phi", "w"], ["phi", "y"]],
        "edst_path": edst_path,
        "edst_dict": None,
        }
    plot_edst(item)

    # item = {
    #     "show_": 1,
    #     "fig": None,
    #     "save_path": None,
    #     "picture_type":  [["x", "x1"], ["y", "y1"], ["z", "z1"], ["phi", "w"]],
    #     "project_path": r"C:\Users\wangh\Desktop\324\v1",
    #     "plt_path": r"C:\Users\wangh\Desktop\324\v1\OutputFile\BeamSet.plt",
    #     "num": 0,
    #     "part_arr": None,
    #     "exist_particle": None,
    #     "dst_dict": None,
    #     }
    #
    # plot_plt(item)

    # dst_path = r"C:\Users\wangh\Desktop\phase_plot\outData_198.295500.dst"
    #
    # default_picture_type = [
    #     ["x", "x1"],
    #     ["y", "y1"],
    #     ["phi", "w"],
    #     ["z", "z1"],
    # ]
    # twiss_dict =  {
    #     ('x', 'x1'): [-0.5955557297222218, 9.331564347619306, 0.1451725109253069, 0.21574159520806604,
    #                   0.21574159520806604, 3.5197134193924007, 3.5197134193924007],
    #     ('y', 'y1'): [-1.5285043418095665, 13.96799872389979, 0.23885494184804823, 0.221916635869112, 0.221916635869112,
    #                   6.032377575558818, 6.032377575558818],
    #     ('z', 'z1'): [-0.22635657542606882, 12.41136999871493, 0.08469953754883325, 0.22470403577547238,
    #                   0.22470403577547238, 5.58181134263423, 5.58181134263423],
    #     ('phi', 'w'): [0.22636619976753608, 1.0725986011069375, 0.9800885954095961, 0.04114192767268835,
    #                    0.04114192767268835, 1.0228596169403126, 1.0228596169403126]
    # }
    #
    # item = {"filePath": dst_path, "pictureType": default_picture_type, "show_": 1, "fig": None, "platform": "qt",
    #                 "sampleInterval": 1, "needData": False, "projectPath": None, "location": "out", "dst_dict": None,
    #         "twiss_dict": twiss_dict}
    #
    # plot_dst(item)



    # dst_path = \
    #     r"C:\Users\wangh\Desktop\phase_plot\1000w.dst"
    #
    # plot_phase = PlotPhase2()
    #
    # item = {
    #     "show_": 1,
    #     "fig": None,
    #
    #     "picture_type":  [["x", "x1"], ["y", "y1"], ["z", "z1"], ["phi", "w"]],
    #     "dst_path": dst_path,
    #     "dst_dict": None,
    #     "twiss_dict": None
    #        }
    #
    # plot_phase2(**item)
