from dataprovision.beamset import BeamsetParameter

from dataprovision.datasetparameter import DatasetParameter


if __name__ == '__main__':
    dataset_path = r"C:\Users\wangh\Desktop\324\v1\OutputFile\DataSet.txt"

    dataset_obj = DatasetParameter(dataset_path)
    dataset_obj.get_parameter()
    dataset_index = dataset_obj.dataset_index
    # print(dataset_index)

    plt_path = r"C:\Users\wangh\Desktop\324\v1\OutputFile\BeamSet.plt"
    plt_obj = BeamsetParameter(plt_path)
    plt_obj.get_parameter()
    plt_index = [i["Index"] for i in plt_obj.allstep_dict]
    # print(plt_index)
    # print(plt_obj.allstep_dict[:4])
    # print(plt_obj.allstep_dict[-4:])
    #
    # print("-" * 50)
    print(len(dataset_index), len(plt_index))
    for i in plt_index:
        if i not in dataset_index:
            print(i)

    print("-"*100)
    for i in range(len(plt_index) - 1):
        if plt_index[i + 1] != plt_index[i] + 1:
            print(f"在位置 {i} 处不连续: {plt_index[i]} -> {plt_index[i + 1]}")

    print("-"*100)

    print("dataset_index", dataset_index[148:155])
    print("plt_index    ", plt_index[148:155])
