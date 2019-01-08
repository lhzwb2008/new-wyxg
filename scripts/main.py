#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time
import sys
import random
from AutoMelody import AutoMelody
from AutoMelody.CHORD import *
      
IS_DEBUG = True

## 错误代码
ERROR_CODE = 10000
ERROR_ZHUGE_SENTENCE_COUNT = 10001     # ‘主歌歌词的句数’参数，超出取值范围
ERROR_FUGE_SENTENCE_COUNT = 10002       # ‘副歌歌词的句数’参数，超出取值范围
ERROR_ZHUGE_NOTE_NUM_TYPE = 10003       # ‘主歌每句歌词的字数’参数的类型错误，必须为数组或者-1
ERROR_ZHUGE_NOTE_NUM_LENGTH = 10004       # ‘主歌每句歌词的字数’参数的长度与指定的主歌歌词句数不一致
ERROR_ZHUGE_NOTE_NUM_VALUE = 10005       # ‘主歌每句歌词的字数’参数，超出取值范围
ERROR_FUGE_NOTE_NUM_TYPE = 10006         # ‘副歌每句歌词的字数’参数的类型错误，必须为数组或者-1
ERROR_FUGE_NOTE_NUM_LENGTH = 10007       # ‘副歌每句歌词的字数’参数的长度与指定的副歌歌词句数不一致
ERROR_FUGE_NOTE_NUM_VALUE = 10008       # ‘副歌每句歌词的字数’参数，超出取值范围
ERROR_HAS_WEAK_START = 10009                # '是否需要弱起'参数，超出取值范围
ERROR_WEAK_BEAT_COUNT = 10010             # '弱起长度'参数，超出取值范围
ERROR_BPM_FLOAT_VALUE = 10011             # '曲速'参数，取值错误
ERROR_CHORD_INDEX = 10012                  # '和弦序号'参数，错误
ERROR_MIDI_PATH = 10013                      # '输出midi路径'参数，错误 


