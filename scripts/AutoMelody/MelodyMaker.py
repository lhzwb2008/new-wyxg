#!/usr/bin/python
# -*- coding: utf-8 -*-

import GLOBAL
from RhythmMaker import *

#LEN_4NOTE = 16 
LEN_CHORD = LEN_4NOTE
 
# 强拍音域变化范围，A为普通，B为高潮部分 
STRONG_CHANGE_RANGE_A = 6 
STRONG_CHANGE_RANGE_B = 9  


class MelodyMaker:
    def __init__(self): 
        
        # 和弦list，字符，每拍1个和弦，2小节=8个和弦
        self.chord_str_list = []   # ["C", "C", "C", "C", "C", "C", "C", "C"]
        
        # 节奏list，长度0~128
        self.rhythm_list = []
        
        # 音符个数
        self.num_note = 0  #len(self.rhythm_list)
        
        # key, scale
        self.key_index = 0 
        self.scale_index = 0

        self.melody_range_a = [47,61]
        self.melody_range_b = [47,65]
        # 音域
        self.range_up_no = self.melody_range_a[1]
        self.range_down_no = self.melody_range_a[0]
        self.range_mid_no = int((self.range_up_no + self.range_down_no)/2)

        # 是section的最后一句（最后一音回归1音）
        self.is_last_sentence = False
        # 是section的第一句（第一个是1音）
        self.is_first_sentence = False
        # 前一个section的最后一个音
        self.last_midino = 0
        # 需要的旋律类型：主歌 / 副歌 
        self.is_zhuge = True
        
        # 弱起
        self.weak_start_64note = 0
        # 强拍位置
        self.STRONG_64NOTE = LEN_2NOTE   # 44拍的情况，
        # 最短的节奏长度
        self.SHORTEST_64NOTE = LEN_8NOTE
        # 强拍音生成时，可允许的变化范围
        self.STRONG_CHANGE_RANGE = STRONG_CHANGE_RANGE_A
        
        self.is_debug = True
        
    def initMelody(self, chord_str_list, rhythm_list, 
                            key_index, scale_index, weak_note_num = 0, 
                            is_last_sentence = False, is_first_sentence = False, last_midino = 0, is_zhuge = True,melody_range_a=[47,61],melody_range_b=[47,65]):
        """ 初始化melody maker """
        # 初始化变量
        self.chord_str_list = chord_str_list[:]
        self.rhythm_list = rhythm_list[:] if rhythm_list else []
        self.num_note = len(self.rhythm_list)
        self.key_index = key_index
        self.scale_index = scale_index 
        self.weak_note_num = weak_note_num
        self.is_last_sentence = is_last_sentence
        self.is_first_sentence = is_first_sentence
        self.last_midino = last_midino
        self.is_zhuge = is_zhuge
        self.melody_range_a = melody_range_a
        self.melody_range_b = melody_range_b
        # 根据当前section类型，设置作曲参数
        self.__initSectionType(is_zhuge)
            
    def __initSectionType(self, is_zhuge):
        """ 初始化结构类型相关数据 """
        if is_zhuge :
            self.STRONG_CHANGE_RANGE = STRONG_CHANGE_RANGE_A
            self.range_up_no = self.melody_range_a[1]
            self.range_down_no = self.melody_range_a[0]
            self.range_mid_no = int((self.range_up_no + self.range_down_no)/2)
        else:
            self.STRONG_CHANGE_RANGE = STRONG_CHANGE_RANGE_B
            self.range_up_no = self.melody_range_b[1]
            self.range_down_no = self.melody_range_b[0]
            self.range_mid_no = int((self.range_up_no + self.range_down_no)/2) 
            
        # 如果是小调，调整音域
        # if self.scale_index == 1:
        #    self.range_up_no -= 3
        #    self.range_down_no -= 3
        #    self.range_mid_no -= 3
         
    def do(self): 
        """ 制作melody，一句=2小节=8拍
            根据强弱拍规则
        """
        if self.is_debug: print " =============== Start Make Melody =============== key=%d scale=%d" %(self.key_index, self.scale_index)
        # 返回变量
        melody_list = []
        # 需要用到的变量
        strong_index_list = []          # 强拍音符的位置
        strong_chord_str_list = []     # 强拍对应的和弦 
        strong_chord_in_pitch_list = []     # 强拍对应的和弦的和弦内音(12内)
        
        if len(self.rhythm_list) == 0:
            return melody_list
        
        ## 开始生成 
        ## 一. 先求出强拍， 按照顺序生成
        # 1. 求出强拍位置，以及对应和弦
        for i in xrange(self.weak_note_num, self.num_note):
            rhythm = self.rhythm_list[i]
            if rhythm.start_64note >= 0 and self.__isStrong(rhythm.start_64note)  or  i == self.num_note - 1:
                # 是强拍 or 最后一个音符( 最后一个音符强制算强拍 )
                # 保存强拍音符的位置
                strong_index_list.append(i)
                # 求出强拍所在和弦
                chord_str = self.__getChordStrBy64Note(self.chord_str_list, rhythm.start_64note) 
                strong_chord_str_list.append(chord_str)
                # 求出和弦对应和弦内音
                if i == self.num_note - 1:
                    # 如果是最后一个音符
                    # 强行使用倒数第2个和弦,使最后一个音符走强拍逻辑
                    chord_str = self.chord_str_list[-2]
                    if self.is_last_sentence:
                        # 歌曲结构的最后一句, # 指定为一级音
                        pitch_list = GLOBAL.inChordPitchByChordStr(chord_str, count = 1) 
                    else:
                        pitch_list = GLOBAL.inChordPitchByChordStr(chord_str)
                    # 15-10-21 modified: 最后一个字，发音不能落在11（xi），大调不能落在9（la）
                    if len(pitch_list) > 1:
                        if 11 in pitch_list:
                            pitch_list.remove(11)
                    if len(pitch_list) > 1:
                        if self.key_index == 0 and 9 in pitch_list:
                            pitch_list.remove(9) 
                else:
                    #  
                    pitch_list = GLOBAL.inChordPitchByChordStr(chord_str) 
                strong_chord_in_pitch_list.append(pitch_list) 
                
                if self.is_debug: print "==========\n 1. strong notes: ", strong_index_list, strong_chord_str_list
                if self.is_debug: print "          > in_chord_pitch_list: ", strong_chord_in_pitch_list 
            
        # 2. 计算每个强拍的旋律（生成旋律线）
        strong_melody_list = self._doStrong(strong_chord_in_pitch_list)  
        if self.is_debug: print "        >> strong_melody_list =", strong_melody_list
 
        ## 二. 求出弱起
        if self.weak_note_num > 0:
            first_midi_no = strong_melody_list[0]
            chord_pitch_list = strong_chord_in_pitch_list[0]
            # 求弱起
            weak_melody_list = self._doWeak(self.weak_note_num, first_midi_no, chord_pitch_list)  
            melody_list.extend(weak_melody_list)
            if self.is_debug: print "        >> weak_melody_list =", weak_melody_list
        
        ## 三. 求出弱拍，按字数匹配melody_pattern
        if self.is_debug: print "========== 2. non-strong notes =========="
        # 循环强拍序号，
        num_strong_note = len(strong_index_list)
        for i in xrange(num_strong_note):
            if self.is_debug: print "---------- %d / %d ----------"%(i + 1, num_strong_note)
            if i < num_strong_note - 1:
                # 1. 计算强拍间的音符个数
                cur_strong_index = strong_index_list[i]
                next_strong_index = strong_index_list[i + 1]
                num_nonstrong_note = next_strong_index - cur_strong_index - 1
                if self.is_debug: print " >> num_nonstrong_note =", num_nonstrong_note
                
                # 2. 计算每个弱拍的旋律 
                cur_midi_no = strong_melody_list[i]
                next_midi_no = strong_melody_list[i + 1]
                if num_nonstrong_note > 0:
                    pre_chord_pitch_list = strong_chord_in_pitch_list[i]  #next_chord_pitch_list = strong_chord_in_pitch_list[i + 1]
                    nonstrong_melody_list = self._doNonStrong(num_nonstrong_note, cur_midi_no, next_midi_no, pre_chord_pitch_list)  
                else:
                    nonstrong_melody_list = []
                
                # 3.  生成音符
                melody_list.append(cur_midi_no)
                melody_list.extend(nonstrong_melody_list)
               
            else:
                # 最后一个音符，特殊处理
                melody_list.append(strong_melody_list[i])   
         
        return melody_list
         
    """  
        作曲子方法
    """
    def _doStrong(self, in_chord_12_list_list, specified_midino_list = []):
        """ 根据强拍和弦，计算主旋律线 
            @in_chord_12_list_list : 和弦内音的list (< 12)
            @specified_midino_list：指定音的list (> 12)
        """ 
        strong_melody_list = []                             # 返回的旋律结果list
        tmp_last_midi_no = self.last_midino            # 临时变量，记录前一个音高
        if tmp_last_midi_no == 0:
            tmp_last_midi_no = self.range_down_no
        count_note = len(in_chord_12_list_list)       # 音符个数
        
        if self.is_debug: print " =============== in_chord_12_list_list =", in_chord_12_list_list
        if self.is_debug: print " =============== specified_midino_list =", specified_midino_list
        
        ## 1. 循环求出每个重音的候补
        candidate_list_list = [ ]
        for i, chord_12_list in enumerate(in_chord_12_list_list):
            # 先求出和弦内音，只需要123音
            chord_12_list = chord_12_list[:3]
            in_chord_list = []
            # 是否有指定
            if i < len(specified_midino_list) and specified_midino_list[i] > 0 and specified_midino_list[i]%12 in chord_12_list:
                # 有指定音，使用指定音
                in_chord_list.append(specified_midino_list[i])
            else:
                # 没有指定 
                # 考虑下一个音的音域范围，如果下一个音有指定，则需要缩小本次的范围
                is_next_specified = ( i + 1 < len(specified_midino_list) and specified_midino_list[i + 1] > 0 ) 
                if is_next_specified:
                    next_up = specified_midino_list[i + 1] + self.STRONG_CHANGE_RANGE
                    next_down = specified_midino_list[i + 1] - self.STRONG_CHANGE_RANGE  
                # 起始音的情况：考虑前音的范围
                is_pre_specified = (i == 0 and self.last_midino  > 12 and self.is_first_sentence == False)
                if is_pre_specified:
                    pre_up = self.last_midino + self.STRONG_CHANGE_RANGE
                    pre_down = self.last_midino - self.STRONG_CHANGE_RANGE  
                # 根据音域，计算所有和弦内音
                for midi_no in xrange(128):
                    if (midi_no%12 in chord_12_list ) and \
                            self.range_down_no < midi_no < self.range_up_no and \
                            (is_next_specified and next_down < midi_no < next_up or (not is_next_specified) )  and \
                            (is_pre_specified and pre_down < midi_no < pre_up or (not is_pre_specified) ) :
                        in_chord_list.append(midi_no) 
            # 保存候选list
            if(len(in_chord_list)==0):
                print in_chord_12_list_list
            candidate_list_list.append(in_chord_list[:])#list深拷贝
        if self.is_debug: print " =============== candidate_list_list 1 =", candidate_list_list
        if self.is_debug: print "self.range_down_no, self.range_up_no,", self.range_down_no, self.range_up_no
        
        ## 2. 指定音，调整前后音的范围
        # 要循环2次
        for t in xrange(len(candidate_list_list)):
            for i, candidate_list in enumerate(candidate_list_list):
                if len(candidate_list) == 1:
                    # 有指定音，调整前后candidate的范围
                    midino = candidate_list[0]
                    # 调整前音
                    if i > 0 and len(candidate_list_list[i - 1]) > 1:
                        for j in xrange(len(candidate_list_list[i - 1]) -1, -1, -1):
                            if not ( midino - self.STRONG_CHANGE_RANGE < candidate_list_list[i - 1][j] < midino + self.STRONG_CHANGE_RANGE ):
                                del candidate_list_list[i - 1][j]
                    # 调整后音
                    if i + 1 < len(candidate_list_list) and len(candidate_list_list[i + 1]) > 1:
                        for j in xrange(len(candidate_list_list[i + 1]) -1, -1, -1):
                            if not ( midino - self.STRONG_CHANGE_RANGE <  candidate_list_list[i + 1][j] < midino + self.STRONG_CHANGE_RANGE ):
                                del candidate_list_list[i + 1][j]
        if self.is_debug: print " =============== candidate_list_list 2 =", candidate_list_list
        
        ## 3. 根据规则，选择弦内音 
        for i, candidate_list in enumerate(candidate_list_list): 
            #      FIXED: 这里是规定起始句必须1音
            #                if i == 0 and ( self.is_first_sentence or self.last_midino == 0 ):
            #                # 第一个音符, 如果是section的第一句 或 没有前音高：选择1音
            #                for midi_no in in_chord_list:
            #                    if midi_no%12 == chord_12_list[0]:
            #                        melody_midi_no = midi_no
            #                        break  
            if len(candidate_list) == 1:
                # 只有一个候选，直接记录
                melody_midi_no = candidate_list[0] 
            else:
                # 多个候选 
                # 第二个音符后的音，选出的和弦内音，不能超出前音的±6音？
                in_chord_range_list = []  # 考虑前音音域后，和弦内音 
                upper_range = tmp_last_midi_no + self.STRONG_CHANGE_RANGE
                lower_range = tmp_last_midi_no - self.STRONG_CHANGE_RANGE  
                # 如果是最后一个音符，需要回归音域中央, 不能超出前一个音的范围
                if i == count_note - 1:
                    if tmp_last_midi_no >= self.range_mid_no + 3:
                        upper_range = tmp_last_midi_no
                    elif tmp_last_midi_no <= self.range_mid_no - 3:
                        lower_range = tmp_last_midi_no 
                # 取出音域范围内的音符
                for midi_no in candidate_list:
                    if lower_range <= midi_no <= upper_range \
                            and ( len(strong_melody_list) == 0 or len(strong_melody_list)>0 and strong_melody_list[0] - self.STRONG_CHANGE_RANGE < midi_no < strong_melody_list[0] + self.STRONG_CHANGE_RANGE):
                        in_chord_range_list.append(midi_no) 
                # 如果没找到，则扩大范围继续找
                if len(in_chord_range_list) == 0:
                    for midi_no in candidate_list:
                        if lower_range <= midi_no <= upper_range:
                            in_chord_range_list.append(midi_no) 
                # 如果还没找到，继续扩大范围继续找
                if len(in_chord_range_list) == 0:
                    for midi_no in candidate_list:
                        if tmp_last_midi_no - self.STRONG_CHANGE_RANGE  <= midi_no <= tmp_last_midi_no + self.STRONG_CHANGE_RANGE:
                            in_chord_range_list.append(midi_no) 
                # 如果还没找到，继续扩大范围继续找
                if len(in_chord_range_list) == 0 and len(candidate_list) > 0:
                    off = 1 
                    while True:
                        for midi_no in candidate_list:
                            if tmp_last_midi_no - self.STRONG_CHANGE_RANGE - off <= midi_no <= tmp_last_midi_no + self.STRONG_CHANGE_RANGE + off:
                                in_chord_range_list.append(midi_no)  
                        off += 1
                        if len(in_chord_range_list) > 0:
                            break
                # 如果有指定，且指定音在和弦内音范围内，则选择指定音，否则随机
                if self.is_debug: print "random in_chord_range_list =", in_chord_range_list, lower_range, "~", upper_range, tmp_last_midi_no
                if len(in_chord_range_list) > 0: 
                    melody_midi_no = RandChoice(in_chord_range_list)
                else:
                    # 这里是临时解决方案：读取缓存后，只有一个候补音，但是该音与前音的差超过了允许范围，
                    melody_midi_no = RandChoice(candidate_list) 
                    if len(candidate_list) > 1:
                        raise "1111" 
                
            # 记录
            tmp_last_midi_no = melody_midi_no
            strong_melody_list.append(melody_midi_no)
            
        return strong_melody_list
        
    def _doWeak(self, num_weak_note, midi_no, chord_pitch_list):
        """ 根据首个强拍音，生成弱起 """ 
        #返回结果
        weak_melody_list = []
        # 先生成临近音符 
        low3 = self.__getDiffPitchInScale(midi_no, -3)
        low2 = self.__getDiffPitchInScale(midi_no, -2)
        low1 = self.__getDiffPitchInScale(midi_no, -1)
        high1 = self.__getDiffPitchInScale(midi_no, +1)
        high2 = self.__getDiffPitchInScale(midi_no, +2) 
        low1c = self.__getDiffPitchInChord(midi_no, chord_pitch_list, -1)
        low1c_1 = self.__getDiffPitchInScale(low1c, +1)
        # 根据音符个数
        if num_weak_note == 1:
            ## 1个音符, 概率表:  10% = (0), (-1), (内-1)
            ##10并不是概率，看的是比例
            p1, p2, p3 = 10, 10, 10
            c1 = lambda : [midi_no, ]
            c2 = lambda : [low1, ]
            c3 = lambda : [low1c, ]
            # 确保不超音域
            if low1 < self.range_down_no: p2 = 0
            if low1c < self.range_down_no: p3 = 0 
            probability_list = (p1, p2, p3 )  
            choice_list = (c1, c2, c3 )  
        elif num_weak_note == 2:
            ## 2个音符, 概率表:  10% = (0, 0), (-2, -1), (0, -1), (内-1, -1), (内-1, -2)
            p1, p2, p3, p4, p5 = 10, 10, 10, 10, 10
            c1 = lambda : [midi_no, midi_no]
            c2 = lambda : [low2, low1]
            c3 = lambda : [midi_no, low1]
            c4 = lambda : [low1c, low1]
            c5 = lambda : [low1c, low2]
            # 确保不超音域
            if low1 < self.range_down_no: p2 = p3 = p4 = 0
            if low2 < self.range_down_no: p2 = p5 =0 
            if low1c < self.range_down_no: p4 = p5 = 0 
            probability_list = (p1, p2, p3, p4, p5 )  
            choice_list = (c1, c2, c3, c4, c5 ) 
        elif num_weak_note == 3:
            ## 3个音符, 概率表:  10%= 随机(-1,0), (-3, -2, -1), (-2, -1, 0) , (内-1, 内-1+1, 内-1), (0,0,0)
            p1, p2, p3, p4, p5 = 10, 10, 10, 10, 1
            c1 = lambda : RandNewList([low1, midi_no], 3)
            c2 = lambda : [low3, low2, low1]
            c3 = lambda : [low2, low1, midi_no] 
            c4 = lambda : [low1c, low1c_1, low1c] 
            c5 = lambda : [midi_no, midi_no, midi_no] 
            # 确保不超音域
            if low1 < self.range_down_no: p1 = p2 = p3 = 0
            if low2 < self.range_down_no: p2 = p3 =0 
            if low3 < self.range_down_no: p2 = 0 
            if low1c < self.range_down_no: p4 = 0 
            if low1c_1 < self.range_down_no: p4 = 0 
            probability_list = (p1, p2, p3, p4, p5 )  
            choice_list = (c1, c2, c3, c4, c5 )
        elif num_weak_note == 4:
            ## 3个音符, 概率表:  10%= 随机(-1,0), (0, -3, -2, -1), (-2, -3, -2, -1) , (-3,-2,-1, 0), (0,+1,+2,+1),  (0,+2,+1,0)
            p1, p2, p3, p4, p5, p6 = 10, 10, 10, 10, 5, 5
            c1 = lambda : RandNewList([low1, midi_no], 4)
            c2 = lambda : [midi_no, low3, low2, low1]
            c3 = lambda : [low2, low3, low2, low1] 
            c4 = lambda : [low3, low2, low1, midi_no] 
            c5 = lambda : [midi_no, high1, high2, high1] 
            c6 = lambda : [midi_no, high2, high1, midi_no] 
            # 确保不超音域
            if low1 < self.range_down_no: p1 = p2 = p3 = p4 = 0
            if low2 < self.range_down_no: p2 = p3 = p4 = 0 
            if low3 < self.range_down_no: p2 = p3 = p4 = 0 
            if high1 > self.range_up_no: p5 = p6 = 0 
            if high2 > self.range_up_no: p5 = p6 = 0 
            probability_list = (p1, p2, p3, p4, p5 )  
            choice_list = (c1, c2, c3, c4, c5 )
        else:
            # 更多音符暂时不做处理
            if self.is_debug: print "Error : cannot deal with num_weak_note =", num_weak_note
            raise "111"
            
        # 随机随一个
        i, chosen_func = RandPercent(probability_list, choice_list) 
        weak_melody_list = chosen_func()
        if self.is_debug: print "num_weak_note, midi_no, chord_pitch_list =", num_weak_note, midi_no, chord_pitch_list
        if self.is_debug: print "weak_melody_list =", weak_melody_list
        return weak_melody_list
             
     
    def _doNonStrong(self, num_nonstrong_note, pre_midi_no, next_midi_no, pre_chord_pitch_list):
        """ 根据前后强拍音，生成中间弱拍旋律 
            2015-09-06: 概率表modified
        """ 
        #返回结果
        nonstrong_melody_list = []
        # 计算前后音的音高差
        diff_pitch_list = self.__diffPitchInScale(pre_midi_no, next_midi_no)
        num_middle_pitch = len(diff_pitch_list)
        if pre_midi_no <= next_midi_no:
            # 上行    
            lower_midi_no, higher_midi_no = pre_midi_no, next_midi_no 
            is_up_trend = True            
        else:
            # 下行
            lower_midi_no, higher_midi_no = next_midi_no, pre_midi_no
            is_up_trend = False         
        if self.is_debug: print " >> Start cal non_strong %d(%d - %d) (%d) by"%(num_nonstrong_note, pre_midi_no, next_midi_no, num_middle_pitch), "chords =", pre_chord_pitch_list
        
        # 先生成临近音符
        low5 = self.__getDiffPitchInScale(pre_midi_no, -5)
        low4 = self.__getDiffPitchInScale(pre_midi_no, -4)
        low3 = self.__getDiffPitchInScale(pre_midi_no, -3)
        low2 = self.__getDiffPitchInScale(pre_midi_no, -2)
        low1 = self.__getDiffPitchInScale(pre_midi_no, -1)
        high1 = self.__getDiffPitchInScale(pre_midi_no, +1)
        high2 = self.__getDiffPitchInScale(pre_midi_no, +2)
        high3 = self.__getDiffPitchInScale(pre_midi_no, +3)
        high4 = self.__getDiffPitchInScale(pre_midi_no, +4)
        high5 = self.__getDiffPitchInScale(pre_midi_no, +5)
        low2c = self.__getDiffPitchInChord(pre_midi_no, pre_chord_pitch_list, -2) 
        low1c = self.__getDiffPitchInChord(pre_midi_no, pre_chord_pitch_list, -1)
        high1c = self.__getDiffPitchInChord(pre_midi_no, pre_chord_pitch_list, +1)
        high2c = self.__getDiffPitchInChord(pre_midi_no, pre_chord_pitch_list, +2)
        lowc12 = self.__getDiffPitchInScale(low1c, -1)  # 夹在c1 c2中间的音
        highc12 = self.__getDiffPitchInScale(high1c, +1)  # 夹在c1 c2中间的音 
        high1_1 = self.__getDiffPitchInScale(pre_midi_no+1, +1)
        low1_1 = self.__getDiffPitchInScale(pre_midi_no-1, -1)
            
        # 根据音符个数
        if num_nonstrong_note == 1:
            # 生成1个音符
            if pre_midi_no == next_midi_no:
                ## 平音，概率表：
                ## 0%=低2音, 33=低1音, 33%=平音, 33%=高1音 , 0=高2音 
                p1, p2, p3, p4, p5 = 0, 33, 33, 33, 0
                c1, c2, c3, c4, c5 = low2, low1, pre_midi_no, high1, high2 
                # 确保不超音域
                if c1 < self.range_down_no: p1 = 0
                if c2 < self.range_down_no: p2 = 0
                if c4 > self.range_up_no: p4 = 0
                if c5 > self.range_up_no: p5 = 0 
                probability_list = (p1, p2, p3, p4, p5)  
                choice_list = (c1, c2, c3, c4, c5) 
            elif num_middle_pitch == 0:
                ## 相差1音，概率表：25%=比低音低1音, 25%=低音, 25%=低音, 25%=比高音高1音 
                p1, p2, p3, p4 = 0, 50, 50, 0 
                c1 = self.__getDiffPitchInScale(lower_midi_no, -1)
                c2 = lower_midi_no 
                c3 = higher_midi_no 
                c4 = self.__getDiffPitchInScale(higher_midi_no, +1)
                # 确保不超音域
                if c1 < self.range_down_no: p1 = 0
                if c4 > self.range_up_no: p4 = 0
                probability_list = (p1, p2, p3, p4)  
                choice_list = (c1, c2, c3, c4)  
            elif num_middle_pitch == 1:
                ## 相差2音，概率表：0%=比低音低1音, 25%=低音, 50%=中间音, 25%=高音, 0%=比高音高1音
                p1, p2, p3, p4, p5 = 0, 15, 70, 15, 0
                c1 = self.__getDiffPitchInScale(lower_midi_no, -1)
                c2 = lower_midi_no 
                c3 = diff_pitch_list[0]
                c4 = higher_midi_no 
                c5 = self.__getDiffPitchInScale(higher_midi_no, +1)
                # 确保不超音域
                if c1 < self.range_down_no: p1 = 0
                if c5 > self.range_up_no: p5 = 0
                probability_list = (p1, p2, p3, p4, p5)  
                choice_list = (c1, c2, c3, c4, c5)  
            elif num_middle_pitch == 2:
                ## 相差3音（中间夹2音符），概率表：0%=比低音低1音, 0%=低音, 0%=中间音1, 100%=±1的相邻音, 0%=中间音2, 0%=高音,0%=比高音高1音
                p1, p2, p3, p4, p5 = 0, 0, 100, 0, 0
                c1 = lower_midi_no 
                c2 = diff_pitch_list[0]
                c3 = high1_1 if is_up_trend else low1_1 
                c4 = diff_pitch_list[1]
                c5 = higher_midi_no
                probability_list = (p1, p2, p3, p4)  
                choice_list = (c1, c2, c3, c4)  
            elif num_middle_pitch == 3:
                ## 相差4音（中间夹3音符），概率表：0%=低音, 0%=中间音1, 10%= ±1的相邻音  90%=中间音2, 0%=中间音3, 0%=高音
                p1, p2, p3, p4, p5, p6 = 0, 0, 10, 90, 0, 0
                c1 = lower_midi_no
                c2 = diff_pitch_list[0] 
                c3 = high1_1 if is_up_trend else low1_1 
                c4 = diff_pitch_list[1]
                c5 = diff_pitch_list[2] 
                c6 = higher_midi_no
                probability_list = (p1, p2, p3, p4, p5, p6)  
                choice_list = (c1, c2, c3, c4, c5, c6)  
            elif num_middle_pitch == 4:
                ## 相差5音（中间夹4音符），概率表：10%=中间音1, 40%=中间音2, 40%=中间音3, 10%=中间音4
                p1, p2, p3, p4 = 00, 50, 50, 00
                c1 = diff_pitch_list[0] 
                c2 = diff_pitch_list[1] 
                c3 = diff_pitch_list[2]
                c4 = diff_pitch_list[3]  
                probability_list = (p1, p2, p3, p4)  
                choice_list = (c1, c2, c3, c4)
            elif num_middle_pitch == 5:
                ## 相差6音（中间夹5音符），概率表：0%=中间音1, 25%=中间音2, 50%=中间音3, 25%=中间音4, 0%=中间音5
                p1, p2, p3, p4, p5 = 0, 5, 90, 5, 0
                c1 = diff_pitch_list[0] 
                c2 = diff_pitch_list[1] 
                c3 = diff_pitch_list[2]
                c4 = diff_pitch_list[3] 
                c5 = diff_pitch_list[4] 
                probability_list = (p1, p2, p3, p4, p5)  
                choice_list = (c1, c2, c3, c4, c5)  
            else:
                ## 相差>6音（中间夹>5音符），概率表：0%=中间音1/2-2, 25%=中间音1/2-1, 50%=中间音1/2, 25%=中间音1/2+1, 0%=中间音1/2+2
                p1, p2, p3, p4, p5 = 0, 5, 90, 5, 0
                c1 = diff_pitch_list[num_middle_pitch/2-2] 
                c2 = diff_pitch_list[num_middle_pitch/2-1] 
                c3 = diff_pitch_list[num_middle_pitch/2]
                c4 = diff_pitch_list[num_middle_pitch/2+1] 
                c5 = diff_pitch_list[num_middle_pitch/2+2] 
                probability_list = (p1, p2, p3, p4, p5)  
                choice_list = (c1, c2, c3, c4, c5)   
            # 随机随一个
            i, midi_no = RandPercent(probability_list, choice_list) 
            nonstrong_melody_list = [midi_no, ]  
        elif num_nonstrong_note == 2:
            # 生成2个音符 
            if pre_midi_no == next_midi_no:
                ## 平音，概率表：10%=洗牌(-1,+1), 洗牌(-1,+0), 洗牌(0,+1), 洗牌(+1,+2), 洗牌(-1,-2),  
                ##                           洗牌(内-1,内-2),  洗牌(内+1,内+2),  洗牌(-1, -1),  洗牌(+1, +1),  洗牌(0, 0)
                p1, p2, p3, p4, p5, p6, p7, p8, p9, p10 = 10, 10, 10, 10, 10, 0, 0, 10, 10, 10
                c1 = lambda : RandShuffle([low1, high1])
                c2 = lambda : RandShuffle([low1, pre_midi_no])
                c3 = lambda : RandShuffle([pre_midi_no, high1])
                c4 = lambda : RandShuffle([high1, high2])
                c5 = lambda : RandShuffle([low1, low2])
                c6 = lambda : RandShuffle([low1c, low2c])
                c7 = lambda : RandShuffle([high1c, high2c])
                c8 = lambda : RandShuffle([low1, low1])
                c9 = lambda : RandShuffle([high1, high1])
                c10 = lambda : RandShuffle([pre_midi_no, pre_midi_no])
                # 确保不超音域
                if low2 < self.range_down_no:  p5 = 0
                elif low1 < self.range_down_no:   p1 = p2 = p5 = p8 = 0
                if high2 > self.range_up_no: p4 = 0
                elif high1 > self.range_up_no:   p1 = p3 = p4 = p9 = 0
                if low2c < self.range_down_no or low1c < self.range_down_no:  p6 = 0 
                if high2c > self.range_up_no or high1c > self.range_up_no:  p7 = 0 
                # 生成概率表
                probability_list = (p1, p2, p3, p4, p5, p6, p7, p8, p9, p10)  
                choice_list = (c1, c2, c3, c4, c5, c6, c7, c8, c9, c10)  
            elif num_middle_pitch == 0:
                ## 相差1音(夹0个音)，上行概率表： 10%=洗牌(-1,+1), 洗牌(-1,+0), 洗牌(0,+1), 洗牌(0, 0), 洗牌(+1,+2), 洗牌(内+1,内+2), 洗牌(+1, +1)
                ##                  下行概率表： 10%=洗牌(-1,+1), 洗牌(-1,+0), 洗牌(0,+1), 洗牌(0, 0), 洗牌(-1,-2), 洗牌(内-1,内-2), 洗牌(-1, -1)
                p1, p2, p3, p4, p5, p6, p7 = 0, 10, 10, 0, 10, 0, 0 
                c1 = lambda : RandShuffle([low1, high1])
                c2 = lambda : RandShuffle([low1, pre_midi_no])
                c3 = lambda : RandShuffle([pre_midi_no, high1])
                c4 = lambda : [pre_midi_no, pre_midi_no]
                if is_up_trend:     # 上行
                    c5 = lambda : RandShuffle([high1, high2])
                    c6 = lambda : RandShuffle([high1c, high2c]) 
                    c7 = lambda : [high1, high1]
                    # 确保不超音域
                    if low1 < self.range_down_no:   p1 = p2 = 0
                    if high2 > self.range_up_no: p5 = 0
                    if high1 > self.range_up_no:   p1 = p3 = p5 = p7 = 0 
                    if high2c > self.range_up_no or high1c > self.range_up_no:  p6 = 0  
                else:     # 下行
                    c5 = lambda : RandShuffle([low1, low2])
                    c6 = lambda : RandShuffle([low1c, low2c]) 
                    c7 = lambda : [low1, low1] 
                    # 确保不超音域
                    if low2 < self.range_down_no:  p5 = 0
                    if low1 < self.range_down_no:   p1 = p2 = p5 = p7 = 0
                    if high1 > self.range_up_no: p1 = p3 = 0 
                    if low2c < self.range_down_no or low1c < self.range_down_no:  p6 = 0  
                # 生成概率表
                probability_list = (p1, p2, p3, p4, p5, p6, p7)  
                choice_list = (c1, c2, c3, c4, c5, c6, c7)
            elif num_middle_pitch == 1:
                ## 相差2音(夹1个音)，上行概率表： 10%= (0, 0), (-1, 0),(-1,+1),(+1, +1), 洗牌(0, +1), 洗牌(+1,+2), 洗牌(内+1,内+2)
                ##                   下行概率表： 10%= (0, 0), (+1, 0),(+1,-1), (-1, -1), 洗牌(0, -1), 洗牌(-1,-2), 洗牌(内-1,内-2)
                p1, p2, p3, p4, p5, p6, p7 = 0, 0, 0, 10, 10, 20, 0 
                c1 = lambda: [pre_midi_no, pre_midi_no]
                if is_up_trend:
                    # 上行
                    c2 = lambda : [low1, pre_midi_no]
                    c3 = lambda : [low1, high1]
                    c4 = lambda : [high1, high1]
                    c5 = lambda :  RandShuffle([pre_midi_no, high1])
                    c6 = lambda :  RandShuffle([high1, high2])
                    c7 = lambda :  RandShuffle([high1c, high2c])
                    # 确保不超音域 
                    if low1 < self.range_down_no:   p2 = p3 = 0
                    if high2 > self.range_up_no: p6 = 0
                    if high1 > self.range_up_no: p3 = p4 = p5 = p6 = 0 
                    if high1c > self.range_up_no or high2c > self.range_up_no:  p7 = 0  
                else:
                    # 下行   
                    c2 = lambda : [high1, pre_midi_no]
                    c3 = lambda : [high1, low1]
                    c4 = lambda : [low1, low1]
                    c5 = lambda :  RandShuffle([pre_midi_no, low1])
                    c6 = lambda :  RandShuffle([low1, low2])
                    c7 = lambda :  RandShuffle([low1c, low2c])
                    # 确保不超音域 
                    if high1 > self.range_up_no:   p2 = p3 = 0
                    if low2 < self.range_down_no: p6 = 0
                    if low1 < self.range_down_no: p3 = p4 = p5 = p6 = 0 
                    if low2c < self.range_down_no or low1c < self.range_down_no:  p7 = 0  
                probability_list = (p1, p2, p3, p4, p5, p6, p7) 
                choice_list = (c1, c2, c3, c4, c5, c6, c7)
            elif num_middle_pitch == 2:
                ## 相差3音(夹2个音)，概率表：
                ##   上行： 50%=(+1, +2),  10%=(+2,+1),  10%=(1, 内+1),  10%=(0, 内+1), 10%=(内+1, 内+2)
                ##   下行： 50%=(-1, -2),  10%=(-2,-1),  10%=(1, 内-1),  10%=(0, 内-1), 10%=(内-1, 内-2)
                p1, p2, p3, p4, p5 = 50, 10, 10, 10, 10
                if is_up_trend:
                    # 上行
                    c1 = lambda : [high1, high2]
                    c2 = lambda : [high2, high1]
                    c3 = lambda : [high1, high1c]
                    c4 = lambda : [pre_midi_no, high1c]
                    c5 = lambda : [high1c, high2c]
                    # 确保不超音域 
                    if high2 > self.range_up_no : p1 = p2 =0
                    if high1 > self.range_up_no:   p1 = p2 = p3 =0
                    if high2c > self.range_up_no :  p5 = 0
                    if high1c > self.range_up_no :  p3 = p4 = p5 = 0
                else:
                    # 下行 
                    c1 = lambda : [low1, low2]
                    c2 = lambda : [low2, low1]
                    c3 = lambda : [low1, low1c]
                    c4 = lambda : [pre_midi_no, low1c]
                    c5 = lambda : [low1c, low2c]
                    # 确保不超音域 
                    if low2 < self.range_down_no : p1 = p2 =0
                    if low1 < self.range_down_no:   p1 = p2 = p3 =0
                    if low2c < self.range_down_no :  p5 = 0
                    if low1c < self.range_down_no :  p3 = p4 = p5 = 0
                probability_list = (p1, p2, p3, p4, p5 )  
                choice_list = (c1, c2, c3, c4, c5 )  
            else: ## if num_middle_pitch == 3:
                ## 相差4~音(夹3~个音)，概率表：
                ##   上行： 50%=(+1, 内+1), 50%=(内+1, 内+2)
                ##   下行： 50%=(-1, 内-1), 50%=(内-1, 内-2)
                p1, p2 = 50, 50
                if is_up_trend:
                    # 上行
                    c1 = lambda : [high1, high1c]
                    c2 = lambda : [high1c, high2c]
                    # 确保不超音域 
                    if high1 > self.range_up_no : p1 = 0 
                    if high2c > self.range_up_no :  p2 = 0
                    if high1c > self.range_up_no :  p1 = p2 = 0
                else:
                    # 下行
                    c1 = lambda : [low1, low1c]
                    c2 = lambda : [low1c, low2c]
                    # 确保不超音域
                    if low1 < self.range_down_no:   p1 = 0
                    if low2c < self.range_down_no :  p2 = 0
                    if low1c < self.range_down_no :  p1 = p2 = 0
                probability_list = (p1, p2 )  
                choice_list = (c1, c2 )   
                
            # 随机随一个
            i, chosen_func = RandPercent(probability_list, choice_list) 
            nonstrong_melody_list = chosen_func()
             
        elif num_nonstrong_note == 3:
            # 生成3个音符   
            if pre_midi_no == next_midi_no:
                ## 平音，概率表：10%=随机(0,+1), 随机(-1,0), 洗牌(0,+1,-1), 洗牌(0,+1,+2), 洗牌(0,-1,-2), (+1,+2,+3), (-1,-2,-3)
                p1, p2, p3, p4, p5, p6, p7 = 10, 10, 10, 10, 10, 10, 10 
                c1 = lambda : RandNewList([pre_midi_no, high1], 3)
                c2 = lambda : RandNewList([low1, pre_midi_no], 3)
                c3 = lambda : RandShuffle([pre_midi_no, high1, low1])
                c4 = lambda : RandShuffle([pre_midi_no, high1, high2])
                c5 = lambda : RandShuffle([pre_midi_no, low1, low2])
                c6 = lambda : [high1, high2, high3]
                c7 = lambda : [low1, low2, low3]  
                # 确保不超音域
                if low3 < self.range_down_no:  p7 = 0
                if low2 < self.range_down_no:  p5 = p7 = 0
                if low1 < self.range_down_no:   p2 = p3 = p5 = p7 = 0
                if high3 > self.range_up_no: p6 = 0
                if high2 > self.range_up_no:   p4 = p6 =0
                if high1 > self.range_up_no:   p1 = p3 = p4 = p6 = 0 
                # 生成概率表
                probability_list = (p1, p2, p3, p4, p5, p6, p7)  
                choice_list = (c1, c2, c3, c4, c5, c6, c7)
            elif num_middle_pitch == 0: 
                ## 差1音，上行概率表：10%=随机(0,+1), 随机(-1,0), 洗牌(0,+1,-1), 洗牌(0,+1,+2), (+1,+2,+3)
                ##				下行概率表：10%=随机(0,+1), 随机(-1,0), 洗牌(0,+1,-1), 洗牌(0,-1,-2), (-1,-2,-3)
                p1, p2, p3, p4, p5 = 10, 10, 10, 10, 10
                c1 = lambda : RandNewList([pre_midi_no, high1], 3)
                c2 = lambda : RandNewList([low1, pre_midi_no], 3)
                c3 = lambda : RandShuffle([pre_midi_no, high1, low1])
                if is_up_trend:
                    c4 = lambda : RandShuffle([pre_midi_no, high1, high2])
                    c5 = lambda : [high1, high2, high3]
                    # 确保不超音域 
                    if low1 < self.range_down_no: p2 = p3 = 0
                    if high3 > self.range_up_no: p5 = 0
                    if high2 > self.range_up_no:   p4 = p5 =0
                    if high1 > self.range_up_no:   p1 = p3 = p4 = p5 = 0 
                else:
                    c4 = lambda : RandShuffle([pre_midi_no, low1, low2])
                    c5 = lambda : [low1, low2, low3]
                    # 确保不超音域
                    if low3 < self.range_down_no:  p5 = 0
                    if low2 < self.range_down_no:  p4 = p5 = 0
                    if low1 < self.range_down_no:   p2 = p3 = p4 = p5 = 0
                    if high1 > self.range_up_no:   p1 = p3 = 0
                # 生成概率表
                probability_list = (p1, p2, p3, p4, p5)  
                choice_list = (c1, c2, c3, c4, c5 )  
            elif num_middle_pitch == 1:
                ## 相差2音(夹1个音)，上行概率表：10%=随机(0,+1), 洗牌(0,+1,-1), 洗牌(0,+1,+2), (+1,+2,+3) 
                ##									下行概率表：10%=随机(0,-1), 洗牌(0,+1,-1), 洗牌(0,-1,-2), (-1,-2,-3)
                p1, p2, p3, p4 = 10, 10, 10, 10 
                if is_up_trend:
                    c1 = lambda : RandNewList([pre_midi_no, high1], 3)
                    c2 = lambda : RandShuffle([low1, pre_midi_no, high1])
                    c3 = lambda : RandShuffle([pre_midi_no, high1, high2])
                    c4 = lambda : [high1, high2, high3]
                    # 确保不超音域
                    if low1 < self.range_down_no:   p2 = 0
                    if high3 > self.range_up_no: p4 = 0
                    if high2 > self.range_up_no:   p3 = p4 =0
                    if high1 > self.range_up_no:   p1 = p2 = p3 = p4 = 0 
                else:
                    c1 = lambda : RandNewList([pre_midi_no, low1], 3)
                    c2 = lambda : RandShuffle([low1, pre_midi_no, high1])
                    c3 = lambda : RandShuffle([pre_midi_no, low1, low2])
                    c4 = lambda : [low1, low2, low3]
                    # 确保不超音域
                    if low3 < self.range_down_no:  p4 = 0
                    if low2 < self.range_down_no:  p3 = p4 = 0
                    if low1 < self.range_down_no:   p1 = p2 = p3 = p4 = 0
                    if high1 > self.range_up_no:   p2 = 0
                # 生成概率表
                probability_list = (p1, p2, p3, p4 )  
                choice_list = (c1, c2, c3, c4 )  
            elif num_middle_pitch == 2:
                ## 相差3音(夹2个音)，概率表： 
                ## 上行概率表：10%=洗牌(0,+1,+2), (+1,+2,+1), (+1,+2,+3), (+1,内+1,内+2), (内+1,内+1.5,内+2)
                ## 下行概率表：10%=洗牌(0,-1,-2), (-1,-2,-1), (-1,-2,-3), (-1,内-1,内-2), (内-1,内-1.5,内-2)
                p1, p2, p3, p4, p5 = 10, 10, 10, 10, 10 
                if is_up_trend:
                    c1 = lambda : RandShuffle([pre_midi_no, high1, high2])
                    c2 = lambda : [high1, high2, high1]
                    c3 = lambda : [high1, high2, high3]
                    c4 = lambda : [high1, high1c, high2c]
                    c5 = lambda : [high1c, highc12, high2c]
                    # 确保不超音域 
                    if high3 > self.range_up_no:     		p3 = 0
                    if high2 > self.range_up_no:   		p1 = p2 = p3 = 0
                    if high1 > self.range_up_no:   		p1 = p2 = p3 = p4 = 0 
                    if high2c > self.range_up_no:   		p4 = p5 = 0
                    if highc12 > self.range_up_no:   	p5 = 0 
                    if high1c > self.range_up_no:   	p4 = p5 = 0 
                else:
                    c1 = lambda : RandShuffle([pre_midi_no, low1, low2])
                    c2 = lambda : [low1, low2, low1]
                    c3 = lambda : [low1, low2, low3]
                    c4 = lambda : [low1, low1c, low2c]
                    c5 = lambda : [low1c, lowc12, low2c]
                    # 确保不超音域
                    if low3 < self.range_down_no: 			p3 = 0
                    if low2 < self.range_down_no:  		p1 = p2 = p3 = 0
                    if low1 < self.range_down_no:   	p1 = p2 = p3 = p4 = 0
                    if low2c < self.range_down_no:   		p4 = p5 = 0
                    if lowc12 < self.range_down_no:   p5 = 0
                    if low1c < self.range_down_no:    p4 = p5 = 0
                # 生成概率表
                probability_list = (p1, p2, p3, p4, p5 )  
                choice_list = (c1, c2, c3, c4, c5 )  
            else:
                ## 相差4~音(夹3~个音)，概率表：
                ## 上行概率表：10%= (+1,+2,+3), (0,内+1,内+2), (+1,内+1,内+2), (内+1,内+1.5,内+2)
                ## 下行概率表：10%= (-1,-2,-3), (0,内-1,内-2), (-1,内-1,内-2), (内-1,内-1.5,内-2)
                p1, p2, p3, p4 = 10, 10, 10, 10 
                if is_up_trend:
                    c1 = lambda : [high1, high2, high3]
                    c2 = lambda : [pre_midi_no, high1c, high2c]
                    c3 = lambda : [high1, high1c, high2c]
                    c4 = lambda : [high1c, highc12, high2c]
                    # 确保不超音域 
                    if high3 > self.range_up_no or high2 > self.range_up_no:   		p1 =  0
                    if high1 > self.range_up_no:   		p1 = p3 = 0 
                    if high2c > self.range_up_no:   		p2 = p3 = p4 = 0
                    if highc12 > self.range_up_no:   	p4 = 0 
                    if high1c > self.range_up_no:   	p2 = p3 = p4 = 0 
                else:
                    c1 = lambda : [low1, low2, low3]
                    c2 = lambda : [pre_midi_no, low1c, low2c]
                    c3 = lambda : [low1, low1c, low2c]
                    c4 = lambda : [low1c, lowc12, low2c]
                    # 确保不超音域
                    if low3 < self.range_down_no or low2 < self.range_down_no:  		p1 = 0
                    if low1 < self.range_down_no:   	p1 = p3 = 0
                    if low2c < self.range_down_no:   		p2 = p3 = p4 = 0
                    if lowc12 < self.range_down_no:   p4 = 0
                    if low1c < self.range_down_no:    p2 = p3 = p4 = 0
                # 生成概率表 
                probability_list = (p1, p2, p3, p4 )  
                choice_list = (c1, c2, c3, c4 )  
                
            # 随机随一个
            i, chosen_func = RandPercent(probability_list, choice_list) 
            nonstrong_melody_list = chosen_func()
            
        elif num_nonstrong_note == 4:
            # 生成4个音符   
            if pre_midi_no == next_midi_no:
                ## 平音，概率表：10%=随机(0,+1), 随机(-1,0), 洗牌(0,+1,-1) 
                p1, p2, p3 = 10, 10, 10
                c1 = lambda : RandNewList([pre_midi_no, high1], 4)
                c2 = lambda : RandNewList([low1, pre_midi_no], 4)
                c3 = lambda : RandShuffle([pre_midi_no, pre_midi_no, high1, low1]) 
                # 确保不超音域 
                if low1 < self.range_down_no:   p2 = p3 = 0 
                if high1 > self.range_up_no:   p1 = p3 = 0 
                # 生成概率表
                probability_list = (p1, p2, p3 )  
                choice_list = (c1, c2, c3 )
            elif num_middle_pitch == 0: 
                ## 差1音，上行概率表：10%=随机(0,+1),  洗牌(0,+1,+2) 
                ##		  下行概率表：10%= 随机(-1,0), 洗牌(0,-1,-2) 
                p1, p2 = 10, 10  
                if is_up_trend:
                    c1 = lambda : RandNewList([pre_midi_no, high1], 4)
                    c2 = lambda : RandShuffle([pre_midi_no, high1, high1, high2]) 
                    # 确保不超音域  
                    if high2 > self.range_up_no:   p2 =0
                    #if high1 > self.range_up_no:   p1 = p2 = 0 
                else:
                    c1 = lambda : RandNewList([low1, pre_midi_no], 4)
                    c2 = lambda : RandShuffle([pre_midi_no, low1, low1, low2]) 
                    # 确保不超音域 
                    if low2 < self.range_down_no:  p2 = 0
                    #if low1 < self.range_down_no:   p1 = p2 = 0 
                # 生成概率表
                probability_list = (p1, p2 )  
                choice_list = (c1, c2 )  
            elif num_middle_pitch == 1:
                ## 相差2音(夹1个音)，上行概率表：10%=随机(0,+1),  洗牌(0,+1,+1,+2) 
                ##					     下行概率表：10%=随机(0,-1),  洗牌(0,-1,-1,-2) 
                p1, p2 = 10, 10 
                if is_up_trend:
                    c1 = lambda : RandNewList([pre_midi_no, high1], 4)
                    c2 = lambda : RandShuffle([pre_midi_no, high1, high1, high2]) 
                    # 确保不超音域 
                    if high2 > self.range_up_no:   p2 =0
                    #if high1 > self.range_up_no:   p1 = p2 = 0 
                else:
                    c1 = lambda : RandNewList([pre_midi_no, low1], 4)
                    c2 = lambda : RandShuffle([pre_midi_no,low1, low1, low2]) 
                    # 确保不超音域 
                    if low2 < self.range_down_no:  p2 = 0
                    #if low1 < self.range_down_no:   p1 = p2 = 0 
                # 生成概率表
                probability_list = (p1, p2 )  
                choice_list = (c1, c2 )  
            else:
                ## 相差3音(夹2个音)，概率表： 
                ## 上行概率表：10%=(+0,+1,+2,+3), (+1,+2,+3,+4)
                ## 下行概率表：10%=(-0,-1,-2,-3), (-1,-2,-3,-4)
                p1, p2 = 10, 10 
                if is_up_trend: 
                    c1 = lambda : [high1, high2, high3, high4]
                    c2 = lambda : [pre_midi_no, high1, high2, high3] 
                    # 确保不超音域 
                    if high4 > self.range_up_no:     		p1 = 0  
                else: 
                    c1 = lambda : [low1, low2, low3, low4]
                    c2 = lambda : [pre_midi_no, low1, low2, low3] 
                    # 确保不超音域
                    if low4 < self.range_down_no: 			p1 = 0 
                # 生成概率表
                probability_list = (p1, p2 )  
                choice_list = (c1, c2 )   
                
            # 随机随一个
            i, chosen_func = RandPercent(probability_list, choice_list) 
            nonstrong_melody_list = chosen_func()
            
        else:
            # 更多音符则分拆 
            nonstrong_melody_list = \
                self._doNonStrong(num_nonstrong_note/2, pre_midi_no, next_midi_no, pre_chord_pitch_list) + \
                self._doNonStrong(num_nonstrong_note - num_nonstrong_note/2, pre_midi_no, next_midi_no, pre_chord_pitch_list)   
          
        # if self.is_debug: print " >> choosed =", i, nonstrong_melody_list
        
        return nonstrong_melody_list
        
    
    
    """ 通用方法 """
    def __getChordStrBy64Note(self, chord_str_list, pos_64note):
        """ 找到音符位置找到所对应的和弦 """
        # 每个和弦的长度为：一拍=4分音符=16
        num_chord = len(chord_str_list)
        chord_index = int(pos_64note/LEN_CHORD)
        
        if chord_index < num_chord:
            # 和弦个数不够
            return chord_str_list[chord_index]
        else:
            return None
        
         
    def __isStrong(self, start_64note):
        """ 是否是强拍 """
        return start_64note % self.STRONG_64NOTE == 0
        
        
    def __diffPitchInScale(self, pre_midi_no, next_midi_no):
        """ 求两个音高之间，夹在中间的调内音 
            返回："""
        # 返回用变量
        diff_pitch_list = []
        
        # 音高相等，则无音高差
        if pre_midi_no == next_midi_no:
            return diff_pitch_list 
            
        # 1. 求出调内音list
        pitch_12_list = GLOBAL.getPitch12InScale(self.scale_index, self.key_index)
        # 2. 循环判断中间的音
        if pre_midi_no <= next_midi_no:
            # 上行
            lower_midi_no = pre_midi_no
            higher_midi_no = next_midi_no
        else:
            # 下行
            lower_midi_no = next_midi_no
            higher_midi_no = pre_midi_no 
        # loop
        for midi_no in xrange(lower_midi_no + 1, higher_midi_no):
            if midi_no%12 in pitch_12_list: 
                # 如果是调内音
                diff_pitch_list.append(midi_no)
        
        return diff_pitch_list
         
    def __getDiffPitchInScale(self, midi_no, offset):
        """ 求：在调内，与指定音高相差offset的音高
            返回：result_midi_no """  
        # 1. 求出调内音list
        pitch_12_list = GLOBAL.getPitch12InScale(self.scale_index, self.key_index)
        # 2. 循环取得相差offset的音
        return self.__getDiffPitchInList(midi_no, pitch_12_list, offset) 
        
    def __getDiffPitchInChord(self, midi_no, chord_pitch_list, offset):
        """ 求：在和弦内音中，与指定音高相差offset的音高
            返回：result_midi_no """ 
        return self.__getDiffPitchInList(midi_no, chord_pitch_list, offset) 
            
    def __getDiffPitchInList(self, midi_no, any_12_list, offset):
        """ 求：在list中，与指定音高相差offset的音高 
            注：list中的数字均<12
            返回：result_midi_no """        
        
        # 无音高差变化
        if offset == 0:
            return midi_no 
             
        # 循环判断相差offset的调内音
        result_midi_no = 0  # 返回用变量 
        if offset > 0:
            # 往高找
            for no in xrange(midi_no + 1, 128):
                if no%12 in any_12_list: 
                    # 如果是调内音
                    offset -= 1
                    if offset <= 0:
                        # 找到
                        result_midi_no = no
                        break  
        else:
            # 往低找
            for no in xrange(midi_no - 1, 0, -1):
                if no%12 in any_12_list: 
                    # 如果是调内音
                    offset += 1
                    if offset >= 0:
                        # 找到
                        result_midi_no = no
                        break   
        
        # 返回结果
        return result_midi_no
        
