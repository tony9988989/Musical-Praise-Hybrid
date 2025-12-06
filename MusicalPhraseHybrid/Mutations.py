"""
变异操作模块 (by zcs)

提供8种变异策略，直接操作creator.Melody对象。
所有变异都保留原对象的key属性不变。
所有涉及音高变化的操作都保证在调性内（基于音级而非半音）。
"""
from Settings import Melody, KEY_SCALE_MAP,Notes
import random
from deap import base, creator, tools, algorithms

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Melody", Melody, fitness=creator.FitnessMax)
PITCH_MIN = 0
PITCH_MAX = 84
BEAT_UNIT = 6  # 最小时值单位（八分音符）

mutation_strategies = []


def get_scale_pitches(key, pitch_min=PITCH_MIN, pitch_max=PITCH_MAX):
    """获取指定调性在音域范围内的所有有效音高"""
    assert key in KEY_SCALE_MAP,"invalid key"

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


def Translation(individual: creator.Melody):
    """
    调性归一化变异：将所有调外音吸附到最近的调内音

    例如C大调中：
    - #C(1) → C(0) 或 D(2)，取最近的
    - #F(6) → F(5) 或 G(7)，取最近的
    """
    key = individual.key
    l=random.choice([-2,-1,1,2])
    new_pitch = []
    for i in individual.pitch:
        if i is None:
            new_pitch.append(None)
        else:
            new_pitch.append(normalize_pitch_to_key(i+l, key))
    individual.pitch = new_pitch
    return individual


mutation_strategies.append(Translation)

def Inversion(individual: creator.Melody):
    """
    倒影变异：以第一个音为轴，将音程关系上下翻转（基于音级）

    在调内音阶上操作，保证结果始终在调内。
    例如C大调：C-E-G（上2级、上4级）→ C-A-F（下2级、下4级）
    休止符 (None) 不参与变异，保持原位。
    """
    if len(individual.pitch) < 2:
        return individual

    key = individual.key
    scale_pitches = get_scale_pitches(key)
    if not scale_pitches:
        return individual

    # 找到第一个非休止符的音作为轴
    axis = None
    first_note_idx = -1
    for i, p in enumerate(individual.pitch):
        if p is not None:
            axis = p
            first_note_idx = i
            break
    
    # 如果全是休止符，则不变
    if axis is None:
        return individual

    # 找到轴音在调内音阶中的位置
    if axis in scale_pitches:
        axis_idx = scale_pitches.index(axis)
    else:
        # 如果轴音是调外音，先吸附到调内
        axis = min(scale_pitches, key=lambda x: abs(x - axis))
        axis_idx = scale_pitches.index(axis)

    new_pitch = individual.pitch[:]

    # 从轴音开始，对后面的所有音符进行倒影
    for i in range(first_note_idx, len(individual.pitch)):
        current = individual.pitch[i]
        
        # 休止符保持不变
        if current is None:
            continue

        # 找到当前音在调内音阶的位置
        if current in scale_pitches:
            current_idx = scale_pitches.index(current)
        else:
            current = min(scale_pitches, key=lambda x: abs(x - current))
            current_idx = scale_pitches.index(current)

        # 计算音级间隔并倒影
        interval = current_idx - axis_idx
        new_idx = axis_idx - interval
        new_idx = max(0, min(len(scale_pitches) - 1, new_idx))

        new_pitch[i] = scale_pitches[new_idx]

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
    休止符 (None) 不参与变异。
    """
    if len(individual.pitch) == 0:
        return individual

    # 获取所有非休止符的索引
    non_rest_indices = [i for i, p in enumerate(individual.pitch) if p is not None]
    
    # 如果没有非休止符，则不变
    if not non_rest_indices:
        return individual

    key = individual.key
    scale_pitches = get_scale_pitches(key)

    if len(scale_pitches) == 0:
        return individual

    # 随机选择一个非休止符的索引
    idx = random.choice(non_rest_indices)
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
    休止符 (None) 也可以被分裂，分裂后两个音符都为空拍。
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

            # 如果原音符是休止符
            if old_pitch is None:
                # 分裂后两个音符都是休止符
                individual.beat[idx] = half_beat
                individual.pitch.insert(idx + 1, None)
                individual.beat.insert(idx + 1, other_half)
            else:
                # 原音符不是休止符
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
    """音符合并：将相邻两个音符合并，时值相加
    如果两个音符中有一个是休止符，则合并后的音符为另一个音符。
    如果两个音符都是休止符，则合并后的音符仍为休止符。
    """
    if len(individual.pitch) < 2:
        return individual
    idx = random.randint(0, len(individual.pitch) - 2)
    merged_beat = individual.beat[idx] + individual.beat[idx + 1]
    
    # 处理合并后的音高
    pitch1 = individual.pitch[idx]
    pitch2 = individual.pitch[idx + 1]
    
    # 合并规则：
    # 1. 如果两个都不是休止符，随机选择一个
    # 2. 如果有一个是休止符，选择另一个
    # 3. 如果两个都是休止符，结果是休止符
    if pitch1 is not None and pitch2 is not None:
        merged_pitch = random.choice([pitch1, pitch2])
    elif pitch1 is not None:
        merged_pitch = pitch1
    elif pitch2 is not None:
        merged_pitch = pitch2
    else:  # pitch1 is None and pitch2 is None
        merged_pitch = None
        
    individual.beat[idx] = merged_beat
    individual.pitch[idx] = merged_pitch
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
    if random.random()<indpb:
        strategy = random.choice(mutation_strategies)
        individual = strategy(individual)
    assert isinstance(individual, creator.Melody), "Invalid Mutational Function"
    return (individual,)
