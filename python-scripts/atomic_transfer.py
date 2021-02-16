import json, time, base64, os
from algosdk.v2client import algod
from algosdk import mnemonic
from algosdk.future import transaction
from algosdk import encoding
from algosdk import account

# user declared account mnemonics for account1 and account2
with open('../accountA.creds', 'r') as fd:
    info = [line.strip() for line in fd]
    mnemonic_1 = info[2].split(': ')[1]
with open('../accountB.creds', 'r') as fd:
    info = [line.strip() for line in fd]
    mnemonic_2 = info[2].split(': ')[1]

# user declared algod connection parameters
algod_address = "https://api.testnet.algoexplorer.io"
algod_token = ""

# Function that waits for a given txId to be confirmed by the network
def wait_for_confirmation(client, txid):
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo

# utility function to get address string
def get_address(mn) :
    pk_account_a = mnemonic.to_private_key(mn)
    address = account.address_from_private_key(pk_account_a)
    print("Address :", address)
    return address

# utility function to generate new account
def generate_new_account() :
    private_key, address = account.generate_account()
    print("Created new account: ", address)
    print("Generated mnemonic: \"{}\"".format(mnemonic.from_private_key(private_key)))
    return address    

# utility function to display account balance
def display_account_algo_balance(client, address) :
    account_info = client.account_info(address)
    print("{}: {} microAlgos".format(address, account_info["amount"]))

def group_transactions() :
	# Initialize an algodClient
    algod_client = algod.AlgodClient(algod_token, algod_address, headers={ "User-Agent": "DoYouLoveMe?" })

	# declared account1 and account2 based on user supplied mnemonics
    print("Loading two existing accounts...")
    account_1 = get_address(mnemonic_1)
    account_2 = get_address(mnemonic_2)

	# convert mnemonic1 and mnemonic2 using the mnemonic.ToPrivateKey() helper function
    sk_1 = mnemonic.to_private_key(mnemonic_1)
    sk_2 = mnemonic.to_private_key(mnemonic_2)

	# display account balances
    print("Initial balances:")
    display_account_algo_balance(algod_client, account_1)
    display_account_algo_balance(algod_client, account_2)

	# get node suggested parameters
    params = algod_client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

	# create transactions
    print("Creating transactions...")
	# from account 2 to account 1
    sender = account_2
    receiver = account_1
    amount = 12 * 1000000
    txn_1 = transaction.PaymentTxn(sender, params, receiver, amount)
    print("...txn_1: from {} to {} for {} microAlgos".format(sender, receiver, amount))
    print("...created txn_1: ", txn_1.get_txid())

	# from account 1 to account 2
    sender = account_1
    receiver = account_2
    amount = 1
    txn_2 = transaction.AssetTransferTxn(sender, params, receiver, amount, 14075399)
    print("...txn_2: from {} to {} for {} microAlgos".format(sender, receiver, amount))
    print("...created txn_2: ", txn_2.get_txid())

	# combine transations
    print("Combining transactions...")
	# the SDK does this implicitly within grouping below
     
    print("Grouping transactions...")
	# compute group id and put it into each transaction
    group_id = transaction.calculate_group_id([txn_1, txn_2])
    print("...computed groupId: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id

	# split transaction group
    print("Splitting unsigned transaction group...")
    # this example does not use files on disk, so splitting is implicit above

	# sign transactions
    print("Signing transactions...")
    stxn_1 = txn_1.sign(sk_2)
    print("...account1 signed txn_1: ", stxn_1.get_txid())
    stxn_2 = txn_2.sign(sk_1)
    print("...account2 signed txn_2: ", stxn_2.get_txid())

	# assemble transaction group
    print("Assembling transaction group...")
    signedGroup =  []
    signedGroup.append(stxn_1)
    signedGroup.append(stxn_2)

	# send transactions
    print("Sending transaction group...")
    tx_id = algod_client.send_transactions(signedGroup)

    # wait for confirmation
    wait_for_confirmation(algod_client, tx_id) 

	# display account balances
    print("Final balances:")
    display_account_algo_balance(algod_client, account_1)
    display_account_algo_balance(algod_client, account_2)

	# display confirmed transaction group
	# tx1
    confirmed_txn = algod_client.pending_transaction_info(txn_1.get_txid())
    print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4)))

	# tx2
    confirmed_txn = algod_client.pending_transaction_info(txn_2.get_txid())
    print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4)))

group_transactions()
