import time
from InputsConfig import InputsConfig as p
from Event import Event, Queue
from Scheduler import Scheduler
from Statistics import Statistics
from Data_Output.Make_figure import Make_figure
from Window import Window
import pandas as pd
if p.model == 3:
    from Models.AppendableBlock.BlockCommit import BlockCommit
    from Models.Consensus import Consensus
    from Models.AppendableBlock.Transaction import FullTransaction as FT
    from Models.AppendableBlock.Node import Node
    from Models.Incentives import Incentives
    from Models.AppendableBlock.Statistics import Statistics
    from Models.AppendableBlock.Verification import Verification

elif p.model == 2:
    from Models.Ethereum.BlockCommit import BlockCommit
    from Models.Ethereum.Consensus import Consensus
    from Models.Ethereum.Transaction import LightTransaction as LT, FullTransaction as FT
    from Models.Ethereum.Node import Node
    from Models.Ethereum.Incentives import Incentives

elif p.model == 1:
    from Models.Bitcoin.BlockCommit import BlockCommit
    from Models.Bitcoin.Consensus import Consensus
    from Models.Transaction import LightTransaction as LT, FullTransaction as FT
    from Models.Bitcoin.Node import Node
    from Models.Incentives import Incentives

elif p.model == 0:
    from Models.BlockCommit import BlockCommit
    from Models.Consensus import Consensus
    from Models.Transaction import LightTransaction as LT, FullTransaction as FT
    from Models.Node import Node
    from Models.Incentives import Incentives

########################################################## Start Simulation ##############################################################
# 时间标记函数


def timerecord(name):
    localtime = time.asctime(time.localtime(time.time()))
    print(name, localtime)

def main():
    for x in range(0,11):
        p.Rate+=[x*0.05]
    print("仿真次数 :", len(p.Rate))
    # timerecord("开始时间 :")
    # i为仿真次数R
    delay_all=[]
    delay_normal=[]
    delay_gover=[]
    for i in range(len(p.Rate)):
        print("*******************************************")
        print("第",i+1,"次仿真")
        # clock为仿真时钟计数器,用于控制仿真事件结束
        clock = 0  # set clock to 0 at the start of the simulation
        # 生成待处理交易
        # timerecord("生成交易:")
        if p.hasTrans:
            if p.Ttechnique == "Light":
                LT.create_transactions()  # generate pending transactions
            elif p.Ttechnique == "Full":
                FT.create_transactions(i)  # generate pending transactions
        # 生成创世区块，将创世区块信息打包到每个节点中
        # timerecord("生成区块:")
        Node.generate_gensis_block()  # generate the gensis block for all miners
        # initiate initial events >= 1 to start with
        # 初始化事件
        # timerecord("初始化事件:")
        b = BlockCommit()
        b.generate_initial_events()
        # 从事件队列中依次取出事件进行处理
        # timerecord("事件处理:")
        while not Queue.isEmpty() and clock <= p.simTime:
            next_event = Queue.get_next_event()
            clock = next_event.time  # move clock to the time of the event
            b.handle_event(next_event)
            Queue.remove_event(next_event)
        # 共识机制：最长链匹配原则解决分叉
        Consensus.fork_resolution()  # apply the longest chain to resolve the forks
        # distribute the rewards between the particiapting nodes
        # 激励机制
        Incentives.distribute_rewards()
        # calculate the simulation results (e.g., block statstics and miners' rewards)
        # 数据统计
        Statistics.calculate()
        # 数据输出
        ########## reset all global variable before the next run #############
        print("所有交易时延为",Statistics.delay_per_chain[0] if Statistics.delay_per_chain[0] else 0,"秒")
        delay_all.append(Statistics.delay_per_chain[0])
        print("正常交易时延为",Statistics.delay_per_chain[1] if Statistics.delay_per_chain[1] else 0,"秒")
        delay_normal.append(Statistics.delay_per_chain[1])
        print("异常交易时延为",Statistics.delay_per_chain[2] if Statistics.delay_per_chain[2] else 0,"秒")
        delay_gover.append(Statistics.delay_per_chain[2])
        Statistics.reset()  # reset all variables used to calculate the results
        Node.resetState()  # reset all the states (blockchains) for all nodes in the network
        # fname = "(Allverify)1day_1e-06M_0.02K.xlsx"
        # # print all the simulation results in an excel file
        # Statistics.print_to_excel(fname)
        Statistics.reset2() 
        # address = ".\(Allverify)1day_1e-06M_0.02K.xlsx"
        # Make_figure.result_pic(address, 3, "区块高度", "交易数量", "区块与交易关系统计图", 6)
        # Make_figure.result_pic(address, 3, "区块高度", "区块延迟", "区块与区块延迟关系统计图", 9)
        # Make_figure.result_pic(address, 3, "区块高度", "交易类型（0代表正常交易）", "区块是否为特殊区块图", 10)
    # Window.mainwindow()
    writer = pd.ExcelWriter('result.xlsx',engine='xlsxwriter')
    df = pd.DataFrame({"delay_all":delay_all,"delay_normal":delay_normal,"delay_gover":delay_gover})
    df.to_excel(writer)
    writer.save()
    print('*****************************************')
    timerecord("结束时间为 :")


######################################################## Run Main method #####################################################################
if __name__ == '__main__':
    main()


