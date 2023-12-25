import json
from web3 import Web3, HTTPProvider


blockchain_address = "http://127.0.0.1:7545"

web3 = Web3(HTTPProvider(blockchain_address))

web3.eth.defaultAccount = web3.eth.accounts[0]

compiled_contract_path = "build/contracts/HelloWorld.json"

deployed_contract_address = "0x1550eD37945D8caEf58F0E44f80b30F3650d6C78"

with open(compiled_contract_path) as file:
    contract_json = json.load(file)
    contract_abi = contract_json["abi"]

contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)

message = contract.functions.sayHello().call()

print(message)
