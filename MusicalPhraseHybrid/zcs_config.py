"""
配置文件读取与自定义旋律输入模块 (by zcs)

提供从文件读取配置参数和用户自定义旋律的功能。
本模块独立于主程序，通过接口调用。
"""
import os

# 从Settings导入音名转换表
try:
    from Settings import TransPitches, Notes
except ImportError:
    # 如果无法导入，使用本地定义
    Notes = ["C", "#C", "D", "#D", "E", "F", "#F", "G", "#G", "A", "#A", "B"]
    valid_notes = []
    for i in range(1, 8):
        valid_notes += [str(Notes[j] + str(i)) for j in range(12)]
    valid_notes.append("Pause")
    TransPitches = {note: i for i, note in enumerate(valid_notes)}

# 默认配置
DEFAULT_CONFIG = {
    'key': 'C',           # 调性
    'seeds': 20,          # 初始种子数量
    'random': 10,         # 随机生成数量
}


def parse_config_line(line):
    """
    解析配置行
    
    格式: @参数名=值
    例如: @key=C, @seeds=20, @random=10
    """
    line = line.strip()
    if not line.startswith('@'):
        return None, None
    
    if '=' not in line:
        return None, None
    
    param, value = line[1:].split('=', 1)
    param = param.strip().lower()
    value = value.strip()
    
    return param, value


def parse_melody_string(melody_str):
    """
    解析旋律字符串，转换为 (pitch_list, beat_list)
    
    输入格式：每行一个音符，格式为 "音名 时值"
    例如：
        C4 12
        E4 12
        G4 24
    
    音名：C1-B7, #C1-#A7, Pause
    时值：6=八分, 12=四分, 18=附点四分, 24=二分, 36=附点二分, 48=全音符
    """
    pitch_list = []
    beat_list = []
    
    lines = melody_str.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 跳过注释行（以 # 开头但不是音名如 #C4）
        if line.startswith('#') and (len(line) < 2 or not line[1].isalpha() or line[1] == ' '):
            continue
        
        parts = line.split()
        if len(parts) >= 2:
            note_name = parts[0]
            try:
                beat = int(parts[1])
            except ValueError:
                continue
            
            if note_name in TransPitches:
                pitch = TransPitches[note_name]
                pitch_list.append(pitch)
                beat_list.append(beat)
            else:
                print(f"警告：无效的音名 '{note_name}'，已跳过")
    
    return pitch_list, beat_list


def load_config_and_melodies(filepath):
    """
    从文件加载配置参数和用户旋律
    
    文件格式：
    1. 配置行（以@开头）：
       @key=C        调性（12个大调之一）
       @seeds=20     初始种子数量
       @random=10    随机生成数量
       
    2. 旋律片段用 "---" 分隔
    
    返回:
        (config, melodies) 元组
        - config: 配置字典
        - melodies: 旋律列表，每个元素为 (pitch_list, beat_list)
    """
    config = DEFAULT_CONFIG.copy()
    melodies = []
    
    if not os.path.exists(filepath):
        print(f"配置文件 {filepath} 不存在，使用默认配置")
        return config, melodies
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析配置行
    lines = content.split('\n')
    content_start = 0
    
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('@'):
            param, value = parse_config_line(line)
            if param == 'key':
                if value in Notes or value.upper() in ['C', '#C', 'D', '#D', 'E', 'F', '#F', 'G', '#G', 'A', '#A', 'B']:
                    config['key'] = value
                else:
                    print(f"警告：无效的调性 '{value}'，使用默认值 C")
            elif param == 'seeds':
                try:
                    config['seeds'] = int(value)
                except ValueError:
                    print(f"警告：无效的种子数 '{value}'")
            elif param == 'random':
                try:
                    config['random'] = int(value)
                except ValueError:
                    print(f"警告：无效的随机数 '{value}'")
            content_start = i + 1
        elif line and not line.startswith('#'):
            break
    
    # 解析旋律片段
    remaining_content = '\n'.join(lines[content_start:])
    fragments = remaining_content.split('---')
    
    for fragment in fragments:
        fragment = fragment.strip()
        if fragment:
            try:
                pitch_list, beat_list = parse_melody_string(fragment)
                if pitch_list and beat_list:
                    # 验证总时值
                    if sum(beat_list) == 192:
                        melodies.append((pitch_list, beat_list))
                    else:
                        print(f"警告：旋律片段时值总和为 {sum(beat_list)}，应为 192，已跳过")
            except Exception as e:
                print(f"警告：解析片段失败 - {e}")
    
    return config, melodies


def create_population_from_config(filepath, melody_creator):
    """
    根据配置文件创建初始种群
    
    参数:
        filepath: 配置文件路径
        melody_creator: 创建Melody对象的函数，签名为 (key, pitch, beat) -> Melody
    
    返回:
        (config, population) 元组
    """
    from zcs_melody import generate_melody
    
    config, user_melodies = load_config_and_melodies(filepath)
    
    key = config['key']
    seeds = config['seeds']
    random_count = config['random']
    custom_count = seeds - random_count
    
    population = []
    
    # 方法a：添加用户提供的旋律
    if user_melodies and custom_count > 0:
        actual_custom = min(custom_count, len(user_melodies))
        for i in range(actual_custom):
            pitch, beat = user_melodies[i % len(user_melodies)]
            melody = melody_creator(key, pitch.copy(), beat.copy())
            population.append(melody)
        print(f"已加载 {actual_custom} 个用户旋律（方法a）")
    
    # 方法b：随机生成剩余数量（使用调性约束）
    remaining = seeds - len(population)
    if remaining > 0:
        print(f"使用调性 {key} 生成随机旋律")
        for _ in range(remaining):
            _, pitch, beat = generate_melody(key=key, use_scale=True)
            melody = melody_creator(key, pitch, beat)
            population.append(melody)
        print(f"已随机生成 {remaining} 个旋律（方法b）")
    
    return config, population


# 导出的接口
__all__ = [
    'parse_melody_string', 'load_config_and_melodies', 
    'create_population_from_config', 'DEFAULT_CONFIG'
]
