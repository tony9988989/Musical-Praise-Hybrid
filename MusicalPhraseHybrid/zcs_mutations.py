"""
变异操作模块 (by zcs)

提供8种变异策略：
1. Keep - 保持不变
2. Transpose - 移调
3. Inversion - 倒影
4. Retrograde - 逆行
5. ChangePitch - 音高微调
6. ChangeRhythm - 节奏微调
7. SplitNote - 音符分裂
8. MergeNotes - 音符合并

本模块独立于主程序，通过接口调用。
"""
import random

# 音域范围：F3 ~ G5（12音制）
PITCH_MIN = 29  # F3
PITCH_MAX = 55  # G5

# 最小时值单位（八分音符）
BEAT_UNIT = 6


def keep(pitch, beat):
    """保持不变（空操作）"""
    return pitch, beat


def transpose(pitch, beat, semitones=None):
    """
    移调变异：将所有音符上移或下移若干半音，保持音程关系不变
    
    参数:
        pitch: 音高列表
        beat: 时值列表
        semitones: 移调半音数（默认随机-5~5）
    """
    if semitones is None:
        semitones = random.randint(-5, 5)
    
    new_pitch = []
    for p in pitch:
        new_p = p + semitones
        new_p = max(PITCH_MIN, min(PITCH_MAX, new_p))
        new_pitch.append(new_p)
    
    return new_pitch, beat


def inversion(pitch, beat):
    """
    倒影变异：以第一个音为轴，将音程关系上下翻转
    """
    if len(pitch) < 2:
        return pitch, beat
    
    axis = pitch[0]
    new_pitch = [axis]
    
    for i in range(1, len(pitch)):
        interval = pitch[i] - axis
        new_p = axis - interval
        new_p = max(PITCH_MIN, min(PITCH_MAX, new_p))
        new_pitch.append(new_p)
    
    return new_pitch, beat


def retrograde(pitch, beat):
    """
    逆行变异：将旋律倒序播放（音高和时值都倒序）
    """
    return pitch[::-1], beat[::-1]


def change_pitch(pitch, beat):
    """
    音高微调：随机选择一个音符，改变其音高（±1~3半音）
    """
    if len(pitch) == 0:
        return pitch, beat
    
    new_pitch = pitch.copy()
    idx = random.randint(0, len(new_pitch) - 1)
    delta = random.choice([-3, -2, -1, 1, 2, 3])
    new_p = new_pitch[idx] + delta
    new_p = max(PITCH_MIN, min(PITCH_MAX, new_p))
    new_pitch[idx] = new_p
    
    return new_pitch, beat


def change_rhythm(pitch, beat):
    """
    节奏微调：相邻音符间转移时值，保持总时值不变
    """
    if len(beat) < 2:
        return pitch, beat
    
    new_beat = beat.copy()
    idx = random.randint(0, len(new_beat) - 2)
    
    if random.random() < 0.5:
        if new_beat[idx] > BEAT_UNIT:
            new_beat[idx] -= BEAT_UNIT
            new_beat[idx + 1] += BEAT_UNIT
    else:
        if new_beat[idx + 1] > BEAT_UNIT:
            new_beat[idx + 1] -= BEAT_UNIT
            new_beat[idx] += BEAT_UNIT
    
    return pitch, new_beat


def split_note(pitch, beat):
    """
    音符分裂：将一个音符分裂成两个，时值平分
    """
    if len(pitch) == 0:
        return pitch, beat
    
    new_pitch = pitch.copy()
    new_beat = beat.copy()
    idx = random.randint(0, len(new_pitch) - 1)
    
    if new_beat[idx] >= 2 * BEAT_UNIT:
        old_beat = new_beat[idx]
        half_beat = old_beat // 2
        half_beat = (half_beat // BEAT_UNIT) * BEAT_UNIT
        if half_beat < BEAT_UNIT:
            half_beat = BEAT_UNIT
        other_half = old_beat - half_beat
        
        if other_half >= BEAT_UNIT:
            old_pitch = new_pitch[idx]
            new_note_pitch = old_pitch + random.choice([-1, 0, 0, 0, 1])
            new_note_pitch = max(PITCH_MIN, min(PITCH_MAX, new_note_pitch))
            
            new_pitch[idx] = old_pitch
            new_beat[idx] = half_beat
            new_pitch.insert(idx + 1, new_note_pitch)
            new_beat.insert(idx + 1, other_half)
    
    return new_pitch, new_beat


def merge_notes(pitch, beat):
    """
    音符合并：将相邻两个音符合并，时值相加
    """
    if len(pitch) < 2:
        return pitch, beat
    
    new_pitch = pitch.copy()
    new_beat = beat.copy()
    idx = random.randint(0, len(new_pitch) - 2)
    
    merged_beat = new_beat[idx] + new_beat[idx + 1]
    new_beat[idx] = merged_beat
    new_pitch.pop(idx + 1)
    new_beat.pop(idx + 1)
    
    return new_pitch, new_beat


# 变异策略列表
MUTATION_STRATEGIES = [
    keep,
    transpose,
    inversion,
    retrograde,
    change_pitch,
    change_rhythm,
    split_note,
    merge_notes,
]


def apply_mutation(pitch, beat, strategy=None):
    """
    应用变异策略
    
    参数:
        pitch: 音高列表
        beat: 时值列表
        strategy: 指定策略函数（默认随机选择）
    
    返回:
        (new_pitch, new_beat) 元组
    """
    if strategy is None:
        strategy = random.choice(MUTATION_STRATEGIES)
    
    return strategy(pitch, beat)


# 导出的接口
__all__ = [
    'keep', 'transpose', 'inversion', 'retrograde',
    'change_pitch', 'change_rhythm', 'split_note', 'merge_notes',
    'MUTATION_STRATEGIES', 'apply_mutation',
    'PITCH_MIN', 'PITCH_MAX', 'BEAT_UNIT'
]
