# -*- coding:UTF-8 -*-
import numpy as np
import xlrd as xlrd
from scipy.stats import norm
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import sys
import importlib
# 参数1 Excel文件位置 参数2 选择要作图的表格    参数3、4、5 xy轴代表含义以及标题文字 参数6列数 函数可以选择某地址文件某一个表格某一列来操作
class Make_figure:
    def result_pic(address, Excel_Choice,xlabel,ylabel,title,FormColumns):
        # 设置字体
        importlib.reload(sys)
        matplotlib.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        # 读取文件
        trainFile = address
        if(Excel_Choice==0):
            data = pd.read_excel(trainFile, 0)
        elif(Excel_Choice==1):
            data = pd.read_excel(trainFile, 1)
        elif(Excel_Choice==2):
            data = pd.read_excel(trainFile, 2)
        elif(Excel_Choice==3):
            data = pd.read_excel(trainFile, 3)
        else:
            print('输入有误！！！')

        #print(data.iloc[:, 1].describe())
        # 设置表格形式
        # 定义x轴、y轴取值范围

        x = range(0, data.iloc[:,FormColumns].count(), 1)
        y = data.iloc[:, FormColumns]
        # 定义折线
        s = plt.plot(x, y, 'b--')
        # 定义文字说明
        s1 = "以太坊区块交易数"
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend([s1], loc="upper left")
        # 图片打印
        plt.show()


