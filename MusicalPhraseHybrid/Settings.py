from deap import base
#-------Basic identifications--------
Notes=["C","#C","D","#D","E","F","#F","G","#G","A","#A","B"]
valid_notes=[]

MELODY_LENGTH=240
for i in range(1,8):
    valid_notes+=[str(Notes[j]+str(i)) for j in range(12)]
valid_notes.append("Pause")
TransPitches=dict([])
for i in range(len(valid_notes)):
    TransPitches[valid_notes[i]]=i

class Melody:
    def __init__(self,key,pitch,beat):
        assert sum(beat)==240,"invalid melody"#Quarter note=12
        assert len(pitch)==len(beat),"invalid melody"
        assert max(pitch)<len(valid_notes) and min(pitch)>=0,"invalid melody"
        assert key in Notes,"invalid melody"
        self.pitch=pitch
        self.beat=beat
        self.key=key
    def __repr__(self):
        c="{\n"
        for i in range(len(self.pitch)):
            c+=valid_notes[self.pitch[i]]+" "+str(self.beat[i])+"\n"
        c+="}"
        return c

