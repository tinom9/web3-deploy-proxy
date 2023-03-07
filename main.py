import json

from web3 import Web3
from web3.contract import ABI
from web3.types import ChecksumAddress, HexStr


def _get_contract_artifact(contract: str) -> dict:
    with open(f"contracts/{contract}.json") as f:
        return json.load(f)


PROXY_ADMIN = _get_contract_artifact("ProxyAdmin")
TRANSPARENT_UPGRADEABLE_PROXY = _get_contract_artifact("TransparentUpgradeableProxy")


def deploy_proxy(w3: Web3, abi: ABI, bytecode: HexStr) -> ChecksumAddress:
    # Deploy contract.
    print("Deploying implementation contract")
    implementation_contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    implementation_ = implementation_contract.constructor().transact()
    implementation__receipt = w3.eth.wait_for_transaction_receipt(implementation_)
    implementation_address = implementation__receipt.contractAddress  # type: ignore[attr-defined]
    print(f"Implementation contract deployed to: {implementation_address}")
    # Deploy ProxyAdmin.
    print("Deploying ProxyAdmin")
    admin_contract = w3.eth.contract(
        abi=PROXY_ADMIN["abi"], bytecode=PROXY_ADMIN["bytecode"]
    )
    admin_tx = admin_contract.constructor().transact()
    admin_tx_receipt = w3.eth.wait_for_transaction_receipt(admin_tx)
    admin_address = admin_tx_receipt.contractAddress  # type: ignore[attr-defined]
    print(f"ProxyAdmin deployed to: {admin_address}")
    # Deploy TransparentUpgradeableProxy.
    print("Deploying TransparentUpgradeableProxy")
    proxy_contract = w3.eth.contract(
        abi=TRANSPARENT_UPGRADEABLE_PROXY["abi"],
        bytecode=TRANSPARENT_UPGRADEABLE_PROXY["bytecode"],
    )
    proxy_tx = proxy_contract.constructor(
        implementation_address, admin_address, ""
    ).transact()
    proxy_tx_receipt = w3.eth.wait_for_transaction_receipt(proxy_tx)
    proxy_address = proxy_tx_receipt.contractAddress  # type: ignore[attr-defined]
    print(f"TransparentUpgradeableProxy deployed to: {proxy_address}")
    return proxy_address
