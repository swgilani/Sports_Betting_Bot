from Sports_Betting_Bot import User
import pytest

def test_User_with_no_values():
    with pytest.raises(Exception) as e_info:
        user = User.User() #Successfully raises exception when no arguments provided.

def test_User_with_incorrect_arguments():
    with pytest.raises(Exception) as e_info:
        user = User.User(1,100,12) #Successfully raises exception when additional arguments provided

def test_UserBalance():
    user = User.User(1,100)
    assert user.getBalance() == 100

def test_UserId():
    user = User.User(1,100)
    assert user.getId() == 1

def test_UserDeposit():
    user = User.User(1,100)
    user.deposit(100)
    assert user.getBalance() == 200

def test_UserWithdraw():
    user = User.User(1,200)
    user.withdraw(100)
    assert user.getBalance() == 100
