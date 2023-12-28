import json
import environ

from web3 import Web3, HTTPProvider

env = environ.Env()
environ.Env.read_env()
blockchain_address = env("BLOCKCHAIN_ADDRESS")
web3 = Web3(HTTPProvider(blockchain_address))
web3.eth.default_account = web3.eth.accounts[0]

compiled_contract_path = (
    "/home/sanah/Desktop/token_master/build/contracts/TokenMaster.json"
)
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

    # Replace occasion_id and seat_number with actual values
    # refund_ticket(31, 5)
    transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    print("Transaction Hash:", transaction_hash)
    message = contract.functions.sayHello().call()
    print(message)


send_transaction()


def create_occasion():

    occasion_name = "Udaipur Occasion"
    occasion_cost = 100
    occasion_max_tickets = 10

    tx_hash = contract.functions.list(
        occasion_name,
        occasion_cost,
        occasion_max_tickets,
        "2024-01-01",
        "12:00 PM",
        "Udaipur Location",
    ).transact()

    web3.eth.waitForTransactionReceipt(tx_hash)
    occasion_id = contract.functions.totalOccasions().call()

    return occasion_id


occasion_id = create_occasion()
print("Occasion ID:", occasion_id)


def get_occasion_and_seat():

    occasion = contract.functions.getOccasion(occasion_id).call()

    seat_number = occasion[8] + 5

    return occasion_id, seat_number


occasion_id, seat_number = get_occasion_and_seat()

print("Seat Number:", seat_number)


def book_ticket(occasion_id, seat_number):
    try:
        occasion = contract.functions.getOccasion(occasion_id).call()
        if occasion[0] == 0:
            print("Invalid occasion ID")
            return
        if not (1 <= seat_number <= occasion[4]):
            print("Invalid seat number")
            return

        if (
            contract.functions.seatTaken(occasion_id, seat_number).call()
            != "0x0000000000000000000000000000000000000000"
        ):
            print("Seat is already taken at this address")
            return

        if occasion[8] >= occasion[4]:
            print("All seats are booked")
            return

        ticket_cost = occasion[2]
        if web3.eth.getBalance(web3.eth.default_account) < ticket_cost:
            print("Insufficient funds")
            return

        transaction_params = {
            "from": web3.eth.default_account,
            "gas": 300000,
            "gasPrice": web3.toWei("10", "gwei"),
            "value": ticket_cost,
        }

        tx_hash = contract.functions.bookTicket(occasion_id, seat_number).transact(
            transaction_params
        )
        web3.eth.waitForTransactionReceipt(tx_hash)

        print(
            f"Ticket successfully booked for Seat {seat_number} in Occasion {occasion_id}"
        )

    except Exception as e:
        print(f"Error booking ticket: {e}")


book_ticket(occasion_id, seat_number)


def refund_ticket(occasion_id, seat_number):
    try:

        buyer_address = contract.functions.seatTaken(occasion_id, seat_number).call()
        if buyer_address == "0x0000000000000000000000000000000000000000":
            print(f"Seat {seat_number} in Occasion {occasion_id} is not taken")
            return

        has_bought = contract.functions.hasBought(occasion_id, buyer_address).call()
        if not has_bought:
            print(
                f"Buyer at address {buyer_address} has not bought a ticket for Seat {seat_number}"
            )
            return

        ticket_cost = contract.functions.getSeatInfo(occasion_id, seat_number).call()[0]
        transaction_params = {
            "from": web3.eth.default_account,
            "gas": 300000,
            "gasPrice": web3.toWei("10", "gwei"),
        }

        tx_hash = contract.functions.refundTicket(occasion_id, seat_number).transact(
            transaction_params
        )
        web3.eth.waitForTransactionReceipt(tx_hash)

        print(
            f"Ticket successfully refunded for Seat {seat_number} in Occasion {occasion_id} to {buyer_address}"
        )

    except Exception as e:
        print(f"Error refunding ticket: {e}")


refund_ticket(occasion_id, seat_number)
