# 初始种群生成与变异操作模块 (by zcs)

## 一、模块结构

```
MusicalPhraseHybrid/
├── demo.py              # 主程序（由zcs修改，添加配置文件支持）
├── Mutations.py         # 变异操作（由zcs实现8种策略）
├── Settings.py          # 基础设置（组长维护，KEY_SCALE_MAP由zcs统一为#C格式）
├── Crossover.py         # 交叉操作（组长维护）
├── melodies.txt         # 【zcs配置】用户旋律配置文件
├── zcs_melody.py        # 【zcs模块】初始种群生成 + 调性约束
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

### 2.2 `Mutations.py` - 变异策略（8种）

直接操作 `creator.Melody` 对象，保留 `key` 属性不变。
**所有涉及音高变化的操作都保证在调性内。**

**辅助函数**：
- `get_scale_pitches(key)` - 获取调内所有有效音高
- `normalize_pitch_to_key(pitch, key)` - 将音高归一化到调内

**策略列表**：
| 函数名 | 音乐术语 | 说明 | 调性约束 |
|--------|----------|------|----------|
| `Keep` | - | 保持不变 | - |
| `NormalizeToKey` | 调性归一化 | 调外音吸附到调内音 | ✅ |
| `Inversion` | 倒影 | 音程翻转后归一化 | ✅ |
| `Retrograde` | 逆行 | 倒序播放 | 不涉及 |
| `ChangePitch` | 音高微调 | 调内移动±1~2音级 | ✅ |
| `ChangeRhythm` | 节奏微调 | 转移时值 | 不涉及 |
| `SplitNote` | 音符分裂 | 新音符在调内选择 | ✅ |
| `MergeNotes` | 音符合并 | 删除音符 | 不涉及 |

**调内变异示例（C大调）**：
```
ChangePitch: C4 → D4（上移1音级）或 E4（上移2音级）
SplitNote:   G4分裂 → G4 + A4（调内相邻音）
Inversion:   倒影后 #F → 归一化为 F 或 G
```

**入口函数**：
```python
def melody_mutation(individual: creator.Melody, indpb=0.1):
    # 随机选择一种策略，原地修改individual
    # 返回 (individual,) 符合DEAP要求
```

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
        Get_Melody_Creator  # 返回 creator.Melody 对象
    )
```

### 3.2 Mutations.py 变异机制

```python
def Transpose(individual: creator.Melody):
    """原地修改individual，保留key属性"""
    # ... 修改 individual.pitch ...
    return individual  # 返回同一个对象
```

---

## 四、设计原则

### 4.1 复用组长代码
| 复用项 | 来源 | 说明 |
|--------|------|------|
| `KEY_SCALE_MAP` | Settings.py | 12个大调音阶定义 |
| `MELODY_LENGTH` | Settings.py | 总时值=240 |
| `Notes` | Settings.py | 音名列表 |
| `TransPitches` | Settings.py | 音名→索引映射 |
| `Melody` 类 | Settings.py | 旋律数据结构 |
| `creator.Melody` | DEAP | 带fitness的Melody |

### 4.2 变异保留key属性
所有变异操作都是**原地修改** `individual.pitch` 和 `individual.beat`，不重新创建对象，因此 `key` 属性自动保留。

---

## 五、音乐理论说明

### 调性归一化 (NormalizeToKey)
将调外音"吸附"到最近的调内音，保证旋律纯净。
```
C大调音阶：C - D - E - F - G - A - B
调外音 #C → 吸附到 C 或 D（取最近）
调外音 #F → 吸附到 F 或 G（取最近）
```

### 倒影 (Inversion)
```
原旋律：  C - E - G  (相对于C: +4, +7 半音)
倒影后：  C - #G - F (相对于C: -4, -7 半音)
```

### 逆行 (Retrograde)
```
原旋律： C - D - E - G
逆行后： G - E - D - C
```

### 调性约束 (Scale Constraint)
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
1. 编辑 `melodies.txt`
2. 设置调性：`@key=G`
3. 添加自定义旋律
4. 运行程序

---

## 七、文件清单

| 文件 | 作者 | 说明 |
|------|------|------|
| `zcs_melody.py` | zcs | 初始种群生成 + 12大调调性约束 |
| `zcs_config.py` | zcs | 配置文件读取 + 自定义旋律输入 |
| `melodies.txt` | zcs | 示例配置文件 |
| `zcs.md` | zcs | 本说明文档 |
| `Mutations.py` | zcs | 8种变异策略实现 |
| `demo.py` | 组长+zcs | 添加配置文件支持 |
| `Settings.py` | 组长+zcs | KEY_SCALE_MAP格式统一为#C |
