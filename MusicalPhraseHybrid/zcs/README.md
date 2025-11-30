# ZCS 旋律生成模块说明文档

## 作者信息
- **模块名称**：`zcs/`
- **作者**：zcs
- **功能**：实现遗传算法中的 **初始种群生成 (GetMelody)** 和 **变异操作 (Mutations)**
- **状态**：✅ 已完成并集成到 `demo.py`

---

## 一、文件结构

```
MusicalPhraseHybrid/
├── Settings.py          # 基础设置（Melody类、音符定义等）
├── Crossover.py         # 杂交操作
├── Mutations.py         # 原变异操作（已被 zcs 模块替代）
├── demo.py              # 主程序（已集成 zcs 模块）✅
│
└── zcs/                 # 🆕 本模块
    ├── __init__.py      # 包初始化，导出主要函数
    ├── melody.py        # 核心实现：Get_Melody + 8种变异策略
    ├── test_melody.py   # 完整测试脚本（6个测试用例）
    └── README.md        # 本说明文档
```

---

## 二、快速开始

### 2.1 运行测试

```bash
cd MusicalPhraseHybrid/zcs
python test_melody.py
```

预期输出：
```
🎉 所有测试通过！模块可以安全使用。
```

### 2.2 运行完整程序

```bash
cd MusicalPhraseHybrid
python demo.py
```

程序将运行 50 代遗传算法，输出最优旋律。

### 2.3 在代码中使用

```python
# 导入主要函数
from zcs import Get_Melody, melody_mutation

# 生成随机旋律
melody = Get_Melody()
print(melody)  # 输出旋律信息

# 对旋律进行变异
mutated = melody_mutation(melody, indpb=0.2)

# 导入单独的变异函数
from zcs.melody import mut_transpose, mut_inversion, mut_retrograde
```

---

## 三、实现的功能

### 3.1 初始种群生成 (GetMelody)

| 函数名 | 说明 |
|--------|------|
| `Get_Melody()` | 生成符合 DEAP 框架的随机旋律个体 |
| `generate_random_melody()` | 底层函数，返回 `(pitch, beat)` 列表 |

**生成规则：**
| 参数 | 值 | 说明 |
|------|-----|------|
| 音域范围 | F3 ~ G5 | 索引 26 ~ 50，共 25 个音 |
| 最小时值 | 6 | 八分音符 |
| 可用时值 | 6, 12, 18, 24, 36, 48 | 八分、四分、附点四分、二分、附点二分、全音符 |
| 总时值 | 240 | 与框架兼容（四分音符 = 12） |

### 3.2 变异操作 (Mutations)

#### 题目要求的三种变换（⭐ 必须实现）

| 函数名 | 音乐术语 | 说明 |
|--------|----------|------|
| `mut_transpose(individual, semitones)` | 移调 | 所有音符整体上移/下移若干半音 |
| `mut_inversion(individual)` | 倒影 | 以第一个音为轴，音程关系上下翻转 |
| `mut_retrograde(individual)` | 逆行 | 将旋律倒序播放（音高和时值都倒序） |

#### 额外实现的变异策略

| 函数名 | 说明 |
|--------|------|
| `mut_keep(individual)` | 保持不变（空操作） |
| `mut_change_pitch(individual)` | 随机改变一个音符的音高（±1~3半音） |
| `mut_change_rhythm(individual)` | 相邻音符间转移时值 |
| `mut_split_note(individual)` | 将一个音符分裂成两个 |
| `mut_merge_notes(individual)` | 将相邻两个音符合并 |

#### 主变异函数

```python
melody_mutation(individual, indpb=0.1)
```
- 随机选择上述 8 种策略之一并应用
- 返回格式：`(individual,)`（符合 DEAP 要求）
- 保证变异后旋律仍然有效（总时值 = 240）

---

## 四、对 demo.py 的修改

### ✅ 已完成的修改（2 处）

#### 修改 1：替换 Get_Melody 函数

```diff
 #-------Create Gene------
-def Get_Melody():
-    #Todo
-    pitch=[77]
-    beat=[240]
-    return creator.Melody(pitch, beat)
+from zcs import Get_Melody  # 使用 zcs 模块的初始种群生成
 toolbox.register("individual",Get_Melody)
```

#### 修改 2：替换 melody_mutation 导入

```diff
 #-----Crossover and Mutation_____
 from Crossover import GetChild
-from Mutations import melody_mutation
+from zcs import melody_mutation  # 使用 zcs 模块的变异操作
```

---

## 五、音乐理论说明

### 5.1 移调 (Transposition)
将旋律整体上移或下移若干半音，保持音程关系不变。

```
原旋律：  C  -  E  -  G   (上行大三度 + 小三度)
上移2音： D  - #F  -  A   (上行大三度 + 小三度) ✓ 音程关系保持
```

### 5.2 倒影 (Inversion)
以某个音为轴，将所有音程关系上下翻转。

```
原旋律：  C  -  E  -  G   (上行大三度 + 小三度)
         ↑     ↑     ↑
轴心：    C    +4    +7   (相对于C的半音数)
         ↓     ↓     ↓
倒影：    C  - bA  -  F   (下行大三度 + 小三度)
              -4    -7   (镜像翻转)
```

### 5.3 逆行 (Retrograde)
将旋律按时间倒序播放。

```
原旋律： C(♩) - D(♪) - E(♩) - G(𝅗𝅥)
逆行后： G(𝅗𝅥) - E(♩) - D(♪) - C(♩)
```

---

## 六、技术细节

### 6.1 与 DEAP 框架的兼容性

本模块完全兼容 DEAP 遗传算法框架：

- `Get_Melody()` 返回 `creator.Melody` 对象
- `melody_mutation()` 返回 `(individual,)` 元组
- 支持 `toolbox.register()` 直接注册

### 6.2 音高索引对照表

```
索引 26 = F3  (起始音)
索引 27 = #F3
索引 28 = G3
...
索引 38 = C4  (中央C)
...
索引 50 = G5  (结束音)
```

### 6.3 时值单位对照表

| 音符类型 | 时值单位 | 说明 |
|----------|----------|------|
| 八分音符 | 6 | 最小单位 |
| 四分音符 | 12 | 基准单位 |
| 附点四分 | 18 | 四分 + 八分 |
| 二分音符 | 24 | 两个四分 |
| 附点二分 | 36 | 二分 + 四分 |
| 全音符 | 48 | 四个四分 |

---

## 七、测试覆盖

| 测试项 | 说明 | 状态 |
|--------|------|------|
| `test_get_melody()` | 验证随机旋律生成的正确性 | ✅ |
| `test_mutation_transpose()` | 验证移调变异 | ✅ |
| `test_mutation_inversion()` | 验证倒影变异 | ✅ |
| `test_mutation_retrograde()` | 验证逆行变异 | ✅ |
| `test_mutation_split_merge()` | 验证音符分裂/合并 | ✅ |
| `test_melody_mutation()` | 验证主变异函数 | ✅ |

---

## 八、后续工作

| 模块 | 状态 | 负责人 | 说明 |
|------|------|--------|------|
| GetMelody | ✅ 已完成 | zcs | 初始种群生成 |
| Mutations | ✅ 已完成 | zcs | 8种变异策略 |
| Crossover | ⏳ 待完善 | 其他组员 | 杂交操作 |
| evaluate_melody | ⏳ 待实现 | 其他组员 | 适应度函数（核心） |

---

## 九、联系方式

如有问题，请联系 **zcs**。
