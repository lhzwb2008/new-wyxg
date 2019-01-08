#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from pypinyin import lazy_pinyin,load_phrases_dict

geci=unicode(sys.argv[1],'utf-8')
load_phrases_dict({u'一地': [[u'yi'], [u'di']],u'乾坤': [[u'qian'], [u'kun']],u'故地': [[u'gu'], [u'di']],u'不得了':[[u'bu'],[u'de'],[u'liao']],u'满地':[[u'man'],[u'di']],u'不见了':[[u'bu'],[u'jian'],[u'liao']],u'了解':[[u'liao'],[u'jie']],u'大黄':[[u'da'],[u'huang']]})
pinyin = lazy_pinyin(geci)
pinyin = ','.join(pinyin)
pinyin = pinyin.encode("utf-8")
pinyins = pinyin.split(',')
newpinyins = []
for p in pinyins:
	if(p=="--"):p="-,-"
	if(p=="---"):p="-,-,-"
	if(p=="----"):p="-,-,-,-"
	if(p=="-----"):p="-,-,-,-,-"
	if(p=="------"):p="-,-,-,-,-,-"
	if(p=="-------"):p="-,-,-,-,-,-,-"
	if(p=="--------"):p="-,-,-,-,-,-,-,-"
	if(p=="---------"):p="-,-,-,-,-,-,-,-,-"
	if(p=="----------"):p="-,-,-,-,-,-,-,-,-,-"
	if(p=="-----------"):p="-,-,-,-,-,-,-,-,-,-,-"
	if(p=="------------"):p="-,-,-,-,-,-,-,-,-,-,-,-"
	newpinyins.append(p)
print ','.join(newpinyins)
