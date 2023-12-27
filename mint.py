from web3 import Web3, HTTPProvider
import json


blockchain_address = "http://127.0.0.1:7545"
web3 = Web3(HTTPProvider(blockchain_address))

web3.eth.defaultAccount = web3.eth.accounts[0]


json_file_path = "build/contracts/MintableToken.json"

account_address = "0x6F3C9AADb1ebC934bCC942999Db10eaC8bb1890E"

with open(json_file_path, "r") as file:
    contract_data = json.load(file)
    contract_abi = contract_data["abi"]
    contract_bytecode = contract_data["bytecode"]


def deploy_contract():
    MintableToken = web3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
    transaction_hash = MintableToken.constructor("MyMintableToken", "MTK").transact(
        {
            "from": account_address,
            "gas": 2000000,
            "gasPrice": web3.toWei("40", "gwei"),
        }
    )

    transaction_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
    contract_address = transaction_receipt["contractAddress"]

    return MintableToken(address=contract_address)


def mint_tokens(contract, to, amount):
    transaction_hash = contract.functions.mint(to, amount).transact(
        {
            "from": account_address,
            "gas": 2000000,
            "gasPrice": web3.toWei("40", "gwei"),
        }
    )

    web3.eth.wait_for_transaction_receipt(transaction_hash)


event_signature = web3.keccak(text="YourEventName(address,uint256)").hex()
print(f"Event Signature: {event_signature}")
mintable_token_contract = deploy_contract()


recipient_address = web3.eth.account.create().address
print(recipient_address)
mint_amount = 10000
mint_tokens(mintable_token_contract, recipient_address, mint_amount)


def watch_events(contract, event_signature):
    filter_params = {
        "address": contract.address,
        "topics": [event_signature],
    }

    logs = web3.eth.getLogs(filter_params)
    print("Raw Logs:")
    print(logs, "check")

    print("Event Details:")
    for log in logs:
        decoded_log = web3.eth.decodeLog(
            [
                {"type": "string", "name": "name", "indexed": False},
                {"type": "uint256", "name": "cost", "indexed": False},
                {"type": "uint256", "name": "tickets", "indexed": False},
                {"type": "string", "name": "date", "indexed": False},
                {"type": "string", "name": "time", "indexed": False},
                {"type": "string", "name": "location", "indexed": False},
            ],
            log.data,
            log.topics[1:],
        )
        print(f"Name: {decoded_log['name']}")
        print(f"Cost: {decoded_log['cost']} tokens")
        print(f"Tickets Available: {decoded_log['tickets']}")
        print(f"Date: {decoded_log['date']}")
        print(f"Time: {decoded_log['time']}")
        print(f"Location: {decoded_log['location']}")
        print("\n")


watch_events(mintable_token_contract, event_signature)
print(watch_events)
