from Settings import Melody
import random
from deap import base, creator, tools, algorithms

# 导入zcs模块提供的变异操作 (by zcs)
from zcs_mutations import apply_mutation, MUTATION_STRATEGIES

mutation_strategies=[]

def Keep(individual:creator.Melody):
    return individual
mutation_strategies.append(Keep)


# 以下变异策略通过zcs_mutations模块实现 (by zcs)
def Transpose(individual:creator.Melody):
    """移调变异"""
    from zcs_mutations import transpose
    new_pitch, new_beat = transpose(individual.pitch, individual.beat)
    individual.pitch = new_pitch
    individual.beat = new_beat
    return individual
mutation_strategies.append(Transpose)


def Inversion(individual:creator.Melody):
    """倒影变异"""
    from zcs_mutations import inversion
    new_pitch, new_beat = inversion(individual.pitch, individual.beat)
    individual.pitch = new_pitch
    individual.beat = new_beat
    return individual
mutation_strategies.append(Inversion)


def Retrograde(individual:creator.Melody):
    """逆行变异"""
    from zcs_mutations import retrograde
    new_pitch, new_beat = retrograde(individual.pitch, individual.beat)
    individual.pitch = new_pitch
    individual.beat = new_beat
    return individual
mutation_strategies.append(Retrograde)


def ChangePitch(individual:creator.Melody):
    """音高微调变异"""
    from zcs_mutations import change_pitch
    new_pitch, new_beat = change_pitch(individual.pitch, individual.beat)
    individual.pitch = new_pitch
    individual.beat = new_beat
    return individual
mutation_strategies.append(ChangePitch)


def ChangeRhythm(individual:creator.Melody):
    """节奏微调变异"""
    from zcs_mutations import change_rhythm
    new_pitch, new_beat = change_rhythm(individual.pitch, individual.beat)
    individual.pitch = new_pitch
    individual.beat = new_beat
    return individual
mutation_strategies.append(ChangeRhythm)


def SplitNote(individual:creator.Melody):
    """音符分裂变异"""
    from zcs_mutations import split_note
    new_pitch, new_beat = split_note(individual.pitch, individual.beat)
    individual.pitch = new_pitch
    individual.beat = new_beat
    return individual
mutation_strategies.append(SplitNote)


def MergeNotes(individual:creator.Melody):
    """音符合并变异"""
    from zcs_mutations import merge_notes
    new_pitch, new_beat = merge_notes(individual.pitch, individual.beat)
    individual.pitch = new_pitch
    individual.beat = new_beat
    return individual
mutation_strategies.append(MergeNotes)


def melody_mutation(individual:creator.Melody,indpb=0.1):
    strategy=mutation_strategies[random.randint(0,len(mutation_strategies)-1)]
    individual=strategy(individual)
    assert isinstance(individual , creator.Melody),"Invalid Mutational Function"
    return (individual,)