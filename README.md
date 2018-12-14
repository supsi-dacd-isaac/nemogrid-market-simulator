# Simulator for NEMoGrid Energy markets

The main aim of `simulator.py` script is to interact with the [smart contracts](https://github.com/supsi-dacd-isaac/nemogrid-smart-contracts) 
of [NEMoGrid](http://nemogrid.eu/) project in order to simulate energy markets. Besides, the script can be used to send manual commands to the contracts.

Here is reported a generic usage of `simulator.py`:
<pre>
python3 simulator.py -o CMD,ARG1,ARG2 -c conf/example.json 
</pre>

In the following `CMD` and `ARG` will be described.

# Python requirements

The script works with Python3.6 or above, it is recommended to create a virtual environment. 
The required modules can be installed with the following command:

<pre>
(venv) # pip install -r requirements.txt
</pre>

# Ethereum requirements
`simulator.py` interacts with an [Ethereum](https://www.ethereum.org/) blockchain where the smart contracts are 
deployed using a Web3 provider, which is also a synced node of the blockchain. 
Presently, `http` and `ipc` provider types are supported. 

Currently, instances of [`GroupsManager`](https://github.com/supsi-dacd-isaac/nemogrid-smart-contracts/blob/master/contracts/GroupsManager.sol) and 
[`NGT`](https://github.com/supsi-dacd-isaac/nemogrid-smart-contracts/blob/master/contracts/NGT.sol) smart contracts are deployed on the [Ropsten](https://ropsten.etherscan.io/) network testnet at the following addresses:
  
`GroupsManager`: [0x5a6ec5f6a28fdb1177d9fd492bba57ae6f8cd698](https://ropsten.etherscan.io/address/0x5a6ec5f6a28fdb1177d9fd492bba57ae6f8cd698) 

`NGT`: [0x1b9705bd8c3ddaef2c0784c2cb230c0ba494ac12](https://ropsten.etherscan.io/address/0x1b9705bd8c3ddaef2c0784c2cb230c0ba494ac12)

If you want to play the markets using the aforementioned deployments you must:

1) Read and **understand** how the [NEMoGrid smart contracts](https://github.com/supsi-dacd-isaac/nemogrid-smart-contracts) work
2) Have a node synced to [Ropsten](https://ropsten.etherscan.io/) network. I did all the tests with [geth](https://github.com/ethereum/go-ethereum) client
3) Have at least three wallets (following named `dso`, `player`, `referee`) on the node with a reasonable amount of ethers to perform the transactions
4) Request to [@dstreppa]('https://github.com/dstreppa') the creation of a [`MarketsManager`](https://github.com/supsi-dacd-isaac/nemogrid-smart-contracts/blob/master/contracts/MarketsManager.sol) 
deployment and the related NGTs minting

# Start the simulator
Once the [`MarketsManager`](https://github.com/supsi-dacd-isaac/nemogrid-smart-contracts/blob/master/contracts/MarketsManager.sol) 
contract has been deployed for your DSO on the address `address_markets_manager` you have to:

1) Properly set the token allowances:
<pre>
(venv) # python simulator.py -o ALLOWANCE,dso,address_markets_manager,X -c conf/ropsten.json
(venv) # python simulator.py -o ALLOWANCE,player,address_markets_manager,X -c conf/ropsten.json
</pre>  

With the commands above the allowances are set to X NGTs.

2) Start the simulator

<pre>
(venv) # python simulator.py -o SIM -c conf/ropsten.json
</pre>  

By default, `simulator.py` runs every two hours a hourly market, taking into account the settings in `conf/ropsten.json`. 
For example `{"walletsAccount": {"dso"}} = 1` means that `eth.accounts[1]` of your `geth` client will be the `dso` in the markets.
For each market a random power peak is generated within the interval `[{"marketsSettings": {"minPower"}} - {"marketsSettings": {"maxPower"}}]`.
Currently, no `referee` transactions are needed to properly settle the markets, i.e. `dso` and `player` never cheat. 

# Acknowledgements
The NEMoGrid project has received funding in the framework of the joint programming initiative ERA-Net Smart Energy Systems’ focus initiative Smart Grids Plus, with support from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 646039.
The authors would like to thank the Swiss Federal Office of Energy (SFOE) and the Swiss Competence Center for Energy Research - Future Swiss Electrical Infrastructure (SCCER-FURIES), for their financial and technical support to this research work.