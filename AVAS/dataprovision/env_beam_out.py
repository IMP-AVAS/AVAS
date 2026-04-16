from utils.readfile import read_txt

class EnvBeamOutParameter():
    """
    对beamout文件进行解析
    """
    def __init__(self, beam_out_path):
        self.beam_out_path = beam_out_path
        self.z = []


    def get_parameter(self):
        beam_out_info = read_txt(self.beam_out_path, out='list')[1:]
        beam_out_info = [[float(j) for j in i] for i in beam_out_info]

        self.z = [i[0] for i in beam_out_info]
        self.beta = [i[1] for i in beam_out_info]
        self.gamma = [i[2] for i in beam_out_info]

        self.alpha_x = [i[3] for i in beam_out_info]
        self.beta_x = [i[4] for i in beam_out_info]
        self.emit_x = [i[5] for i in beam_out_info]

        self.alpha_y = [i[6] for i in beam_out_info]
        self.beta_y = [i[7] for i in beam_out_info]
        self.emit_y = [i[8] for i in beam_out_info]

        self.alpha_z = [i[9] for i in beam_out_info]
        self.beta_z = [i[10] for i in beam_out_info]
        self.emit_z = [i[11] for i in beam_out_info]

if __name__ == '__main__':
    beam_out_path = r'C:\Users\anxin\Desktop\AVAS_control\apps\beam_out.txt'
    v = EnvBeamOutParameter(beam_out_path)
    v.get_parameter()
