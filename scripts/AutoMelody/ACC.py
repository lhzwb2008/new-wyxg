#!/usr/bin/python
# -*- coding: utf-8 -*-

import GLOBAL

def GetAccByChord(chord_str_list, acc_type_index, acc_vel):
    """ 根据和弦，生成简单的钢琴伴奏，长度1小节
        chord_str_list ： 含4个和弦
        acc_type_index ： 指定伴奏型    
    """
    note_list = []
    if acc_type_index == 0:
        """ 1. 每拍弹3下 """ 
        for i, chord_str in enumerate(chord_str_list):
            # 求出和弦内音
            pitch_list = GLOBAL.inChordPitchByChordStr(chord_str)
            # 生成弹奏音符: [音高，起始，长度，力度]
            note_left_list = [[x + 36, 16*i, 16, acc_vel] for x in pitch_list[:1]]   # 左手只弹奏根音
            note_right_list = [[x + 60, 16*i, 16, acc_vel]  for x in pitch_list]      # 右手
            note_list.extend(note_left_list + note_right_list) 
    elif acc_type_index == 1:
        """ 2. 每2拍弹3下 """ 
        for i, chord_str in enumerate(chord_str_list):
            if i%2 ==0:
                # 求出和弦内音
                pitch_list = GLOBAL.inChordPitchByChordStr(chord_str)
                # 生成弹奏音符: [音高，起始，长度，力度]
                note_left_list = [[x + 36, 16*i, 32, acc_vel] for x in pitch_list[:1]]   # 左手只弹奏根音
                note_right_list = [[x + 60, 16*i, 32, acc_vel]  for x in pitch_list]      # 右手
                note_list.extend(note_left_list + note_right_list)  
    elif acc_type_index == 2:
        """ 3. 分解，3131 """ 
        for i, chord_str in enumerate(chord_str_list):
            # 求出和弦内音
            pitch_list = GLOBAL.inChordPitchByChordStr(chord_str)
            if i%2 ==0:
                # 生成弹奏音符: [音高，起始，长度，力度]
                note_right_list = [[x + 60, 16*i, 16, acc_vel]  for x in pitch_list]      # 右手
                note_list.extend(note_right_list)  
            else:
                note_left_list = [[x + 48, 16*i, 16, acc_vel] for x in pitch_list[:1]]   # 左手只弹奏根音
                note_list.extend(note_left_list)  
    elif acc_type_index == 3:
        """ 3. 分解，1111 """
        for i, chord_str in enumerate(chord_str_list):
            # 求出和弦内音
            pitch_list = GLOBAL.inChordPitchByChordStr(chord_str)
            if i %2 ==0:
                # 生成弹奏音符: [音高，起始，长度，力度]
                pitch_list.sort()
                note_left_list = [[x + 48, 16*i, 8, acc_vel] for x in pitch_list[:1]]   # 左手只弹奏根音
                note_right_list = [[x + 60, 16*i + 8*(j+1), 8, acc_vel]  for j, x in enumerate(pitch_list)]      # 右手
                note_list.extend(note_left_list + note_right_list) 
    # 返回
    return note_list 
    
if __name__ == "__main__": 
    print GetAccByChord('#Cm')
    print GetAccByChord("Am")
    
