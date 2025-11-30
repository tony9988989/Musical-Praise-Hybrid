from Settings import Melody
import random
from deap import base, creator, tools, algorithms
mutation_strategies=[]
def Keep(individual:creator.Melody):
    return individual
mutation_strategies.append(Keep)
#Todo
def melody_mutation(individual:creator.Melody,indpb=0.1):
    strategy=mutation_strategies[random.randint(0,len(mutation_strategies)-1)]
    individual=strategy(individual)
    assert isinstance(individual , creator.Melody),"Invalid Mutational Function"
    return (individual,)