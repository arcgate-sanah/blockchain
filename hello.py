import json
import environ

from web3 import Web3, HTTPProvider

env = environ.Env()
environ.Env.read_env()

blockchain_address = env("BLOCKCHAIN_ADDRESS")

web3 = Web3(HTTPProvider(blockchain_address))

web3.eth.defaultAccount = web3.eth.accounts[0]

compiled_contract_path = "build/contracts/HelloWorld.json"

deployed_contract_address = ("DEPLOYED_CONTRACT_ADDRESSES")

with open(compiled_contract_path) as file:
    contract_json = json.load(file)
    contract_abi = contract_json["abi"]

contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)

message = contract.functions.sayHello().call()

print(message)
