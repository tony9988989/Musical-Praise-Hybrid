# ZCS 模块说明

> **状态**：✅ 已完成并集成到 `demo.py`

**详细文档请查看 → [zcs/README.md](./zcs/README.md)**

---

## 快速导航

| 文件 | 说明 |
|------|------|
| 📁 `zcs/` | 模块文件夹 |
| 📄 `zcs/melody.py` | 核心代码（GetMelody + 8种变异策略） |
| 🧪 `zcs/test_melody.py` | 测试脚本（6个测试用例，全部通过） |
| 📖 `zcs/README.md` | 完整说明文档 |

---

## 主要函数

| 函数名 | 说明 |
|--------|------|
| `Get_Melody()` | 生成初始旋律个体（音域 F3~G5） |
| `melody_mutation()` | 主变异函数（含移调、倒影、逆行等 8 种策略） |

---

## 快速使用

### 运行测试
```bash
cd MusicalPhraseHybrid/zcs
python test_melody.py
```

### 运行完整程序
```bash
cd MusicalPhraseHybrid
python demo.py
```

### 在代码中使用
```python
from zcs import Get_Melody, melody_mutation
```

---

## 实现的变异操作

| 变异类型 | 函数名 | 题目要求 |
|----------|--------|----------|
| 移调 | `mut_transpose()` | ⭐ 必须 |
| 倒影 | `mut_inversion()` | ⭐ 必须 |
| 逆行 | `mut_retrograde()` | ⭐ 必须 |
| 音高微调 | `mut_change_pitch()` | 额外 |
| 节奏调整 | `mut_change_rhythm()` | 额外 |
| 音符分裂 | `mut_split_note()` | 额外 |
| 音符合并 | `mut_merge_notes()` | 额外 |

---

**作者**：zcs
