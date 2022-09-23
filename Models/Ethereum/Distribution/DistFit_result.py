import numpy as np
class DistFit_result():
    def getresult():
        
        fname = 'gasLimit.txt'
        gasLimit=np.loadtxt(fname)
        
        fname = 'usedGas.txt'
        usedGas =np.loadtxt(fname)
        
        fname = 'gasPrice.txt'
        gasPrice =np.loadtxt(fname)
        
        CPUTime=[]

        return gasLimit, usedGas, gasPrice, CPUTime
