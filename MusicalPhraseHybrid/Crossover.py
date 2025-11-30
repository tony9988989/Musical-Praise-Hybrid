from Settings import Melody, Notes
import random
from deap import base, creator, tools, algorithms

# ----------- crossover function by zyx -------------

# ----------------- 调式音阶函数 -----------------
KEY_SCALE_MAP = {
    "C": [0,2,4,5,7,9,11],
    "#C":[1,3,5,6,8,10,0],
    "D": [2,4,6,7,9,11,1],
    "#D":[3,5,7,8,10,0,2],
    "E": [4,6,8,9,11,1,3],
    "F": [5,7,9,10,0,2,4],
    "#F":[6,8,10,11,1,3,5],
    "G": [7,9,11,0,2,4,6],
    "#G":[8,10,0,1,3,5,7],
    "A": [9,11,1,2,4,6,8],
    "#A":[10,0,2,3,5,7,9],
    "B": [11,1,3,4,6,8,10]
}

# ----------------- 平移到指定调式 -----------------
def shift_pitch_to_key(pitch_list, from_key, to_key):
    shift = (Notes.index(to_key) - Notes.index(from_key)) % 12
    shifted = []
    for p in pitch_list:
        octave = p // 12
        note = p % 12
        new_note = note + shift
        shifted.append(octave*12 + new_note)
    return shifted

# ----------------- 单点 crossover-----------------
def one_point_crossover(parent1_pitch, parent1_beat, parent2_pitch, parent2_beat):
    cum1 = [0]
    for b in parent1_beat:
        cum1.append(cum1[-1]+b)
    cum2 = [0]
    for b in parent2_beat:
        cum2.append(cum2[-1]+b)
    length = len(parent1_pitch)
    legal_points = []
    for k in range(1, length):
        beat_sum1 = cum1[k] + (cum2[-1]-cum2[k])
        beat_sum2 = cum2[k] + (cum1[-1]-cum1[k])
        if 236 <= beat_sum1 <= 240 and 236 <= beat_sum2 <= 240:
            legal_points.append(k)
    if not legal_points:
        return parent1_pitch, parent1_beat, parent2_pitch, parent2_beat
    else:
        k = random.choice(legal_points)
    c1_pitch = parent1_pitch[:k] + parent2_pitch[k:]
    c1_beat  = parent1_beat[:k] + parent2_beat[k:]
    c2_pitch = parent2_pitch[:k] + parent1_pitch[k:]
    c2_beat  = parent2_beat[:k] + parent1_beat[k:]
    c1_beat[-1] += 240 - sum(c1_beat)
    c2_beat[-1] += 240 - sum(c2_beat)
    return c1_pitch, c1_beat, c2_pitch, c2_beat

# ----------------- 主函数 -----------------
def GetChild(parent1: Melody, parent2: Melody):
    # 1. 平移父母到 C 大调
    p1_pitch_c = shift_pitch_to_key(parent1.pitch, parent1.key, "C")
    p2_pitch_c = shift_pitch_to_key(parent2.pitch, parent2.key, "C")
    
    # 2. 单点 crossover
    c1_pitch, c1_beat, c2_pitch, c2_beat = one_point_crossover(
        p1_pitch_c, parent1.beat, p2_pitch_c, parent2.beat
    )
    
    # 3. 平移回父母调式
    c1_pitch = shift_pitch_to_key(c1_pitch, "C", parent1.key)
    c2_pitch = shift_pitch_to_key(c2_pitch, "C", parent2.key)
    
    # 4. 创建子代 Melody
    child1 = creator.Melody(parent1.key, c1_pitch, c1_beat)
    child2 = creator.Melody(parent2.key, c2_pitch, c2_beat)
    
    assert isinstance(child1, creator.Melody) and isinstance(child2, creator.Melody), "Invalid Crossover Function"
    return child1, child2
