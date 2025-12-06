import random
import numpy as np
from deap import base, creator, tools, algorithms
from Settings import Melody

#-------Basic Deap settings-------
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Melody", Melody, fitness=creator.FitnessMax)
toolbox = base.Toolbox()

#-------Create Gene------
# 导入zcs模块提供的初始种群生成功能 (by zcs)
from zcs_melody import generate_melody
from zcs_config import load_config_and_melodies, create_population_from_config

# === 配置模式选择 (by zcs) ===
# True = 从配置文件读取（自定义旋律+随机生成）
# False = 纯随机生成
USE_CONFIG_FILE = True
CONFIG_FILE_PATH = "melodies.txt"

# 全局调性设置（从配置加载后更新）
CURRENT_KEY = "C"

def Get_Melody():
    """生成初始个体：随机旋律（音域F3~G5，总时值192）"""
    key, pitch, beat = generate_melody(key=CURRENT_KEY, use_scale=True)
    return creator.Melody(key, pitch, beat)

def Get_Melody_Creator(key, pitch, beat):
    """工厂函数：从pitch/beat创建Melody对象"""
    return creator.Melody(key, pitch, beat)

toolbox.register("individual",Get_Melody)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


#-----Fitness-----
from Settings import Notes  # 需要引用 Notes 来确定调性主音索引
import statistics
import math

def evaluate_melody(melody):
    """
    空拍现在还没加，我暂时认为作为“None”存在pitch列表中了
    """
    if not melody.pitch or not melody.beat:
        return (0,)

    score = 0.0
    pitches = melody.pitch
    beats = melody.beat
    key = melody.key

    if key not in Notes:
        offset = 0 
    else:
        offset = Notes.index(key)
    normalized_noNone = []
    normalized = []
    for p in pitches:
        if p is None:
            normalized.append(None)
        else:
            normalized.append((p - offset) % 12)
    for i in range(len(normalized)): # normalized:
        normalized_noNone.append(normalized[i])
        if normalized[i] is None:
            if i==0:
                normalized_noNone[-1] = 0  # 空拍开头用主音代替计算
            else:
                normalized_noNone[-1] = normalized_noNone[-2]  # 空拍用前一个音代替计算
    
    # 音区范围
    pitch_range = max(normalized_noNone) - min(normalized_noNone)
    if pitch_range > 24:
        score -= (pitch_range - 18) ** 2
    else:
        score += (pitch_range)

    # 不要太跳跃也不要太无聊
    jump = []
    jump_list = [0,1.0,1.0,1.5,3.0,4.0,6.0,6.0,8.0,8.0,8.0,8.0]
    stable_list = [10.0,-30.0,4.0,-30.0,5.0,1.0,-30.0,8.0,-30.0,3.0,-30.0,0.0]

    for i in range(len(normalized_noNone) - 1):
        interval = abs(normalized_noNone[i+1] - normalized_noNone[i])
        if interval < len(jump_list):
            jump.append(jump_list[interval])
        else:
            jump.append(20.0)
        
    score -= ((sum(jump) - 20.0)/math.sqrt(len(jump))) ** 2
    score -= statistics.stdev(jump) ** 2

    # 总音符数在一个范围内
    note_count = len([p for p in pitches if p is not None])
    if note_count < 16:
        score -= (16 - note_count) ** 2
    elif note_count > 48:
        score -= (note_count - 48) ** 2
    else:
        score += note_count * 2.0
    
    # 总pause时长在一个范围内
    pause_duration = sum([beats[i] for i in range(len(pitches)) if pitches[i] is None])
    if pause_duration < 24:
        score -= (24 - pause_duration) ** 2
    elif pause_duration > 96:
        score -= (pause_duration - 96) ** 2
    else:
        score += (96 - pause_duration) * 0.5

    # 连唱超过3个音符奖励，但连唱超过一小节惩罚
    consec_count = 0
    consec_duration = 0.0
    for i in range(len(pitches)):
        if pitches[i] is not None:
            consec_count +=1
            consec_duration += beats[i]
        else:
            if consec_count >=4:
                score += (consec_count -3) *5.0
            if consec_duration > 48.0:
                score -= ((consec_duration - 48.0) * 0.2) **2
            consec_count =0
            consec_duration = 0.0

    # 连续pause超过两拍，惩罚
    pause_duration = 0
    for i in range(len(pitches)):
        if pitches[i] is None:
            pause_duration += beats[i]
        else:
            if pause_duration >= 24.0:
                score -= ((pause_duration -24.0) * 0.2) ** 2.0
            pause_duration =0
    # 长停留音应较稳定
    for i in range(len(normalized)):
        if normalized[i] is None:
            continue
        if beats[i] >= 24.0:
            score += stable_list[normalized[i] % 12] * (beats[i] / 6.0)
        elif stable_list[normalized[i] % 12] < 0:
            score += stable_list[normalized[i] % 12] * (beats[i] / 6.0)
    
    # 奖励结尾落在主\属音上
    if normalized_noNone[-1] == 0:
        score += 10.0
    elif normalized_noNone[-1] == 7:
        score += 5.0

    # 奖励结尾为长音
    if beats[-1] >= 12.0:
        score += 10.0

    # 奖励每两个小节结尾为空拍

    sum_beats=0.0
    for i in range(len(normalized)):
        if sum_beats + beats[i] >= 96.0 and sum_beats < 96.0 or sum_beats + beats[i] >= 192.0 and sum_beats < 192.0:
            if normalized[i] is None:
                score += 20.0
        sum_beats += beats[i]

    # 奖励不同小节的节奏相似性
    # todo

    # 奖励不同小节具有相同的前缀节奏和旋律
    # todo


    return (score,)


#-----Crossover and Mutation_____
from Crossover import GetChild
from Mutations import melody_mutation


# --- 6. 注册所有操作到工具箱 ---
toolbox.register("evaluate", evaluate_melody)
toolbox.register("mate", GetChild)
toolbox.register("mutate", melody_mutation, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)


# === 创建初始种群 (by zcs) ===
if USE_CONFIG_FILE:
    # 从配置文件加载：支持自定义旋律 + 随机生成
    try:
        config, population = create_population_from_config(
            CONFIG_FILE_PATH, 
            Get_Melody_Creator
        )
        CURRENT_KEY = config['key']
        print(f"\n=== 配置信息 ===")
        print(f"调性: {CURRENT_KEY}")
        print(f"种群大小: {len(population)}")
        print(f"================\n")
    except Exception as e:
        print(f"配置加载失败: {e}，使用默认随机生成")
        population = toolbox.population(n=200)
else:
    # 纯随机生成
    population = toolbox.population(n=200)


hof = tools.HallOfFame(1)


stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("max", np.max)


algorithms.eaSimple(population, toolbox, cxpb=0.7, mutpb=0.2, ngen=50,
                        stats=stats, halloffame=hof, verbose=True)

best_melody = hof[0]
print("\n--- Best Melody ---")
print(best_melody)
