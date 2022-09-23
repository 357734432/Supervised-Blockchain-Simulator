from Scheduler import Scheduler
from InputsConfig import InputsConfig as p
from Models.Ethereum.Node import Node
from Statistics import Statistics
from Models.Ethereum.Transaction import LightTransaction as LT, FullTransaction as FT
from Models.Network import Network
from Models.Ethereum.Consensus import Consensus as c
from Models.BlockCommit import BlockCommit as BaseBlockCommit

class BlockCommit(BaseBlockCommit):
    # Handling and running Events
    def handle_event(self,event):
        if event.type == "create_block":
            self.generate_block(event)
        elif event.type == "receive_block":
            self.receive_block(event)

    # Block Creation Event
    def generate_block (self,event):
        miner = p.NODES[event.block.miner]
        minerId = miner.id
        eventTime = event.time
        blockPrev = event.block.previous
        if blockPrev == miner.last_block().id:
            Statistics.totalBlocks += 1 # count # of total blocks created!
            if p.hasTrans:
                if p.Ttechnique == "Light": blockTrans,blockSize = LT.execute_transactions()
                elif p.Ttechnique == "Full": blockTrans,blockSize,specialTra = FT.execute_transactions(miner,eventTime)

                event.block.transactions = blockTrans
                event.block.usedgas= blockSize
                event.block.specialTra = specialTra



            if p.hasUncles:
                self.update_unclechain(miner)
                blockUncles = Node.add_uncles(miner) # add uncles to the block
                event.block.uncles = blockUncles #(only when uncles activated)

            miner.blockchain.append(event.block)
            #print(eventTime,"时生成",event.block.id,"号区块，含有",len(event.block.transactions),"条交易")
            if p.hasTrans and p.Ttechnique == "Light":LT.create_transactions() # generate transactions
            self.propagate_block(event.block)
            self.generate_next_block(miner,eventTime)# Start mining or working on the next block

    # Block Receiving Event
    def receive_block (self,event):

        miner = p.NODES[event.block.miner]
        minerId = miner.id
        currentTime = event.time
        blockPrev = event.block.previous # previous block id


        node = p.NODES[event.node] # recipint
        lastBlockId= node.last_block().id # the id of last block
        #print(currentTime,"时接收",event.block.id,"号区块，含有",len(event.block.transactions),"条交易")
        #### case 1: the received block is built on top of the last block according to the recipient's blockchain ####
        if blockPrev == lastBlockId:
            node.blockchain.append(event.block) # append the block to local blockchain

            if p.hasTrans and p.Ttechnique == "Full": self.update_transactionsPool(node, event.block)

            self.generate_next_block(node,currentTime)# Start mining or working on the next block

         #### case 2: the received block is  not built on top of the last block ####
        else:
            depth = event.block.depth + 1
            if (depth > len(node.blockchain)):
                self.update_local_blockchain(node,miner,depth)
                self.generate_next_block(node,currentTime)# Start mining or working on the next block

            #### 2- if depth of the received block <= depth of the last block, then reject the block (add it to unclechain) ####
            else:
                 uncle=event.block
                 node.unclechain.append(uncle)

            if p.hasUncles: self.update_unclechain(node)
            if p.hasTrans and p.Ttechnique == "Full": 
                b=BaseBlockCommit()
                b.update_transactionsPool(node,event.block) # not sure yet.

    # Upon generating or receiving a block, the miner start working on the next block as in POW
    def generate_next_block(self,node,currentTime):
	    if node.hashPower > 0:
                 blockTime = currentTime + c.Protocol(node) # time when miner x generate the next block
                 Scheduler.create_block_event(node,blockTime)

    def generate_initial_events(self):
            currentTime=0
            for node in p.NODES:
            	self.generate_next_block(node,currentTime)

    def propagate_block (self,block):
        for recipient in p.NODES:
            if recipient.id != block.miner:
                blockDelay= Network.block_prop_delay() # draw block propagation delay from a distribution !! or you can assign 0 to ignore block propagation delay
                Scheduler.receive_block_event(recipient,block,blockDelay)
            else:
                Scheduler.receive_block_event(recipient,block,0)
    def update_local_blockchain(self,node,miner,depth):
        # the node here is the one that needs to update its blockchain, while miner here is the one who owns the last block generated
        # the node will update its blockchain to mach the miner's blockchain
        from InputsConfig import InputsConfig as p
        i=0
        while (i < depth):
            if (i < len(node.blockchain)):
                if (node.blockchain[i].id != miner.blockchain[i].id): # and (self.node.blockchain[i-1].id == Miner.blockchain[i].previous) and (i>=1):
                    node.unclechain.append(node.blockchain[i]) # move block to unclechain
                    newBlock = miner.blockchain[i]
                    node.blockchain[i]= newBlock
                    if p.hasTrans and p.Ttechnique == "Full": 
                        b=BaseBlockCommit()
                        b.update_transactionsPool(node,newBlock)
            else:
                newBlock = miner.blockchain[i]
                node.blockchain.append(newBlock)
                if p.hasTrans and p.Ttechnique == "Full": 
                    b=BaseBlockCommit()
                    b.update_transactionsPool(node,newBlock)
            i+=1

    # Upon receiving a block, update local unclechain to remove all uncles included in the received block
    def update_unclechain(self,node):
        ### remove all duplicates uncles in the miner's unclechain
        a = set()
        x=0
        while x < len(node.unclechain):
            if node.unclechain[x].id in a:
                del node.unclechain[x]
                x-=1
            else:
                a.add(node.unclechain[x].id)
            x+=1

        j=0
        while j < len (node.unclechain):
            for k in node.blockchain:
                if node.unclechain[j].id == k.id:
                    del node.unclechain[j] # delete uncle after inclusion
                    j-=1
                    break
            j+=1

        j=0
        while j < len (node.unclechain):
            c="t"
            for k in node.blockchain:
                u=0
                while u < len(k.uncles):
                    if node.unclechain[j].id == k.uncles[u].id:
                        del node.unclechain[j] # delete uncle after inclusion
                        j-=1
                        c="f"
                        break
                    u+=1
                if c=="f":
                    break
            j+=1
