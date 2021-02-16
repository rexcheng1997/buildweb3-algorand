import base64, json
from algosdk import mnemonic, encoding
from algosdk.v2client import algod
from algosdk.future.transaction import LogicSigTransaction, PaymentTxn, AssetTransferTxn, calculate_group_id

def wait_for_confirmation(client, txid):
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo

algod_client = algod.AlgodClient(algod_token='', algod_address='https://api.testnet.algoexplorer.io', headers={ "User-Agent": "DoYouLoveMe?" })

with open('../accountA.creds', 'r') as fd:
    info = [line.strip() for line in fd]
    accountA = info[2].split(': ')[1]
accountA = { 'pk': mnemonic.to_public_key(accountA), 'sk': mnemonic.to_private_key(accountA) }
other = '4O6BRAPVLX5ID23AZWV33TICD35TI6JWOHXVLPGO4VRJATO6MZZQRKC7RI'
asset_id = 14035004

params = algod_client.suggested_params()
params.fee = 1000
params.flat_fee = True

txn1 = PaymentTxn(accountA['pk'], params, other, 42 * 1000000)
txn2 = AssetTransferTxn(other, params, accountA['pk'], 1, asset_id)
print(f'First transaction ID: {txn1.get_txid()}')
print(f'Second transaction ID: {txn2.get_txid()}')

gid = calculate_group_id([txn1, txn2])
txn1.group = txn2.group = gid
print(f'Group ID of the two transactions: {gid}')

stxn1 = txn1.sign(accountA['sk'])
with open('../step5.lsig', 'rb') as fd:
    lsig = encoding.future_msgpack_decode(base64.b64encode(fd.read()))
stxn2 = LogicSigTransaction(txn2, lsig)
print(f'First signed transaction ID: {stxn1.get_txid()}')
print(f'Second signed transaction ID: {stxn2.get_txid()}')

txid = algod_client.send_transactions([stxn1, stxn2])
print(f'Send transaction with txID: {txid}')

confirmed_txn = wait_for_confirmation(algod_client, txid)
print(json.dumps(confirmed_txn, indent=4))
