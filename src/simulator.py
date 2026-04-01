"""
🚨 核心原则 (Core Rule):
在这个文件里，严禁使用 float 或者 decimal.Decimal 来表示价格或流动性。
必须严格使用大整数 (BigInt - Python内置的 int) 和按位截断 (//) 来模拟 Solidity 物理法则。

请参考 04_Resources/Project1_V3_Math_CheatSheet.md 的公式来写你的代码。
"""

# V3 魔法常数 Q96
Q96 = 2**96

class V3PoolStateMachine:
    def __init__(self, initial_price, initial_liquidity, fee_tier=0.003):
        """
        初始化池子状态。
        
        Args:
            initial_price: 初始价格 (ETH/USDC)
            initial_liquidity: 初始流动性
            fee_tier: 手续费层级 (默认 0.3%)
        """
        # 存储手续费层级
        self.fee_tier = fee_tier
        
        # 存储流动性
        self.liquidity = initial_liquidity
        
        # 计算初始 sqrt_price (Q64.96 格式)
        self.sqrt_price = self.price_to_sqrt_price(initial_price)
        
        # 计算当前 tick
        self.current_tick = self.sqrt_price_to_tick(self.sqrt_price)
        
        # 存储 tick 字典
        self.ticks = {}
        
        # 存储 token 余额
        self.token0_balance = 0
        self.token1_balance = 0
    
    def price_to_sqrt_price(self, price):
        """
        将价格转换为 sqrt_price (Q64.96 格式)
        """
        # 使用整数运算实现 sqrt_price 计算
        # 这里使用二分查找法来计算平方根
        if price == 0:
            return 0
        
        # 将价格转换为整数
        price_int = int(price * 10**18)  # 假设价格精度为 18 位
        
        # 计算平方根
        sqrt_price = 0
        high = price_int
        low = 0
        
        for _ in range(100):  # 足够的迭代次数以确保精度
            mid = (high + low) // 2
            mid_squared = mid * mid
            
            if mid_squared == price_int:
                sqrt_price = mid
                break
            elif mid_squared < price_int:
                low = mid
                sqrt_price = mid
            else:
                high = mid
        
        # 转换为 Q64.96 格式
        return (sqrt_price * Q96) // (10**9)  # 调整精度
    
    def sqrt_price_to_tick(self, sqrt_price):
        """
        将 sqrt_price 转换为 tick
        """
        # 实现 tick 计算
        # tick = log2(sqrt_price^2) * 2^(tick_spacing)
        # 这里使用近似计算
        if sqrt_price == 0:
            return -2**24
        
        # 计算对数
        tick = 0
        temp = sqrt_price
        
        if temp > Q96:
            while temp > Q96 * 2:
                temp = temp // 2
                tick += 1
        else:
            while temp < Q96:
                temp = temp * 2
                tick -= 1
        
        return tick
    
    def swap(self, amount_in, token_in, limit_price):
        """
        执行 swap 操作
        
        Args:
            amount_in: 输入的代币数量
            token_in: 输入的代币类型 (0 表示 token0, 1 表示 token1)
            limit_price: 价格限制
            
        Returns:
            amount_out: 输出的代币数量
        """
        if amount_in <= 0:
            return 0
        
        # 计算手续费
        fee = int(amount_in * self.fee_tier)
        amount_in_after_fee = amount_in - fee
        
        # 计算输出数量
        if token_in == 0:  # 输入 token0，输出 token1
            # 计算价格变化
            new_sqrt_price = ((self.liquidity * Q96) + (amount_in_after_fee * self.sqrt_price)) // self.liquidity
            
            # 检查价格限制
            limit_sqrt_price = self.price_to_sqrt_price(limit_price)
            if new_sqrt_price > limit_sqrt_price:
                new_sqrt_price = limit_sqrt_price
                # 重新计算实际输入数量
                amount_in_after_fee = ((new_sqrt_price * self.liquidity) - (self.liquidity * Q96)) // self.sqrt_price
            
            # 计算输出数量
            amount_out = (self.liquidity * (self.sqrt_price - new_sqrt_price)) // (self.sqrt_price * new_sqrt_price // Q96)
            
            # 更新状态
            self.sqrt_price = new_sqrt_price
            self.current_tick = self.sqrt_price_to_tick(new_sqrt_price)
            self.token0_balance += amount_in
            self.token1_balance -= amount_out
        else:  # 输入 token1，输出 token0
            # 计算价格变化
            new_sqrt_price = (self.liquidity * Q96) // ((self.liquidity * Q96) // self.sqrt_price + amount_in_after_fee)
            
            # 检查价格限制
            limit_sqrt_price = self.price_to_sqrt_price(limit_price)
            if new_sqrt_price < limit_sqrt_price:
                new_sqrt_price = limit_sqrt_price
                # 重新计算实际输入数量
                amount_in_after_fee = (self.liquidity * Q96) // self.sqrt_price - (self.liquidity * Q96) // new_sqrt_price
            
            # 计算输出数量
            amount_out = (self.liquidity * (new_sqrt_price - self.sqrt_price)) // (self.sqrt_price * new_sqrt_price // Q96)
            
            # 更新状态
            self.sqrt_price = new_sqrt_price
            self.current_tick = self.sqrt_price_to_tick(new_sqrt_price)
            self.token1_balance += amount_in
            self.token0_balance -= amount_out
        
        return amount_out

