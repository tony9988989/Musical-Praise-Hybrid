# 初始种群生成与变异操作模块 (by zcs)

## 一、模块结构

本次实现采用**解耦设计**，所有功能独立存放在 `zcs_*.py` 模块中，通过接口集成到主程序。

```
MusicalPhraseHybrid/
├── demo.py              # 主程序（由zcs修改，添加配置文件支持）
├── Mutations.py         # 变异操作入口（由zcs添加8种策略）
├── Settings.py          # 基础设置（组长维护，KEY_SCALE_MAP由zcs统一为#C格式）
├── Crossover.py         # 交叉操作（组长维护）
├── melodies.txt         # 【zcs配置】用户旋律配置文件
├── zcs_melody.py        # 【zcs模块】初始种群生成 + 调性约束
├── zcs_mutations.py     # 【zcs模块】变异策略实现（8种）
├── zcs_config.py        # 【zcs模块】配置文件读取 + 自定义旋律输入
└── zcs.md               # 【zcs文档】本说明文件
```

---

## 二、功能模块说明

### 2.1 `zcs_melody.py` - 初始种群生成（含调性约束）

提供 `generate_melody()` 函数，用于生成随机旋律，支持12个大调的调性约束。

**接口**：
```python
from zcs_melody import generate_melody, get_scale_pitches

# 生成C大调旋律（只使用C大调音阶内的音）
key, pitch, beat = generate_melody(key="C", use_scale=True)

# 获取G大调在F3~G5音域内的所有有效音高
valid_pitches = get_scale_pitches("G")
```

**参数**：
| 参数 | 值 | 说明 |
|------|-----|------|
| PITCH_MIN | 29 | F3（12音制，12*2+5） |
| PITCH_MAX | 55 | G5（12音制，12*4+7） |
| MELODY_LENGTH | 240 | 总时值（来自Settings.py） |
| VALID_BEATS | [6,12,18,24,36,48] | 可用时值 |
| DEFAULT_KEY | "C" | 默认调性 |

**调性约束**：
- 使用 `Settings.py` 中的 `KEY_SCALE_MAP` 定义12个大调音阶
- 生成旋律时只使用该调性的音阶内音高
- 支持的调性：C, #C, D, #D, E, F, #F, G, #G, A, #A, B

---

### 2.2 `zcs_mutations.py` - 变异策略（8种）

提供8种变异策略的**纯函数**实现，不依赖DEAP框架。

**接口**：
```python
from zcs_mutations import apply_mutation, MUTATION_STRATEGIES

# 随机应用一种变异
new_pitch, new_beat = apply_mutation(pitch, beat)

# 指定应用某种变异
from zcs_mutations import transpose
new_pitch, new_beat = transpose(pitch, beat, semitones=3)
```

**策略列表**：
| 函数名 | 音乐术语 | 说明 |
|--------|----------|------|
| `keep` | - | 保持不变（空操作） |
| `transpose` | 移调 | 整体上移/下移半音（默认±5随机） |
| `inversion` | 倒影 | 以首音为轴，音程上下翻转 |
| `retrograde` | 逆行 | 倒序播放（音高+时值都倒序） |
| `change_pitch` | 音高微调 | 随机改变一个音高（±1~3半音） |
| `change_rhythm` | 节奏微调 | 相邻音符转移时值（保持总时值） |
| `split_note` | 音符分裂 | 一个音符分裂成两个（时值平分） |
| `merge_notes` | 音符合并 | 合并相邻两个音符（时值相加） |

---

### 2.3 `zcs_config.py` - 配置文件读取与自定义旋律输入

提供从文件读取配置参数和用户自定义旋律的功能。

**接口**：
```python
from zcs_config import load_config_and_melodies, create_population_from_config

# 仅读取配置和旋律
config, melodies = load_config_and_melodies("melodies.txt")

# 直接创建初始种群（推荐）
config, population = create_population_from_config("melodies.txt", melody_creator)
```

**配置文件格式 (`melodies.txt`)**：
```text
# 配置参数（以@开头）
@key=C        # 调性（12个大调之一）
@seeds=20     # 初始种群总数
@random=10    # 随机生成的数量（剩余使用用户旋律填充）

# 用户自定义旋律（每行：音名 时值）
C4 12
D4 12
E4 24
...
---
# 多段旋律用 --- 分隔
G4 24
A4 24
...
```

**输入格式说明**：
| 项目 | 格式 | 示例 |
|------|------|------|
| 音名 | `<音名><八度>` | C4, #F5, G3 |
| 时值 | 整数 | 6=八分, 12=四分, 24=二分, 48=全音符 |
| 休止符 | Pause | Pause 12 |
| 旋律总时值 | 必须=240 | 两小节4/4拍 |

