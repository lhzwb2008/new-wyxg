#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
 
# 和弦list的个数
CHORD_COUNT = 26

# 主歌和弦走向
CHORD_ZHUGE_4_LIST = [ ('C', 'C', 'C', 'C', 'F', 'F', 'F', 'F', 'G', 'G', 'G', 'G', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'F', 'F', 'F', 'F', 'G', 'G', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('C', 'C', 'C', 'C', 'Dm', 'Dm', 'Dm', 'Dm', 'G', 'G', 'G', 'G', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'Dm', 'Dm', 'Dm', 'Dm', 'G', 'G', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'Dm', 'Dm', 'E', 'E', 'E', 'E', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'Dm', 'Dm', 'E', 'E', 'E', 'E', 'Am', 'Am', 'Am', 'Am'),
                                    ('Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'Dm', 'Dm', 'G', 'G', 'G', 'G', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'Dm', 'Dm', 'G', 'G', 'G', 'G', 'Am', 'Am', 'Am', 'Am'),
                                    ('C', 'C', 'G', 'G', 'Am', 'Am', 'Am', 'Am', 'F', 'F', 'C', 'C', 'Dm', 'Dm', 'G', 'G', 'C', 'C', 'Em', 'Em', 'Am', 'Am', 'Am', 'Am', 'F', 'F', 'G', 'G', 'C', 'C', 'C', 'C'),
                                    ('C', 'C', 'C', 'C', 'G', 'G', 'Em', 'Em', 'Am', 'Am', 'Am', 'Am', 'Em', 'Em', 'Em', 'Em', 'F', 'F', 'G', 'G', 'Em', 'Em', 'Am', 'Am', 'F', 'F', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('C', 'C', 'C', 'C', 'G', 'G', 'G', 'G', 'Am', 'Am', 'Am', 'Am', 'Em', 'Em', 'Em', 'Em', 'F', 'F', 'F', 'F', 'C', 'C', 'Am', 'Am', 'Dm', 'Dm', 'Dm', 'Dm', 'G', 'G', 'G', 'G'), 
                                    ('C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'Dm', 'Dm', 'Dm', 'Dm', 'Dm', 'Dm', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'), 
                                    ('C', 'C', 'G', 'G', 'Am', 'Am', 'Am', 'Am', 'F', 'F', 'F', 'F', 'G', 'G', 'G', 'G', 'F', 'F', 'G', 'G', 'C', 'G', 'Am', 'Am', 'F', 'F', 'G', 'G', 'C', 'C', 'C', 'C'),
                                    ('C', 'C', 'C', 'C', 'Em', 'Em', 'Em', 'Em', 'C', 'C', 'C', 'C', 'Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'Dm', 'Dm', 'G', 'G', 'G', 'G', 'C', 'C', 'C', 'C', 'G', 'G', 'G', 'G'), 
                                    ('C', 'C', 'G', 'G', 'F', 'F', 'C', 'C', 'F', 'F', 'C', 'C', 'Dm', 'Dm', 'G', 'G', 'C', 'C', 'G', 'G', 'F', 'F', 'F', 'F', 'C', 'C', 'Am', 'Am', 'Dm', 'Dm', 'G', 'G'), 
                                    ('C', 'C', 'C', 'C', 'Am', 'Am', 'Am', 'Am', 'G', 'G', 'G', 'G', 'Em', 'Em', 'Em', 'Em', 'Am', 'Am', 'Am', 'Am', 'F', 'F', 'F', 'F', 'Dm', 'Dm', 'Dm', 'Dm', 'G', 'G', 'G', 'G'), 
                                    ('C', 'C', 'G', 'G', 'F', 'F', 'Am', 'Am', 'F', 'F', 'G', 'G', 'F', 'F', 'G', 'G', 'C', 'C', 'G', 'G', 'F', 'F', 'Am', 'Am', 'F', 'F', 'G', 'G', 'F', 'F', 'G', 'G'), 
                                    ('C', 'C', 'Am', 'Am', 'G', 'G', 'Em', 'Em', 'Am', 'Am', 'F', 'F', 'G', 'G', 'C', 'C', 'C', 'C', 'Am', 'Am', 'G', 'G', 'Em', 'Em', 'Am', 'Am', 'F', 'F', 'G', 'G', 'C', 'C'), 
                                    ('C', 'C', 'C', 'C', 'Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'Dm', 'Dm', 'G', 'G', 'G', 'G', 'Em', 'Em', 'Em', 'Em', 'Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'Dm', 'Dm', 'G', 'G', 'G', 'G'), 
                                    ('C', 'C', 'C', 'C', 'Am', 'Am', 'Am', 'Am', 'F', 'F', 'F', 'F', 'G', 'G', 'G', 'G', 'Em', 'Em', 'Em', 'Em', 'Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('C', 'C', 'G', 'G', 'C', 'C', 'C', 'C', 'F', 'F', 'Dm', 'Dm', 'G', 'G', 'G', 'G', 'C', 'C', 'G', 'G', 'C', 'C', 'C', 'C', 'F', 'F', 'Dm', 'Dm', 'G', 'G', 'G', 'G'), 
                                    ('C', 'C', 'C', 'C', 'Am', 'Am', 'Am', 'Am', 'F', 'F', 'C', 'C', 'Dm', 'Dm', 'G', 'G', 'Am', 'Am', 'Am', 'Am', 'F', 'F', 'C', 'C', 'Dm', 'Dm', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('Am', 'Am', 'Am', 'Am', 'C', 'C', 'C', 'C', 'Em', 'Em', 'Em', 'Em', 'G', 'G', 'G', 'G', 'Am', 'Am', 'Am', 'Am', 'C', 'C', 'C', 'C', 'G', 'G', 'G', 'G', 'Dm', 'Dm', 'Dm', 'Dm'), 
                                    ('Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'Am', 'Am', 'C', 'C', 'G', 'G', 'Am', 'Am', 'Am', 'Am', 'C', 'C', 'G', 'G', 'Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('C', 'C', 'C', 'C', 'Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'Dm', 'Dm', 'G', 'G', 'G', 'G', 'Em', 'Em', 'Em', 'Em', 'Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('Am', 'Am', 'Em', 'Em', 'Am', 'Am', 'Am', 'Am', 'G', 'G', 'G', 'G', 'C', 'C', 'C', 'C', 'F', 'Dm', 'C', 'C', 'G', 'G', 'Am', 'Am', 'Em', 'Em', 'Em', 'Em', 'Am', 'Am', 'Am', 'Am'), 
                                    ('Am', 'Am', 'Am', 'Am', 'Em', 'Em', 'Em', 'Em', 'Dm', 'Dm', 'Dm', 'Dm', 'C', 'C', 'C', 'C', 'Dm', 'Dm', 'Dm', 'Dm', 'Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'Em', 'Em', 'Am', 'Am', 'Am', 'Am'), 
                                    ('C', 'C', 'Am', 'Am', 'Dm', 'Dm', 'Dm', 'Dm', 'F', 'F', 'G', 'G', 'C', 'C', 'C', 'C', 'C', 'C', 'Am', 'Am', 'Dm', 'Dm', 'Dm', 'Dm', 'F', 'F', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('C', 'C', 'C', 'C', 'Am', 'Am', 'Am', 'Am', 'F', 'F', 'F', 'F', 'G', 'G', 'G', 'G', 'Am', 'Am', 'Em', 'Em', 'Am', 'Am', 'Em', 'Em', 'F', 'F', 'F', 'F', 'G', 'G', 'G', 'G'), 
                                    ('C', 'C', 'G', 'G', 'C', 'C', 'Am', 'Am', 'F', 'F', 'C', 'C', 'G', 'G', 'G', 'G', 'C', 'C', 'F', 'F', 'Am', 'Am', 'Em', 'Em', 'C', 'C', 'Em', 'Em', 'Am', 'Am', 'Am', 'Am'), 
                                  ]

# 副歌和弦走向 
CHORD_FUGE_4_LIST = [ ('C', 'C', 'C', 'C', 'F', 'F', 'F', 'F', 'G', 'G', 'G', 'G', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'F', 'F', 'F', 'F', 'G', 'G', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('C', 'C', 'C', 'C', 'Dm', 'Dm', 'Dm', 'Dm', 'G', 'G', 'G', 'G', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'Dm', 'Dm', 'Dm', 'Dm', 'G', 'G', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'Dm', 'Dm', 'E', 'E', 'E', 'E', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'Dm', 'Dm', 'E', 'E', 'E', 'E', 'Am', 'Am', 'Am', 'Am'),
                                    ('Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'Dm', 'Dm', 'G', 'G', 'G', 'G', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'Dm', 'Dm', 'G', 'G', 'G', 'G', 'Am', 'Am', 'Am', 'Am'),
                                    ('F', 'F', 'G', 'G', 'Em', 'Em', 'Am', 'Am', 'F', 'F', 'G', 'G', 'C', 'C', 'C', 'C', 'F', 'F', 'G', 'G', 'Em', 'Em', 'Am', 'Am', 'F', 'F', 'G', 'G', 'C', 'C', 'C', 'C'),
                                    ('C', 'C', 'C', 'C', 'G', 'G', 'Em', 'Em', 'Am', 'Am', 'Am', 'Am', 'F', 'F', 'F', 'F', 'F', 'F', 'Em', 'Em', 'Em', 'Em', 'Am', 'Am', 'Dm', 'Dm', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('C', 'C', 'G', 'G', 'Em', 'Em', 'Am', 'Am', 'F', 'F', 'F', 'F', 'G', 'G', 'G', 'G', 'C', 'C', 'G', 'G', 'Em', 'Em', 'Am', 'Am', 'F', 'F', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('C', 'C', 'C', 'C', 'Am', 'Am', 'Am', 'Am', 'Em', 'Em', 'Em', 'Em', 'Am', 'Am', 'Am', 'Am', 'F', 'F', 'F', 'F', 'Em', 'Em', 'Em', 'Em', 'Am', 'Am', 'Em', 'Em', 'C', 'C', 'C', 'C'), 
                                    ('F', 'F', 'G', 'G', 'Em', 'Em', 'Am', 'Am', 'F', 'F', 'G', 'G', 'C', 'C', 'C', 'C', 'F', 'F', 'G', 'G', 'Em', 'Em', 'Am', 'Am', 'F', 'F', 'G', 'G', 'C', 'C', 'C', 'C'),
                                    ('C', 'C', 'Em', 'Em', 'Am', 'Am', 'G', 'G', 'Dm', 'Dm', 'G', 'G', 'C', 'C', 'C', 'C', 'Em', 'Em', 'Em', 'Em', 'Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('C', 'C', 'G', 'G', 'F', 'F', 'C', 'C', 'C', 'C', 'Am', 'Am', 'Dm', 'Dm', 'G', 'G', 'C', 'C', 'G', 'G', 'F', 'F', 'C', 'C', 'C', 'C', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('Am', 'Am', 'G', 'G', 'Em', 'Em', 'Am', 'Am', 'Dm', 'Dm', 'G', 'G', 'C', 'C', 'C', 'C', 'Am', 'Am', 'G', 'G', 'Em', 'Em', 'Am', 'Am', 'Dm', 'Dm', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('F', 'F', 'Am', 'Am', 'Dm', 'Dm', 'G', 'G', 'C', 'C', 'Am', 'Am', 'Dm', 'Dm', 'G', 'G', 'F', 'F', 'Am', 'Am', 'Dm', 'Dm', 'G', 'G', 'C', 'C', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('Am', 'Am', 'G', 'G', 'Am', 'Am', 'G', 'G', 'Em', 'Em', 'Am', 'Am', 'F', 'F', 'G', 'G', 'Am', 'Am', 'G', 'G', 'Am', 'Am', 'G', 'G', 'Em', 'Em', 'Am', 'Am', 'F', 'G', 'C', 'C'), 
                                    ('C', 'C', 'C', 'C', 'Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'Dm', 'Dm', 'G', 'G', 'G', 'G', 'Em', 'Em', 'Em', 'Em', 'Am', 'Am', 'Am', 'Am', 'Dm', 'Dm', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('C', 'C', 'C', 'C', 'Am', 'Am', 'Am', 'Am', 'F', 'F', 'F', 'F', 'G', 'G', 'G', 'G', 'C', 'C', 'C', 'C', 'Am', 'Am', 'Am', 'Am', 'F', 'F', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('Am', 'Am', 'G', 'G', 'F', 'F', 'G', 'G', 'Am', 'Am', 'G', 'G', 'F', 'F', 'G', 'G', 'Am', 'Am', 'G', 'G', 'F', 'F', 'G', 'G', 'Am', 'Am', 'G', 'G', 'F', 'G', 'C', 'C'), 
                                    ('C', 'C', 'Am', 'Am', 'F', 'F', 'Em', 'Em', 'Am', 'Am', 'Dm', 'Dm', 'G', 'G', 'G', 'G', 'C', 'C', 'Am', 'Am', 'F', 'F', 'Em', 'Em', 'Am', 'Am', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('Am', 'Am', 'Am', 'Am', 'C', 'C', 'C', 'C', 'Am', 'Am', 'Am', 'Am', 'G', 'G', 'G', 'G', 'Am', 'Am', 'Am', 'Am', 'C', 'C', 'C', 'C', 'Am', 'Am', 'G', 'G', 'Am', 'Am', 'Am', 'Am'), 
                                    ('F', 'F', 'F', 'F', 'C', 'C', 'C', 'C', 'F', 'F', 'F', 'F', 'C', 'C', 'C', 'C', 'F', 'F', 'G', 'G', 'C', 'G', 'Am', 'Am', 'Dm', 'Dm', 'Dm', 'Dm', 'G', 'G', 'C', 'C'), 
                                    ('Am', 'Am', 'Dm', 'Dm', 'Am', 'Am', 'Dm', 'Dm', 'Am', 'Am', 'Dm', 'Dm', 'G', 'G', 'G', 'G', 'Dm', 'Dm', 'Em', 'Em', 'Dm', 'Dm', 'Em', 'Em', 'Dm', 'Dm', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('C', 'C', 'G', 'G', 'C', 'C', 'C', 'C', 'G', 'G', 'G', 'G', 'C', 'C', 'C', 'C', 'F', 'Dm', 'C', 'C', 'F', 'Dm', 'C', 'C', 'Am', 'Am', 'Em', 'Em', 'Am', 'Am', 'Am', 'Am'), 
                                    ('Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'F', 'F', 'F', 'F', 'Em', 'Em', 'Em', 'Em', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am', 'Am'), 
                                    ('F', 'F', 'G', 'G', 'C', 'C', 'C', 'C', 'F', 'F', 'G', 'G', 'C', 'C', 'C', 'C', 'F', 'F', 'G', 'G', 'C', 'Em', 'Am', 'Am', 'Dm', 'Dm', 'G', 'G', 'C', 'C', 'C', 'C'), 
                                    ('C', 'C', 'G', 'G', 'Am', 'Am', 'Em', 'Em', 'F', 'F', 'Em', 'Em', 'F', 'F', 'G', 'G', 'C', 'C', 'G', 'G', 'Am', 'Am', 'Em', 'Em', 'F', 'F', 'Em', 'Em', 'F', 'G', 'C', 'C'), 
                                    ('C', 'C', 'G', 'G', 'C', 'C', 'Am', 'Am', 'F', 'F', 'C', 'C', 'G', 'G', 'G', 'G', 'C', 'C', 'F', 'F', 'Am', 'Am', 'Em', 'Em', 'C', 'C', 'Em', 'Em', 'Am', 'Am', 'Am', 'Am'), 
                                  ]
 
# 和弦对应的调式: C和弦开头的，为C大调(key=0, scale=0)；Am和弦开头的，为A小调( key=9, scale=1)
KEY_LIST = [0,0,9,9,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9,9,0,9,9,0,0,0]
SCALE_LIST = [0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,1,0,0,0]

# 大调和弦序号
MAJOR_INDEX_LIST = [0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 20, 23, 24, 25]
MINOR_INDEX_LIST = [2, 3, 18, 19, 21, 22]

""" 随机选择一个和弦 """
def GetAChord():
    chord_index = random.randint(0, CHORD_COUNT - 1)
    return chord_index

""" 随机选择一个和弦 - 大调"""
def GetAMajorChord():
    chord_index = random.choice(MAJOR_INDEX_LIST)
    return chord_index

""" 随机选择一个和弦 - 小调"""
def GetAMinorChord():
    chord_index = random.choice(MINOR_INDEX_LIST)
    return chord_index

""" 获取主歌的和弦 """
def GetChord4Zhuge(chord_index, sentence_count):
    # 检查和弦序号，不能超出范围
    if chord_index < 0 or chord_index >= CHORD_COUNT:
        return None
    
    if sentence_count== 4:
        # 4句，返回全部
        return CHORD_ZHUGE_4_LIST[chord_index]
    elif sentence_count == 2:
        # 2句，掐头去尾(前面2小节+后面2小节)
        return CHORD_ZHUGE_4_LIST[chord_index][:8] +  CHORD_ZHUGE_4_LIST[chord_index][-8:]
    elif sentence_count == 1:
        # 1句，返回前面2小节
        return CHORD_ZHUGE_4_LIST[chord_index][:8]
    elif sentence_count == 8:
        return CHORD_ZHUGE_4_LIST[chord_index]*2

    return None

""" 获取副歌的和弦 """
def GetChord4Fuge(chord_index, sentence_count):
    # 检查和弦序号，不能超出范围
    if chord_index < 0 or chord_index >= CHORD_COUNT:
        return None

    # 根据句数，分配和弦
    if sentence_count== 4:
        # 4句，返回全部
        return CHORD_FUGE_4_LIST[chord_index]
    elif sentence_count == 2:
        # 2句，掐头去尾(前面2小节+后面2小节)
        return CHORD_FUGE_4_LIST[chord_index][:8] +  CHORD_FUGE_4_LIST[chord_index][-8:]
    elif sentence_count == 1:
        # 1句，返回前面2小节
        return CHORD_FUGE_4_LIST[chord_index][:8]
    elif sentence_count == 8:
        return CHORD_FUGE_4_LIST[chord_index]*2
         
""" 获取和弦对应的调式信息 """
def GetKey(chord_index): 
    return KEY_LIST[chord_index]
    
def GetScale(chord_index): 
    return SCALE_LIST[chord_index]
     
