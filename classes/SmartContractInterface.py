import json

class SmartContractInterface:
    """
    Interface class for Ethereum smart contracts
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
        self.address = address
        self.truffle_output_file = truffle_output_file
        self.web3 = web3
        self.logger = logger

        # get the contract data
        with open(self.truffle_output_file) as json_data:
            data = json.load(json_data)

        # set the contract instance
        try:
            self.contract = self.web3.eth.contract(address=self.web3.toChecksumAddress(self.address), abi=data['abi'])
        except Exception as e:
            self.logger.error('Unable to define the smart contract: %s' % str(e))

    @staticmethod
    def hexbytes_2_string(input_hexbytes):
        """
        Transform a HexBytes object into a string

        :param input_hexbytes: input data
        :type input_hexbytes: HexBytes
        :return: output string
        :rtype: string
        """
        output_string = '0x'
        for i in range(0, len(input_hexbytes)):
            output_string += format(input_hexbytes[i], '02x')
        return output_string

    def _wait_transaction(self, tx_hash, timeout=300):
        """
        Wait for a transaction

        :param tx_hash: hash of the transaction to wait
        :type tx_hash: string
        :param timeout: timeout on the transaction
        :type timeout: int
        """

        self.logger.info('Transaction %s created into the pool' % self.hexbytes_2_string(tx_hash))

        # wait for the transaction mining
        res = self.web3.eth.waitForTransactionReceipt(tx_hash, timeout=timeout)

        self.logger.info('Transaction %s successfully mined in block %i' % (self.hexbytes_2_string(tx_hash),
                                                                            res['blockNumber']))
