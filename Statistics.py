from InputsConfig import InputsConfig as p
from Models.Consensus import Consensus as c
from Models.Incentives import Incentives
import pandas as pd


class Statistics:

    ########################################################### Global variables used to calculate and print simuation results ###########################################################################################
    totalBlocks=0
    mainBlocks= 0
    totalUncles=0
    uncleBlocks=0
    staleBlocks=0
    uncleRate=0
    staleRate=0
    blockData=[]
    blocksResults=[]
    profits= [[0 for x in range(7)] for y in range(p.Runs * len(p.NODES))] # rows number of miners * number of runs, columns =7
    index=0
    chain=[]
    trans=[]
    delay_per_block=[]
    delay_per_chain=[0,0,0] # 分别为 所有交易平均时延、正常交易平均时延、异常交易平均时延

    def calculate():
        Statistics.global_chain() # print the global chain
        Statistics.blocks_results() # calcuate and print block statistics e.g., # of accepted blocks and stale rate etc
        Statistics.profit_results() # calculate and distribute the revenue or reward for miners
        # Statistics.transcations()
        #Statistics.exp_result1()
        Statistics.exp_result2()
    ########################################################### Calculate block statistics Results ###########################################################################################
    def blocks_results():
        total_trans = 0

        Statistics.mainBlocks= len(c.global_chain)-1
        Statistics.staleBlocks = Statistics.totalBlocks - Statistics.mainBlocks
        for b in c.global_chain:
            if p.model==2: Statistics.uncleBlocks += len(b.uncles)
            else: Statistics.uncleBlocks = 0
            total_trans += len(b.transactions)
        Statistics.staleRate= round(Statistics.staleBlocks/Statistics.totalBlocks * 100, 2)
        if p.model==2: Statistics.uncleRate= round(Statistics.uncleBlocks/Statistics.totalBlocks * 100, 2)
        else: Statistics.uncleRate==0
        Statistics.blockData = [ Statistics.totalBlocks, Statistics.mainBlocks,  Statistics.uncleBlocks, Statistics.uncleRate, Statistics.staleBlocks, Statistics.staleRate, total_trans]
        Statistics.blocksResults+=[Statistics.blockData]

    ########################################################### Calculate and distibute rewards among the miners ###########################################################################################
    def profit_results():

        for m in p.NODES:
            i = Statistics.index + m.id * p.Runs
            Statistics.profits[i][0]= m.id
            if p.model== 0: Statistics.profits[i][1]= "NA"
            else: Statistics.profits[i][1]= m.hashPower
            Statistics.profits[i][2]= m.blocks
            Statistics.profits[i][3]= round(m.blocks/Statistics.mainBlocks * 100,2)
            if p.model==2:
                Statistics.profits[i][4]= m.uncles
                Statistics.profits[i][5]= round((m.blocks + m.uncles)/(Statistics.mainBlocks + Statistics.totalUncles) * 100,2)
            else: Statistics.profits[i][4]=0; Statistics.profits[i][5]=0
            Statistics.profits[i][6]= m.balance

        Statistics.index+=1

    ########################################################### prepare the global chain  ###########################################################################################
    def global_chain():
        if p.model==0 or p.model==1:
                for i in c.global_chain:
                        block= [i.depth, i.id, i.previous, i.timestamp, i.miner, len(i.transactions), i.size]
                        Statistics.chain +=[block]
        elif p.model==2:
            for i in range(1, len(c.global_chain)):
                block = [c.global_chain[i].depth, c.global_chain[i].id, c.global_chain[i].previous,
                         c.global_chain[i].timestamp, c.global_chain[i].miner, len(c.global_chain[i].transactions),
                         c.global_chain[i].usedgas, len(c.global_chain[i].uncles),
                         (c.global_chain[i].timestamp - c.global_chain[i - 1].timestamp), c.global_chain[i].specialTra]
                Statistics.chain += [block]
    ########################################################### prepare the transcations  ###########################################################################################
    def transcations():
        for i in range(1,len(c.global_chain)):
            trans_of_block=[c.global_chain[i].depth,c.global_chain[i].miner]
            for j in range(0,len(c.global_chain[i].transactions)):
                trans_of_block+=[c.global_chain[i].transactions[j].id]
            Statistics.trans += [trans_of_block]
    ########################################################### prepare the experience results  ###########################################################################################
    def exp_result1():
        ##计算区块中异常交易和正常交易的平均时延
        for i in range(1,len(c.global_chain)):
            result = [c.global_chain[i].depth]
            trans_delay = 0
            Spctrans_delay = 0
            for j in range(0,len(c.global_chain[i].transactions)):
                if c.global_chain[i].transactions[j].type == 0:
                    trans_delay += c.global_chain[i].timestamp - c.global_chain[i].transactions[j].timestamp[0]  #单个交易的延时=区块生成时间减去交易生成时间
                else:
                    Spctrans_delay += c.global_chain[i].timestamp -c.global_chain[i].transactions[j].timestamp[0]
                if j+1 == len(c.global_chain[i].transactions):
                    trans_delay = trans_delay / len(c.global_chain[i].transactions)
                    if c.global_chain[i].specialTra != 0: #如果有特殊交易
                        Spctrans_delay = Spctrans_delay / c.global_chain[i].specialTra
                    else :
                        Spctrans_delay="Null"
                    result += [trans_delay,Spctrans_delay]
            Statistics.delay_per_block += [result]

    def exp_result2():
        num0 = 0
        num1 = 0
        num2 = 0
        for i in range(1,len(c.global_chain)):
            for j in range(0,len(c.global_chain[i].transactions)):
                Statistics.delay_per_chain[0] += c.global_chain[i].timestamp -c.global_chain[i].transactions[j].timestamp[0]
                num0 += 1
                if c.global_chain[i].transactions[j].type == 0:
                    Statistics.delay_per_chain[1] += c.global_chain[i].timestamp -c.global_chain[i].transactions[j].timestamp[0]  #单个交易的延时=区块生成时间减去交易生成时间
                    num1 +=1
                else:
                    Statistics.delay_per_chain[2] += c.global_chain[i].timestamp -c.global_chain[i].transactions[j].timestamp[0]
                    num2 += 1
        if num0 != 0 :
            Statistics.delay_per_chain[0] /= num0
        if num1 != 0 :
            Statistics.delay_per_chain[1] /= num1
        if num2 != 0 :
            Statistics.delay_per_chain[2] /= num2
    ########################################################### Print simulation results to Excel ###########################################################################################
    def print_to_excel(fname):

        df1 = pd.DataFrame({'Block Time': [p.Binterval], 'Block Propagation Delay': [p.Bdelay], 'No. Miners': [len(p.NODES)], 'Simulation Time': [p.simTime]})
        #data = {'Stale Rate': Results.staleRate,'Uncle Rate': Results.uncleRate ,'# Stale Blocks': Results.staleBlocks,'# Total Blocks': Results.totalBlocks, '# Included Blocks': Results.mainBlocks, '# Uncle Blocks': Results.uncleBlocks}

        df2= pd.DataFrame(Statistics.blocksResults)
        df2.columns= ['Total Blocks', 'Main Blocks', 'Uncle blocks', 'Uncle Rate', 'Stale Blocks', 'Stale Rate', '# transactions']

        df3 = pd.DataFrame(Statistics.profits)
        df3.columns = ['Miner ID', '% Hash Power','# Mined Blocks', '% of main blocks','# Uncle Blocks','% of uncles', 'Profit (in ETH)']

        df4 = pd.DataFrame(Statistics.chain)
        #df4.columns= ['Block Depth', 'Block ID', 'Previous Block', 'Block Timestamp', 'Miner ID', '# transactions','Block Size']
        if p.model==2: df4.columns= ['Block Depth', 'Block ID', 'Previous Block', 'Block Timestamp', 'Miner ID', '# transactions','Block Limit', 'Uncle Blocks', 'Block delay','Special Transction']
        else: df4.columns= ['Block Depth', 'Block ID', 'Previous Block', 'Block Timestamp', 'Miner ID', '# transactions', 'Block Size']

        # df5 = pd.DataFrame(Statistics.trans)
        # # df5.columns=['Block Depth','Miner ID','Trans ID']

        df5 = pd.DataFrame(Statistics.delay_per_block)
        df5.columns = ['Block Depth', 'Trans Delay','Special Trans Delay']

        writer = pd.ExcelWriter(fname, engine='xlsxwriter')
        df1.to_excel(writer, sheet_name='InputConfig')
        df2.to_excel(writer, sheet_name='SimOutput')
        df3.to_excel(writer, sheet_name='Profit')
        df4.to_excel(writer,sheet_name='Chain')
        # df5.to_excel(writer,sheet_name='Trans')
        df5.to_excel(writer,sheet_name='Result')
        
        writer.save()

    ########################################################### Reset all global variables used to calculate the simulation results ###########################################################################################
    def reset():
        Statistics.totalBlocks=0
        Statistics.totalUncles=0
        Statistics.mainBlocks= 0
        Statistics.uncleBlocks=0
        Statistics.staleBlocks=0
        Statistics.uncleRate=0
        Statistics.staleRate=0
        Statistics.blockData=[]

    def reset2():
        Statistics.blocksResults=[]
        Statistics.profits= [[0 for x in range(7)] for y in range(p.Runs * len(p.NODES))] # rows number of miners * number of runs, columns =7
        Statistics.index=0
        Statistics.chain=[]
        Statistics.trans=[]
        Statistics.delay_per_block=[]
        Statistics.delay_per_chain=[0,0,0]
