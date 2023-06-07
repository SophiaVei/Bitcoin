# Bitcoin

Implementation of two scripts using Python 3 and any additional library bitcoin-utils.

The first one (Script1.py) creates a P2SH Bitcoin address where all funds sent to it are locked
until a specific time, specified either by block height, or UNIX Epoch time; other than the
time locking the redeem script is equivalent to P2PKH.

The second program (Script2.py) allows someone to spend all funds from this address.

Both programs:  
● uses regtest
● assumse a local Bitcoin regtest node is running

The first program:
● accepts a public (or optionally a private) key for the P2PKH part of the redeem script
● accepts a future time expressed either in block height or in UNIX Epoch time
● displays the P2SH address

The second program:
● accepts a future time, expressed either in block height or in UNIX Epoch time, and a
private key (to recreate the redeem script as above and also uses to unlock the
P2PKH part)
● accepts a P2SH address to get the funds from (the one created by the first script)
● checks if the P2SH address has any UTXOs to get funds from
● accepts a P2PKH address to send the funds to
● calculates the appropriate fees with respect to the size of the transaction
● sends all funds that the P2SH address received to the P2PKH address provided
● displays the raw unsigned transaction
● signs the transaction
● displays the raw signed transaction
● displays the transaction id
● verifies that the transaction is valid and will be accepted by the Bitcoin nodes
● if the transaction is valid, it is sent to the blockchain
