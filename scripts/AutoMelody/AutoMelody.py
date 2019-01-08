#!/usr/bin/python
# -*- coding: utf-8 -*-

import copy
from TOOLRAND import * 
from GLOBAL import * 
from CHORD import * 
from ACC import * 
from MelodyMaker import *
from RhythmMaker import *
from Midi import *

class AutoMelody():
    def __init__(self):
        self.is_debug = True
        
        # 固定的变量
        self.chord_per_sentence = 8    # 每1句歌词(= 2个小节)，对应8个chord
         
        # 输入的变量
        self.sentence_count  = 8
        self.note_num_list     = [7, 7, 7, 7,  8, 8, 8, 8]
        self.has_weak_start            = True
        self.weak_beat_count         = 1
        self.bpm_float                   = 120. 
        self.midi_path                   = "out.mid" 
        self.key_index                  = 0
        self.scale_index                = 0  
        self.is_only_melody           = 0   
        self.melody_instru_index       = 0
        self.acc_instru_index           = 0
        self.acc_type_A_index             = 0
        self.acc_type_B_index             = 0
        self.melody_vel                     = 120
        self.acc_vel                        = 60
        self.melody_range_a                     = [47,61]
        self.melody_range_b                        = [47,65]
        # 中间变量
        self.chord_str_list           = []     # 和弦 list
        self.weak_note_num_list = []          # 每句的弱起音符数
         
        # 结果变量 
        self.melody_note_list = []    # 旋律 ： [ (midino, start64, len64, vel),   ] 
        self.acc_note_list = []        # 伴奏 ： [ (midino, start64, len64, vel),   ]

    def initAM(self, 
                    zhuge_sentence_count,           # 主歌的歌词句数(1句=2小节)：取值范围(0,1,2, 4), -1表示随机
                    fuge_sentence_count,           # 副歌的歌词句数(1句=2小节)：取值范围(0,1,2,4), -1表示随机
                    zhuge_note_num_list,            # 主歌每句歌词的字数数组：取值范围(2~13), 数组长度需与zhuge_sentence_count相同，-1表示随机
                    fuge_note_num_list,              # 副歌每句歌词的字数数组：取值范围(2~13), 数组长度需与fuge_sentence_count相同， -1表示随机
                    has_weak_start,                  # 是否有弱起，取值范围(0,1), -1表示随机
                    weak_beat_count,               # 弱起长度（拍数），取值范围(0,1,2,3,4), -1表示随机, 仅在has_weak_start==1的情况下有效
                    bpm_float,                         # 曲速，取值范围(60~160), -1表示随机
                    chord_index,                       # 指定和弦的序号，-1表示随机
                    midi_path,                          # midi输出路径 
                    is_only_melody,                  # 是否只导出旋律 : 0=只导出旋律， 1=导出旋律+伴奏， 2=导出旋律+伴奏 2个midi
                    melody_instru_index,            # 主旋律乐器(0~128)
                    acc_instru_index,                 # 伴奏乐器(0~128)
                    acc_type_A_index,                 # 主歌伴奏型
                    acc_type_B_index,                 # 副歌伴奏型
                    melody_vel,                            # 旋律音符力度
                    acc_vel,                                # 伴奏音符力度
                    melody_range_a,
                    melody_range_b
                                    ):
        """ 初始化 
        """
        # 赋值 
        self.sentence_count  = zhuge_sentence_count + fuge_sentence_count
        self.note_num_list     = zhuge_note_num_list + fuge_note_num_list
        self.has_weak_start      = has_weak_start
        self.weak_beat_count   = weak_beat_count
        self.bpm_float              = bpm_float 
        self.midi_path              = midi_path 
        self.is_only_melody       = is_only_melody 
        self.melody_instru_index = melody_instru_index 
        self.acc_instru_index      = acc_instru_index 
        self.acc_type_A_index    = acc_type_A_index 
        self.acc_type_B_index    = acc_type_B_index 
        self.melody_range_a     = melody_range_a
        self.melody_range_b     = melody_range_b
        # 副歌起始位置, 是主歌结束的位置
        self.fuge_start_sentence = zhuge_sentence_count
                
        # 生成和弦: 根据和弦序号+句数，从和弦DB中读取对应的和弦
        zhuge_chord_str_list = GetChord4Zhuge(chord_index, zhuge_sentence_count)  
        fuge_chord_str_list = GetChord4Fuge(chord_index, fuge_sentence_count)
        if zhuge_chord_str_list is None:
            self.chord_str_list = fuge_chord_str_list
        elif fuge_chord_str_list is None:
            self.chord_str_list = zhuge_chord_str_list
        else:
            self.chord_str_list = zhuge_chord_str_list + fuge_chord_str_list
        # 读取和弦对应的调式信息
        self.key_index             = GetKey(chord_index)
        self.scale_index           = GetScale(chord_index)  
        
        # 初始化弱起音符个数
        self.weak_note_num_list = [0 for x in xrange(len(self.note_num_list))]
        
        # 如果有弱起，计算每句的弱起音符个数 
        if self.weak_beat_count > 0 and len(self.note_num_list) > 0:
            # 计算平均音符数
            avg_note_num = sum(self.note_num_list) / len(self.note_num_list)
            if self.weak_beat_count == 1:
                # 弱起1拍
                base_num = RandChoice((1, 2))
                for i, num_note in enumerate(self.note_num_list): 
                    if num_note > avg_note_num:
                        self.weak_note_num_list[i] = base_num
                    else:
                        self.weak_note_num_list[i] = base_num - 1
                    # 弱起音符数 必须少于 该句音符数
                    if self.weak_note_num_list[i] >= self.note_num_list[i]:
                        self.weak_note_num_list[i] = self.note_num_list[i] - 1
            elif self.weak_beat_count == 2:
                # 弱起2拍
                base_num = RandChoice((1, 2, 3, 4))
                for i, num_note in enumerate(self.note_num_list):  
                    if num_note > avg_note_num:
                        self.weak_note_num_list[i] = base_num
                    else:
                        self.weak_note_num_list[i] = base_num - 1
                    # 弱起音符数 必须少于 该句音符数
                    if self.weak_note_num_list[i] >= self.note_num_list[i]:
                        self.weak_note_num_list[i] = self.note_num_list[i] - 1
                  

    def do(self):
        """ 自动作曲 """  
        # 工作类实例
        rm = RhythmMaker()
        mm = MelodyMaker()
        
        # 初始化
        self.melody_note_list = []      # 旋律音符list : [ (midino, start64, len64, vel),  ... ]  
        self.acc_note_list = []          # 伴奏音符list : [ (midino, start64, len64, vel),  ... ] 
         
        ## =============== 主旋律 ======================
        # 循环主歌和副歌的每一句, 生成rhythm + melody  
        melody_list = []
        rhythm_list = [] 
        for i in xrange(self.sentence_count):
            ## 1. 初始化变量
            # 判断当前生成的是主歌还是副歌
            if i < self.fuge_start_sentence:
                # 是主歌 
                is_zhuge = True 
                is_first_sentence = (i == 0)                                                # 是否是主歌的第一句（第一个是1音）
                is_last_sentence = ( i == self.fuge_start_sentence - 1)      # 是否是主歌的最后一句（最后一个音强制为1音）
            else:
                # 是副歌
                is_zhuge = False
                is_first_sentence = (i == self.fuge_start_sentence)      # 是否是主歌的第一句（第一个是1音）
                is_last_sentence = ( i == self.sentence_count - 1)      # 是否是主歌的最后一句（最后一个音强制为1音）
        
            note_count = self.note_num_list[i]                            # 当前句需要生成的音符个数
            chord_str_list = self.chord_str_list[i*self.chord_per_sentence : (i+1)*self.chord_per_sentence]                           # 当前句对应的和弦
            weak_note_num = self.weak_note_num_list[i]     # 弱起音符个数
            last_midino = 0 if len(melody_list) == 0 else melody_list[-1]       # 前一个midino 
            ## 2. 生成melody
            melody_list = []
            rhythm_list = [] 
                       
            #  先生成节奏 
            rm.initRhythm(note_count, 
                                weak_beat_count = self.weak_beat_count, 
                                weak_note_num = weak_note_num
                                )
            rhythm_list = rm.do()
            #  再生成旋律 
            mm.initMelody(chord_str_list, rhythm_list, self.key_index, self.scale_index, 
                                weak_note_num = weak_note_num, 
                                is_first_sentence = is_first_sentence, 
                                is_last_sentence = is_last_sentence, 
                                last_midino = last_midino, 
                                is_zhuge = is_zhuge,
                                melody_range_a = self.melody_range_a,
                                melody_range_b = self.melody_range_b,
                                )
            melody_list = mm.do()
            if self.is_debug : print "==========\n Result melody: ",  melody_list   

            # 检查结果: 防止 旋律音符个数 ≠ 节奏音符个数
            if len(melody_list) != len(rhythm_list):
                print "Error: len(melody_list) != len(rhythm_list)", len(melody_list), len(rhythm_list)
                raise "error"

            ## 3. 保存旋律+节奏（同时计算歌曲中的起止）
            if self.weak_note_num_list[0] == 0:
                offset = 128 * i   # 64为前面空出1小节
            else:
                offset = 128 * i + 64
            for k in xrange(len(melody_list)): 
                midi_no = melody_list[k]
                rhythm_note = rhythm_list[k]
                start, length = rhythm_note.start_64note, rhythm_note.len_64note
                self.melody_note_list.append( [midi_no, 
                                                            start + offset, 
                                                            length, 
                                                            self.melody_vel
                                                            ] )   
               
        ## =============== 一轨伴奏 ====================== 
        # 循环主歌和副歌的每小节（4拍，一拍对应一个和弦，1拍长度16，4拍长度64）, 生成伴奏音符
        self.acc_note_list = [] 
        if self.is_only_melody > 0:
            for i in xrange(len(self.chord_str_list)/4): 
                # 循环每一小节, 生成伴奏
                if i / 2 < self.fuge_start_sentence:
                    # 主歌伴奏
                    acc_list = GetAccByChord(self.chord_str_list[i*4:(i+1)*4], self.acc_type_A_index, self.acc_vel)
                else:
                    # 副歌伴奏
                    acc_list = GetAccByChord(self.chord_str_list[i*4:(i+1)*4], self.acc_type_B_index, self.acc_vel)
                # 保存伴奏音符（同时计算歌曲中的起止）
                if self.weak_note_num_list[0] == 0:
                    offset = 64 * i   # 64为前面空出1小节
                else:
                    offset = 64 * i + 64
                for j in xrange(len(acc_list)):  
                    acc_list[j][1] += offset 
                self.acc_note_list.extend(acc_list)
       
        # 结束
        if self.is_debug: print "melody_done =", self.melody_note_list
        if self.is_debug: print "acc_done =", self.acc_note_list
    
    
    def exportMidi(self):
        """ 导出midi """ 
        m = midiAnalyzer(self.midi_path) 
        # set midi info
        beat_per_bar = 4
        base_beat = 4
        key = 0
        format = 1
        tick_per_64note = 30
        tick_per_quarternote = int(tick_per_64note *2*2*2*2)
        m.setTickPerQuarterNote(None, tick_per_quarternote)
        m.setFormat(format) 
        m.setTempo(self.bpm_float)
        m.setBeat(beat_per_bar, base_beat)
        m.setKey(key)  
        # set events
        out_midi_list = [copy.deepcopy(self.melody_note_list), copy.deepcopy(self.acc_note_list)]
        # 处理note
        for i in xrange(2):
            for j in xrange(len(out_midi_list[i])):
                if out_midi_list[i][j][1] * tick_per_64note < 0:
                    out_midi_list[i][j][1] = 0
                    out_midi_list[i][j][2] = 0
                else:
                    out_midi_list[i][j][1] = int(out_midi_list[i][j][1] * tick_per_64note)
                    out_midi_list[i][j][2] = out_midi_list[i][j][1] + int(out_midi_list[i][j][2] * tick_per_64note)
                    out_midi_list[i][j][3] = min(127, int(out_midi_list[i][j][3] ))
                
        # 写入midi
        channel_index_list = [0, 1]
        instrument_index_list = [self.melody_instru_index, self.acc_instru_index]
        m.writeMidi(out_midi_list, channel_index_list, instrument_index_list)  
         
    def exportMidiMelody(self):
        """ 只导出melody的midi """ 
        m = midiAnalyzer(self.midi_path+"_melody.mid") 
        # set midi info
        beat_per_bar = 4
        base_beat = 4
        key = 0
        format = 1
        tick_per_64note = 30
        tick_per_quarternote = int(tick_per_64note *2*2*2*2)
        m.setTickPerQuarterNote(None, tick_per_quarternote)
        m.setFormat(format) 
        m.setTempo(self.bpm_float)
        m.setBeat(beat_per_bar, base_beat)
        m.setKey(key)  
        # set events
        out_midi_list = [copy.deepcopy(self.melody_note_list),  ]
        # 处理note
        for i in xrange(1):
            for j in xrange(len(out_midi_list[i])):
                if out_midi_list[i][j][1] * tick_per_64note < 0:
                    out_midi_list[i][j][1] = 0
                    out_midi_list[i][j][2] = 0
                else:
                    out_midi_list[i][j][1] = int(out_midi_list[i][j][1] * tick_per_64note)
                    out_midi_list[i][j][2] = out_midi_list[i][j][1] + int(out_midi_list[i][j][2] * tick_per_64note)
                    out_midi_list[i][j][3] = min(127, int(out_midi_list[i][j][3] ))
                
        # 写入midi
        channel_index_list = [0, ]
        instrument_index_list = [ self.melody_instru_index, ]
        m.writeMidi(out_midi_list, channel_index_list, instrument_index_list)  
         
    def exportMidiAcc(self):
        """ 只导出acc的midi """ 
        m = midiAnalyzer(self.midi_path+"_acc.mid") 
        # set midi info
        beat_per_bar = 4
        base_beat = 4
        key = 0
        format = 1
        tick_per_64note = 30
        tick_per_quarternote = int(tick_per_64note *2*2*2*2)
        m.setTickPerQuarterNote(None, tick_per_quarternote)
        m.setFormat(format) 
        m.setTempo(self.bpm_float)
        m.setBeat(beat_per_bar, base_beat)
        m.setKey(key)  
        # set events
        out_midi_list = [ copy.deepcopy(self.acc_note_list), ]
        # 处理note
        for i in xrange(1):
            for j in xrange(len(out_midi_list[i])):
                if out_midi_list[i][j][1] * tick_per_64note < 0:
                    out_midi_list[i][j][1] = 0
                    out_midi_list[i][j][2] = 0
                else:
                    out_midi_list[i][j][1] = int(out_midi_list[i][j][1] * tick_per_64note)
                    out_midi_list[i][j][2] = out_midi_list[i][j][1] + int(out_midi_list[i][j][2] * tick_per_64note)
                    out_midi_list[i][j][3] = min(127, int(out_midi_list[i][j][3] ))
                
        # 写入midi
        channel_index_list = [0, ]
        instrument_index_list = [self.acc_instru_index, ]
        m.writeMidi(out_midi_list, channel_index_list, instrument_index_list)  
