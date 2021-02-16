from sys import exit
import json, base64
from algosdk import mnemonic
from algosdk.v2client import algod
from algosdk.future.transaction import PaymentTxn

algod_client = algod.AlgodClient(algod_token='', algod_address='https://api.testnet.algoexplorer.io', headers={ 'User-Agent': 'DoYouLoveMe?' })

with open('../accountB.creds', 'r') as fd:
    info = [line.strip() for line in fd]
    account_address = info[0].split(': ')[1]
    passphrase = info[2].split(': ')[1]
    try:
        private_key = info[1].split(': ')[1]
    except:
        private_key = mnemonic.to_private_key(passphrase)

assert(account_address == mnemonic.to_public_key(passphrase))
assert(private_key == mnemonic.to_private_key(passphrase))

RECEIVER_ACCOUNT = '4O6BRAPVLX5ID23AZWV33TICD35TI6JWOHXVLPGO4VRJATO6MZZQRKC7RI'
TX_AMOUNT = int(1.42 * 1e6)

account_info = algod_client.account_info(account_address)
balance = account_info.get('amount')
print(f'Account balance: {balance} microAlgos')
assert(balance > TX_AMOUNT)

params = algod_client.suggested_params()
params.flat_fee = True
params.fee = 1e3
note = 'my second Algorand transaction'.encode()
unsigned_txn = PaymentTxn(account_address, params, RECEIVER_ACCOUNT, TX_AMOUNT, None, note)
signed_txn = unsigned_txn.sign(private_key)
txid = algod_client.send_transaction(signed_txn)
print(f'Pending transaction with txID: {txid}')

def wait_for_confirmation(client, txid, timeout):
    current = start = client.status()['last-round'] + 1;
    while current < start + timeout:
        try:
            pending_txn = client.pending_transaction_info(txid)
        except:
            return
        if pending_txn.get('confirmed-round', 0) > 0:
            return pending_txn
        elif pending_txn['pool-error']:
            raise Exception(f'pool error: {pending_txn["pool-error"]}')
        client.status_after_block(current)
        current += 1
    raise Exception(f'pending tx not found in timeout rounds, timeout value = : {timeout}')

try:
    confirmed_txn = wait_for_confirmation(algod_client, txid, 5)
except Exception as err:
    print(err)
    exit(-1)

print(f'Transaction information: {json.dumps(confirmed_txn, indent=4)}')
print('Note: {}'.format(base64.b64decode(confirmed_txn['txn']['txn']['note']).decode()))
