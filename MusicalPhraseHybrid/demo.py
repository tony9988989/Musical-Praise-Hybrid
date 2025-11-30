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
    """生成初始个体：随机旋律（音域F3~G5，总时值240）"""
    key, pitch, beat = generate_melody(key=CURRENT_KEY, use_scale=True)
    return creator.Melody(key, pitch, beat)

def Get_Melody_Creator(key, pitch, beat):
    """工厂函数：从pitch/beat创建Melody对象"""
    return creator.Melody(key, pitch, beat)

toolbox.register("individual",Get_Melody)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


#-----Fitness-----
def evaluate_melody(melody):
    #Todo
    score=0
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