def do(  zhuge_sentence_count = -1,           # 主歌的歌词句数(1句=2小节)：取值范围(0,1,2, 4), -1表示随机
            fuge_sentence_count = -1,           # 副歌的歌词句数(1句=2小节)：取值范围(0,1,2,4), -1表示随机
            zhuge_note_num_list = -1,            # 主歌每句歌词的字数数组：取值范围(2~13), 数组长度需与zhuge_sentence_count相同，-1表示随机
            fuge_note_num_list = -1,              # 副歌每句歌词的字数数组：取值范围(2~13), 数组长度需与fuge_sentence_count相同， -1表示随机
            has_weak_start = -1,                  # 是否有弱起，取值范围(0,1), -1表示随机
            weak_beat_count = -1,               # 弱起的长度(拍数)，取值范围(0,1,2), -1表示随机, 此参数仅在has_weak_start==1的情况下有效
            bpm_float = 120,                         # 曲速，取值范围(60~160), -1表示随机
            chord_index = -1,                       # 指定和弦的序号，-1表示随机
            midi_path = "out.mid",               # midi输出路径 
            is_only_melody = 0,                   # 是否只导出旋律midi : 0=只导出旋律， 1=导出旋律+伴奏， 2=导出旋律+伴奏 2个midi
            chord_type = 0,                       # 和弦类型指定：-1=随机，0=大调随机，1=小调随机。此参数仅在chord_index=-1时有效。
            bpm_min = 60,                           # 曲速的范围，最小值。此参数仅在bpm_float=-1时有效。
            bpm_max = 160,                        # 曲速的范围，最大值。此参数仅在bpm_float=-1时有效。
            melody_instru_index = 73,          # 主旋律乐器指定：0~128
            acc_instru_index = 0,                # 伴奏乐器指定：0~128
            acc_type_A_index = 0,                # 主歌伴奏型指定：0~3
            acc_type_B_index = 0,                # 副歌伴奏型指定：0~3
            melody_vel = 120,                      # 旋律音符的力度：0~127
            acc_vel = 60,                             # 伴奏音符的力度：0~127
            melody_range_a = [47,61],
            melody_range_b = [47,65],
            ) :                    
    """  
    说明：负责调用作曲模块，同时保证模块的输入参数是合法的
    参数:  见上
    步骤：
        1. 分析输入参数，初始化变量，调用作曲模块；
        2. 作曲模块根据输入，生成一段主旋律；
        3. 将主旋律导出为midi文件。
    """ 
    ### 1、分析输入参数，初始化变量，调用作曲模块
    logMessage("=========== 1. Start analyze parameters ==============")
    
    # ---------------------- 1.1 分析主歌的句数 ---------------------- 
    if zhuge_sentence_count not in (-1, 0, 1, 2, 4, 8):
        logMessage(u"错误：主歌句数取值范围为：(-1, 0, 1, 2, 4)，其中-1代表随机，您的输入为：%d"%zhuge_sentence_count)
        return ERROR_ZHUGE_SENTENCE_COUNT
    
    # 如果主歌句数为-1，则随机
    if zhuge_sentence_count == -1:
        zhuge_sentence_count = random.choice((0, 1, 2, 4, 8))
    
    # ---------------------- 1.2 分析副歌的句数 ---------------------- 
    if fuge_sentence_count not in (-1, 0, 1, 2, 4, 8):
        logMessage(u"错误：副歌句数取值范围为：(-1, 0, 1, 2, 4)，其中-1代表随机，您的输入为：%d"%fuge_sentence_count)
        return ERROR_FUGE_SENTENCE_COUNT
    
    # 如果副歌句数为-1，
    if fuge_sentence_count == -1:
        fuge_sentence_count = random.choice((0, 1, 2, 4, 8))
    
    # ---------------------- 1.3 分析主歌的每句歌词数 ---------------------- 
    if zhuge_note_num_list != -1 and type(zhuge_note_num_list) != list:
        logMessage(u"错误：\'主歌每句歌词的字数\'这个变量必须为数组，或者输入-1命令系统进行随机，您的输入为：%s"%( str(zhuge_note_num_list)))
        return ERROR_ZHUGE_NOTE_NUM_TYPE
        
    # 如果需要随机，则随机
    if zhuge_note_num_list == -1:
        # 每句的歌词数都需要随机
        zhuge_note_num_list = []
        for i in xrange(zhuge_sentence_count):
            zhuge_note_num_list.append(random.randint(2, 13))
    
    # 检查每句歌词的字数是否都有指定
    if len(zhuge_note_num_list) != zhuge_sentence_count:
        logMessage(u"错误：\'主歌每句歌词的字数\'这个变量的数组长度与歌词句数不一致：%d != %d"%(len(zhuge_note_num_list), zhuge_sentence_count))
        return ERROR_ZHUGE_NOTE_NUM_LENGTH
        
    # 检查每句歌词的字数是否在取值范围内(2~13)， 如果是-1，需要随机
    for i in xrange(len(zhuge_note_num_list)):
        # 检查是否随机
        if zhuge_note_num_list[i] == -1:
            zhuge_note_num_list[i] = random.randint(2, 13)
        # 检查取值范围
        if zhuge_note_num_list[i] > 13 or zhuge_note_num_list[i] < 2:
            logMessage(u"错误：主歌第%d句的歌词字数为%d，超出取值范围(2 ~ 13) "%(i, zhuge_note_num_list[i]))
            return ERROR_ZHUGE_NOTE_NUM_VALUE
        
                
    # ---------------------- 1.4 分析副歌的每句歌词数 ---------------------- 
    if fuge_note_num_list != -1 and type(fuge_note_num_list) != list:
        logMessage(u"错误：\'副歌每句歌词的字数\'这个变量必须为数组，或者输入-1命令系统进行随机，您的输入为：%s"%( str(fuge_note_num_list)))
        return ERROR_FUGE_NOTE_NUM_TYPE
        
    # 如果需要随机，则随机
    if fuge_note_num_list == -1:
        # 每句的歌词数都需要随机
        fuge_note_num_list = []
        for i in xrange(fuge_sentence_count):
            fuge_note_num_list.append(random.randint(2, 13))
    
    # 检查每句歌词的字数是否都有指定
    if len(fuge_note_num_list) != fuge_sentence_count:
        logMessage(u"错误：\'副歌每句歌词的字数\'这个变量的数组长度与歌词句数不一致：%d != %d"%(len(fuge_note_num_list), fuge_sentence_count))
        return ERROR_FUGE_NOTE_NUM_LENGTH
        
    # 检查每句歌词的字数是否在取值范围内(2~13),  如果是-1，需要随机
    for i in xrange(len(fuge_note_num_list)):
        # 检查是否随机
        if fuge_note_num_list[i] == -1:
            fuge_note_num_list[i] = random.randint(2, 13)
        # 检查取值范围
        if fuge_note_num_list[i] > 13 or fuge_note_num_list[i] < 2:
            logMessage(u"错误：副歌第%d句的歌词字数为%d，超出取值范围(2 ~ 13) "%(i, fuge_note_num_list[i]))
            return ERROR_FUGE_NOTE_NUM_VALUE
        
    # ---------------------- 1.5 检查弱起参数 ---------------------- 
    if has_weak_start not in (-1, 0, 1):
        logMessage(u"错误：弱起的取值范围为：(-1, 0, 1)，其中-1代表随机，您的输入为：%d"%has_weak_start)
        return ERROR_HAS_WEAK_START
        
    # 如果需要随机，则随机
    if has_weak_start == -1:
        has_weak_start = random.choice((0, 1))
    
    # 如果需要弱起，检查弱起音符个数
    if has_weak_start == 1:
        if weak_beat_count not in (-1, 0, 1, 2 ):
            logMessage(u"错误：弱起长度的取值范围为：(-1,0,1,2 )，其中-1代表随机，您的输入为：%d"%weak_beat_count)
            return ERROR_WEAK_BEAT_COUNT
            
        # 如果需要随机，则随机
        if weak_beat_count == -1:
            weak_beat_count = random.choice((1, 2))
            
        # 如果此参数为0，则不需要弱起
        if weak_beat_count == 0:
            has_weak_start = 0
            
    # ---------------------- 1.6 检查曲速参数 ---------------------- 
    # 检查曲速是否需要随机
    if bpm_float == -1:
        bpm_float = random.randint(bpm_min, bpm_max)
        
    
    # ---------------------- 1.7 检查和弦序号参数 ---------------------- 
    # 检查和弦序号是否需要随机
    if chord_index == -1:
        if chord_type == 0:
            # 选出一个大调和弦
            chord_index = GetAMajorChord()
        elif chord_type == 1:
            # 选出一个小调和弦
            chord_index = GetAMinorChord()
        else:
            # 大小调均可
            chord_index = GetAChord()

        
    # 检查和弦序号取值范围
    if chord_index >= CHORD_COUNT or  chord_index < 0:
        logMessage(u"错误：和弦序号的取值范围为：(0 ~ %d)，其中-1代表随机，您的输入为：%d"%(CHORD_COUNT - 1, chord_index))
        return ERROR_CHORD_INDEX
     
    # ---------------------- 1.8 检查输出midi路径参数 ---------------------- 
    if not midi_path.endswith(".mid"):
        logMessage(u"错误：输出路径不合法，您的输入为：%s"%(midi_path))
        return ERROR_MIDI_PATH 
    
    if IS_DEBUG:
        print " Parameters:"
        print " > zhuge_sentence_count =", zhuge_sentence_count
        print " > fuge_sentence_count =", fuge_sentence_count
        print " > zhuge_note_num_list =", zhuge_note_num_list
        print " > fuge_note_num_list =", fuge_note_num_list
        print " > has_weak_start =", has_weak_start
        print " > weak_beat_count =", weak_beat_count
        print " > bpm_float =", bpm_float
        print " > chord_index =", chord_index
        print " > midi_path =", midi_path
        print " > is_only_melody =", is_only_melody
        print " > melody_instru_index =", melody_instru_index
        print " > acc_instru_index =", acc_instru_index
        print " > acc_type_A_index =", acc_type_A_index
        print " > acc_type_B_index =", acc_type_B_index
        print " > melody_vel =", melody_vel
        print " > acc_vel =", acc_vel
     
    ### 2、作曲模块根据输入，生成一段主旋律
    logMessage("=========== 2. Start make melody ==============" )
    # 创建实例
    am = AutoMelody.AutoMelody() 
    # 初始化
    am.initAM(zhuge_sentence_count, 
                    fuge_sentence_count, 
                    zhuge_note_num_list, 
                    fuge_note_num_list, 
                    has_weak_start, 
                    weak_beat_count, 
                    bpm_float, 
                    chord_index, 
                    midi_path, 
                    is_only_melody, 
                    melody_instru_index, 
                    acc_instru_index, 
                    acc_type_A_index, acc_type_B_index, 
                    melody_vel, acc_vel,
                    melody_range_a,melody_range_b
                    )
    # 开始作曲
    am.do() 
     
    ### 3、将主旋律导出为midi文件
    logMessage("=========== 3. Start export midi file ==============" )
    if is_only_melody == 0:
        # 只导出melody
        am.exportMidi()
    elif is_only_melody == 1:
        # 导出melody+acc
        am.exportMidi()
    else:
        # 导出2个midi
        am.exportMidiMelody()
        am.exportMidiAcc()
         
    ### 结束
    logMessage("=========== Done ==============" )
    
    return 1

