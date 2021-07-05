# Python Reef Interface

Python Reef Interface Library

## Description
This library specializes in interfacing with the Reef node, providing additional convenience methods to deal with
SCALE encoding/decoding (the default output and input format of the Substrate JSONRPC), metadata parsing, type registry
management and versioning of types.

## Documentation
Python Reef Interface is the fork of [Python Substrate Interface](https://polkascan.github.io/py-substrate-interface/). Most of the documentation on the link should apply here as well.

## Installation
```bash
pip install reef-interface
```

## Initialization

The following examples show how to initialize:

```python
reef = ReefInterface(url="testnet")
```

`url` can be `testnet`, `mainnet` or an `ws://<url>` URL for custom node.
