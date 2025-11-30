from Settings import Melody, Notes,KEY_SCALE_MAP
import random
from deap import base, creator, tools, algorithms

# ----------- crossover function by zyx -------------

# ----------------- 平移到指定调式 -----------------
def shift_pitch_to_key(pitch_list, from_key, to_key):
    shift = (Notes.index(to_key) - Notes.index(from_key)) % 12
    shifted = []
    for p in pitch_list:
        octave = p // 12
        note = p % 12
        new_note = note + shift
        shifted.append(octave * 12 + new_note)
    return shifted


# ----------------- 单点 crossover-----------------
def crossover(parent1_pitch, parent1_beat, parent2_pitch, parent2_beat):
    cum1 = [0]
    for b in parent1_beat:
        cum1.append(cum1[-1] + b)
    cum2 = [0]
    for b in parent2_beat:
        cum2.append(cum2[-1] + b)
    length = len(parent1_pitch)
    legal_points = []
    for k in range(1, length):
        beat_sum1 = cum1[k] + (cum2[-1] - cum2[k])
        beat_sum2 = cum2[k] + (cum1[-1] - cum1[k])
        # 保证总和为 240
        if (beat_sum1 == 240 and beat_sum2 == 240):
            legal_points.append(k)
    c1_pitch=[]
    c1_beat=[]
    c2_pitch=[]
    c2_beat=[]
    if not legal_points:
        # 如果没有合法点，直接返回父母，不做 crossover
        return parent1_pitch, parent1_beat, parent2_pitch, parent2_beat
    else:
        for p in legal_points:
            choice=random.randint(0,1)
            if choice==1:
                c1_pitch+= parent1_pitch[:p]
                c1_beat += parent1_beat[:p]
                c2_pitch += parent2_pitch[:p]
                c2_beat += parent2_beat[:p]
            else:
                c2_pitch += parent1_pitch[:p]
                c2_beat += parent1_beat[:p]
                c1_pitch += parent2_pitch[:p]
                c1_beat += parent2_beat[:p]
    return c1_pitch, c1_beat, c2_pitch, c2_beat



# ----------------- 主函数 -----------------
def GetChild(parent1: Melody, parent2: Melody):
    # 1. 平移父母到 C 大调
    c1_pitch = shift_pitch_to_key(parent1.pitch, parent1.key, "C")
    c2_pitch = shift_pitch_to_key(parent2.pitch, parent2.key, "C")
    c1_beat = parent1.beat[:]
    c2_beat = parent2.beat[:]

    # 2. 可以多次杂交（循环调用 crossover）
    c1_pitch, c1_beat, c2_pitch, c2_beat = crossover(
        c1_pitch, c1_beat, c2_pitch, c2_beat
    )

    # 3. 平移回父母调式
    c1_pitch = shift_pitch_to_key(c1_pitch, "C", parent1.key)
    c2_pitch = shift_pitch_to_key(c2_pitch, "C", parent2.key)

    # 4. 创建子代 Melody
    child1 = creator.Melody(parent1.key, c1_pitch, c1_beat)
    child2 = creator.Melody(parent2.key, c2_pitch, c2_beat)

    assert isinstance(child1, creator.Melody) and isinstance(child2, creator.Melody), "Invalid Crossover Function"
    return child1, child2
