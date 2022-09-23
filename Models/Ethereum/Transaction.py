from datetime import time

from Models.Ethereum.Distribution.DistFit import DistFit
import random
from InputsConfig import InputsConfig as p
import numpy as np
from Models.Network import Network
import operator
from Models.Ethereum.Distribution.DistFit_result import DistFit_result
from Data_RW.Read_result import Read_result as Read_result

#时间标记函数
def timerecord(name):
    localtime = time.asctime(time.localtime(time.time()))
    print(name, localtime)

class Transaction(object):

    """ Defines the Ethereum Block model.

    :param int id: the uinque id or the hash of the transaction
    :param int timestamp: the time when the transaction is created. In case of Full technique, this will be array of two value (transaction creation time and receiving time)
    :param int sender: the id of the node that created and sent the transaction
    :param int to: the id of the recipint node
    :param int value: the amount of cryptocurrencies to be sent to the recipint node
    :param int size: the transaction size in MB
    :param int gasLimit: the maximum amount of gas units the transaction can use. It is specified by the submitter of the transaction
    :param int usedGas: the amount of gas used by the transaction after its execution on the EVM
    :param int gasPrice: the amount of cryptocurrencies (in Gwei) the submitter of the transaction is willing to pay per gas unit
    :param float fee: the fee of the transaction (usedGas * gasPrice)
    :param int type: the type of the transaction (normal:type=0 ,special:type=1)
    """

    def __init__(self,
	 id=0,
	 timestamp=0 or [],
	 sender=0,
         to=0,
         value=0,
	 size=0.000546,
         gasLimit= 8000000,
         usedGas=0,
         gasPrice=0,
         fee=0,
         Type=0):

        self.id = id
        self.timestamp = timestamp
        self.sender = sender
        self.to= to
        self.value=value
        self.size = size
        self.gasLimit=gasLimit
        self.usedGas = usedGas
        self.gasPrice=gasPrice
        self.fee= usedGas * gasPrice
        self.type = Type



class LightTransaction():

    pool=[] # shared pool of pending transactions
    #x=0 # counter to only fit distributions once during the simulation

    def create_transactions():

        LightTransaction.pool=[]
        Psize= int(p.Tn * p.Binterval)

        #if LightTransaction.x<1:
        DistFit.fit() # fit distributions
        gasLimit,usedGas,gasPrice,_ = DistFit.sample_transactions(Psize) # sampling gas based attributes for transactions from specific distribution

        for i in range(Psize):
            # assign values for transactions' attributes. You can ignore some attributes if not of an interest, and the default values will then be used
            tx= Transaction()

            tx.id= random.randrange(100000000000)
            tx.sender = random.choice (p.NODES).id
            tx.to= random.choice (p.NODES).id
            tx.gasLimit=gasLimit[i]
            tx.usedGas=usedGas[i]
            tx.gasPrice=gasPrice[i]/1000000000
            tx.fee= tx.usedGas * tx.gasPrice

            LightTransaction.pool += [tx]


        random.shuffle(LightTransaction.pool)


    ##### Select and execute a number of transactions to be added in the next block #####
    def execute_transactions():
        transactions= [] # prepare a list of transactions to be included in the block
        limit = 0 # calculate the total block gaslimit
        count=0
        blocklimit = p.Blimit

        pool = sorted(LightTransaction.pool, key=lambda x: x.gasPrice, reverse=True) # sort pending transactions in the pool based on the gasPrice value

        while count < len(pool):
                if  (blocklimit >= pool[count].gasLimit):
                    blocklimit -= pool[count].usedGas
                    transactions += [pool[count]]
                    limit += pool[count].usedGas
                count+=1

        return transactions, limit

