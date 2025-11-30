"""
变异操作模块 (by zcs)

提供8种变异策略，直接操作creator.Melody对象。
所有变异都保留原对象的key属性不变。
"""
from Settings import Melody
import random
from deap import base, creator, tools, algorithms

# 音域范围：F3 ~ G5（12音制）
PITCH_MIN = 29  # F3
PITCH_MAX = 55  # G5
BEAT_UNIT = 6   # 最小时值单位（八分音符）

mutation_strategies = []


def Keep(individual: creator.Melody):
    """保持不变（空操作）"""
    return individual
mutation_strategies.append(Keep)


def Transpose(individual: creator.Melody):
    """移调变异：将所有音符上移或下移若干半音"""
    semitones = random.randint(-5, 5)
    new_pitch = []
    for p in individual.pitch:
        new_p = p + semitones
        new_p = max(PITCH_MIN, min(PITCH_MAX, new_p))
        new_pitch.append(new_p)
    individual.pitch = new_pitch
    return individual
mutation_strategies.append(Transpose)


def Inversion(individual: creator.Melody):
    """倒影变异：以第一个音为轴，将音程关系上下翻转"""
    if len(individual.pitch) < 2:
        return individual
    axis = individual.pitch[0]
    new_pitch = [axis]
    for i in range(1, len(individual.pitch)):
        interval = individual.pitch[i] - axis
        new_p = axis - interval
        new_p = max(PITCH_MIN, min(PITCH_MAX, new_p))
        new_pitch.append(new_p)
    individual.pitch = new_pitch
    return individual
mutation_strategies.append(Inversion)


def Retrograde(individual: creator.Melody):
    """逆行变异：将旋律倒序播放"""
    individual.pitch = individual.pitch[::-1]
    individual.beat = individual.beat[::-1]
    return individual
mutation_strategies.append(Retrograde)


def ChangePitch(individual: creator.Melody):
    """音高微调：随机选择一个音符，改变其音高（±1~3半音）"""
    if len(individual.pitch) == 0:
        return individual
    idx = random.randint(0, len(individual.pitch) - 1)
    delta = random.choice([-3, -2, -1, 1, 2, 3])
    new_p = individual.pitch[idx] + delta
    new_p = max(PITCH_MIN, min(PITCH_MAX, new_p))
    individual.pitch[idx] = new_p
    return individual
mutation_strategies.append(ChangePitch)


def ChangeRhythm(individual: creator.Melody):
    """节奏微调：相邻音符间转移时值，保持总时值不变"""
    if len(individual.beat) < 2:
        return individual
    idx = random.randint(0, len(individual.beat) - 2)
    if random.random() < 0.5:
        if individual.beat[idx] > BEAT_UNIT:
            individual.beat[idx] -= BEAT_UNIT
            individual.beat[idx + 1] += BEAT_UNIT
    else:
        if individual.beat[idx + 1] > BEAT_UNIT:
            individual.beat[idx + 1] -= BEAT_UNIT
            individual.beat[idx] += BEAT_UNIT
    return individual
mutation_strategies.append(ChangeRhythm)


def SplitNote(individual: creator.Melody):
    """音符分裂：将一个音符分裂成两个，时值平分"""
    if len(individual.pitch) == 0:
        return individual
    idx = random.randint(0, len(individual.pitch) - 1)
    if individual.beat[idx] >= 2 * BEAT_UNIT:
        old_beat = individual.beat[idx]
        half_beat = (old_beat // 2 // BEAT_UNIT) * BEAT_UNIT
        if half_beat < BEAT_UNIT:
            half_beat = BEAT_UNIT
        other_half = old_beat - half_beat
        if other_half >= BEAT_UNIT:
            old_pitch = individual.pitch[idx]
            new_pitch = old_pitch + random.choice([-1, 0, 0, 0, 1])
            new_pitch = max(PITCH_MIN, min(PITCH_MAX, new_pitch))
            individual.beat[idx] = half_beat
            individual.pitch.insert(idx + 1, new_pitch)
            individual.beat.insert(idx + 1, other_half)
    return individual
mutation_strategies.append(SplitNote)


def MergeNotes(individual: creator.Melody):
    """音符合并：将相邻两个音符合并，时值相加"""
    if len(individual.pitch) < 2:
        return individual
    idx = random.randint(0, len(individual.pitch) - 2)
    merged_beat = individual.beat[idx] + individual.beat[idx + 1]
    individual.beat[idx] = merged_beat
    individual.pitch.pop(idx + 1)
    individual.beat.pop(idx + 1)
    return individual
mutation_strategies.append(MergeNotes)


def melody_mutation(individual: creator.Melody, indpb=0.1):
    """
    变异入口函数
    
    随机选择一种变异策略应用到个体上。
    变异是原地修改，保留key属性不变。
    返回格式符合DEAP要求：(individual,)
    """
    strategy = mutation_strategies[random.randint(0, len(mutation_strategies) - 1)]
    individual = strategy(individual)
    assert isinstance(individual, creator.Melody), "Invalid Mutational Function"
    return (individual,)