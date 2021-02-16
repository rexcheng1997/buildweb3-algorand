from algosdk import account, mnemonic

private_key, account_address = account.generate_account()
words = mnemonic.from_private_key(private_key)

with open('../accountA.creds', 'w') as fd:
    fd.write(f'Account address: {account_address}\n')
    fd.write(f'Private key: {private_key}\n')
    fd.write(f'Private key mnemonic: {words}')
