"""
变异操作模块 (by zcs)

提供8种变异策略，直接操作creator.Melody对象。
所有变异都保留原对象的key属性不变。
所有涉及音高变化的操作都保证在调性内（基于音级而非半音）。
"""
from Settings import Melody, KEY_SCALE_MAP
import random
from deap import base, creator, tools, algorithms

# 音域范围：F3 ~ G5（12音制）
PITCH_MIN = 29  # F3
PITCH_MAX = 55  # G5
BEAT_UNIT = 6   # 最小时值单位（八分音符）

mutation_strategies = []


def get_scale_pitches(key, pitch_min=PITCH_MIN, pitch_max=PITCH_MAX):
    """获取指定调性在音域范围内的所有有效音高"""
    if key not in KEY_SCALE_MAP:
        return list(range(pitch_min, pitch_max + 1))
    
    scale = KEY_SCALE_MAP[key]
    valid_pitches = []
    for pitch in range(pitch_min, pitch_max + 1):
        if pitch % 12 in scale:
            valid_pitches.append(pitch)
    return valid_pitches


def normalize_pitch_to_key(pitch, key):
    """将单个音高归一化到调内最近的音"""
    if key not in KEY_SCALE_MAP:
        return pitch
    
    key_scale = KEY_SCALE_MAP[key]
    note = pitch % 12
    closest = min(key_scale, key=lambda x: abs(x - note))
    octave = pitch // 12
    new_p = closest + 12 * octave
    return max(PITCH_MIN, min(PITCH_MAX, new_p))


def Keep(individual: creator.Melody):
    """保持不变（空操作）"""
    return individual
mutation_strategies.append(Keep)


def NormalizeToKey(individual: creator.Melody):
    """
    调性归一化变异：将所有调外音吸附到最近的调内音
    
    例如C大调中：
    - #C(1) → C(0) 或 D(2)，取最近的
    - #F(6) → F(5) 或 G(7)，取最近的
    """
    key = individual.key
    new_pitch = [normalize_pitch_to_key(p, key) for p in individual.pitch]
    individual.pitch = new_pitch
    return individual
mutation_strategies.append(NormalizeToKey)


def Inversion(individual: creator.Melody):
    """
    倒影变异：以第一个音为轴，将音程关系上下翻转（基于音级）
    
    在调内音阶上操作，保证结果始终在调内。
    例如C大调：C-E-G（上2级、上4级）→ C-A-F（下2级、下4级）
    """
    if len(individual.pitch) < 2:
        return individual
    
    key = individual.key
    scale_pitches = get_scale_pitches(key)
    
    if len(scale_pitches) == 0:
        return individual
    
    axis = individual.pitch[0]
    
    # 找到轴音在调内音阶中的位置
    if axis in scale_pitches:
        axis_idx = scale_pitches.index(axis)
    else:
        axis = min(scale_pitches, key=lambda x: abs(x - axis))
        axis_idx = scale_pitches.index(axis)
    
    new_pitch = [axis]
    
    for i in range(1, len(individual.pitch)):
        current = individual.pitch[i]
        
        if current in scale_pitches:
            current_idx = scale_pitches.index(current)
        else:
            current = min(scale_pitches, key=lambda x: abs(x - current))
            current_idx = scale_pitches.index(current)
        
        # 计算音级间隔并倒影
        interval = current_idx - axis_idx
        new_idx = axis_idx - interval
        new_idx = max(0, min(len(scale_pitches) - 1, new_idx))
        
        new_pitch.append(scale_pitches[new_idx])
    
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
    """
    音高微调：随机选择一个音符，在调内上下移动1~2个音级
    
    例如C大调中：C → D（上移1级）或 C → E（上移2级）
    """
    if len(individual.pitch) == 0:
        return individual
    
    key = individual.key
    scale_pitches = get_scale_pitches(key)
    
    if len(scale_pitches) == 0:
        return individual
    
    idx = random.randint(0, len(individual.pitch) - 1)
    current_pitch = individual.pitch[idx]
    
    if current_pitch not in scale_pitches:
        current_pitch = min(scale_pitches, key=lambda x: abs(x - current_pitch))
    
    try:
        scale_idx = scale_pitches.index(current_pitch)
    except ValueError:
        return individual
    
    # 在调内移动±1~2个音级
    delta = random.choice([-2, -1, 1, 2])
    new_scale_idx = scale_idx + delta
    new_scale_idx = max(0, min(len(scale_pitches) - 1, new_scale_idx))
    
    individual.pitch[idx] = scale_pitches[new_scale_idx]
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
    """
    音符分裂：将一个音符分裂成两个，时值平分
    新音符在调内上下移动0~1个音级
    """
    if len(individual.pitch) == 0:
        return individual
    
    key = individual.key
    scale_pitches = get_scale_pitches(key)
    
    idx = random.randint(0, len(individual.pitch) - 1)
    if individual.beat[idx] >= 2 * BEAT_UNIT:
        old_beat = individual.beat[idx]
        half_beat = (old_beat // 2 // BEAT_UNIT) * BEAT_UNIT
        if half_beat < BEAT_UNIT:
            half_beat = BEAT_UNIT
        other_half = old_beat - half_beat
        
        if other_half >= BEAT_UNIT:
            old_pitch = individual.pitch[idx]
            
            if old_pitch in scale_pitches:
                scale_idx = scale_pitches.index(old_pitch)
            else:
                old_pitch = min(scale_pitches, key=lambda x: abs(x - old_pitch))
                scale_idx = scale_pitches.index(old_pitch)
            
            # 新音符在调内移动0或±1音级
            delta = random.choice([-1, 0, 0, 0, 1])
            new_scale_idx = scale_idx + delta
            new_scale_idx = max(0, min(len(scale_pitches) - 1, new_scale_idx))
            new_pitch = scale_pitches[new_scale_idx]
            
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


# 导出接口
__all__ = [
    'mutation_strategies', 'melody_mutation',
    'Keep', 'NormalizeToKey', 'Inversion', 'Retrograde',
    'ChangePitch', 'ChangeRhythm', 'SplitNote', 'MergeNotes',
    'get_scale_pitches', 'normalize_pitch_to_key',
    'PITCH_MIN', 'PITCH_MAX', 'BEAT_UNIT'
]
