from Settings import Melody, Notes,KEY_SCALE_MAP
import random
from deap import base, creator, tools, algorithms

# ----------- crossover function by zyx -------------

# ----------------- 平移到指定调式 -----------------
def shift_pitch_to_key(pitch_list, from_key, to_key):
    shift = (Notes.index(to_key) - Notes.index(from_key)) % 12
    shifted = []
    for p in pitch_list:
        if p is None:
            shifted.append(None)
            continue
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

    # Use the minimum length of beats to avoid IndexError
    # A melody is represented by a list of pitches and a list of beats (durations).
    # We assume that for any given melody, the pitch list and beat list have the same length.
    # The crossover operation exchanges segments of two parent melodies to create two child melodies.
    length = min(len(parent1_beat), len(parent2_beat))

    legal_points = []
    # A crossover point `k` is an index in the melody lists. The crossover happens *before* this index.
    # We iterate through all possible crossover points.
    for k in range(1, length):
        # The total duration of the resulting children must be preserved (assumed to be 192).
        # Duration of child1 = (duration of parent1's head) + (duration of parent2's tail)
        beat_sum1 = cum1[k] + (cum2[-1] - cum2[k])
        # Duration of child2 = (duration of parent2's head) + (duration of parent1's tail)
        beat_sum2 = cum2[k] + (cum1[-1] - cum1[k])
        
        # Check if both children maintain the required total duration.
        if (beat_sum1 == 192 and beat_sum2 == 192):
            legal_points.append(k)

    # If no points are found that preserve the total duration,
    # the crossover is aborted, and the parents are returned unchanged.
    if not legal_points:
        return parent1_pitch[:], parent1_beat[:], parent2_pitch[:], parent2_beat[:]

    # If legal points exist, choose one at random for a single-point crossover.
    k = random.choice(legal_points)

    # Create children by swapping the segments after the crossover point.
    c1_pitch = parent1_pitch[:k] + parent2_pitch[k:]
    c1_beat = parent1_beat[:k] + parent2_beat[k:]
    c2_pitch = parent2_pitch[:k] + parent1_pitch[k:]
    c2_beat = parent2_beat[:k] + parent1_beat[k:]

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
