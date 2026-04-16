import numpy as np

file_path = r"C:\Users\wangh\Desktop\wws3\v1\转换\synData.txt"
input_file = r"C:\Users\wangh\Desktop\wws3\v1\转换\lattice_mulp.txt"
output_file = r"C:\Users\wangh\Desktop\wws3\v1\转换\new_lattice.txt"

t_values = []
rphase_values = []

with open(file_path, 'r') as f:
    for line in f:
        parts = line.strip().split()

        if len(parts) >= 8:
            col_6 = parts[6]
            col_7 = parts[7]
            #col_8 = parts[8]

            if col_6 != 'invalid' and col_7 != 'invalid':
                t_values.append(float(parts[4]))
                rphase_values.append(float(parts[7]))
print(t_values)
print(rphase_values)
with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

modified_lines = []
value_index = 0
for line in lines:
    stripped_line = line.strip()
    if stripped_line.startswith('field') and not stripped_line.startswith('!'):
        elements = stripped_line.split()
        if len(elements) >= 5 and elements[4] == '1':
            elements[3] = '2'
            rphase_values[value_index] = rphase_values[value_index] - t_values[value_index] * float(elements[5]) * 360
            print(rphase_values[value_index], t_values[value_index] * float(elements[5]) * 360, rphase_values[value_index])

            while (rphase_values[value_index] > 180.0):
                rphase_values[value_index] -= 360.0
            while (rphase_values[value_index] < -180.0):
                rphase_values[value_index] += 360.0
            print(rphase_values[value_index] )
            # import sys
            # sys.exit()
            if value_index < len(rphase_values):
                elements[6] = str(rphase_values[value_index])
                value_index += 1
            else:
                print(f"束线绝对相位设置异常，文件中没有足够相位用于设置")

            modified_line = ' '.join(elements) + '\n'
            modified_lines.append(modified_line)
            print(f"已修改: {modified_line.strip()}")
        else:
            modified_lines.append(line)
    else:
        modified_lines.append(line)

if value_index == len(rphase_values):
    print("正常完成束线绝对相位设置")
else:
    print("束线绝对相位设置异常，存在文件中的相位未设置到束线")

with open(output_file, 'w', encoding='utf-8') as f:
    f.writelines(modified_lines)

