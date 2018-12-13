import logging
import argparse
import json
import time
import random
import calendar

from web3 import Web3
from datetime import datetime

from classes.GroupsManager import GroupsManager as GSM
from classes.MarketsManager import MarketsManager as MSM
from classes.NGT import NGT

def actuate_manual_commands(web3, operation_mode, wallets, contracts, cfg, logger):
    data = operation_mode.split(',')
    cmd = data[0]
    args = data[1:len(data)]

    # Mint new NGTs
    if cmd == 'MINT':
        address = web3.toChecksumAddress(web3.eth.accounts[int(args[0])])
        amount = args[1]

        # mint new tokens
        contracts['ngt'].mint(minter=wallets['owner'], beneficiary=address, amount=int(amount))
        logger.info('Minted %s NGTs and assigned to %s, current balance = %s NGT' % (amount, address,
                                                                                     contracts['ngt'].balance(address)))
    # Get balance
    elif cmd == 'BALANCE':
        address = web3.toChecksumAddress(web3.eth.accounts[int(args[0])])
        logger.info('Amount[%s] = %i NGT' % (address, contracts['ngt'].balance(address)))    # Get balance

    # Get balance for a given address
    elif cmd == 'BALANCE_ADDR':
        address = web3.toChecksumAddress(args[0])
        logger.info('Amount[%s] = %i NGT' % (address, contracts['ngt'].balance(address)))

    # Get allowance
    elif cmd == 'ALLOWANCE':
        owner = web3.toChecksumAddress(web3.eth.accounts[int(args[0])])
        spender = web3.toChecksumAddress(args[1])
        logger.info('Allowance[%s->%s] = %i NGT' % (owner, spender, contracts['ngt'].allowance(owner, spender)))

    # Get address of the markets manager for a given dso
    elif cmd == 'ADDR_MARKETS_MANAGER':
        dso = web3.toChecksumAddress(web3.eth.accounts[int(args[0])])
        logger.info('Address = %s' % contracts['gsm'].get_address(dso))

    # Modify token allowance
    elif cmd == 'ALLOW':
        owner = web3.toChecksumAddress(web3.eth.accounts[int(args[0])])
        spender = web3.toChecksumAddress(args[1])
        amount = args[2]

        # increase the token allowance
        contracts['ngt'].increase_allowance(allower=owner, beneficiary=spender, amount=int(amount))
        logger.info('Allowance of %s for %s set to %i NGT' % (owner, spender, contracts['ngt'].allowance(owner, spender)))

    # add a group of markets
    elif cmd == 'ADD_GROUP':
        owner = web3.toChecksumAddress(web3.eth.accounts[int(args[0])])
        dso = web3.toChecksumAddress(web3.eth.accounts[int(args[1])])

        # increase the token allowance
        contracts['gsm'].add_group(owner=owner, dso=dso)
        logger.info('Group for DSO %s available at address %s' % (dso, contracts['gsm'].get_address(dso)))

    elif cmd == 'PREPARE':
        # define accounts

        if contracts['gsm'].get_flag(dso=wallets['dso']) is False:
            # create group
            logger.info('Create group for DSO %s' % wallets['dso'])
            contracts['gsm'].add_group(owner=wallets['owner'], dso=wallets['dso'])

        # get address of the market manager
        addr_mm = contracts['gsm'].get_address(dso=wallets['dso'])

        # mint token
        logger.info('Mint')
        contracts['ngt'].mint(minter=wallets['owner'], beneficiary=wallets['dso'],
                              amount=cfg['marketsSettings']['tokens']['minting']['forDSO'])
        contracts['ngt'].mint(minter=wallets['owner'], beneficiary=wallets['player'],
                              amount=cfg['marketsSettings']['tokens']['minting']['forPlayer'])
        contracts['ngt'].mint(minter=wallets['owner'], beneficiary=wallets['referee'],
                              amount=cfg['marketsSettings']['tokens']['minting']['forReferee'])
        # set allowance
        logger.info('Set allowance')
        contracts['ngt'].increase_allowance(allower=wallets['dso'], beneficiary=addr_mm,
                                            amount=cfg['marketsSettings']['tokens']['allowance']['DSO2Market'])
        contracts['ngt'].increase_allowance(allower=wallets['player'], beneficiary=addr_mm,
                                            amount=cfg['marketsSettings']['tokens']['allowance']['Player2Market'])

    else:
        logger.warning('Command %s is not available' % operation_mode)