class FullTransaction():
    x=0 # counter to only fit distributions once during the simulation

    def create_transactions(rate):
        # Tn为每秒生成的交易数，Binterval为生成区块的平均时间，Psize应为区块链总交易数
        # Psize= int(p.Tn * p.simTime) # p.Binterval 改为 p.simTime
        Psize = 2000
        # x为拟合分布的次数，即从读取现实区块链数据的次数
        # if FullTransaction.x<1:
        #     DistFit.fit() # fit distributions 拟合分布，耗时最长，只进行一次
        # gasLimit,usedGas,gasPrice,_ = DistFit.sample_transactions(Psize) # sampling gas based attributes for transactions from specific distribution
        # 直接读取拟合结果
        gasLimit, usedGas, gasPrice, _ = DistFit_result.getresult()
        #依次生成基本交易
        print("共创建",Psize,"条正常交易")
        for i in range(Psize):
            # assign values for transactions' attributes. You can ignore some attributes if not of an interest, and the default values will then be used
            #交易初始化
            tx= Transaction()
            #随机生成交易id,random.randrange随机范围内选择任意元素,random.randint随机范围内选择任意整数
            tx.id= random.randrange(100000000000)
            #生成交易时间戳
            creation_time= random.randint(0,p.simTime-1)
            receive_time= creation_time
            tx.timestamp= [creation_time,receive_time]
            #定义交易相关参数, random.choice从元组中随机选择一个元素
            sender= random.choice (p.NODES)
            tx.sender = sender.id
            tx.to= random.choice (p.NODES).id
            tx.gasLimit=gasLimit[i]
            tx.usedGas=usedGas[i]
            tx.gasPrice=gasPrice[i]/1000000000
            tx.fee= tx.usedGas * tx.gasPrice
            # print("%s号正常交易的创建时间为："%(tx.id)+"%s"%(tx.timestamp[0]))
            #交易加入交易池
            sender.transactionsPool.append(tx)
            FullTransaction.transaction_prop(tx)
        # 依次生成特殊交易
        if (Read_result.hasTra):
            # lists = Read_result.read_result()
            # number = len(lists)
            number=int(Psize*p.Rate[rate])
            print("共创建",number,"条特殊交易")
            for i in range(number):
                # assign values for transactions' attributes. You can ignore some attributes if not of an interest, and the default values will then be used
                # # 交易初始化
                # tx = Transaction()
                # # 写入交易id
                # tx.id = lists[i]['id']
                # sender = p.NODES[lists[i]['sender']]
                # # 生成交易时间戳
                # creation_time = random.randint(0, p.simTime - 1)
                # receive_time = creation_time
                # tx.timestamp = [creation_time, receive_time]
                # # 写入交易相关参数
                # tx.sender = sender.id
                # tx.to = lists[i]['to']
                # tx.gasLimit = lists[i]['gasLimit']
                # tx.usedGas = lists[i]['usedGas']
                # tx.gasPrice = lists[i]['gasPrice'] / 1000000000
                # tx.fee = tx.usedGas * tx.gasPrice
                #交易初始化
                tx= Transaction()
                #随机生成交易id,random.randrange随机范围内选择任意元素,random.randint随机范围内选择任意整数
                tx.id= random.randrange(100000000000)
                #生成交易时间戳
                creation_time= random.randint(0,p.simTime-1)
                receive_time= creation_time
                tx.timestamp= [creation_time,receive_time]
                #定义交易相关参数, random.choice从元组中随机选择一个元素
                sender= random.choice (p.NODES)
                tx.sender = sender.id
                tx.to= random.choice (p.NODES).id
                tx.gasLimit=gasLimit[i]
                tx.usedGas=usedGas[i]
                tx.gasPrice=gasPrice[i]/1000000000
                tx.fee= tx.usedGas * tx.gasPrice
                # print("%s号异常交易的创建时间为："%(tx.id)+"%s"%(tx.timestamp[0]))
                # tx.gasLimit = gasLimit[i]*100
                # tx.usedGas = usedGas[i]*10
                # tx.gasPrice = gasPrice[i] / 10000000
                # tx.fee = tx.usedGas * tx.gasPrice
                tx.type = 1
                # 交易加入交易池
                sender.transactionsPool.append(tx)
                FullTransaction.transaction_prop(tx)


    # Transaction propogation & preparing pending lists for miners
    def transaction_prop(tx):
        # Fill each pending list. This is for transaction propogation
        for i in p.NODES:
            if tx.sender != i.id:
                t= tx
                t.timestamp[1] = t.timestamp[1] + Network.tx_prop_delay() # transaction propogation delay in seconds
                i.transactionsPool.append(t)


    def execute_transactions(miner,currentTime):
        transactions= [] # prepare a list of transactions to be included in the block
        limit = 0 # calculate the total block gaslimit
        count=0
        SpecialTra = 0
        blocklimit = p.Blimit
        
        miner.transactionsPool.sort(key=operator.attrgetter('gasPrice'), reverse=True)
        pool = miner.transactionsPool

        while count < len(pool):
            if (pool[count].type==1):
                if  (blocklimit >= pool[count].gasLimit and pool[count].timestamp[1] <= currentTime):
                    blocklimit -= pool[count].usedGas
                    transactions += [pool[count]]
                    limit += pool[count].usedGas
                    SpecialTra += 1
                    # for i in p.NODES:
                    #    del  i.transactionsPool[count]
                    pool.pop(count)
            count+=1
        
        count=0
        while count < len(pool):
            if  (blocklimit >= pool[count].gasLimit and pool[count].timestamp[1] <= currentTime):
                blocklimit -= pool[count].usedGas
                transactions += [pool[count]]
                limit += pool[count].usedGas
                # for i in p.NODES:
                #        del  i.transactionsPool[count]
                pool.pop(count)
            count+=1

        # print("矿工",miner.id,"生成",SpecialTra,"条特殊交易")

        return transactions, limit,SpecialTra

