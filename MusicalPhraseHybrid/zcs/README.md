# ZCS 旋律生成模块说明文档

## 作者信息
- 模块名称：`zcs/`
- 功能：实现遗传算法中的 **初始种群生成 (GetMelody)** 和 **变异操作 (Mutations)**

---

## 一、文件结构

```
MusicalPhraseHybrid/
├── Settings.py          # 原有代码（不修改）
├── Crossover.py         # 原有代码（不修改）
├── Mutations.py         # 原有代码（不修改）
├── demo.py              # 原有代码（不修改）
│
└── zcs/                 # 🆕 我们的工作成果
    ├── __init__.py      # 包初始化文件
    ├── melody.py        # 核心模块：GetMelody + Mutations
    ├── test_melody.py   # 完整测试脚本
    └── README.md        # 本说明文档
```

---

## 二、使用方法

### 2.1 运行测试（验证模块正确性）

```bash
cd MusicalPhraseHybrid/zcs
python test_melody.py
```

预期输出：
```
🎉 所有测试通过！模块可以安全使用。
```

### 2.2 作为模块导入

```python
# 方法 1：导入整个包
from zcs import Get_Melody, melody_mutation

# 方法 2：导入具体函数
from zcs.melody import mut_transpose, mut_inversion, mut_retrograde
```

---

## 三、实现的功能

### 3.1 初始种群生成 (GetMelody)

| 函数名 | 说明 |
|--------|------|
| `Get_Melody()` | 生成符合 DEAP 框架的随机旋律个体 |
| `generate_random_melody()` | 底层函数，返回 (pitch, beat) 列表 |

**特性：**
- 音域：F3 ~ G5（题目要求）
- 时值：最小为八分音符（6 单位）
- 总时值：240（与原框架兼容）

### 3.2 变异操作 (Mutations)

| 函数名 | 说明 | 题目要求 |
|--------|------|----------|
| `mut_transpose()` | 移调：整体上移/下移半音 | ⭐ 必须 |
| `mut_inversion()` | 倒影：以第一音为轴翻转 | ⭐ 必须 |
| `mut_retrograde()` | 逆行：倒序播放 | ⭐ 必须 |
| `mut_change_pitch()` | 微调单个音高 | 额外 |
| `mut_change_rhythm()` | 相邻音符时值转移 | 额外 |
| `mut_split_note()` | 分裂一个音符 | 额外 |
| `mut_merge_notes()` | 合并相邻音符 | 额外 |

| 主函数 | 说明 |
|--------|------|
| `melody_mutation(individual, indpb)` | 随机选择一种变异策略并应用 |

---

## 四、需要对原程序的修改

### ⚠️ 重要：以下修改需要经组长同意后实施

原 `demo.py` 中需要修改 **2 处**：

#### 修改 1：替换 Get_Melody 函数

**原代码（demo.py 第 12-16 行）：**
```python
def Get_Melody():
    #Todo
    pitch=[77]
    beat=[240]
    return creator.Melody(pitch, beat)
```

**修改为：**
```python
from zcs import Get_Melody

def Get_Melody():
    return Get_Melody()
```

或者直接：
```python
from zcs import Get_Melody
# 然后在 toolbox.register 时直接使用
```

#### 修改 2：替换 melody_mutation 导入

**原代码（demo.py 第 27 行）：**
```python
from Mutations import melody_mutation
```

**修改为：**
```python
from zcs import melody_mutation
```

---

## 五、替代方案（不修改原文件）

如果组长不同意修改原文件，可以创建一个新的主程序文件：

```python
# main_zcs.py - 新建此文件
import random
import numpy as np
from deap import base, creator, tools, algorithms
from Settings import Melody

# DEAP 初始化
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Melody", Melody, fitness=creator.FitnessMax)
toolbox = base.Toolbox()

# 使用 zcs 模块的函数
from zcs import Get_Melody, melody_mutation

toolbox.register("individual", Get_Melody)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# 适应度函数（暂时使用原来的）
def evaluate_melody(melody):
    score = 0
    return (score,)

# 使用原有的 Crossover
from Crossover import GetChild

toolbox.register("evaluate", evaluate_melody)
toolbox.register("mate", GetChild)
toolbox.register("mutate", melody_mutation, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)

# 运行遗传算法
population = toolbox.population(n=200)
hof = tools.HallOfFame(1)
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("max", np.max)

algorithms.eaSimple(population, toolbox, cxpb=0.7, mutpb=0.2, ngen=50,
                    stats=stats, halloffame=hof, verbose=True)

best_melody = hof[0]
print("\n--- Best Melody ---")
print(best_melody)
```

---

## 六、音乐理论说明

### 6.1 移调 (Transposition)
将旋律整体上移或下移若干半音，保持音程关系不变。
- 例：C-E-G 上移2个半音 → D-#F-A

### 6.2 倒影 (Inversion)
以某个音为轴，将所有音程关系上下翻转。
- 例：C-E-G（上行大三度+小三度）→ C-bA-F（下行大三度+小三度）

### 6.3 逆行 (Retrograde)
将旋律按时间倒序播放。
- 例：C-D-E-G → G-E-D-C

---

## 七、后续工作

| 模块 | 状态 | 负责人 |
|------|------|--------|
| GetMelody | ✅ 已完成 | zcs |
| Mutations | ✅ 已完成 | zcs |
| Crossover | ⏳ 待完成 | 其他组员 |
| evaluate_melody | ⏳ 待完成 | 其他组员 |

---

## 八、联系方式

如有问题，请联系 zcs。
