import json

from web3 import Web3

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
        output_string = '0x'
        for i in range(0, len(input_hexbytes)):
            output_string += format(input_hexbytes[i], '02x')
        return output_string

