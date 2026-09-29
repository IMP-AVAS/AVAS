
c_light = 299792458
Pi = 3.14159265358979323846


#底层基础原件
mulp_element = ['drift', 'field', 'quad', 'solenoid', 'bend', 'steerer', "edge", ]


#多粒子原件基础命令，即模拟相关命令
mulp_basic_command = mulp_element + \
               ['start', 'end', 'superpose', 'superposeend', 'outputplane', "superposeout", "automaticoutput", "spacechargecomp"]


#误差模拟中，用来写入到lattice的命令
err_write_command = mulp_basic_command + ['err_step', 'err_cav_ncpl_dyn', 'err_quad_ncpl_dyn', 'err_beam_dyn',
                                          'err_quad_dyn_on', 'err_cav_dyn_on', 'err_beam_dyn_on' ]

#束诊原件，在控制层定义的原件
control_diag_element = ['diag_energy', 'diag_size', 'diag_position']

all_element = mulp_element + control_diag_element


########################################################
error_elemment_command = ['err_quad_ncpl_stat', 'err_quad_ncpl_dyn', 'err_cav_ncpl_stat', 'err_cav_ncpl_dyn',
                          'err_quad_cpl_stat', 'err_quad_cpl_dyn', 'err_cav_cpl_stat', 'err_cav_cpl_dyn', ]


#误差设置命令  静态/ 动态/ ncpl /cpl/cav/ quad/
error_elemment_command_stat_ncpl = ['err_quad_ncpl_stat', 'err_cav_ncpl_stat'] #stat ncpl
error_elemment_command_dyn_ncpl = ['err_quad_ncpl_dyn', 'err_cav_ncpl_dyn']  #dyn ncpl

error_elemment_command_quad_ncpl = ['err_quad_ncpl_stat', 'err_quad_ncpl_dyn'] #quad ncpl
error_elemment_command_cav_ncpl = ['err_cav_ncpl_stat', 'err_cav_ncpl_dyn', ]  #cav ncpl


error_elemment_command_stat_cpl = ['err_quad_cpl_stat', 'err_cav_cpl_stat'] #stat cpl
error_elemment_command_dyn_cpl = ['err_quad_cpl_dyn', 'err_cav_cpl_dyn'] #dyn cpl

error_elemment_command_quad_cpl = ['err_quad_cpl_stat', 'err_quad_cpl_dyn']  #quad cpl
error_elemment_command_cav_cpl = ['err_cav_cpl_stat', 'err_cav_cpl_dyn', ]  #cav cpl



error_elemment_command_ncpl = ['err_quad_ncpl_stat', 'err_quad_ncpl_dyn', 'err_cav_ncpl_stat', 'err_cav_ncpl_dyn']

error_elemment_command_quad = ['err_quad_ncpl_stat', 'err_quad_cpl_stat',
                                      'err_quad_ncpl_dyn', 'err_quad_cpl_dyn', ]

error_elemment_command_cav = ['err_cav_ncpl_stat', 'err_cav_cpl_stat',
                                      'err_cav_ncpl_dyn', 'err_cav_cpl_dyn', ]


error_beam_command = ['err_beam_stat', 'err_beam_dyn']
error_beam_stat = ['err_beam_stat']
error_beam_dyn = ['err_beam_dyn']

#误差开启命令
error_elemment_dyn_on = ['err_quad_dyn_on', 'err_cav_dyn_on']
error_elemment_stat_on = ['err_quad_stat_on', 'err_cav_stat_on']

error_beam_dyn_on = ['err_beam_dyn_on']
error_beam_stat_on = ['err_beam_stat_on']

#########################################################################


#以后用mulpud代表多粒子底层， envud代表包络底层，gpuud代表gpu底层

greek_letters_upper = {'alpha': '\u0391', 'beta': '\u0392', 'gamma': '\u0393', 'phi': '\u03A6'}

decimals7 = 7