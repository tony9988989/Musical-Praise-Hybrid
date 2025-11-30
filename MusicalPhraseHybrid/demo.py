import random
import numpy as np
from deap import base, creator, tools, algorithms
from Settings import Melody

#-------Basic Deap settings-------
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Melody", Melody, fitness=creator.FitnessMax)
toolbox = base.Toolbox()

#-------Create Gene------
def Get_Melody():
    #Todo
    pitch=[77]
    beat=[240]
    return creator.Melody(pitch, beat)
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

