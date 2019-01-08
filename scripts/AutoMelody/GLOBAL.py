#!/usr/bin/python
# -*- coding: utf-8 -*-

# 每拍中的64分音符个数 （4分音符为1拍）
NOTE64_PER_BEAT = 16
CHORD_PER_BAR = 4
CHORD_PER_BEAT = 1
 
KEY_LIST = ("C", "#C", "D", "#D", "E", "F", "#F", "G", "#G", "A", "#A", "B")

CHORD_ROOT = ("C", "#C", "D", "#D", "E", "F", "#F", "G", "#G", "A", "#A", "B")
CHORD_TYPE = ("", "m", "m7", "7", "M7", "maj7")


# 和弦类型演奏音音
# 和弦内音
chord_type_in = ((0, 4, 7, 12, 16, 19),  #
                                 (0, 3, 7, 12, 15, 19),   # m
                                 (0, 3, 7, 10, ),   # m7
                                 (0, 4, 7, 10, ),   # 7
                                 (0, 4, 7, 11, ),   # M7
                                 (0, 4, 7, 11, ),   # maj7 
                    )   

# 调式  : 必须两个音高【0-24】
scale_content = ((0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23), (0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22),
                        )  
     
     
"""  转换key：'C'->0  'D'->1... """
def keyStr2KeyIndex( key_str ):
    try:
        return KEY_LIST.index(key_str)
    except:
        # wrong key_str
        return -1
    
"""  转换chord：'C'->(0,0)  'Dm'->(1,1) """
def chordStr2RootAndType(chord_str):
    try:
        if chord_str.startswith('#'):
            if len(chord_str)>=3:
                root=CHORD_ROOT.index(chord_str[0:2])
                type=CHORD_TYPE.index(chord_str[2:])
            else:
                root=CHORD_ROOT.index(chord_str)
                type=0
        else:
            if len(chord_str)>=2:
                root=CHORD_ROOT.index(chord_str[0:1])
                type=CHORD_TYPE.index(chord_str[1:])
            else :
                root=CHORD_ROOT.index(chord_str)
                type=0
        return root, type
    except :
        return -1
        
""" 求和弦内音 (1,2,3音~4 5 6音)  count为取得级数"""
def inChordPitchByChordStr(chord_str, count = 6):  
    root, type = chordStr2RootAndType(chord_str)
    return inChordPitchByChordRootType(root, type, count)
    
""" 求和弦内音 (1,2,3音~4 5 6音) """
def inChordPitchByChordRootType(root, type, count = 6): 
    in_chord_list = []
    for x in chord_type_in[type][:count]:
        if (root + x)%12 not in in_chord_list:
            in_chord_list.append((root + x)%12)
    return in_chord_list
    
""" 求调内音 （一个八度内）"""
def getPitch12InScale(scale_index, key_index, need_sort = False):
    pitch_12_list = []
    # 循环scale内音，根据key升降调
    for midi_no in scale_content[scale_index]:
        shift_midi_no = (midi_no + key_index)%12
        if shift_midi_no not in pitch_12_list:
            pitch_12_list.append(shift_midi_no)
    
    # 需要sort?
    if need_sort:
        pitch_12_list.sort()

    return pitch_12_list
    
if __name__ == "__main__": 
    print chordStr2RootAndType('#Cm')
    print inChordPitchByChordStr("Am")
    print getPitch12InScale(0, 0)
    print getPitch12InScale(1, 9) 
