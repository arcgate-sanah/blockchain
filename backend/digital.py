import json
import environ
import mysql.connector
import time

from web3 import Web3, HTTPProvider


env = environ.Env()
environ.Env.read_env()
blockchain_address = env("BLOCKCHAIN_ADDRESS")
web3 = Web3(HTTPProvider(blockchain_address))
web3.eth.default_account = web3.eth.accounts[0]

compiled_contract_path = env("CONTRACT_JSON_PATH")
deployed_contract_address = env("DEPLOYED_CONTRACT_ADDRESS")

with open(compiled_contract_path) as file:
    contract_json = json.load(file)
    contract_abi = contract_json["abi"]

contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)

db = mysql.connector.connect(
    host=env("DB_HOST"),
    user=env("DB_USER"),
    password=env("DB_PASSWORD"),
    database=env("DB_DATABASE"),
)


timestap = time.time()


def send_transaction():
    sender_private_key = env("SENDER_PRIVATE_KEY")

    sender_address = env("SENDER_ADDRESS")

    transaction_value = web3.to_wei(1, "ether")

    nonce = web3.eth.get_transaction_count(sender_address)

    gas_price = web3.to_wei("10", "gwei")

    gas_limit = 310000

    transaction_params = {
        "from": sender_address,
        "gas": gas_limit,
        "gasPrice": gas_price,
        "value": transaction_value,
        "nonce": nonce,
    }

    data = contract.functions.sendTransaction().build_transaction(transaction_params)
    signed_transaction = web3.eth.account.sign_transaction(data, sender_private_key)
    transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    print("Transaction Hash:", transaction_hash)
    return transaction_hash


def create_occasion():
    occasion_name = "Udaipur Occasion"
    occasion_cost = 100
    occasion_max_tickets = 10

    tx_hash = contract.functions.list(
        occasion_name,
        occasion_cost,
        occasion_max_tickets,
        "2024-06-23",
        "12:00 PM",
        "Udaipur Location",
    ).transact()

    web3.eth.wait_for_transaction_receipt(tx_hash)
    occasion_id = contract.functions.totalOccasions().call()

    return occasion_id


occasion_id = create_occasion()


def get_occasion_and_seat():
    occasion = contract.functions.getOccasion(occasion_id).call()

    seat_number = occasion[8] + 5

    return occasion_id, seat_number


occasion_id, seat_number = get_occasion_and_seat()


def book_ticket(occasion_id, seat_number):
    try:
        occasion = contract.functions.getOccasion(occasion_id).call()
        if occasion[0] == 0:
            print("Invalid occasion ID")
            return
        if not (1 <= seat_number <= occasion[4]):
            print("Invalid seat number")
            return

        if occasion[8] >= occasion[4]:
            print("All seats are booked")
            return

        ticket_cost = occasion[2]
        if web3.eth.get_balance(web3.eth.default_account) < ticket_cost:
            print("Insufficient funds")
            return
        if occasion[8] >= occasion[4]:
            print("All seats are booked")
            return

        transaction_params = {
            "from": web3.eth.default_account,
            "gas": 300000,
            "gasPrice": web3.to_wei("10", "gwei"),
            "value": ticket_cost,
        }

        tx_hash = contract.functions.bookTicket(occasion_id, seat_number).transact(
            transaction_params
        )
        web3.eth.wait_for_transaction_receipt(tx_hash)

        print(
            f"Ticket successfully booked for Seat {seat_number} in Occasion {occasion_id}"
        )

    except Exception as e:
        print(f"Error booking ticket: {e}")


def save_transaction_to_database(transaction_hash, occasion_id, seat_number):
    mycursor = db.cursor()
    sql = "INSERT INTO tx_history (transaction_hash, occasion_id, seat_number) VALUES (%s, %s, %s)"
    transaction_hash_str = str(
        transaction_hash,
    )
    tx = (
        transaction_hash_str,
        occasion_id,
        seat_number,
    )
    mycursor.execute(sql, tx)
    db.commit()
    return tx


def retrieve_transaction_data(occasion_id, seat_number):
    mycursor = db.cursor()

    select_sql = "SELECT * FROM tx_history WHERE occasion_id = %s AND seat_number = %s"
    select_values = (occasion_id, seat_number)

    try:
        mycursor.execute(select_sql, select_values)
        retrieved_data = mycursor.fetchone()
        print("Retrieved data:", retrieved_data)
    except Exception as e:
        print(f"Error executing SELECT query: {e}")
        return None

    return retrieved_data


def refund_ticket(occasion_id, seat_number):
    try:
        buyer_address = contract.functions.seatTaken(occasion_id, seat_number).call()
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
            "gasPrice": web3.to_wei("10", "gwei"),
        }

        tx_hash = contract.functions.refundTicket(occasion_id, seat_number).transact(
            transaction_params
        )
        web3.eth.wait_for_transaction_receipt(tx_hash)

        print(
            f"Ticket successfully refunded for Seat {seat_number} in Occasion {occasion_id} to {buyer_address}"
        )

    except Exception as e:
        print(f"Error refunding ticket: {e}")


transaction_hash = send_transaction()
occasion_id = create_occasion()
occasion_id, seat_number = get_occasion_and_seat()
book_ticket(occasion_id, seat_number)
tx_database = save_transaction_to_database(transaction_hash, occasion_id, seat_number)
print("Save_transaction_to_database", tx_database)
retrieved_data = retrieve_transaction_data(occasion_id, seat_number)
refund_ticket(occasion_id, seat_number)
