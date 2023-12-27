import json
import environ

from web3 import Web3, HTTPProvider

env = environ.Env()
environ.Env.read_env()
blockchain_address = env("BLOCKCHAIN_ADDRESS")
web3 = Web3(HTTPProvider(blockchain_address))

compiled_contract_path = "build/contracts/TokenMaster.json"
deployed_contract_address = env("DEPLOYED_CONTRACT_ADDRESS")

with open(compiled_contract_path) as file:
    contract_json = json.load(file)
    contract_abi = contract_json["abi"]

contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)


def send_transaction():

    sender_private_key = env("SENDER_PRIVATE_KEY")

    sender_address = env("SENDER_ADDRESS")

    transaction_value = web3.toWei(1, "ether")

    nonce = web3.eth.getTransactionCount(sender_address)

    gas_price = web3.toWei("10", "gwei")

    gas_limit = 310000

    transaction_params = {
        "from": sender_address,
        "gas": gas_limit,
        "gasPrice": gas_price,
        "value": transaction_value,
        "nonce": nonce,
    }

    data = contract.functions.sendTransaction().buildTransaction(transaction_params)
    signed_transaction = web3.eth.account.sign_transaction(data, sender_private_key)

    transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    print("Transaction Hash:", transaction_hash)
    message = contract.functions.sayHello().call()
    print(message)


send_transaction()
