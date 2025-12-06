from deap import base
#-------Basic identifications--------
Notes=["C","#C","D","#D","E","F","#F","G","#G","A","#A","B"]
valid_notes=[]
KEY_SCALE_MAP = {
    "C": [0, 2, 4, 5, 7, 9, 11],
    "#C": [1, 3, 5, 6, 8, 10, 0],
    "D": [2, 4, 6, 7, 9, 11, 1],
    "#D": [3, 5, 7, 8, 10, 0, 2],
    "E": [4, 6, 8, 9, 11, 1, 3],
    "F": [5, 7, 9, 10, 0, 2, 4],
    "#F": [6, 8, 10, 11, 1, 3, 5],
    "G": [7, 9, 11, 0, 2, 4, 6],
    "#G": [8, 10, 0, 1, 3, 5, 7],
    "A": [9, 11, 1, 2, 4, 6, 8],
    "#A": [10, 0, 2, 3, 5, 7, 9],
    "B": [11, 1, 3, 4, 6, 8, 10]
}
MELODY_LENGTH=192
for i in range(1,8):
    valid_notes+=[str(Notes[j]+str(i)) for j in range(12)]
valid_notes.append("Pause")
TransPitches=dict([])
for i in range(len(valid_notes)):
    TransPitches[valid_notes[i]]=i

class Melody:
    def __init__(self,key,pitch,beat):
        assert sum(beat)==MELODY_LENGTH,"invalid melody"#Quarter note=12
        assert len(pitch)==len(beat),"invalid melody"
        #assert max(pitch)<len(valid_notes) and min(pitch)>=0,"invalid melody" #这里pitch中允许None表示空拍，要检查的话要改一改
        assert key in Notes,"invalid melody"
        self.pitch=pitch
        self.beat=beat
        self.key=key
    def __repr__(self):
        c="{\n"
        for i in range(len(self.pitch)):
            if self.pitch[i] is None:
                c+="Pause "+str(self.beat[i])+"\n"
            else:
                c+=valid_notes[self.pitch[i]]+" "+str(self.beat[i])+"\n"
        c+="}"
        return c



