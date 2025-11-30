import random
import numpy as np
from deap import base, creator, tools, algorithms
from Settings import Melody

#-------Basic Deap settings-------
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Melody", Melody, fitness=creator.FitnessMax)
toolbox = base.Toolbox()

#-------Create Gene------
PITCH_MIN, PITCH_MAX = 26, 50  # 音域：F3 ~ G5
BEAT_UNIT = 6                   # 最小时值：八分音符
VALID_BEATS = [6, 12, 18, 24, 36, 48]
MELODY_LENGTH = 240

def Get_Melody():
    """生成初始个体：随机旋律（音域F3~G5，总时值240）"""
    pitch_list = []
    beat_list = []
    remaining = MELODY_LENGTH
    
    while remaining > 0:
        available_beats = [b for b in VALID_BEATS if b <= remaining]
        if not available_beats:
            if remaining >= BEAT_UNIT:
                beat = remaining
            else:
                break
        else:
            beat = random.choice(available_beats)
        
        pitch = random.randint(PITCH_MIN, PITCH_MAX)
        
        pitch_list.append(pitch)
        beat_list.append(beat)
        remaining -= beat
    
    return creator.Melody(pitch_list, beat_list)
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

