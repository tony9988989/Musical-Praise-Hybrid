# melody.py
# 作者：zcs
# 功能：实现 GetMelody（初始种群生成）和 Mutations（变异操作）
# 本文件不修改原有代码，通过导入方式接入现有程序

import random
import sys
import os

# 添加父目录到路径，以便导入 Settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Settings import Melody, valid_notes, TransPitches, MELODY_LENGTH
from deap import creator

# ============================================================
# 第一部分：音域定义（题目要求 F3 ~ G5）
# ============================================================

# 题目给定的乐音体系 S = {F3, #F3, ..., B3, C4, #C4, ..., B4, C5, #C5, ..., #F5, G5}
# 需要找到这些音在 valid_notes 中的索引

def get_valid_pitch_range():
    """
    获取题目要求的音域范围 F3 ~ G5 在 valid_notes 中的索引
    返回: (min_pitch, max_pitch) 索引范围
    """
    # valid_notes 的结构: C1, #C1, D1, #E1, F1, #F1, G1, #G1, A1, #A1, B1, C2, ...
    # 每个八度有 11 个音（注意原代码 Notes 列表有 11 个元素）
    # F3 对应的索引
    
    # 查找 F3 的索引
    f3_idx = None
    g5_idx = None
    
    for i, note in enumerate(valid_notes):
        if note == "F3":
            f3_idx = i
        if note == "G5":
            g5_idx = i
    
    # 如果找不到精确匹配，手动计算
    # 每个八度 11 个音，从 C 开始
    # 八度 n 的起始索引 = (n-1) * 11
    # C=0, #C=1, D=2, #E=3, F=4, #F=5, G=6, #G=7, A=8, #A=9, B=10
    
    if f3_idx is None:
        # F3: 八度3，F是第4个音（0-indexed: 4）
        f3_idx = (3 - 1) * 11 + 4  # = 2*11 + 4 = 26
    
    if g5_idx is None:
        # G5: 八度5，G是第6个音（0-indexed: 6）
        g5_idx = (5 - 1) * 11 + 6  # = 4*11 + 6 = 50
    
    return f3_idx, g5_idx

# 获取有效音高范围
PITCH_MIN, PITCH_MAX = get_valid_pitch_range()

# ============================================================
# 第二部分：时值定义
# ============================================================

# MELODY_LENGTH = 240，四分音符 = 12 单位
# 最短时值为八分音符 = 6 单位
# 常用时值：
#   八分音符 = 6
#   四分音符 = 12
#   附点四分 = 18
#   二分音符 = 24
#   附点二分 = 36
#   全音符 = 48

BEAT_UNIT = 6  # 八分音符，最小单位
VALID_BEATS = [6, 12, 18, 24, 36, 48]  # 常用时值

# ============================================================
# 第三部分：GetMelody - 随机生成初始旋律
# ============================================================

def generate_random_melody():
    """
    随机生成一段旋律，满足：
    1. 总时值 = MELODY_LENGTH (240)
    2. 音高在 F3 ~ G5 范围内
    3. 最短时值为八分音符 (6)
    
    返回: (pitch_list, beat_list)
    """
    pitch_list = []
    beat_list = []
    remaining = MELODY_LENGTH
    
    while remaining > 0:
        # 选择一个不超过剩余时值的时值
        available_beats = [b for b in VALID_BEATS if b <= remaining]
        if not available_beats:
            # 如果没有合适的标准时值，使用剩余时值（必须是6的倍数）
            if remaining >= BEAT_UNIT:
                beat = remaining
            else:
                # 不应该发生，但作为安全措施
                break
        else:
            beat = random.choice(available_beats)
        
        # 随机选择音高
        pitch = random.randint(PITCH_MIN, PITCH_MAX)
        
        pitch_list.append(pitch)
        beat_list.append(beat)
        remaining -= beat
    
    return pitch_list, beat_list


def Get_Melody():
    """
    生成初始个体的函数，符合 DEAP 框架要求
    返回: creator.Melody 对象
    """
    pitch, beat = generate_random_melody()
    return creator.Melody(pitch, beat)


# ============================================================
# 第四部分：Mutations - 变异操作
# ============================================================

