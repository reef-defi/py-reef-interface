# Python Reef Interface

Python Reef Interface Library

## Description
This library specializes in interfacing with the Reef node, providing additional convenience methods to deal with
SCALE encoding/decoding (the default output and input format of the Substrate JSONRPC), metadata parsing, type registry
management and versioning of types. 

[Documentation](https://reef-defi.github.io/py-reef-interface/reefinterface/base.html#reefinterface.base.ReefInterface)

## Installation
```bash
pip install reef-interface
```

## Initialization

The following examples show how to initialize:

```python
from reefinterface import ReefInterface

reef = ReefInterface(url="testnet")
```

`url` can be `testnet`, `mainnet` or an `ws://<url>` URL for custom node.


## Features

### Retrieve extrinsics for a certain block

```python
# Set block_hash to None for chain tip
block_hash = "0x51d15792ff3c5ee9c6b24ddccd95b377d5cccc759b8e76e5de9250cf58225087"

# Retrieve extrinsics in block
result = reef.get_block(block_hash=block_hash)

for extrinsic in result['extrinsics']:
    if extrinsic.address:
        signed_by_address = extrinsic.address.value
    else:
        signed_by_address = None

    print('\nPallet: {}\nCall: {}\nSigned by: {}'.format(
        extrinsic.call_module.name,
        extrinsic.call.name,
        signed_by_address
    ))

    # Loop through call params
    for param in extrinsic.params:

        if param['type'] == 'Compact<Balance>':
            param['value'] = '{} {}'.format(param['value'] / 10 ** 18
            r.token_decimals, reef.token_symbol)

        print("Param '{}': {}".format(param['name'], param['value']))
```

### Subscribe to new block headers

```python
def subscription_handler(obj, update_nr, subscription_id):

    print(f"New block #{obj['header']['number']} produced by {obj['author']}")

    if update_nr > 10:
        return {'message': 'Subscription will cancel when a value is returned', 'updates_processed': update_nr}


result = reef.subscribe_block_headers(subscription_handler, include_author=True)
```

### Storage queries
The modules and storage functions are provided in the metadata (see
`reef.get_metadata_storage_functions()`),
parameters will be automatically converted to SCALE-bytes (also including decoding of SS58 addresses).

Example: 

```python
result = reef.query(
    module='System',
    storage_function='Account',
    params=['F4xQKRUagnSGjFqafyhajLs94e7Vvzvr8ebwYJceKpr8R7T']
)

print(result.value['nonce'])
print(result.value['data']['free'])
```

Or get the account info at a specific block hash:

```python
account_info = reef.query(
    module='System',
    storage_function='Account',
    params=['F4xQKRUagnSGjFqafyhajLs94e7Vvzvr8ebwYJceKpr8R7T'],
    block_hash='0x176e064454388fd78941a0bace38db424e71db9d5d5ed0272ead7003a02234fa'
)

print(account_info.value['nonce']) #  7673
print(account_info.value['data']['free']) # 637747267365404068
```

### Storage subscriptions

When a callable is passed as kwarg `subscription_handler`, there will be a subscription created for given storage query. 
Updates will be pushed to the callable and will block execution until a final value is returned. This value will be returned
as a result of the query and finally automatically unsubscribed from further updates.

```python
def subscription_handler(account_info_obj, update_nr, subscription_id):

    if update_nr == 0:
        print('Initial account data:', account_info_obj.value)

    if update_nr > 0:
        # Do something with the update
        print('Account data changed:', account_info_obj.value)

    # The execution will block until an arbitrary value is returned, which will be the result of the `query`
    if update_nr > 5:
        return account_info_obj


result = reef.query("System", "Account", ["5GNJqTPyNqANBkUVMN1LPPrxXnFouWXoe2wNSmmEoLctxiZY"],
                         subscription_handler=subscription_handler)

print(result)
```

### Query a mapped storage function
Mapped storage functions can be iterated over all key/value pairs, for these type of storage functions `query_map` 
can be used.

The result is a `QueryMapResult` object, which is an iterator:

```python
# Retrieve the first 199 System.Account entries
result = reef.query_map('System', 'Account', max_results=199)

for account, account_info in result:
    print(f"Free balance of account '{account.value}': {account_info.value['data']['free']}")
```

These results are transparently retrieved in batches capped by the `page_size` kwarg, currently the 
maximum `page_size` restricted by the RPC node is 1000    

```python
# Retrieve all System.Account entries in batches of 200 (automatically appended by `QueryMapResult` iterator)
result = reef.query_map('System', 'Account', page_size=200, max_results=400)

for account, account_info in result:
    print(f"Free balance of account '{account.value}': {account_info.value['data']['free']}")
```

### Create and send signed extrinsics

The following code snippet illustrates how to create a call, wrap it in a signed extrinsic and send it to the network:

```python
from reefinterface import ReefInterface, Keypair
from reefinterface.exceptions import SubstrateRequestException

reef = ReefInterface(url="testnet")

keypair = Keypair.create_from_mnemonic('episode together nose spoon dose oil faculty zoo ankle evoke admit walnut')

call = reef.compose_call(
    call_module='Balances',
    call_function='transfer',
    call_params={
        'dest': '5E9oDs9PjpsBbxXxRE9uMaZZhnBAV38n2ouLB28oecBDdeQo',
        'value': 1 * 10**18
    }
)

extrinsic = reef.create_signed_extrinsic(call=call, keypair=keypair)

try:
    receipt = reef.submit_extrinsic(extrinsic, wait_for_inclusion=True)
    print("Extrinsic '{}' sent and included in block '{}'".format(receipt.extrinsic_hash, receipt.block_hash))

except SubstrateRequestException as e:
    print("Failed to send: {}".format(e))
```

The `wait_for_inclusion` keyword argument used in the example above will block giving the result until it gets 
confirmation from the node that the extrinsic is succesfully included in a block. The `wait_for_finalization` keyword
will wait until extrinsic is finalized. Note this feature is only available for websocket connections. 

### Examining the ExtrinsicReceipt object

The `reef.submit_extrinsic` example above returns an `ExtrinsicReceipt` object, which contains information about the on-chain 
execution of the extrinsic. Because the `block_hash` is necessary to retrieve the triggered events from storage, most
information is only available when `wait_for_inclusion=True` or `wait_for_finalization=True` is used when submitting
an extrinsic. 


Examples:
```python
receipt = reef.submit_extrinsic(extrinsic, wait_for_inclusion=True)
print(receipt.is_success) # False
print(receipt.weight) # 216625000
print(receipt.total_fee_amount) # 2749998966
print(receipt.error_message['name']) # 'LiquidityRestrictions'
```

`ExtrinsicReceipt` objects can also be created for all existing extrinsics on-chain:

```python

receipt = ExtrinsicReceipt(
    reef=reef,
    extrinsic_hash="0x56fea3010910bd8c0c97253ffe308dc13d1613b7e952e7e2028257d2b83c027a",
    block_hash="0x04fb003f8bc999eeb284aa8e74f2c6f63cf5bd5c00d0d0da4cd4d253a643e4c9"
)

print(receipt.is_success) # False
print(receipt.extrinsic.call_module.name) # 'Identity'
print(receipt.extrinsic.call.name) # 'remove_sub'
print(receipt.weight) # 359262000
print(receipt.total_fee_amount) # 2483332406
print(receipt.error_message['docs']) # [' Sender is not a sub-account.']

for event in receipt.triggered_events:
    print(f'* {event.value}')
```

### Create mortal extrinsics

By default, _immortal_ extrinsics are created, which means they have an indefinite lifetime for being included in a 
block. However, it is recommended to use specify an expiry window, so you know after a certain amount of time if the 
extrinsic is not included in a block, it will be invalidated.

```python 
extrinsic = reef.create_signed_extrinsic(call=call, keypair=keypair, era={'period': 64})
```

The `period` specifies the number of blocks the extrinsic is valid counted from current head.


### Multi-signing

In the below example we see signing with Alice and Bob, who have a common Multisig account. The transfer will not be done until both of them sign the extrinsic. Other extrinsics are available [here](https://polkadot.js.org/docs/substrate/extrinsics/#multisig).


```python
# Multisig example
from reefinterface import Keypair, ReefInterface

# Connect to node
try:
    network = "ws://127.0.0.1:9944"
    substrate = ReefInterface(url=network)
except ConnectionRefusedError:
    print("Reef node could not be reached.")
    exit()

alice = Keypair.create_from_uri("//Alice")
bob = Keypair.create_from_uri("//Bob")

# Extrinsic to be multi-signed
transfer = substrate.compose_call(
    call_module="Balances",
    call_function="transfer",
    call_params={"dest": alice.ss58_address, "value": 123 * 10 ** 18},
)
extrinsic = substrate.create_unsigned_extrinsic(transfer)

# First sign will be done with alice
call = substrate.compose_call(
    call_module="Multisig",
    call_function="approve_as_multi",
    call_params={
        "threshold": 2,  # number of signatures requires
        "other_signatories": [bob.ss58_address],  # cannot be empty
        "maybe_timepoint": None,  # must be None for the first approval
        "call_hash": "0x" + extrinsic.extrinsic_hash.hex(),
        "max_weight": 215137000,
    },
)

call_extrinsic = substrate.create_signed_extrinsic(call, alice)
receipt = substrate.submit_extrinsic(call_extrinsic, wait_for_inclusion=True)

# Check the events
for event in receipt.triggered_events:
    print(f"* {event.value}")

# ----------- SIGNING WITH BOB -----------
# First get the timepoint (block_number, extrinsic_index) for the first approval above
timepoint = {
    "height": substrate.get_block_number(receipt.block_hash),
    "index": receipt.extrinsic_idx,
}

# Compose call, extrinsic should match the one above
call = substrate.compose_call(
    call_module="Multisig",
    call_function="as_multi",
    call_params={
        "threshold": 2,
        "other_signatories": [alice.ss58_address],
        "maybe_timepoint": timepoint,
        "call": {
            "call_module": "Balances",
            "call_function": "transfer",
            "call_args": {
                "dest": alice.ss58_address,
                "value": 123 * 10 ** 18,
            },
        },
        "store_call": False,
        "max_weight": 215137000,
    },
)

call_extrinsic = substrate.create_signed_extrinsic(call, bob)
receipt = substrate.submit_extrinsic(call_extrinsic, wait_for_inclusion=True)

# Check the events
for event in receipt.triggered_events:
    print(f"* {event.value}")
```


### Keypair creation and signing

```python
mnemonic = Keypair.generate_mnemonic()
keypair = Keypair.create_from_mnemonic(mnemonic)
signature = keypair.sign("Test123")
if keypair.verify("Test123", signature):
    print('Verified')
```

By default, a keypair is using SR25519 cryptography, alternatively ED25519 can be explictly specified:

```python
keypair = Keypair.create_from_mnemonic(mnemonic, crypto_type=KeypairType.ED25519)
```

### Creating keypairs with soft and hard key derivation paths

```python
mnemonic = Keypair.generate_mnemonic()
keypair = Keypair.create_from_uri(mnemonic + '//hard/soft')
```

By omitting the mnemonic the default development mnemonic is used: 

```python
keypair = Keypair.create_from_uri('//Alice')
```

### Getting estimate of network fees for extrinsic in advance

```python
keypair = Keypair(ss58_address="EaG2CRhJWPb7qmdcJvy3LiWdh26Jreu9Dx6R1rXxPmYXoDk")

call = reef.compose_call(
    call_module='Balances',
    call_function='transfer',
    call_params={
        'dest': 'EaG2CRhJWPb7qmdcJvy3LiWdh26Jreu9Dx6R1rXxPmYXoDk',
        'value': 1 * 10**18
    }
)
payment_info = reef.get_payment_info(call=call, keypair=keypair)
# {'class': 'normal', 'partialFee': 2499999066, 'weight': 216625000}
```

### Offline signing of extrinsics

This example generates a signature payload which can be signed on another (offline) machine and later on sent to the 
network with the generated signature.

- Generate signature payload on online machine:
```python
reef = ReefInterface(url="testnet")

call = reef.compose_call(
    call_module='Balances',
    call_function='transfer',
    call_params={
        'dest': '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY',
        'value': 1 * 10**18
    }
)

era = {'period': 64, 'current': 22719}
nonce = 0

signature_payload = reef.generate_signature_payload(call=call, era=era, nonce=nonce)
```

- Then on another (offline) machine generate the signature with given `signature_payload`:

```python
keypair = Keypair.create_from_mnemonic("nature exchange gasp toy result bacon coin broccoli rule oyster believe lyrics")
signature = keypair.sign(signature_payload)
```

- Finally on the online machine send the extrinsic with generated signature:

```python
keypair = Keypair(ss58_address="5EChUec3ZQhUvY1g52ZbfBVkqjUY9Kcr6mcEvQMbmd38shQL")

extrinsic = reef.create_signed_extrinsic(
    call=call,
    keypair=keypair,
    era=era,
    nonce=nonce,
    signature=signature
)

result = reef.submit_extrinsic(
    extrinsic=extrinsic
)

print(result.extrinsic_hash)
```

### Accessing runtime constants
All runtime constants are provided in the metadata (see `reef.get_metadata_constants()`),
to access these as a decoded `ScaleType` you can use the function `reef.get_constant()`:

```python
constant = reef.get_constant("Balances", "ExistentialDeposit")

print(constant.value) # 10000000000
```

### Batching calls
By using `Utility` pallet, we can submit multiple calls within a single call. In the below example we create 100 transfer calls of 10k REEF.

```python
from reefinterface import Keypair, ReefInterface

# Connect to node
try:
    network = "ws://127.0.0.1:9944"
    substrate = ReefInterface(url=network)
except ConnectionRefusedError:
    print("Reef node could not be reached.")
    exit()

alice = Keypair.create_from_uri("//Alice")
bob = Keypair.create_from_uri("//Bob")

# Transfer 1M REEF in 100 calls of 10k
call = substrate.compose_call(
    call_module="Utility",
    call_function="batch",
    call_params={
        "calls": [
            {
                "call_module": "Balances",
                "call_function": "transfer",
                "call_args": {"dest": bob.ss58_address, "value": 10000 * 10 ** 18},
            }
        ]
        * 100
    },
)

extrinsic = substrate.create_signed_extrinsic(
    call=call, keypair=alice, era={"period": 64}
)

receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)

# Check the events
for event in receipt.triggered_events:
    print(f"* {event.value}")
```

## Cleanup and context manager

At the end of the lifecycle of a `ReefInterface` instance, calling the `close()` method will do all the necessary 
cleanup, like closing the websocket connection.

When using the context manager this will be done automatically:

```python
with ReefInterface(url="testnet") as reef:
    events = reef.query("System", "Events")

# connection is now closed
```

## Contact and Support 

For questions, please reach out to us on our [matrix](http://matrix.org) chat group: [Reef Developer Chat](https://app.element.io/#/room/#reef:matrix.org).
