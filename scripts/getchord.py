import sys
from AutoMelody.CHORD import *
chord_type = int(sys.argv[1])
chord_index = 0
if chord_type == 0:
    chord_index = GetAMajorChord()
elif chord_type == 1:
    chord_index = GetAMinorChord()
else:
    chord_index = GetAChord()
print chord_index
