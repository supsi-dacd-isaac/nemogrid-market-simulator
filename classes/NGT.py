from classes.SmartContractInterface import SmartContractInterface as SMI

class NGT (SMI):
    """
    Interface NGT smart contract
    """

    def __init__(self, web3, address, truffle_output_file, logger):
        """
        Constructor

        :param web3: Web3 provider
        :type web3: Web3 provider instance
        :param address: address of the contract
        :type address: string
        :param truffle_output_file: path of the Truffle output file containing the ABI data
        :type truffle_output_file: string
        :param logger: Logger
        :type logger: logger object
        """
        # set the main parameters
        super().__init__(web3, address, truffle_output_file, logger)

    def mint(self, minter, beneficiary, amount):
        pars = {
                    'from': self.web3.toChecksumAddress(minter),
                    'gas': self.contract.functions.mint(beneficiary, amount).estimateGas(),
                    'gasPrice': self.web3.eth.gasPrice
               }

        try:

            tx_hash = self.contract.functions.mint(beneficiary, amount).transact(pars)
            self.logger.info('Transaction %s created into the pool' % SMI.hexbytes_2_string(tx_hash))

            # wait for the transaction mining
            res = self.web3.eth.waitForTransactionReceipt(tx_hash, timeout=300)

            self.logger.info('Transaction %s successfully mined in block %i' % (SMI.hexbytes_2_string(tx_hash),
                                                                                res['blockNumber']))
        except Exception as e:
            self.logger.error('EXCEPTION -> %s' % str(e))

    def increase_allowance(self, allower, beneficiary, amount):
        pars = {
                    'from': self.web3.toChecksumAddress(allower),
                    'gas': self.contract.functions.increaseAllowance(beneficiary, amount).estimateGas(),
                    'gasPrice': self.web3.eth.gasPrice
               }

        try:

            tx_hash = self.contract.functions.increaseAllowance(beneficiary, amount).transact(pars)
            self.logger.info('Transaction %s created into the pool' % SMI.hexbytes_2_string(tx_hash))

            # wait for the transaction mining
            res = self.web3.eth.waitForTransactionReceipt(tx_hash, timeout=300)

            self.logger.info('Transaction %s successfully mined in block %i' % (SMI.hexbytes_2_string(tx_hash),
                                                                                res['blockNumber']))
        except Exception as e:
            self.logger.error('EXCEPTION -> %s' % str(e))

    def balance(self, address):
        return self.contract.functions.balanceOf(address).call()

    def allowance(self, owner, spender):
        return self.contract.functions.allowance(owner, spender).call()




