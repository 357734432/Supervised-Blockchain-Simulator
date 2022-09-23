from Models.Ethereum.Distribution.DistFit import DistFit
from InputsConfig import InputsConfig as p
import numpy as np

#执行一次 保存2000条拟合数据

Trans_count = int(p.Tn * p.simTime)


DistFit.fit() # fit distributions 拟合分布，耗时最长，只进行一次

gasLimit,usedGas,gasPrice,_ = DistFit.sample_transactions(Trans_count) # sampling gas based attributes for transactions from specific distribution

fname = 'gasLimit.txt'
np.savetxt(fname,gasLimit)

fname = 'usedGas.txt'
np.savetxt(fname,gasLimit)

fname = 'gasPrice.txt'
np.savetxt(fname,gasLimit)

# f = open(fname,'w')
# f.write(str(gasPrice))
# f.close()