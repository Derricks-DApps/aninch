import json
from web3 import Web3
from web3 import EthereumTesterProvider
from solcx import compile_source, compile_standard, install_solc

install_solc("0.8.12")

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
last_block = web3.eth.get_block('latest')
p = web3.is_address("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")
balance = web3.eth.get_balance("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")
contract_address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

with open("HelloWorld.sol", "r") as file:
    contract = file.read()

compiled_smartcontract = compile_source(contract, output_values = ['abi', 'bin'])
contract_id, contract_interface = compiled_smartcontract.popitem()
abi = contract_interface["abi"]
bytecode = contract_interface["bin"]
hello_world = web3.eth.contract(abi = abi, bytecode = bytecode)
# calling the constructor deploys the contract
transaction = hello_world.constructor().transact()
receipt = web3.eth.wait_for_transaction_receipt(transaction)
hello_world_contract = web3.eth.contract(address = receipt.contractAddress, abi = abi)
hello_world_contract.functions.sayMessage().call()
# modify state of contract to update value, do transaction on the contract instance (maybe rename initial transaction() to  deploy_transaction
new_transaction_hash = hello_world_contract.functions.setMessage("Yesh!").transact()

# Better way of compiling solidity file directly
solidity_binary = compile_standard({
    "language": "Solidity",
    "sources": { "HelloWorld.sol": {
        "content": contract
    }},
    "settings": {
        "outputSelection": {
            "*": { "*":
                  ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        }
    }, solc_version = "0.8.12")

