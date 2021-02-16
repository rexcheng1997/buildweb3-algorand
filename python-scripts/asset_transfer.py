import json
from algosdk import mnemonic
from algosdk.v2client import algod
from algosdk.future.transaction import AssetTransferTxn

def wait_for_confirmation(client, txid):
    """
    Utility function to wait until the transaction is
    confirmed before proceeding.
    """
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo

def print_asset_holding(algod_client, account, asset_id):
    account_info = algod_client.account_info(account)
    i = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][i]
        i += 1
        if scrutinized_asset['asset-id'] == asset_id:
            print('Asset ID: {}'.format(scrutinized_asset['asset-id']))
            print(json.dumps(scrutinized_asset, indent=4))
            break

accountA = dict()
with open('../accountA.creds', 'r') as fd:
    info = [line.strip() for line in fd]
    accountA['mnemonic'] = info[2].split(': ')[1]
    accountA['pk'] = mnemonic.to_public_key(accountA['mnemonic'])
    accountA['sk'] = mnemonic.to_private_key(accountA['mnemonic'])
accountB = dict()
with open('../accountB.creds', 'r') as fd:
    info = [line.strip() for line in fd]
    accountB['mnemonic'] = info[2].split(': ')[1]
    accountB['pk'] = mnemonic.to_public_key(accountB['mnemonic'])
    accountB['sk'] = mnemonic.to_private_key(accountB['mnemonic'])

algod_client = algod.AlgodClient(algod_token='', algod_address='https://api.testnet.algoexplorer.io', headers={ 'User-Agent': 'DoYouLoveMe?' })

params = algod_client.suggested_params()
params.fee = 1000
params.flat_fee = True
asset_id = 14075399
txn = AssetTransferTxn(sender=accountA['pk'], sp=params, receiver=accountB['pk'], amt=1, index=asset_id)
stxn = txn.sign(accountA['sk'])
txid = algod_client.send_transaction(stxn)
print(txid)
wait_for_confirmation(algod_client, txid)
print_asset_holding(algod_client, accountB['pk'], asset_id)
