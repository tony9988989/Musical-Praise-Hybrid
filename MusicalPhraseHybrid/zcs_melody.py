"""
初始种群生成模块 (by zcs)

提供 generate_melody 函数用于随机生成旋律个体。
支持12个大调的调性约束。
本模块独立于主程序，通过接口调用。
"""
import random

# 从主程序导入设置（复用组长代码）
try:
    from Settings import KEY_SCALE_MAP, MELODY_LENGTH, Notes
except ImportError:
    # 如果无法导入，使用本地定义（兼容独立测试）
    Notes = ["C", "#C", "D", "#D", "E", "F", "#F", "G", "#G", "A", "#A", "B"]
    KEY_SCALE_MAP = {
        "C": [0, 2, 4, 5, 7, 9, 11],
        "#C": [1, 3, 5, 6, 8, 10, 0],
        "D": [2, 4, 6, 7, 9, 11, 1],
        "#D": [3, 5, 7, 8, 10, 0, 2],
        "E": [4, 6, 8, 9, 11, 1, 3],
        "F": [5, 7, 9, 10, 0, 2, 4],
        "#F": [6, 8, 10, 11, 1, 3, 5],
        "G": [7, 9, 11, 0, 2, 4, 6],
        "#G": [8, 10, 0, 1, 3, 5, 7],
        "A": [9, 11, 1, 2, 4, 6, 8],
        "#A": [10, 0, 2, 3, 5, 7, 9],
        "B": [11, 1, 3, 4, 6, 8, 10]
    }
    MELODY_LENGTH = 240

# 音域范围：F3 ~ G5
# 在12音制下（每个八度12个音）：
#   F3 = 12*2 + 5 = 29
#   G5 = 12*4 + 7 = 55
PITCH_MIN = 29  # F3
PITCH_MAX = 55  # G5

# 时值设置
BEAT_UNIT = 6                   # 最小时值：八分音符
VALID_BEATS = [6, 12, 18, 24, 36, 48]  # 可用时值列表

# 默认调性
DEFAULT_KEY = "C"


def get_scale_pitches(key, pitch_min=PITCH_MIN, pitch_max=PITCH_MAX):
    """
    获取指定调性在给定音域范围内的所有有效音高索引
    
    参数:
        key: 调性名称 (如 'C', 'G', 'D' 等)
        pitch_min: 最小音高索引
        pitch_max: 最大音高索引
    
    返回:
        该调性内的所有有效音高索引列表
    """
    if key not in KEY_SCALE_MAP:
        print(f"警告：未知调性 '{key}'，使用默认调性 {DEFAULT_KEY}")
        key = DEFAULT_KEY
    
    scale = KEY_SCALE_MAP[key]
    valid_pitches = []
    
    for pitch in range(pitch_min, pitch_max + 1):
        note_in_octave = pitch % 12  # 每个八度12个音
        if note_in_octave in scale:
            valid_pitches.append(pitch)
    
    return valid_pitches


def generate_melody(key=None, use_scale=True):
    """
    生成随机旋律
    
    参数:
        key: 调性（如 "C", "G", "D" 等），默认为 "C"
        use_scale: 是否使用调性约束，默认为True
    
    返回:
        (key, pitch_list, beat_list) 元组
    """
    if key is None:
        key = DEFAULT_KEY
    
    # 获取该调性的有效音高
    if use_scale:
        valid_pitches = get_scale_pitches(key)
    else:
        valid_pitches = list(range(PITCH_MIN, PITCH_MAX + 1))
    
    pitch_list = []
    beat_list = []
    remaining = MELODY_LENGTH
    
    while remaining > 0:
        # 选择可用的时值
        available_beats = [b for b in VALID_BEATS if b <= remaining]
        if not available_beats:
            if remaining >= BEAT_UNIT:
                beat = remaining
            else:
                break
        else:
            beat = random.choice(available_beats)
        
        # 随机选择音高（在调性音阶内）
        pitch = random.choice(valid_pitches)
        
        pitch_list.append(pitch)
        beat_list.append(beat)
        remaining -= beat
    
    return key, pitch_list, beat_list


# 导出的接口
__all__ = [
    'generate_melody', 'get_scale_pitches',
    'PITCH_MIN', 'PITCH_MAX', 'BEAT_UNIT', 'VALID_BEATS', 
    'MELODY_LENGTH', 'DEFAULT_KEY', 'KEY_SCALE_MAP'
]