# Main
if __name__ == "__main__":
    # get input arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-o', help='operation mode')
    arg_parser.add_argument('-c', help='configuration file')
    arg_parser.add_argument('-l', help='log file')
    args = arg_parser.parse_args()

    # set operation mode
    operation_mode = args.o

    # set configuration dictionary
    cfg = json.loads(open(args.c).read())

    # set logging object
    if not args.l:
        log_file = None
    else:
        log_file = args.l

    # logger
    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)-15s::%(levelname)s::%(funcName)s::%(message)s', level=logging.INFO,
                        filename=log_file)

    logging.info('Starting program')

    # set the web3 provider instance
    if cfg['web3Provider']['type'] == 'ipc':
        web = Web3(Web3.IPCProvider(cfg['web3Provider']['url']))
    elif cfg['web3Provider']['type'] == 'http':
        web3 = Web3(Web3.HTTPProvider(cfg['web3Provider']['url']))

    # define the wallets of the actors with thhe proper format
    wallets = {
                'owner': web3.toChecksumAddress(web3.eth.accounts[cfg['walletsAccount']['owner']]),
                'dso': web3.toChecksumAddress(web3.eth.accounts[cfg['walletsAccount']['dso']]),
                'player': web3.toChecksumAddress(web3.eth.accounts[cfg['walletsAccount']['player']]),
                'referee': web3.toChecksumAddress(web3.eth.accounts[cfg['walletsAccount']['referee']])
              }

    # define the contracts
    sc_folder = '%sbuild/contracts/' % cfg['smartContracts']['truffleProjectFolder']
    contracts = {
                    'ngt': NGT(web3=web3, address=cfg['smartContracts']['NGT']['address'], logger=logger,
                               truffle_output_file='%s%s' % (sc_folder, cfg['smartContracts']['NGT']['fileName'])),

                    'gsm': GSM(web3=web3, address=cfg['smartContracts']['GroupsManager']['address'], logger=logger,
                               truffle_output_file='%s%s' % (sc_folder, cfg['smartContracts']['GroupsManager']['fileName']))
                }
    logger.info('Operation mode -> %s' % operation_mode)

    # Simulator mode (SIM)
    if operation_mode == 'SIM':
        # get the address of the markets manager
        addr_mm = contracts['gsm'].get_address(dso=wallets['dso'])

        msm = MSM(web3=web3, address=addr_mm, logger=logger,
                  truffle_output_file='%s%s' % (sc_folder, cfg['smartContracts']['MarketsManager']['fileName']))

        while True:
            # Start a market
            logger.info('Start a market')

            logger.info('Open the market')
            idx = msm.open(dso=wallets['dso'], player=wallets['player'], referee=wallets['referee'],
                           pars=cfg['smartContracts']['MarketsManager']['defaults'])

            logger.info('state[%i] = %i' % (idx, msm.get_state(idx=idx)))

            # wait for a second
            time.sleep(1)

            logger.info('Confirm the market opening')
            msm.confirm_opening(player=wallets['player'], idx=idx,
                                staking=cfg['smartContracts']['MarketsManager']['defaults']['playerStaking'])
            logger.info('state[%i] = %i' % (idx, msm.get_state(idx=idx)))

            logger.info('DSO balance = %i' % contracts['ngt'].balance(wallets['dso']))
            logger.info('Player balance = %i' % contracts['ngt'].balance(wallets['player']))

            # set a random power peak
            power_peak = random.randint(cfg['marketsSettings']['minPower'], cfg['marketsSettings']['maxPower'])
            logger.info('Simulated measured power peak = %i kW' % power_peak)

            # set the seconds to wait
            secs_to_wait = msm.get_end_time(idx=idx) - int(calendar.timegm(datetime.utcnow().timetuple())) + 10

            # wait for the market end
            logger.info('Wait for %i seconds' % secs_to_wait)
            time.sleep(secs_to_wait)

            # settle the market
            logger.info('Settle the market')
            msm.settle(dso=wallets['dso'], idx=idx, power_peak=power_peak)
            logger.info('state[%i] = %i' % (idx, msm.get_state(idx=idx)))

            # wait for a second
            time.sleep(1)

            # confirm the settlement
            logger.info('Confirm the market settlement')
            msm.confirm_settle(player=wallets['player'], idx=idx, power_peak=power_peak)
            logger.info('state[%i] = %i' % (idx, msm.get_state(idx=idx)))

            logger.info('DSO balance = %i' % contracts['ngt'].balance(wallets['dso']))
            logger.info('Player balance = %i' % contracts['ngt'].balance(wallets['player']))

            # Wait for 5 seconds
            logger.info('Wait for 5 seconds')
            time.sleep(5)

    # manual operation mode
    else:
        actuate_manual_commands(web3=web3, operation_mode=operation_mode, wallets=wallets, contracts=contracts,
                                cfg=cfg, logger=logger)
