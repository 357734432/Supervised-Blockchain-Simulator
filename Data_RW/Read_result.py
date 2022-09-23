import numpy as np

class Read_result:
    hasTra = True;
    def read_result():
        file = open("BlockSim-master/Data_RW/result.txt", "r")

        # a=eval("{'id':0,'timestamp':0,'sender':0,'to':0,'value':0,'size':0.000546,'gasLimit':8000000,'usedGas':0,'gasPrice':0,'fee':0}")
        # print(a['size'])
        list = file.readlines()  # 每一行数据写入到list中
        # print(list)
        lists = []
        if (len(list) != 0):
            for fields in list:
                fields = fields.strip();  # fields.strip()用来删除字符串两端的空白字符。
                # fields = fields.strip("{}");  # fields.strip("[]")用来删除字符串两端花括号
                fields = fields.strip('"');  # fields.strip("[]")用来删除字符串两端方括号
                # fields = fields.strip(",");  # fields.strip(",")用来删除字符串两端逗号
                fields = fields.strip('\n');  # fields.strip("\n")用来删除字符串两端换行符
                # fields = fields.split(",");  # fields.split(",")的作用是以逗号为分隔符，将字符串进行分隔。
                # print(fields);
                result = eval(fields)
                lists.append(result);
        else:
            print("数据格式有误");
        return lists


# tracks = np.array(lists)
# boxes = tracks[:, 2:6]  # 读入边界框坐标
# print(boxes)

