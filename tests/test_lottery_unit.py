# myCode
from operator import index
from brownie import Lottery, accounts, config, network, exceptions
from web3 import Web3
from scripts.deploy import deploy_lottery
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, fund_with_link, get_account, get_contract
import pytest


def test_get_entrance_fee(lottery_contract):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery_contract = deploy_lottery()
    # Act
    # 2,000 eth / usd
    # usdEntryFee is 50
    # 2000/1 == 50/x == 0.025
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery_contract.getEntranceFee()
    # Assert
    assert expected_entrance_fee == entrance_fee

def test_cant_enter_unless_starter(lottery_contract):
    # Arrange 
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery_contract = deploy_lottery()
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery_contract.enter({"from" : get_account(), "value" : lottery_contract.getEntranceFee()})

def test_can_start_and_enter_lottery(lottery_contract): 
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from" : account})
    # Act
    lottery.enter({"from" : account, "value" : lottery.getEntranceFee()})
    assert lottery.players(0) == account

def test_can_end_lottery(lottery_contract):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from" : account})
    lottery.enter({"from" : account, "value" : lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from" : account})
    assert lottery.lottery_state() == 2

def test_can_pick_winner_correctly(lottery_contract):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account()
    lottery_contract.startLottery({"from": account})
    lottery_contract.enter({"from" : account, "value" : lottery_contract.getEntranceFee()})
    lottery_contract.enter({"from" : account(index=1), "value" : lottery_contract.getEntranceFee()})
    lottery_contract.enter({"from" : account(index=2), "value" : lottery_contract.getEntranceFee()})
    fund_with_link(lottery_contract)
    transaction = lottery_contract.endLottery({"from" : account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(request_id, STATIC_RG, lottery_contract.address, 
    {"from" : account}
    )
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery_contract.balance()
    # 777 % 3 == 0
    assert lottery_contract.recentWinner() == account
    assert lottery_contract.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery