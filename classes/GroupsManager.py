from classes.SmartContractInterface import SmartContractInterface as SMI

class GroupsManager (SMI):
    """
    Interface class to interact with GroupsManager contract
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

    def add_group(self, owner, dso):
        """
        Add a group

        :param owner: address of the owner
        :type owner: string
        :param dso: address of the DSO
        :type dso: string
        """
        if self.get_flag(dso) is False:
            try:
                tx_pars = {
                            'from': self.web3.toChecksumAddress(owner),
                            'gas': self.contract.functions.addGroup(self.web3.toChecksumAddress(dso)).estimateGas(),
                            'gasPrice': self.web3.eth.gasPrice
                          }

                tx_hash = self.contract.functions.addGroup(dso).transact(tx_pars)
                self.logger.info('Transaction %s created into the pool' % SMI.hexbytes_2_string(tx_hash))

                # wait for the transaction mining
                res = self.web3.eth.waitForTransactionReceipt(tx_hash, timeout=300)

                self.logger.info('Transaction %s successfully mined in block %i' % (SMI.hexbytes_2_string(tx_hash),
                                                                                    res['blockNumber']))
            except Exception as e:
                self.logger.error('REVERT: Unable to add group for address %s' % dso)
        else:
            self.logger.info('Group already exist at address %s' % self.get_address(dso))

    def get_flag(self, dso):
        return self.contract.functions.getFlag(dso).call()

    def get_address(self, dso):
        return self.contract.functions.getAddress(dso).call()
