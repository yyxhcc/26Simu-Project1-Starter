# 🪐 Project 1: Uniswap V3 State Machine (Starter Template)

> 🎈 **重要声明 (IMPORTANT)**: 
> 你当前所处的是**“纯净实战沙盒 (Starter Sandbox)”**。这里没有任何理论大纲和作业规格书。
> 本课程的所有红头文件、教学指导、工具链规范以及 Project 1 的打分标准（Rubric），均由 **教官的全球唯一主库 (SSOT)** 发布与维护。
> 👉 **[点击此处阅读课程原点：26Simu-Management-Modeling](https://github.com/booblu/26Simu-Management-Modeling)**
> 👉 **[点击此处查询 P1 任务规格书与计分板](https://github.com/booblu/26Simu-Management-Modeling/blob/main/03_Assignments/Project1_V3_State_Machine.md)**
> 👉 **[点击此处打开避坑保命的 Math Cheat Sheet](https://github.com/booblu/26Simu-Management-Modeling/blob/main/04_Resources/Project1_V3_Math_CheatSheet.md)**

## 🎯 你的脚手架任务 (Your Sandbox Mission)
1. 把你在主库里学到的底层物理知识（Q64.96 定点数算法）移植进 `src/simulator.py` 里的那个空骨架中。
2. 疯狂地在 `tests/test_invariants.py` 中写能够把系统搞死（触发底板击穿）的独立红线测试断言。
3. 按照 `spec.yaml` 填写你做实验的初始环境与假设条件。

## 🚀 启动指北 (How to Run)

**1. 布置机房环境 (Install Environment)**
```bash
python -m pip install -r requirements.txt
```

**2. 呼叫日常断言法官 (Run CI Tests - 也是 GitHub 的判官流程)**
在推送到 Github 寻求跑分之前，请务必在你的电脑本地先拿满绿标：
```bash
pytest tests/ -v
```

**3. 启动全流水线与生成决策数据表 (Run Experiments)**
```bash
python experiments/run_all.py
```

## 📝 决策洞察 Memo (CEO 的信)

作为 CTO 和 CEO，我通过实现和测试 V3 状态机，得出以下关键发现：

### 1. 核心技术实现
- **Q64.96 定点数算法**：使用大整数和按位截断来模拟 Solidity 物理法则，确保价格计算的精确性。
- **Swap 函数设计**：实现了基于流动性和价格变化的交易逻辑，包括手续费计算、价格限制检查和状态更新。
- **Tick 计算**：通过 sqrt_price 计算当前 tick，为后续的区间穿越和流动性管理奠定基础。

### 2. 红线测试结果
- **零交易测试**：输入 0 个币的交易不会改变池子状态，确保系统的稳定性。
- **余额非负测试**：无论执行多少次交易，Token0 和 Token1 的余额永远不会变为负数，保证资金安全。
- **价格影响测试**：大额交易不会导致价格异常波动，确保市场的稳定性。

### 3. 资金死亡滑点阈值分析
在极度失衡情况下，V3 单池的资金死亡滑点主要取决于以下因素：
- **流动性深度**：流动性越大，滑点越小；流动性越小，滑点越大。
- **交易规模**：交易规模越大，滑点越大；交易规模越小，滑点越小。
- **价格区间**：当价格接近区间边界时，流动性可能会急剧减少，导致滑点突然增大。

### 4. 改进建议
- **动态流动性管理**：根据市场情况自动调整流动性分布，减少滑点。
- **价格限制优化**：设置更合理的价格限制，平衡交易执行和滑点控制。
- **风险监控**：建立实时风险监控系统，及时发现和处理异常交易。

通过以上实现和分析，我们可以更全面地理解 V3 单池的运行机制，为后续的优化和扩展提供有力支持。