---

## 三、与主程序的集成方式

### 3.1 demo.py 中的集成

```python
# === 导入zcs模块 ===
from zcs_melody import generate_melody
from zcs_config import create_population_from_config

# === 配置模式选择 ===
USE_CONFIG_FILE = True
CONFIG_FILE_PATH = "melodies.txt"

# === 创建初始种群 ===
if USE_CONFIG_FILE:
    config, population = create_population_from_config(
        CONFIG_FILE_PATH, 
        Get_Melody_Creator
    )
else:
    population = toolbox.population(n=200)
```

### 3.2 Mutations.py 中的集成

```python
# 导入zcs模块提供的变异操作
from zcs_mutations import transpose, inversion, ...

def Transpose(individual):
    """将纯函数包装为DEAP兼容格式"""
    new_pitch, new_beat = transpose(individual.pitch, individual.beat)
    individual.pitch = new_pitch
    individual.beat = new_beat
    return individual
```

---

## 四、设计原则

### 4.1 解耦设计
- **zcs模块**：纯逻辑实现，不依赖DEAP或主程序结构
- **主程序接口**：`Mutations.py` 和 `demo.py` 负责包装和调用
- **好处**：组长修改主程序结构时，只需调整接口层

### 4.2 复用组长代码
| 复用项 | 来源 | 说明 |
|--------|------|------|
| `KEY_SCALE_MAP` | Settings.py | 12个大调音阶定义 |
| `MELODY_LENGTH` | Settings.py | 总时值=240 |
| `Notes` | Settings.py | 音名列表 |
| `TransPitches` | Settings.py | 音名→索引映射 |
| `Melody` 类 | Settings.py | 旋律数据结构 |

### 4.3 兼容性设计
- 所有zcs模块在无法导入Settings时，使用本地备份定义
- 支持独立测试，无需依赖主程序环境

---

## 五、音乐理论说明

### 移调 (Transposition)
将旋律整体上移或下移若干半音，保持音程关系不变。
```
原旋律：  C - E - G  (上行大三度 + 小三度)
上移2音： D - #F - A (上行大三度 + 小三度)
```

### 倒影 (Inversion)
以某个音为轴，将所有音程关系上下翻转。
```
原旋律：  C - E - G  (相对于C: +4, +7 半音)
倒影后：  C - #G - F (相对于C: -4, -7 半音)
```

### 逆行 (Retrograde)
将旋律按时间倒序播放。
```
原旋律： C - D - E - G
逆行后： G - E - D - C
```

### 调性约束 (Scale Constraint)
生成旋律时只使用指定调性的自然音阶：
```
C大调：C - D - E - F - G - A - B（无升降号）
G大调：G - A - B - C - D - E - #F（一个升号）
```

---

## 六、使用方法

### 快速开始
```bash
cd MusicalPhraseHybrid
python demo.py
```

### 自定义旋律
1. 编辑 `melodies.txt` 配置文件
2. 设置调性：`@key=G`
3. 添加自定义旋律（每行：音名 时值）
4. 运行程序

### 切换模式
在 `demo.py` 中设置：
```python
USE_CONFIG_FILE = True   # 从配置文件读取
USE_CONFIG_FILE = False  # 纯随机生成
```

---

## 七、版本适配说明

本模块已适配组长更新后的主程序：

| 项目 | 旧版本 | 新版本（已适配） |
|------|--------|-----------------|
| Settings.py Notes | 11音（#E代替E） | 12音（标准） |
| Melody类 | `(pitch, beat)` | `(key, pitch, beat)` |
| 音高索引总数 | 0-77 | 0-84 |
| F3~G5索引 | 26-50 | 29-55 |
| KEY_SCALE_MAP格式 | C#/D#... | #C/#D...（由zcs统一） |

---

## 八、文件清单

| 文件 | 作者 | 说明 |
|------|------|------|
| `zcs_melody.py` | zcs | 初始种群生成 + 12大调调性约束 |
| `zcs_mutations.py` | zcs | 8种变异策略纯函数实现 |
| `zcs_config.py` | zcs | 配置文件读取 + 自定义旋律输入 |
| `melodies.txt` | zcs | 示例配置文件 |
| `zcs.md` | zcs | 本说明文档 |
| `Mutations.py` | 组长+zcs | 添加8种策略包装函数 |
| `demo.py` | 组长+zcs | 添加配置文件支持 |
| `Settings.py` | 组长+zcs | KEY_SCALE_MAP格式统一为#C |