def logMessage(message):
    """ 处理信息： 打印到控制台 """
    if IS_DEBUG: 
        print message 
    
if __name__ == "__main__":
    """ Main """ 
    zhuge_sentence_count = int(sys.argv[9])      # 主歌的歌词句数(1句=2小节)：取值范围(0,1,2, 4), -1表示随机
    fuge_sentence_count = int(sys.argv[10])         # 副歌的歌词句数(1句=2小节)：取值范围(0,1,2,4), -1表示随机
    zhuge_note_num_list =  [int(x) for x in sys.argv[2].split(',')]        # 主歌每句歌词的字数数组：取值范围(2~13), 数组长度需与zhuge_sentence_count相同，-1表示随机
    fuge_note_num_list = [int(x) for x in sys.argv[3].split(',')]          # 副歌每句歌词的字数数组：取值范围(2~13), 数组长度需与fuge_sentence_count相同， -1表示随机
    has_weak_start = int(sys.argv[11])                 # 是否有弱起，取值范围(0,1), -1表示随机
    weak_beat_count = -1              # 弱起的长度(拍数)，取值范围(0,1,2), -1表示随机, 此参数仅在has_weak_start==1的情况下有效
    bpm_float = int(sys.argv[5])                        # 曲速，取值范围(60~160), -1表示随机
    chord_index = int(sys.argv[4])                     # 指定和弦的序号，-1表示随机
    midi_path = sys.argv[1]            # midi输出路径
    is_only_melody = 0                 # 是否只导出旋律midi : 0=只导出旋律， 1=导出旋律+伴奏， 2=导出旋律+伴奏 2个midi
    chord_type = int(sys.argv[8])                    # 和弦类型指定：-1=随机，0=大调随机，1=小调随机
    bpm_min = 80                        # 曲速的范围，最小值
    bpm_max = 150                   # 曲速的范围，最大值
    (melody_instru_index,acc_instru_index) = (0,0)
    acc_type_A_index = random.choice([0,1])                 # 主歌伴奏型指定：0~3
    acc_type_B_index = random.choice([2,3])                 # 副歌伴奏型指定：0~3
    melody_vel = 120                # 旋律音符的力度：0~127
    acc_vel = 60                      # 伴奏音符的力度：0~127
    melody_range_a = [int(x) for x in sys.argv[6].split(',')]
    melody_range_b = [int(x) for x in sys.argv[7].split(',')]
    do(zhuge_sentence_count, fuge_sentence_count, zhuge_note_num_list, fuge_note_num_list, 
        has_weak_start, weak_beat_count, bpm_float, chord_index, 
        midi_path, is_only_melody, chord_type, bpm_min, bpm_max, melody_instru_index, acc_instru_index, 
        acc_type_A_index, acc_type_B_index, melody_vel, acc_vel,melody_range_a,melody_range_b )
     