class MelodyNote: 
    def __init__(self, midi_no, rhythm_note ): 
        self.midi_no = midi_no
        self.start_64note = rhythm_note.start_64note
        self.len_64note = rhythm_note.len_64note
        self.is_strong = False
        self.is_weak = False 
        
        self.end_64note = self.start_64note + self.len_64note 
        
    def __repr__(self):
        return "[%d, %d, %d, %d]"%(self.midi_no, self.start_64note, self.len_64note, self.is_strong)
        
         
        
if __name__ == "__main__":
    
    num_lyric = 7
    weak_beat_count = 1
    weak_note_num = 2
    # 先生成节奏
    rhythm_maker = RhythmMaker()
    rhythm_maker.initRhythm(num_lyric, weak_beat_count = weak_beat_count, weak_note_num = weak_note_num)
    rhythm_list = rhythm_maker.do()
    
    # 打印标准2小节
    print "Standard 2 bars:"
    printRhythm([RhythmNote(0, 64), RhythmNote(64, 64)])
    # 打印生成节拍
    print "Rhythm 2 bars:"
    printRhythm(rhythm_list)
    
    # 生成chord
    chord_str_list = ["C", "C", "C", "C", "G", "G", "G", "G"]#, "Am", "Am", "Am", "Am", "Em", "Em", "Em", "Em", "F", "F", "F", "F", "G", "G", "G", "G", "F", "F", "F", "F", "C", "C", "C", "C" ]
    mm = MelodyMaker()
    #mm.initMelody(chord_str_list, rhythm_list, weak_note_num = weak_note_num)
    #melody_list = mm.do() 
    #print "==========\n Result melody: ",  melody_list  
    printRhythm(rhythm_list)
    
    #if len(melody_list) != len(rhythm_list):
    #    print "Error: len(melody_list) != len(rhythm_list)", len(melody_list), len(rhythm_list)
    #    raise "error"

