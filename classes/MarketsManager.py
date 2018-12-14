import calendar
from calendar import monthrange
from datetime import datetime, timedelta

from classes.SmartContractInterface import SmartContractInterface as SMI

class MarketsManager (SMI):
    """
    Interface class to interact with MarketsManager contract
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

    def open(self, dso, player, referee, pars):
        """
        Open a market

        :param dso: address of the DSO
        :type dso: string
        :param player: address of the player
        :type player: string
        :param referee: address of the referee
        :type referee: string
        :param pars: market parameters
        :type pars: dict
        :return market identifier
        :rtype int
        """

        # set the starting timestamp

        # monthly markets
        utc_now = datetime.utcnow()
        if pars['type'] == 0:
            days_info = monthrange(utc_now.year, utc_now.month)
            start_dt = utc_now+ timedelta(days=days_info[1])
            start_dt = datetime(start_dt.year, start_dt.month, 1, 0, 0, 0)
        # daily markets
        elif pars['type'] == 1:
            start_dt =utc_now + timedelta(days=1)
            start_dt = datetime(start_dt.year, start_dt.month, start_dt.day, 0, 0, 0)
        # hourly markets
        elif pars['type'] == 2:
            start_dt = utc_now + timedelta(hours=1)
            start_dt = datetime(start_dt.year, start_dt.month, start_dt.day, start_dt.hour, 0, 0)
        else:
            return False

        start_ts = calendar.timegm(start_dt.timetuple())

        try:
            tx_pars = {
                        'from': dso,
                        'gas': self.contract.functions.open(player,
                                                            start_ts,
                                                            pars['type'],
                                                            referee,
                                                            pars['maxLower'],
                                                            pars['maxUpper'],
                                                            pars['revenueFactor'],
                                                            pars['penaltyFactor'],
                                                            pars['dsoStaking'],
                                                            pars['playerStaking'],
                                                            pars['percReferee']).estimateGas({'from': dso}),
                        'gasPrice': self.web3.eth.gasPrice
                      }

            tx_hash = self.contract.functions.open(player,
                                                   start_ts,
                                                   pars['type'],
                                                   referee,
                                                   pars['maxLower'],
                                                   pars['maxUpper'],
                                                   pars['revenueFactor'],
                                                   pars['penaltyFactor'],
                                                   pars['dsoStaking'],
                                                   pars['playerStaking'],
                                                   pars['percReferee']).transact(tx_pars)
            self._wait_transaction(tx_hash)

            idx = self.calc_idx(address=player, ts=start_ts, market_type=2)
            self.logger.info('Created market with idx %s, ts=%i' % (idx, start_ts))
            self.logger.info('Player -> %s' % self.get_player(idx))
            self.logger.info('Start time -> %i' % self.get_start_time(idx))
            self.logger.info('End time -> %i' % self.get_end_time(idx))
            self.logger.info('State -> %i' % self.get_state(idx))
            return idx

        except Exception as e:
            self.logger.error('EXCEPTION -> %s' % str(e))
            return -1

    def confirm_opening(self, player, idx, staking):
        """
        Confirm a market opening

        :param player: address of the player
        :type player: string
        :param idx: market identifier
        :type idx: int
        :param staking: player staking
        :type staking: int
        """

        try:
            tx_pars = {
                        'from': player,
                        'gas': self.contract.functions.confirmOpening(idx, staking).estimateGas({'from': player}),
                        'gasPrice': self.web3.eth.gasPrice
                      }

            tx_hash = self.contract.functions.confirmOpening(idx, staking).transact(tx_pars)
            self._wait_transaction(tx_hash)

            self.logger.info('Confirmed opening of market with idx %s' % idx)

        except Exception as e:
            self.logger.error('EXCEPTION -> %s' % str(e))

    def settle(self, dso, idx, power_peak):
        """
        Settle the market

        :param dso: address of the dso
        :type dso: string
        :param idx: market identifier
        :type idx: int
        :param power_peak: measured power peak
        :type power_peak: int
        """
        try:
            tx_pars = {
                        'from': dso,
                        'gas': self.contract.functions.settle(idx, power_peak).estimateGas({'from': dso}),
                        'gasPrice': self.web3.eth.gasPrice
                      }

            tx_hash = self.contract.functions.settle(idx, power_peak).transact(tx_pars)
            self._wait_transaction(tx_hash)

            self.logger.info('Settlement market with idx %s' % idx)

        except Exception as e:
            self.logger.error('EXCEPTION -> %s' % str(e))

    def confirm_settle(self, player, idx, power_peak):
        """
        Confirm a settlement

        :param player: address of the player
        :type player: string
        :param idx: market identifier
        :type idx: int
        :param power_peak: measured power peak
        :type power_peak: int
        """
        try:
            tx_pars = {
                        'from': player,
                        'gas': self.contract.functions.confirmSettlement(idx, power_peak).estimateGas({'from': player}),
                        'gasPrice': self.web3.eth.gasPrice
                      }

            tx_hash = self.contract.functions.confirmSettlement(idx, power_peak).transact(tx_pars)
            self._wait_transaction(tx_hash)

            self.logger.info('Settlement market with idx %s' % idx)

        except Exception as e:
            self.logger.error('EXCEPTION -> %s' % str(e))

    def get_state(self, idx):
        return int(self.contract.functions.getState(idx).call())

    def get_flag(self, idx):
        return self.contract.functions.getFlag(idx).call()

    def get_start_time(self, idx):
        return self.contract.functions.getStartTime(idx).call()

    def get_end_time(self, idx):
        return self.contract.functions.getEndTime(idx).call()

    def get_player(self, idx):
        return self.contract.functions.getPlayer(idx).call()

    def calc_idx(self, address, ts, market_type):
        return self.contract.functions.calcIdx(address, ts, market_type).call()