# 变异策略列表
mutation_strategies = []


def mut_keep(individual):
    """保持不变（空操作）"""
    return individual

mutation_strategies.append(mut_keep)


def mut_transpose(individual, semitones=None):
    """
    移调变异：将所有音符上移或下移若干半音
    
    参数:
        individual: Melody 对象
        semitones: 移调半音数，None 则随机选择 [-5, 5]
    """
    if semitones is None:
        semitones = random.randint(-5, 5)
    
    new_pitch = []
    for p in individual.pitch:
        new_p = p + semitones
        # 确保在有效范围内
        new_p = max(PITCH_MIN, min(PITCH_MAX, new_p))
        new_pitch.append(new_p)
    
    individual.pitch = new_pitch
    return individual

mutation_strategies.append(mut_transpose)


def mut_inversion(individual):
    """
    倒影变异：以旋律的第一个音为轴，将音程关系上下翻转
    例如：原旋律上行3度 -> 倒影后下行3度
    """
    if len(individual.pitch) < 2:
        return individual
    
    axis = individual.pitch[0]  # 以第一个音为轴
    new_pitch = [axis]  # 第一个音不变
    
    for i in range(1, len(individual.pitch)):
        interval = individual.pitch[i] - axis
        new_p = axis - interval  # 镜像翻转
        # 确保在有效范围内
        new_p = max(PITCH_MIN, min(PITCH_MAX, new_p))
        new_pitch.append(new_p)
    
    individual.pitch = new_pitch
    return individual

mutation_strategies.append(mut_inversion)


def mut_retrograde(individual):
    """
    逆行变异：将旋律倒序播放
    音高和时值都倒序
    """
    individual.pitch = individual.pitch[::-1]
    individual.beat = individual.beat[::-1]
    return individual

mutation_strategies.append(mut_retrograde)


def mut_change_pitch(individual):
    """
    音高微调：随机选择一个音符，改变其音高（±1~3半音）
    """
    if len(individual.pitch) == 0:
        return individual
    
    idx = random.randint(0, len(individual.pitch) - 1)
    delta = random.choice([-3, -2, -1, 1, 2, 3])
    new_p = individual.pitch[idx] + delta
    new_p = max(PITCH_MIN, min(PITCH_MAX, new_p))
    individual.pitch[idx] = new_p
    return individual

mutation_strategies.append(mut_change_pitch)


def mut_change_rhythm(individual):
    """
    节奏微调：随机选择相邻两个音符，在它们之间转移时值
    保持总时值不变
    """
    if len(individual.beat) < 2:
        return individual
    
    idx = random.randint(0, len(individual.beat) - 2)
    
    # 从 idx 转移一个最小单位到 idx+1，或反过来
    if random.random() < 0.5:
        # idx -> idx+1
        if individual.beat[idx] > BEAT_UNIT:
            individual.beat[idx] -= BEAT_UNIT
            individual.beat[idx + 1] += BEAT_UNIT
    else:
        # idx+1 -> idx
        if individual.beat[idx + 1] > BEAT_UNIT:
            individual.beat[idx + 1] -= BEAT_UNIT
            individual.beat[idx] += BEAT_UNIT
    
    return individual

mutation_strategies.append(mut_change_rhythm)


