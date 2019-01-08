#!/usr/bin/python
# -*- coding: utf-8 -*-

import copy
from TOOLRAND import *

# 最小长度单位：64分音符
LEN_64NOTE = 1
LEN_32NOTE = 2
LEN_16NOTE = 4
LEN_8NOTE = 8
LEN_4NOTE = 16
LEN_2NOTE = 32
LEN_1NOTE = 64
LEN_2BARs = 128
 
class RhythmMaker:
    def __init__(self):
        
        # 音符个数
        self.num_note = 0
         
        # 是否打印测试信息
        self.is_debug = True
        
        # 弱起的音符个数
        self.weak_start_64note = 0
        
        # 强拍的位置
        self.STRONG_64NOTE = LEN_2NOTE   # 4/4拍的情况
        
        # 最短的节奏长度
        self.SHORTEST_64NOTE = LEN_8NOTE

        
    def initRhythm(self, num_note, weak_beat_count = 0, weak_note_num = 0):
        """ 初始化节奏参数
            @num_note：音符的个数 
            @weak_beat_count: 弱起长度(几拍, 1拍=16)
            @weak_note_num: 需要弱起的音符个数 
        """
        self.num_note = num_note  
        self.weak_beat_count = weak_beat_count
        self.weak_note_num = weak_note_num
        # 检查弱起音符个数, 不得超过总音符的个数
        if weak_note_num > num_note:
            self.weak_note_num = num_note - 1
         
        
    def do(self):
        """ 制作rhythm，一句=2小节=8拍
            根据字数生成节奏
            长度：( 1拍=16，2拍=32，3拍=48, 4拍=64 )
        """
        if self.is_debug:  print " =============== Start Make Rhythm =============== " 
        
        # 只支持：2-13字
        if self.num_note > 13 or self.num_note < 2:
            print "Error : num_note out of range:", self.num_note
            return None
            
        ## 1. 生成弱起节奏
        has_weak = self.weak_beat_count > 0 and self.weak_note_num > 0
        if has_weak:
            # 如果有弱起
            # 主节奏的音符个数
            num_main_note = self.num_note - self.weak_note_num
            # 生成弱起节奏
            weak_rhythm_list = self.__rhythmWeakTemplate( self.weak_note_num )
        else:
            # 主节奏的音符个数
            num_main_note = self.num_note 
            weak_rhythm_list = []
        
        if self.is_debug: print " \n  Rhythm make result of WEAK: ", weak_rhythm_list, "\n=========="
        if self.is_debug: print " num_main_note = self.num_note - self.weak_note_num ",num_main_note ,  self.num_note ,  self.weak_note_num
        
        ## 2. 生成主节奏
        if num_main_note <= 0:
            raise "shouldn't be here"
        elif num_main_note == 1:
            # 1个字 直接调用模板
            main_rhythm_list = self.__rhythmTemplate1( 0, LEN_2BARs, has_weak ) 
        elif num_main_note == 2:
            # 2个字 直接调用模板
            main_rhythm_list = self.__rhythmTemplate2( 0, LEN_2BARs ) 
        else:
            # 3个字以上，递归生成
            main_rhythm_list = self._structDispatcher(num_main_note, 0, LEN_2BARs,  need_expand = False) 
            
            if self.is_debug: print "==========\n  Rhythm make result bofore smooth: ", main_rhythm_list, "\n "
 
        ## 3. 优化节奏, 处理弱起
        main_rhythm_list = self._smoothRhythm(main_rhythm_list)
        
        if self.is_debug: print " \n  Rhythm make result of MAIN: ", main_rhythm_list, "\n=========="
        	
        ## 4. 合并弱起+主节奏
        rhythm_list = weak_rhythm_list + main_rhythm_list
        if self.is_debug: print " \n  Rhythm make result finally: ", rhythm_list, "\n=========="
         
        return rhythm_list
        
    def _structDispatcher(self, num_note, start_64note, len_64note, need_expand = False):
        """
            节奏的结构模板
            @num_note: 音符个数 
            @start_64note：起始位置
            @need_expand: 是否需要扩展
            返回：
        """
        if self.is_debug: 
            print ">> _structDispatcher: num_note=%d, start_64note=%d, len_64note=%d, need_expand=%d "\
                        %(num_note, start_64note, len_64note, need_expand) 
            
        rhythm_list = []
        
        # 按音符个数
        if num_note == 1:
            # 1个音符：直接调用模板 
            rhythm_list = self.__rhythmPattern1(  start_64note, len_64note, need_expand )
            
        elif num_note == 2:
            # 2个音符：直接调用模板 
            rhythm_list = self.__rhythmPattern2( start_64note, len_64note, need_expand )
            
        else:
            ## 3个音符以上，需要拆分 ##
            # 1. 首先获取一个2字模板
            rhythm_template_list = self._structDispatcher( 2, start_64note, len_64note, need_expand = True )
            if rhythm_template_list == None or len(rhythm_template_list) != 2:  
                # error
                print "shouldn't be here... num_note=%d "%(num_note) 
                raise "shouldn't be here..."  
            else:
                note1 = rhythm_template_list[0]
                note2 = rhythm_template_list[1]
                
            # 2. 根据音符数生成概率表 
            if num_note == 3: 
                # 3个音符: 
                ## 概率表：70% 3=2+1  30% 3=1+2 ##
                    # 未指定规则，则按概率拆分 
                    p1, p2 = 70, 30
                    c1, c2 = (2, 1), (1, 2)
                    probability_list = (p1, p2)  
                    choice_list = (c1, c2) 
            elif num_note == 4: 
                # 4个音符:  
                ## 概率表：60% 4=3+1  30% 4=2+2  10% 4=1+3 ##  
                p1, p2, p3 = 60, 30, 10
                c1, c2, c3 = (3, 1), (2, 2), (1, 3)
                probability_list = (p1, p2, p3)  
                choice_list = (c1, c2, c3) 
            elif num_note == 5: 
                # 5个音符:  
                ## 概率表：10% 5=1+4,  20% 5=2+3,  50% 5=3+2,  20% 5=4+1  ##  
                p1, p2, p3, p4 = 5, 20, 50, 25
                c1, c2, c3, c4 = (1, 4), (2, 3), (3, 2), (4, 1)
                probability_list = (p1, p2, p3, p4)  
                choice_list = (c1, c2, c3, c4) 
            elif num_note == 6: 
                # 6个音符:  
                ## 概率表：0% 6=1+5,  20% 6=2+4,  50% 6=3+3,  25% 6=4+2   5% 6=5+1  ##  
                p1, p2, p3, p4, p5 = 0, 20, 50, 25, 5
                c1, c2, c3, c4, c5 = (1, 5), (2, 4), (3, 3), (4, 2), (5, 1)
                probability_list = (p1, p2, p3, p4, p5)  
                choice_list = (c1, c2, c3, c4, c5) 
            elif num_note == 7: 
                # 7个音符:  
                ## 概率表： 0% 7=1+6,  0% 7=2+5,  50% 7=3+4,  30% 7=4+3,  15% 7=5+2,  
                ##             5% 7=6+1  ##  
                p1, p2, p3, p4, p5, p6 = 0, 0, 50, 30, 15, 5
                c1, c2, c3, c4, c5, c6 = (1, 6), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1)
                probability_list = (p1, p2, p3, p4, p5, p6)  
                choice_list = (c1, c2, c3, c4, c5, c6) 
            elif num_note == 8: 
                # 8个音符:  
                ## 概率表：0% 8=1+7,  0% 8=2+6,  5% 5=3+5,  50% 8=4+4,  35% 8=5+3,  
                ##          10% 8=6+2,  0% 8=7+1  ## 
                p1, p2, p3, p4, p5, p6, p7 = 0, 0, 5, 50, 35, 10, 0
                c1, c2, c3, c4, c5, c6, c7 = (1, 7), (2, 6), (3, 5), (4, 4), (5, 3), (6, 2), (7, 1)
                probability_list = (p1, p2, p3, p4, p5, p6, p7)  
                choice_list = (c1, c2, c3, c4, c5, c6, c7) 
            elif num_note == 9: 
                # 9个音符:  
                ## 概率表：0% 9=1+8,  0% 9=2+7,  0% 9=3+6,  15% 9=4+5,  50% 9=5+4,  
                ##          30% 9=6+3,  5% 9=7+2,  0% 9=8+1  ## 
                p1, p2, p3, p4, p5, p6, p7, p8 = 0, 0, 0, 15, 50, 30, 5, 0
                c1, c2, c3, c4, c5, c6, c7, c8 = (1, 8), (2, 7), (3, 6), (4, 5), (5, 4), (6, 3), (7, 2), (8, 1)
                probability_list = (p1, p2, p3, p4, p5, p6, p7, p8)  
                choice_list = (c1, c2, c3, c4, c5, c6, c7, c8) 
            elif num_note == 10: 
                # 10个音符:  
                ## 概率表：0% 10=1+9,  0% 10=2+8,  0% 10=3+7,  5% 10=4+6,  50% 10=5+5,  
                ##          30% 10=6+4,  10% 10=7+3,  5% 10=8+2,  0% 10=9+1  ##  
                p1, p2, p3, p4, p5, p6, p7, p8, p9 = 0, 0, 0, 5, 50, 30, 10, 5, 0
                c1, c2, c3, c4, c5, c6, c7, c8, c9 = (1, 9), (2, 8), (3, 7), (4, 6), (5, 5), (6, 4), (7, 3), (8, 2), (9, 11)
                probability_list = (p1, p2, p3, p4, p5, p6, p7, p8, p9)  
                choice_list = (c1, c2, c3, c4, c5, c6, c7, c8, c9) 
            elif num_note == 11: 
                # 11个音符:  
                ## 概率表：0% 11=1+10,  0% 11=2+9,  0% 11=3+8,  0% 11=4+7,  15% 11=5+6,  
                ##          40% 11=6+5,  30% 11=7+4,  10% 11=8+3,  5% 11=9+2,  0% 11=10+1  ##  
                p1, p2, p3, p4, p5, p6, p7, p8, p9, p10 = 0, 0, 0, 0, 15, 40, 30, 10, 5, 0
                c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = (1, 10), (2, 9), (3, 8), (4, 7), (5, 6), (6, 5), (7, 4), (8, 3), (9, 2), (10, 1)
                probability_list = (p1, p2, p3, p4, p5, p6, p7, p8, p9, p10)  
                choice_list = (c1, c2, c3, c4, c5, c6, c7, c8, c9, c10) 
            elif num_note == 12: 
                # 12个音符:  
                ## 概率表：0% 12=1+11,  0% 12=2+10,  0% 12=3+9,  0% 12=4+8,  15% 12=5+7,  
                ##          40% 12=6+6,  30% 12=7+5,  10% 12=8+4,  5% 12=9+3,  0% 12=10+2,
                ##          0% 12=11+1   ##  
                p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11 = 0, 0, 0, 0, 15, 40, 30, 10, 5, 0, 0
                c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11 = \
                                (1, 11), (2, 10), (3, 9), (4, 8), (5, 7), (6, 6), (7, 5), (8, 4), (9, 3), (10, 2), (11, 1)
                probability_list = (p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11)  
                choice_list = (c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11)  
            elif num_note == 13:  
                # 13个音符:  
                ## 概率表：0% 13=1+12,  0% 13=2+11,  0% 13=3+10,  0% 13=4+9,  0% 13=5+8,  
                ##          10% 13=6+7,  50% 13=7+6,  25% 13=8+5,  10% 10=9+4,  5% 13=10+3, 
                ##            0% 13=11+2,  0% 13=12+1,   ##  
                p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12 = 0, 0, 0, 0, 0, 10, 50, 25, 10, 5, 0, 0
                c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12 = \
                                    (1, 12), (2, 11), (3, 10), (4, 9), (5, 8), (6, 7), (7, 6), (8, 5), (9, 4), (10, 3), (11, 2), (12, 1)
                probability_list = (p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12)  
                choice_list = (c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12) 
                 
            # 3. 概率算出结果
            i, (part1_note_num, part2_note_num) = RandPercent(probability_list, choice_list)  
                
            if self.is_debug: print "  >> calculating : part1_note_num=%d, part2_note_num=%d" %(part1_note_num, part2_note_num)
            # 修正结果：如果拆分的太小，则调整
            while(note1.len_64note / part1_note_num < self.SHORTEST_64NOTE):
                part1_note_num -= 1
                part2_note_num += 1
            while(note2.len_64note / part2_note_num < self.SHORTEST_64NOTE):
                part2_note_num -= 1
                part1_note_num += 1
            # 4. 生成rhythm_list  
            # 拆分  
            tmp_list1 = self._structDispatcher(part1_note_num, note1.start_64note, note1.len_64note)
            if self.is_debug: print "  >> Result: tmp_list1=", tmp_list1
            tmp_list2 = self._structDispatcher(part2_note_num, note2.start_64note, note2.len_64note)
            if self.is_debug: print "  >> Result: tmp_list2=", tmp_list2
            # combine
            rhythm_list.extend(tmp_list1) 
            rhythm_list.extend(tmp_list2)   
            
        return rhythm_list

    """ 
        节奏扩展用模板 
    """
    ## 1个字的扩展用模板   
    def __rhythmPattern1(self, start_64note, len_64note, need_expand):
        # 1个音符  
        note = RhythmNote(start_64note, len_64note)
        rhythm_list = [note, ]   
        return rhythm_list
        
    ## 2个字的扩展用模板   
    def __rhythmPattern2(self, start_64note, len_64note, need_expand):  
        # 2个音符:   如果need_expand，则平分 
        ## 概率表：50% 2=1+1  30% 2=1.5+0.5  20% 2=0.5+1.5 ##  
        rhythm_list = []  
        # 共三种分法
        c1 = self.__splitHalf(start_64note, len_64note)
        c2 = self.__splitHalf31(start_64note, len_64note)
        c3 = self.__splitHalf13(start_64note, len_64note)
        # 检查分法，不能拆分到小于最小节奏单位
        if c2[1].len_64note < self.SHORTEST_64NOTE:
            c2 = c1
        if c3[0].len_64note < self.SHORTEST_64NOTE:
            c3 = c1
        
        choice_list = (c1, c2, c3)
      
        # 按概率拆分 
        if need_expand:
            # 需扩展， 只能平分
            p1, p2, p3 = 100, 0, 0
        else:
            # 不许扩展，随机
            p1, p2, p3 = 50, 30, 20
        probability_list = (p1, p2, p3)  
        # 概率选出
        i, rhythm_list = RandPercent(probability_list, choice_list) 

            
        return rhythm_list
             
    """ 优化节奏 """
    def _smoothRhythm(self, rhythm_list):
        """ 优化节奏 """
        if rhythm_list == None or len(rhythm_list) <= 2:
            return rhythm_list
            
        ## 0. 处理弱起
        next_weak_start_64 = LEN_2BARs - self.weak_beat_count * LEN_4NOTE
        # （1）start64note在下一句的弱起中
        while rhythm_list[-1].start_64note >= next_weak_start_64:
            # 删除音符，取出最长的音符, 拆成2个
            rhythm_list = rhythm_list[:-1]
            self.__splitLongestNote(rhythm_list) 
        # （2）end64note在下一句的弱起中
        last_note = rhythm_list[-1]
        if last_note.end_64note >= next_weak_start_64:
            # 修改长度
            last_note.setLen64note( last_note.len_64note - ( last_note.end_64note - next_weak_start_64 ))
 
        ## 1. 去除结尾短音符(至少要4分音符) and (最后一个音符起始必须<=于96)
        while len(rhythm_list) >= 3 and (rhythm_list[-1].len_64note <= LEN_4NOTE or rhythm_list[-1].start_64note > 96):
            # 1.1 最后一个音符 <= 4分音符, 合并最后2个音符
            last_note = rhythm_list[-1]
            last_2_note = rhythm_list[-2]
            last_2_note.setLen64note(last_2_note.len_64note + last_note.len_64note)
            # 修改list
            rhythm_list = rhythm_list[:-2]
            # 1.2 取出最长的音符, 拆成2个
            self.__splitLongestNote(rhythm_list) 
            # 1.3 追加最后的长音符
            rhythm_list.append(last_2_note) 
         
        ## 2. 缩短结尾长音符
        last_note = rhythm_list[-1] 
        if len(rhythm_list) >= 3 and last_note.end_64note == LEN_2BARs: 
            # 若 > 2分音符 + 4分， 最后留出1.5拍
            if last_note.len_64note > LEN_2NOTE + LEN_4NOTE:
                last_note.setLen64note(last_note.len_64note - (LEN_4NOTE + LEN_8NOTE))
            # 若 > 2分音符， 最后留出1拍
            elif last_note.len_64note > LEN_2NOTE:
                last_note.setLen64note(last_note.len_64note - LEN_4NOTE)
            # 若 > 4分音符， 最后留出0.5拍
            elif last_note.len_64note > LEN_4NOTE:
                last_note.setLen64note(last_note.len_64note - LEN_8NOTE)
            # 修改list
            rhythm_list[-1] = last_note
            
        ## 3. 量化为16分音符
        i = 0
        while i < len(rhythm_list):
            if rhythm_list[i].start_64note % LEN_16NOTE != 0:
                # 修改起始
                off = rhythm_list[i].start_64note % LEN_16NOTE
                if i == 0:
                    rhythm_list[i].start_64note -= off 
                    rhythm_list[i].setLen64note(rhythm_list[i].len_64note + off)
                else:
                    pre_len = rhythm_list[i - 1].len_64note
                    cur_len = rhythm_list[i].len_64note
                    if pre_len >= cur_len or off >= rhythm_list[i].len_64note:
                        # 前音长，往前移动
                        rhythm_list[i - 1].setLen64note(rhythm_list[i].len_64note - off)
                        rhythm_list[i].start_64note -= off 
                        rhythm_list[i].setLen64note(rhythm_list[i].len_64note + off)
                    else:
                        # 后音长，往后移动
                        rhythm_list[i - 1].setLen64note(rhythm_list[i].len_64note + off)
                        rhythm_list[i].start_64note += off 
                        rhythm_list[i].setLen64note(rhythm_list[i].len_64note - off) 
            i += 1 
        # 返回
        return rhythm_list
         
    """ 处理缓存cache """
    def modifyCacheRhythm(self, cache_rhythm_list, cache_melody_list, new_num_note):
        """ 修改缓存的节奏，用来处理字数不同的情况 
            规则：增加连音符号- || 拆分弱音
        """
        cache_num_note = len(cache_rhythm_list) 
        if self.is_debug: print "cache_num_note == new_num_note ", cache_num_note, new_num_note
        if cache_num_note == new_num_note:
            # 音符相同
            pass
        elif cache_num_note > new_num_note:
            # 音符多了，需要合并 
            while len(cache_rhythm_list) > new_num_note:
                self.__joinShortestCacheNote(cache_rhythm_list, cache_melody_list)   
        else:
            # 音符少了，需要拆分弱音
            while len(cache_rhythm_list) < new_num_note:
                self.__splitLongestCacheNote(cache_rhythm_list, cache_melody_list)
                
        # 优化
        cache_rhythm_list = self._smoothRhythm(cache_rhythm_list)
        
        return cache_rhythm_list
        
    def __splitLongestNote(self, rhythm_list ):
        """ 取出最长的音符, 拆成2个 
            @exclude_last_note: 是否排除最后一个音符
        """ 
        # 求出最长音符 
        longest_index = self.__getLongestNoteIndex(rhythm_list)
        longest_note = rhythm_list[longest_index]
        split_list = self._structDispatcher( 2, longest_note.start_64note, longest_note.len_64note) 
        # 修改list
        rhythm_list[longest_index] = split_list[0]
        rhythm_list.insert(longest_index + 1, split_list[1])
         
    def __splitLongestCacheNote(self, rhythm_list, melody_list ):
        """ 【处理缓存】取出最长的音符, 拆成2个 （最后一个音符不拆）
        """ 
        # 求出最长音符 
        longest_index = self.__getLongestNoteIndex(rhythm_list[:-1])
        longest_note = rhythm_list[longest_index]
        split_list = self._structDispatcher( 2, longest_note.start_64note, longest_note.len_64note) 
        # 修改节奏
        rhythm_list[longest_index] = split_list[0]
        rhythm_list.insert(longest_index + 1, split_list[1])
        # 修改音高
        melody_list.insert(longest_index + 1, melody_list[longest_index]) 
        
    def __joinShortestCacheNote(self, rhythm_list, melody_list):
        """ 【处理缓存音符】取出最短的音符, 合并，合并后也需要是最短的音符 """ 
        # 从短到长排列list
        length_list, index_list = self.__sortNoteIndex(rhythm_list) 
        num_note = len(rhythm_list)
        if self.is_debug: print "length_list, index_list ", length_list, index_list, "num_note =", num_note
        # 循环最短音符列表，找到相邻的序号，选出3个候补
        cand_len_list, cand_i1_list, cand_i2_list = [], [], []  
        for i in xrange(num_note - 1):
            for j in xrange(i + 1, num_note): 
                if (index_list[i] == index_list[j] + 1 and not self.__isStrong(rhythm_list[index_list[i]].start_64note)) or \
                   (index_list[i] == index_list[j] - 1 and not self.__isStrong(rhythm_list[index_list[j]].start_64note)):
                    # 如果相邻，且后音不是强拍，则记录
                    cand_len_list.append(length_list[i] + length_list[j])
                    cand_i1_list.append(index_list[i])
                    cand_i2_list.append(index_list[j])
            # 查找5个
            if len(cand_len_list) >= 5:
                break
        if self.is_debug: print " cand_len_list =", cand_len_list, cand_i1_list, cand_i2_list
        # 查找合并长度最短的序号
        min_index = cand_len_list.index(min(cand_len_list))
        i1 = cand_i1_list[min_index]
        i2 = cand_i2_list[min_index] 
        # 合并i1+i2
        if i1 > i2: i1, i2 = i2, i1    # 保证i1 < i2
        rhythm_list[i1].setLen64note(rhythm_list[i1].len_64note + rhythm_list[i2].len_64note) 
        # 删除i2
        del rhythm_list[i2]
        # 修改音高list
        del melody_list[i2] 
  
        
    """ 
        节奏模板 （固定，专门用来1字和2字节奏）
    """
    ## 1个字的节奏   
    def __rhythmTemplate1(self, start_64note, len_64note, has_weak = False ):
        # 1个音符   不用扩展，一句就一个歌词
        # 起点随机, 长度随机 
        rhythm_list = []
        # 起始： 60%在第一拍，20%在第二拍，20%在第三拍 | 如果有弱起，则起点必须为开始
        if has_weak:
            p1, p2, p3 = 100, 0, 0
        else:
            p1, p2, p3 = 60, 20, 20 
        c1, c2, c3 = 0, 16, 32
        probability_lsit = (p1, p2, p3)
        choice_list = (c1, c2, c3)  
        i, note_start = RandPercent(probability_lsit, choice_list) 
        # 长度： 60%=64，20%=48，20%=80
        p1, p2, p3 = 60, 20, 20 
        c1, c2, c3 = 48, 64, 80
        probability_lsit = (p1, p2, p3)
        choice_list = (c1, c2, c3)  
        i, note_len = RandPercent(probability_lsit, choice_list)  
        # 处理弱起
        if self.weak_beat_count > 0 and note_start + note_len > len_64note - self.weak_beat_count * LEN_4NOTE:
        		note_len = len_64note - self.weak_beat_count * LEN_4NOTE - note_start
        # note
        note = RhythmNote(note_start + start_64note, note_len) 
        # 保存音符
        rhythm_list.append(note)
        return rhythm_list
         
    ## 2个字的节奏   
    def __rhythmTemplate2(self, start_64note, len_64note ):  
        # 2个音符：起点随机, 长度随机
        
        rhythm_list = []
        ## 概率表：25% 2=1+1,   25% 2=1+0.5,  25% 2=0.5+1,  25% 2=0.5+0.5 ##
        c1 = self.__splitHalf(start_64note, len_64note)       # 2个全音符
        c2 = self.__splitHalf(start_64note, len_64note)       # 1个全音符+1个2分音符
        c2[1].setLen64note(LEN_2NOTE)
        c3 = self.__splitHalf13(start_64note, len_64note)    # 1个2分音符+1个全音符
        c3[1].setLen64note(LEN_1NOTE)
        c4 = self.__splitHalf13(start_64note, len_64note)     # 1个2分音符+1个2分音符
        c4[1].setLen64note(LEN_2NOTE)
        choice_list = (c1, c2, c3, c4)
         
        # 按概率计算
        p1, p2, p3, p4 = 25, 25, 25, 25 
        probability_lsit = (p1, p2, p3, p4)
        choice_list = (c1, c2, c3, c4)  
        i, rhythm_list = RandPercent(probability_lsit, choice_list)   
            
        # 处理弱起
        last_note = rhythm_list[-1]
        if self.weak_beat_count > 0 and last_note.start_64note + last_note.len_64note > start_64note + len_64note - self.weak_beat_count * LEN_4NOTE:
        		last_note.setLen64note(start_64note + len_64note - self.weak_beat_count * LEN_4NOTE - last_note.start_64note)
        		
        return rhythm_list 
         
    """ 弱起节奏模板 """
    ## 
    def __rhythmWeakTemplate(self, num_note):
        # 根据不同弱起音符个数生成
        rhythm_list = []
        
        if num_note == 1:
            # 1个音符，
            p1, p2 = 25, 25
            c1 = [RhythmNote(-16, 16),]
            c2 = [RhythmNote(-8, 8), ]  
            probability_lsit = (p1, p2)
            choice_list = (c1, c2)  
        elif num_note == 2:
            # 2个音符，
            p1 = 25
            c1 = [RhythmNote(-16, 8), RhythmNote(-8, 8)] 
            probability_lsit = (p1, )
            choice_list = (c1, )  
        elif num_note == 3:
            # 3个音符，
            p1 = 25
            c1 = [RhythmNote(-24, 8), RhythmNote(-16, 8), RhythmNote(-8, 8)] 
            probability_lsit = (p1, )
            choice_list = (c1, )  
        elif num_note == 4:
            # 4个音符，
            p1 = 25
            c1 = [RhythmNote(-32, 8), RhythmNote(-24, 8), RhythmNote(-16, 8), RhythmNote(-8, 8)] 
            probability_lsit = (p1, )
            choice_list = (c1, )  
        else:
            # 不支持更多音符
            print "Error: num_note =", num_note
            raise 
            
            #if len_beat == 1:
            #    # 长度1拍
            #elif len_beat == 2:
            #    # 长度2拍 
        i, rhythm_list = RandPercent(probability_lsit, choice_list)  
        return rhythm_list
 
    """ 通用方法 """
    def __splitHalf(self, start, length):
        # 2= 1+1
        half = length/2
        note1 = RhythmNote(start, half)
        note2 = RhythmNote(start + half, length - half)
        return [note1, note2]
        
    def __splitHalf13(self, start, length):
        # 2= 0.5+1.5
        half = length/2
        half2 = half/2
        note1 = RhythmNote(start, half2)
        note2 = RhythmNote(start + half2, length - half2)
        return [note1, note2]
        
    def __splitHalf31(self, start, length):
        # 2= 1.5+0.5
        half = length/2
        half2 = half/2
        note1 = RhythmNote(start, half + half2)
        note2 = RhythmNote(start + half + half2, length - half - half2)
        return [note1, note2]
        
    def __getLongestNoteIndex(self, rhythm_list):
        # 取出最长的音符
        longest_len = 0 
        longest_index = 0 
        for i, rhythm in enumerate(rhythm_list):
            if rhythm.len_64note > longest_len:
                longest_len = rhythm.len_64note 
                longest_index = i
        return longest_index
        
    def __isStrong(self, start_64note):
        # 是否是强拍
        return start_64note % self.STRONG_64NOTE == 0

    def __sortNoteIndex(self, rhythm_list):
        """ 音符排序：从短到长 """
        num_note = len(rhythm_list)
        length_list = [x.len_64note for x in rhythm_list]
        index_list = [i for i in xrange(num_note)] 
        # 冒泡
        for i in xrange(num_note):
            for j in xrange(num_note - 1):
                k = j + 1
                if length_list[j] > length_list[k]:
                    length_list[j], length_list[k] = length_list[k], length_list[j]
                    index_list[j], index_list[k] = index_list[k], index_list[j]
        return length_list, index_list


