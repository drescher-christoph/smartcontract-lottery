from brownie import network
import pytest
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, fund_with_link
from scripts.deploy import deploy_lottery
import time

def test_can_pick_winner(lottery_contract):
    # Arrange
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account()
    lottery_contract.startLottery({"from" : account})
    lottery_contract.enter({"from" : account, "value" : lottery_contract.getEntranceFee()})
    lottery_contract.enter({"from" : account, "value" : lottery_contract.getEntranceFee()})
    fund_with_link(lottery_contract)
    lottery_contract.endLottery({"from" : account})
    time.sleep(60)
    assert lottery_contract.recentWinner() == account
    assert lottery_contract.balance == 0