def mut_split_note(individual):
    """
    音符分裂：随机选择一个音符，将其分裂成两个音符
    时值平分，音高相同或相邻
    """
    if len(individual.pitch) == 0:
        return individual
    
    idx = random.randint(0, len(individual.pitch) - 1)
    
    # 只有时值足够才能分裂
    if individual.beat[idx] >= 2 * BEAT_UNIT:
        old_beat = individual.beat[idx]
        half_beat = old_beat // 2
        # 确保是最小单位的倍数
        half_beat = (half_beat // BEAT_UNIT) * BEAT_UNIT
        if half_beat < BEAT_UNIT:
            half_beat = BEAT_UNIT
        other_half = old_beat - half_beat
        
        if other_half >= BEAT_UNIT:
            # 分裂
            old_pitch = individual.pitch[idx]
            # 第二个音可以是相同音高或相邻音高
            new_pitch = old_pitch + random.choice([-1, 0, 0, 0, 1])  # 倾向于保持相同
            new_pitch = max(PITCH_MIN, min(PITCH_MAX, new_pitch))
            
            individual.pitch[idx] = old_pitch
            individual.beat[idx] = half_beat
            individual.pitch.insert(idx + 1, new_pitch)
            individual.beat.insert(idx + 1, other_half)
    
    return individual

mutation_strategies.append(mut_split_note)


def mut_merge_notes(individual):
    """
    音符合并：随机选择相邻两个音符，合并成一个
    使用第一个音符的音高，时值相加
    """
    if len(individual.pitch) < 2:
        return individual
    
    idx = random.randint(0, len(individual.pitch) - 2)
    
    # 合并时值
    new_beat = individual.beat[idx] + individual.beat[idx + 1]
    
    # 保留第一个音的音高
    individual.beat[idx] = new_beat
    individual.pitch.pop(idx + 1)
    individual.beat.pop(idx + 1)
    
    return individual

mutation_strategies.append(mut_merge_notes)


def melody_mutation(individual, indpb=0.1):
    """
    主变异函数：随机选择一种变异策略并应用
    
    参数:
        individual: Melody 对象
        indpb: 变异概率（由 DEAP 框架传入，此处未使用）
    
    返回:
        (individual,) - DEAP 要求返回元组
    """
    strategy = random.choice(mutation_strategies)
    individual = strategy(individual)
    
    # 验证旋律仍然有效
    assert isinstance(individual, creator.Melody), "Invalid Mutation Function"
    
    return (individual,)


# ============================================================
# 第五部分：辅助函数
# ============================================================

def print_melody_info(melody):
    """打印旋律的详细信息"""
    print(f"音符数量: {len(melody.pitch)}")
    print(f"总时值: {sum(melody.beat)} (应为 {MELODY_LENGTH})")
    print(f"音高范围: {min(melody.pitch)} ~ {max(melody.pitch)}")
    print(f"音高 (索引): {melody.pitch}")
    print(f"时值: {melody.beat}")
    print(f"音符名称: {[valid_notes[p] for p in melody.pitch]}")


def validate_melody(melody):
    """验证旋律是否符合要求"""
    try:
        assert sum(melody.beat) == MELODY_LENGTH, f"总时值错误: {sum(melody.beat)} != {MELODY_LENGTH}"
        assert len(melody.pitch) == len(melody.beat), "音高和时值列表长度不匹配"
        assert all(p >= 0 and p <= 77 for p in melody.pitch), "音高超出范围"
        assert all(b >= BEAT_UNIT for b in melody.beat), f"存在小于最小时值({BEAT_UNIT})的音符"
        return True, "验证通过"
    except AssertionError as e:
        return False, str(e)


# ============================================================
# 第六部分：测试代码
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("ZCS Melody 模块测试")
    print("=" * 50)
    
    # 测试音域范围
    print(f"\n1. 音域范围测试:")
    print(f"   PITCH_MIN = {PITCH_MIN} ({valid_notes[PITCH_MIN]})")
    print(f"   PITCH_MAX = {PITCH_MAX} ({valid_notes[PITCH_MAX]})")
    
    # 测试随机生成旋律
    print(f"\n2. 随机生成旋律测试:")
    for i in range(3):
        pitch, beat = generate_random_melody()
        print(f"   旋律 {i+1}: {len(pitch)} 个音符, 总时值 = {sum(beat)}")
        valid, msg = validate_melody(type('Melody', (), {'pitch': pitch, 'beat': beat})())
        print(f"   验证: {msg}")
    
    # 测试变异操作（需要 DEAP creator 已初始化）
    print(f"\n3. 变异操作测试:")
    print(f"   可用变异策略: {len(mutation_strategies)} 种")
    for i, strategy in enumerate(mutation_strategies):
        print(f"   [{i}] {strategy.__name__}: {strategy.__doc__.split(chr(10))[0].strip() if strategy.__doc__ else '无说明'}")
    
    print("\n" + "=" * 50)
    print("测试完成!")
    print("=" * 50)
