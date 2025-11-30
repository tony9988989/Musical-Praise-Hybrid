"""
初始种群生成模块 (by zcs)

提供 Get_Melody 函数用于随机生成旋律个体。
本模块独立于主程序，通过接口调用。
"""
import random

# 音域范围：F3 ~ G5
# 在12音制下（每个八度12个音）：
#   F3 = 12*2 + 5 = 29
#   G5 = 12*4 + 7 = 55
PITCH_MIN = 29  # F3
PITCH_MAX = 55  # G5

# 时值设置
BEAT_UNIT = 6                   # 最小时值：八分音符
VALID_BEATS = [6, 12, 18, 24, 36, 48]  # 可用时值列表
MELODY_LENGTH = 240             # 总时值（5个小节，四分音符=12）

# 默认调性
DEFAULT_KEY = "C"


def generate_melody(key=None):
    """
    生成随机旋律
    
    参数:
        key: 调性（如 "C", "G", "D" 等），默认为 "C"
    
    返回:
        (key, pitch_list, beat_list) 元组
    """
    if key is None:
        key = DEFAULT_KEY
    
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
        
        # 随机选择音高（在指定音域范围内）
        pitch = random.randint(PITCH_MIN, PITCH_MAX)
        
        pitch_list.append(pitch)
        beat_list.append(beat)
        remaining -= beat
    
    return key, pitch_list, beat_list


# 导出的接口
__all__ = ['generate_melody', 'PITCH_MIN', 'PITCH_MAX', 'BEAT_UNIT', 'VALID_BEATS', 'MELODY_LENGTH', 'DEFAULT_KEY']
