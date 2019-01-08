#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time
import sys
import random
from AutoAcc.Section import *
from AutoAcc.CHORD import *
from AutoAcc.ACC import *
from AutoAcc.GLOBAL import *
from AutoAcc import AutoAcc
      
# 全局变量
IS_DEBUG = True
 
## 错误代码
ERROR_CODE = 20000
ERROR_SECTION_INDEX_LIST_TYPE = 20001            # 歌曲结构格式错误
ERROR_SECTION_INDEX_LIST_VALUE = 20002            # 歌曲结构值错误
ERROR_section_barlen_list_TYPE = 20003            # 歌曲结构长度格式错误
ERROR_section_barlen_list_LEN = 20004            # 歌曲结构长度list不一致的错误
ERROR_EMOTION_OUT_RANGE = 20005           # 指定emotion序号超出范围
ERROR_GENRE_OUT_RANGE = 20006               # 指定genre序号超出范围
ERROR_TEMPLATE_OUT_RANGE = 20007         # 指定template序号超出范围
ERROR_CHORD_INDEX = 20008                      # '和弦序号'参数，错误
ERROR_BPM_FLOAT_VALUE = 20009             # '曲速'参数，取值错误 
ERROR_CHORD_LIST_LEN = 20010             # '和弦list'参数，长度错误
ERROR_CHORD_LIST_VALUE = 20011             # '和弦list'参数，取值错误 
ERROR_MIDI_PATH = 20012                      # '输出midi路径'参数，错误 

# 生成
def do( 
            section_index_list = [],         # 歌曲结构：结构定义参考AutoAcc.Section
            section_barlen_list = [],              # 歌曲结构长度：小节数
            emotion_index = 0,                # 歌曲情感
            genre_index = 0,                    # 歌曲曲风
            template_index = 2,                # 采用指定伴奏模板，>0则无视emotion和genre，-1则无指定（由emotion和genre选出）

            chord_index = -1,                       # 指定和弦的序号，-1表示随机
            chord_type = -1,                       # 和弦类型指定：-1=随机，0=大调随机，1=小调随机。此参数仅在chord_index=-1时有效。
            chord_str_list = [],                    # 和弦指定：是list且元素>0，则使用。1个小节要有4个和弦
            bpm_float = -1,                         # 曲速，取值范围(60~160), -1表示随机，由emotion和genre决定 
 
            midi_path = "out.mid",               # midi输出路径   
    
            ) :                    
    """  
    说明：调用伴奏模块生成acc，保存为midi格式，同时保证模块的输入参数是合法的
    参数:  见上
    步骤：
        1. 分析输入参数，初始化变量；
        2. 调用伴奏模块；
        3. 将伴奏导出为midi文件。
    """ 
    ### 1、分析输入参数，初始化变量 
    logMessage("=========== 1. Start analyze parameters ==============")
    # ---------------------- 1.1 分析歌曲结构 ----------------------
    # section_index_list必须是个长度>0的list
    if type(section_index_list) != list or len(section_index_list) <=0:
        logMessage(u"错误：输入的结构错误: %s"%(str(section_index_list)))
        return ERROR_SECTION_INDEX_LIST_TYPE
    # section_index_list中的值必须在指定范围内
    for x in section_index_list:
        if x not in range(COUNT_SEC_TYPE):
            logMessage(u"错误：输入的结构index错误: %d"%(x))
            return ERROR_SECTION_INDEX_LIST_VALUE
    # section_barlen_list必须是个长度>0的list
    if type(section_barlen_list) != list or len(section_barlen_list) <=0:
        logMessage(u"错误：输入的结构错误: %s"%(str(section_barlen_list)))
        return ERROR_section_barlen_list_TYPE
    # section_barlen_list的长度必须与section_index_list一致
    if len(section_barlen_list) != len(section_index_list):
        logMessage(u"错误：section_barlen_list与section_index_list的长度不一致: %d != %d"%(len(section_barlen_list), len(section_index_list)))
        return ERROR_section_barlen_list_LEN
             
    # ---------------------- 1.2 分析emotion  genre  template结构 ----------------------
    if template_index < 0:
        # 未指定template，则需要检查emotion和genre
        if emotion_index < 0 or emotion_index >= EMOTION_COUNT:
            logMessage(u"错误：输入的emotion超出范围: %d out range of (%d ~ %d)"%(emotion_index,  0, EMOTION_COUNT-1))
            return ERROR_EMOTION_OUT_RANGE
        if genre_index < 0 or genre_index >= GENRE_COUNT:
            logMessage(u"错误：输入的genre超出范围: %d out range of (%d ~ %d)"%(genre_index,  0, GENRE_COUNT-1))
            return ERROR_GENRE_OUT_RANGE 
    # 检查template的序号
    if template_index < -1 or template_index >= TEMPLATE_COUNT:
        logMessage(u"错误：输入的template超出范围: %d out range of (%d ~ %d)"%(template_index,  0, TEMPLATE_COUNT-1))
        return ERROR_TEMPLATE_OUT_RANGE
    # 如果template未指定，则指定一个
    if template_index == -1:
        template_index = getTemplateIndexByEmotionGenre(emotion_index, genre_index)
    
    # ---------------------- 1.3 检查和弦序号参数 ---------------------- 
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
    # ---------------------- 1.4 检查曲速参数 ---------------------- 
    # 检查曲速是否需要随机
    if bpm_float == -1:
        bpm_float = getBpmFloatByEmotionGenre(emotion_index, genre_index)
        
    # 检查曲速取值范围
    if bpm_float > 240 or  bpm_float < 20:
        logMessage(u"错误：曲速取值范围为：(%d ~ %d)，其中-1代表随机，您的输入为：%d"%(20, 240, bpm_float))
        return ERROR_BPM_FLOAT_VALUE
        
    # 检查输入和弦
    if type(chord_str_list) == list and len(chord_str_list) > 0:
        # 输入和弦个数要够
        if len(section_barlen_list) != len(chord_str_list):
            logMessage(u"错误：输入和弦的section个数与歌曲section个数不符：%d != %d"%(len(section_barlen_list), len(chord_str_list)))
            return ERROR_CHORD_LIST_LEN
            
        for i, section_chord_list in enumerate(chord_str_list):
            # 小节数与和弦个数相符（1个小节=4个和弦）
            if len(section_chord_list) != section_barlen_list[i]*4:
                logMessage(u"错误：输入和弦个数与小节数不符，小节数为%d*4，输入和弦个数为%d"%(section_barlen_list[i], len(section_chord_list)))
                return ERROR_CHORD_LIST_LEN
            # 输入和弦要能被识别
            for chord_str in section_chord_list: 
                if chordStr2RootAndType(chord_str) < 0:
                    logMessage(u"错误：无法识别和弦:%s"%(chord_str))
                    return ERROR_CHORD_LIST_VALUE
    
    # ---------------------- 1.7 检查输出midi路径参数 ---------------------- 
    if not midi_path.endswith(".mid"):
        logMessage(u"错误：输出路径不合法，您的输入为：%s"%(midi_path))
        return ERROR_MIDI_PATH 
    
    if IS_DEBUG:
        print " Parameters:"
        print " > section_index_list =", section_index_list
        print " > section_barlen_list =", section_barlen_list
        print " > emotion_index =", emotion_index
        print " > genre_index =", genre_index
        print " > template_index =", template_index
        print " > chord_index =", chord_index
        print " > chord_type =", chord_type
        print " > chord_str_list =", chord_str_list
        print " > bpm_float =", bpm_float 
        print " > midi_path =", midi_path  
   
    ### 2、调用伴奏模块；
    logMessage("=========== 2. Start make accompaniment ==============" )
    # 创建实例
    aa = AutoAcc.AutoAcc() 
    # 初始化
    aa.initAA(  section_index_list, 
                    section_barlen_list, 
                    template_index, 
                    chord_index,
                    chord_str_list,
                    bpm_float,  
                    )
    # 开始做伴奏
    aa.do() 
    
    # 伴奏音符-导出midi 
    aa.exportMidi(midi_path)
    
         
    ### 结束
    logMessage("=========== Done ==============" )
    
    return 1

