from bitcoinrpc.authproxy import JSONRPCException
from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, Sequence
from bitcoinutils.keys import P2pkhAddress, P2shAddress, PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.constants import TYPE_ABSOLUTE_TIMELOCK
from bitcoinutils.proxy import NodeProxy
from decimal import Decimal
import requests

def main(p2pkh_input,destination,absblocks,from_p2sh_input):
    # always remember to setup the network
    setup('regtest')

    proxy = NodeProxy('kk', 'kk').get_proxy()

    absolute_blocks = absblocks

    p2pkh_sk = PrivateKey(p2pkh_input)

    p2pkh_addr = p2pkh_sk.get_public_key().get_address()

    seq = Sequence(TYPE_ABSOLUTE_TIMELOCK, absolute_blocks)

    redeem_script = Script([
        seq.for_script(), 'OP_CHECKLOCKTIMEVERIFY', 'OP_DROP', 'OP_DUP', 'OP_HASH160',
        p2pkh_addr.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'
    ])

    from_p2sh = P2shAddress.from_script(redeem_script)
    if from_p2sh.to_string()==from_p2sh_input:
        print("p2sh address verified")
    else:
        print("address not verified")
        exit()
    print("     source: " + from_p2sh.to_string())


    utxos = {}
    funds = Decimal(0)
    transactions = [tx for tx in proxy.listtransactions() if tx['address'] == from_p2sh.to_string()]

    for tx in transactions:
        txid = tx["txid"]
        amount = tx["amount"]
        utxos[txid] = tx
        if tx['category'] == 'send':
            funds -= amount

        print(" utxo tx id: " + str(txid))
        print(tx)
        print("utxo amount: " + str(amount))

    funds = int(to_satoshis(funds))
    if funds == 0:
        print("no funds")
        exit()
    print("      funds: " + str(funds) + " satoshis")

    destinationAddress = destination  # P2PKH destination address

    addressP2PKH = P2pkhAddress.from_address(destinationAddress)


    response= requests.get('https://mempool.space/api/v1/fees/recommended')
    feeRate= response.json()['fastestFee']
    txins = []

    for tx in transactions:
        txid = tx["txid"]
        vout = 0
        if "details" in tx and len(tx["details"]) > 0:
            vout = tx["details"][0]["vout"]
        txins.append(TxInput(txid, vout, sequence=b"\xfe\xff\xff\xff"))

    finalFee = (int(len(tx) * feeRate))/10**8

    amount = funds - finalFee
    txout = TxOutput(to_satoshis(amount), addressP2PKH.to_script_pub_key())

    tx = Transaction(txins, [txout])

    print("     amount: " + str(amount) + " satoshis")
    print("        finalFee: " + str(finalFee) + " satoshis")

    # Show the raw unsigned transaction
    print("raw unsigned transaction:\n" + tx.serialize())



    p2pkh_pk = p2pkh_sk.get_public_key()
    for j, txin in enumerate(txins):
        signature = p2pkh_sk.sign_input(tx, j, redeem_script)
        txin.script_sig = Script(
            [signature, p2pkh_pk.to_hex(), redeem_script.to_hex()]
        )

        # Display the raw signed transaction
    print("raw signed transaction:\n" + tx.serialize())



    print("   transaction id: " + tx.get_txid())

    # Verify that the transaction is valid and will be accepted by the Bitcoin nodes
    isvalid = proxy.testmempoolaccept([tx.serialize()])[0]["allowed"]
    result = proxy.testmempoolaccept([tx.serialize()])[0]
    isvalid = result["allowed"]
    reject_reason = result.get("reject-reason", "Unknown")


    # If the transaction is valid, send it to the blockchain
    if isvalid:
        proxy.sendrawtransaction(tx.serialize())
        print("The transaction has been successfully sent.")
    else:
        print("The transaction could not be sent.")


if __name__ == "__main__":
    main(p2pkh_input = 'cQpbwQxrH6ZTEqLBLR2budobtasgeys9JmWwnYShuAFeXnf3bhXV',destination = "mmNWnSurCKUcBR2tfUiSkeHBgtXk8UotVb",absblocks=int(10),from_p2sh_input="2N3iyJzpssk4fwRWZDaM1sNX5cSPZVJJGHC")