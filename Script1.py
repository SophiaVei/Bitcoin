from bitcoinutils.setup import setup
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, Sequence
from bitcoinutils.keys import P2pkhAddress, P2shAddress, PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.constants import TYPE_ABSOLUTE_TIMELOCK
import argparse

def main():
    # always remember to setup the network
    setup('regtest')

    parser = argparse.ArgumentParser(description='Generate P2SH address from public key and future time')
    parser.add_argument('privateKey', type=str, help='P2PKH private key')  # private key
    parser.add_argument('futureTime', type=int, help='Future time expressed in block height')  # future time
    args = parser.parse_args()
    # set values
    absolute_blocks = args.futureTime

    # set values
    absolute_blocks = args.futureTime

    seq = Sequence(TYPE_ABSOLUTE_TIMELOCK, absolute_blocks)

    # secret key corresponding to the pubkey needed for the P2SH (P2PKH) transaction
    p2pkh_sk = PrivateKey(args.privateKey)

    # get the address (from the public key)
    p2pkh_addr = p2pkh_sk.get_public_key().get_address()

    # create the redeem script
    redeem_script = Script([seq.for_script(), 'OP_CHECKLOCKTIMEVERIFY', 'OP_DROP', 'OP_DUP', 'OP_HASH160', p2pkh_addr.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])

    # create a P2SH address from a redeem script
    addr = P2shAddress.from_script(redeem_script)
    print(addr.to_string())

if __name__ == "__main__":
    main()