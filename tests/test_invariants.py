import pytest
import os
import sys

# 把 src 目录加进环境变量，让 pytest 找得到你的代码
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from simulator import V3PoolStateMachine

def test_zero_amount_swap():
    """
    红线测试 1：如果输入 0 个币的交易，底层的池子价格刻度和余额必须纹丝不动。
    """
    # 初始化池子
    initial_price = 2500
    initial_liquidity = 1000000000000000000
    pool = V3PoolStateMachine(initial_price, initial_liquidity)
    
    # 记录初始状态
    initial_sqrt_price = pool.sqrt_price
    initial_tick = pool.current_tick
    initial_token0_balance = pool.token0_balance
    initial_token1_balance = pool.token1_balance
    
    # 执行 0 个币的交易
    amount_out = pool.swap(0, 0, 3000)
    
    # 断言状态未改变
    assert pool.sqrt_price == initial_sqrt_price, "价格刻度发生了变化！"
    assert pool.current_tick == initial_tick, "Tick 发生了变化！"
    assert pool.token0_balance == initial_token0_balance, "Token0 余额发生了变化！"
    assert pool.token1_balance == initial_token1_balance, "Token1 余额发生了变化！"
    assert amount_out == 0, "输出数量不为 0！"


def test_balance_non_negative():
    """
    红线测试 2：池子里的 Token0 和 Token1 的余额永远不可能变成负数。
    """
    # 初始化池子
    initial_price = 2500
    initial_liquidity = 1000000000000000000
    pool = V3PoolStateMachine(initial_price, initial_liquidity)
    
    # 执行多次交易，确保余额不会变为负数
    for i in range(10):
        # 输入 token0，输出 token1
        amount_out = pool.swap(1000, 0, 3000)
        assert pool.token0_balance >= 0, "Token0 余额变为负数！"
        assert pool.token1_balance >= 0, "Token1 余额变为负数！"
        
        # 输入 token1，输出 token0
        amount_out = pool.swap(1000, 1, 2000)
        assert pool.token0_balance >= 0, "Token0 余额变为负数！"
        assert pool.token1_balance >= 0, "Token1 余额变为负数！"


def test_price_impact():
    """
    红线测试 3：验证价格影响的合理性，确保交易不会导致价格异常波动。
    """
    # 初始化池子
    initial_price = 2500
    initial_liquidity = 1000000000000000000
    pool = V3PoolStateMachine(initial_price, initial_liquidity)
    
    # 执行大额交易
    amount_in = 1000000
    amount_out = pool.swap(amount_in, 0, 3000)
    
    # 确保输出数量大于 0
    assert amount_out > 0, "输出数量为 0！"
    
    # 确保价格在合理范围内
    assert pool.current_tick > -10000, "Tick 过低！"
    assert pool.current_tick < 10000, "Tick 过高！"

