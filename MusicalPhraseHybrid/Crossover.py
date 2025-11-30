from Settings import Melody
import random
from deap import base, creator, tools, algorithms

# ----------- crossover function by zyx -------------

# ----------------- 调式音阶函数 -----------------
KEY_SCALE_MAP = {
    "C": [0,2,4,5,7,9,11],
    "C#":[1,3,5,6,8,10,0],
    "D": [2,4,6,7,9,11,1],
    "D#":[3,5,7,8,10,0,2],
    "E": [4,6,8,9,11,1,3],
    "F": [5,7,9,10,0,2,4],
    "F#":[6,8,10,11,1,3,5],
    "G": [7,9,11,0,2,4,6],
    "G#":[8,10,0,1,3,5,7],
    "A": [9,11,1,2,4,6,8],
    "A#":[10,0,2,3,5,7,9],
    "B": [11,1,3,4,6,8,10]
}

def normalize_to_key(pitch_list, key):
    """ 将 pitch 列表归一化到指定 key """
    key_scale = KEY_SCALE_MAP[key]
    normalized = []
    for p in pitch_list:
        note = p % 12
        closest = min(key_scale, key=lambda x: abs(x - note))
        octave = p // 12
        normalized.append(closest + 12 * octave)
    return normalized

# ----------------- 交叉策略 -----------------
def one_point_crossover(p1, p2):
    length = len(p1.pitch)
    if length <= 1:
        return p1.pitch[:], p1.beat[:], p2.pitch[:], p2.beat[:]
    k = random.randint(1, length-1)
    return (p1.pitch[:k]+p2.pitch[k:], p1.beat[:k]+p2.beat[k:],
            p2.pitch[:k]+p1.pitch[k:], p2.beat[:k]+p1.beat[k:])

def two_point_crossover(p1, p2):
    length = len(p1.pitch)
    if length <= 2:
        return one_point_crossover(p1, p2)
    k1,k2 = sorted(random.sample(range(1,length),2))
    return (p1.pitch[:k1]+p2.pitch[k1:k2]+p1.pitch[k2:], p1.beat[:k1]+p2.beat[k1:k2]+p1.beat[k2:],
            p2.pitch[:k1]+p1.pitch[k1:k2]+p2.pitch[k2:], p2.beat[:k1]+p1.beat[k1:k2]+p2.beat[k2:])

def uniform_crossover(p1, p2):
    c1_pitch,c2_pitch=[],[]
    c1_beat,c2_beat=[],[]
    for i in range(len(p1.pitch)):
        if random.random()<0.5:
            c1_pitch.append(p1.pitch[i]); c1_beat.append(p1.beat[i])
            c2_pitch.append(p2.pitch[i]); c2_beat.append(p2.beat[i])
        else:
            c1_pitch.append(p2.pitch[i]); c1_beat.append(p2.beat[i])
            c2_pitch.append(p1.pitch[i]); c2_beat.append(p1.beat[i])
    return c1_pitch, c1_beat, c2_pitch, c2_beat

# ----------------- 修正 beat -----------------
def normalize_beat(beat):
    total = sum(beat)
    if total == 0:
        return [240]
    factor = 240 / total
    new_beat = [max(1,int(b*factor)) for b in beat]
    diff = 240 - sum(new_beat)
    new_beat[-1] += diff
    return new_beat

# ----------------- 主函数 -----------------
crossover_strategies = [one_point_crossover, two_point_crossover, uniform_crossover]

def GetChild(parent1:Melody, parent2:Melody):
    # 1. 随机选择交叉策略
    c1_pitch,c1_beat,c2_pitch,c2_beat = random.choice(crossover_strategies)(parent1, parent2)
    
    # 2. 动态选择父母调式
    chosen_key = random.choice([parent1.key, parent2.key])
    c1_pitch = normalize_to_key(c1_pitch, chosen_key)
    c2_pitch = normalize_to_key(c2_pitch, chosen_key)
    
    # 3. 修正 beat
    c1_beat = normalize_beat(c1_beat)
    c2_beat = normalize_beat(c2_beat)
    
    # 4. 创建子代 Melody
    child1 = creator.Melody(chosen_key, c1_pitch, c1_beat)
    child2 = creator.Melody(chosen_key, c2_pitch, c2_beat)
    assert isinstance(child1 , creator.Melody) and isinstance(child2 , creator.Melody),"Invalid Crossover Function"
    return child1, child2