def logMessage(message):
    """ 处理信息： 打印到控制台 """
    if IS_DEBUG: 
        print message 
    
if __name__ == "__main__":
    """ Main """ 
    #section_index_list = [sec_intro, sec_a11, sec_b11, sec_mid1, sec_end,  ]         # 歌曲结构：结构定义参考AutoAcc.Section
    section_index_list = [ sec_a11,sec_a12, sec_b11,sec_b12]         # 歌曲结构：结构定义参考AutoAcc.Section
    # section_barlen_list = [8, 8, 8, 8, 4 ]           # 歌曲结构长度：每个结构的小节数，4句=8小节  3句=6小节  2句=4小节  1句=2小节
    section_barlen_list = [int(sys.argv[6]), int(sys.argv[7]),int(sys.argv[8]),int(sys.argv[9]) ]           # 歌曲结构长度：每个结构的小节数，4句=8小节  3句=6小节  2句=4小节  1句=2小节
    emotion_index = int(sys.argv[4])               # 歌曲情感
    genre_index = int(sys.argv[5])                   # 歌曲曲风
    template_index = -1            # 采用指定伴奏模板，>0则无视emotion和genre，-1则无指定（由emotion和genre选出）

    chord_index = int(sys.argv[1])                       # 指定和弦的序号，-1表示随机
    chord_type = -1                       # 和弦类型指定：-1=随机，0=大调随机，1=小调随机。此参数仅在chord_index=-1时有效。
    chord_str_list = []
    # 和弦指定：是list且元素>0，则使用。1个小节要有4个和弦
    #chord_str_list = [  ['C', 'C', 'C', 'C', 'F', 'F', 'F', 'F', 'G', 'G', 'G', 'G', 'C', 'C', 'C', 'C'],['C', 'C', 'C', 'C', 'F', 'F', 'F', 'F', 'G', 'G', 'G', 'G', 'C', 'C', 'C', 'C' ]]     # 第1个section的和弦
                         
    bpm_float = int(sys.argv[3])                        # 曲速，取值范围(60~160), -1表示随机，由emotion和genre决定 
 
    midi_path = sys.argv[2]              # midi输出路径  
              
    do(section_index_list, section_barlen_list, emotion_index, genre_index,  template_index, 
    chord_index, chord_type, chord_str_list, 
    bpm_float,  midi_path ) 
     