class RhythmNote:
    def __init__(self, start_64note, len_64note):
        self.start_64note = start_64note
        self.len_64note = len_64note 
        self.end_64note = start_64note + len_64note 
        
    def setLen64note(self, len_64note):
        self.len_64note = len_64note
        self.end_64note = self.start_64note + len_64note 
        
    def __repr__(self):
        return "[%d,%d,%d]"%(self.start_64note, self.len_64note, self.end_64note)
        


#########################
#####   TEST
#########################
def printRhythm(rhythm_list):
    # 每个占位符=32分音符
    for rhythm in rhythm_list:
        print "|", 
        for i in xrange(rhythm.len_64note/2 - 2):
            print "_", 
        print "|", 
    print ""

#TODO：  

if __name__ == "__main__":
    # 设置参数
    num_note = 12
    weak_beat_count = 1
    weak_note_num = 2
    
    # 执行
    rhythm_maker = RhythmMaker()
    rhythm_maker.initRhythm(num_note, weak_beat_count = weak_beat_count, weak_note_num = weak_note_num)
    rhythm_list = rhythm_maker.do()
    
    # 打印标准2小节
    print "Standard 2 bars:"
    printRhythm([RhythmNote(0, 64), RhythmNote(64, 64)])
    # 打印生成节拍
    print "Rhythm 2 bars:"
    printRhythm(rhythm_list)




