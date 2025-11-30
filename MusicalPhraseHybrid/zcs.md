# 初始种群生成与变异操作模块 (by zcs)

## 一、模块结构

本次实现采用**解耦设计**，所有功能独立存放在单独的模块中，通过接口集成到主程序。

```
MusicalPhraseHybrid/
├── demo.py              # 主程序（调用接口）
├── Mutations.py         # 变异操作入口（调用接口）
├── Settings.py          # 基础设置（组长维护）
├── Crossover.py         # 交叉操作（组长维护）
├── zcs_melody.py        # 【zcs模块】初始种群生成
├── zcs_mutations.py     # 【zcs模块】变异策略实现
└── zcs.md               # 【zcs文档】本说明文件
```

---

## 二、模块说明

### 2.1 `zcs_melody.py` - 初始种群生成

提供 `generate_melody()` 函数，用于生成随机旋律。

**接口**：
```python
from zcs_melody import generate_melody

key, pitch, beat = generate_melody()  # 返回 (调性, 音高列表, 时值列表)
```

**参数**：
| 参数 | 值 | 说明 |
|------|-----|------|
| PITCH_MIN | 29 | F3（12音制） |
| PITCH_MAX | 55 | G5（12音制） |
| MELODY_LENGTH | 240 | 总时值 |
| VALID_BEATS | [6,12,18,24,36,48] | 可用时值 |

### 2.2 `zcs_mutations.py` - 变异策略

提供8种变异策略的纯函数实现。

**接口**：
```python
from zcs_mutations import apply_mutation, MUTATION_STRATEGIES

new_pitch, new_beat = apply_mutation(pitch, beat)  # 随机应用一种变异
```

**策略列表**：
| 函数名 | 音乐术语 | 说明 |
|--------|----------|------|
| `keep` | - | 保持不变 |
| `transpose` | 移调 | 整体上移/下移半音 |
| `inversion` | 倒影 | 音程上下翻转 |
| `retrograde` | 逆行 | 倒序播放 |
| `change_pitch` | - | 随机改变一个音高 |
| `change_rhythm` | - | 相邻音符转移时值 |
| `split_note` | - | 音符分裂成两个 |
| `merge_notes` | - | 合并相邻音符 |

---

## 三、与主程序的集成

### 3.1 demo.py 中的调用

```python
# 导入zcs模块提供的初始种群生成功能 (by zcs)
from zcs_melody import generate_melody

def Get_Melody():
    key, pitch, beat = generate_melody()
    return creator.Melody(key, pitch, beat)
```

### 3.2 Mutations.py 中的调用

```python
# 导入zcs模块提供的变异操作 (by zcs)
from zcs_mutations import transpose, inversion, retrograde, ...

def Transpose(individual):
    new_pitch, new_beat = transpose(individual.pitch, individual.beat)
    individual.pitch = new_pitch
    individual.beat = new_beat
    return individual
```

---

## 四、音乐理论说明

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
倒影后：  C - Ab - F (相对于C: -4, -7 半音)
```

### 逆行 (Retrograde)
将旋律按时间倒序播放。
```
原旋律： C - D - E - G
逆行后： G - E - D - C
```

---

## 五、版本适配说明

本模块已适配组长更新后的主程序：

| 项目 | 旧版本 | 新版本（已适配） |
|------|--------|-----------------|
| Settings.py Notes | 11音（#E代替E） | 12音（标准） |
| Melody类 | `(pitch, beat)` | `(key, pitch, beat)` |
| 音高范围 | 0-77 | 0-84 |
| F3~G5索引 | 26-50 | 29-55 |

---

## 六、使用方法

```bash
cd MusicalPhraseHybrid
python demo.py
```

程序将运行50代遗传算法，输出最优旋律。
