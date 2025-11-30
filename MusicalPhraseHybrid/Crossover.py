from Settings import Melody
import random
from deap import base, creator, tools, algorithms
def GetChild(parent1:Melody,parent2:Melody):
    #Todo
    child1=creator.Melody([77],[240])
    child2=creator.Melody([77],[240])
    assert isinstance(child1 , creator.Melody) and isinstance(child2 , creator.Melody),"Invalid Crossover Function"
    return child1,child2