#!/usr/bin/python
# -*- coding: utf-8 -*-

import random

""" 从list中按照概率随机 
使用例：RandPercent( [25,50,25], ["a","b","c"] )
返回：结果的位置索引 + 结果内容
"""
def RandPercent(percent_list, choice_list):
    # 
    rtn = None
    # 检查参数
    if len(percent_list) != len(choice_list):
        return -1, rtn
    
    # 随机参数
    sum_percent = sum(percent_list)
    num_choice = len(percent_list)
    r_int = random.randint(0, sum_percent - 1)

    new_percent_list = []
    for i in xrange(num_choice):
        new_percent_list.append(sum(percent_list[:i+1]))

    # 随机一个
    for i in xrange(num_choice):
        if r_int < new_percent_list[i]: 
            rtn = choice_list[i]            
            break 
    return i, rtn

""" 按照概率随机, 返回随到数据的index
使用例：RandPercentIndex( [25,50,25] ) 
"""
def RandPercentIndex(percent_list):
    # 
    rtn = None
    # 检查参数
    if not percent_list:
        return rtn
    
    num_choice = len(percent_list)
    choice_list = range(num_choice)
    return RandPercent(percent_list, choice_list) 
    
""" 0-99中随机取数 """
def RandInt100():
    return random.randint(0, 99)

"""  随机选数 """
def RandInt(max_int): 
    return random.randint(0, max_int) 
    
""" 指定范围，随机取数 """
def RandIntRange(a, b):
    return random.randint(a, b)
    
""" list中随机取元素 """
def  RandChoice(randlist):
    return random.choice(randlist)
    
"""  洗牌 """
def RandShuffle(randlist):
    tmp_list = randlist[:]
    random.shuffle(tmp_list)
    return tmp_list
    
"""  随机新list，list中的元素是从candidate_list中取出的(可重复) """
def RandNewList(candidate_list, count, must_include_index_list = []):
    """ must_include_index_list: 必须包含的元素index """
    rtn_list = []
    for i in xrange(count):
        x = random.choice(candidate_list)
        rtn_list.append(x)
        
    # 检查是否包括must_include_index_list的元素
    if len(must_include_index_list) > 0:
        must_included = False
        for x in rtn_list:
            if x in must_include_index_list:
                must_included = True
                break
        # 如果未包含，随机替换
        if not must_included:
            i = random.randint(0, count - 1)
            x = random.choice(must_include_index_list)
            rtn_list[i] = x
        
    return rtn_list
    

"""
测试 
"""
if __name__ == "__main__": 
    for i in xrange(10):
        print RandPercent( [25,50,25], ["a","b","c"] )
    
    a = [0, 1, 2, 3, 4]
    RandShuffle(a)
    print a
