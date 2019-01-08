#!/bin/sh
name=$1
gecicount=$2
geci=$3
template_num=$4
source=$5

cd /opt/lampp/htdocs/code/scripts/sing
pinyin=`/usr/bin/python2.6 /opt/lampp/htdocs/code/scripts/sing/pinyin.py $geci` 
/opt/lampp/htdocs/code/scripts/sing/testcallso /opt/lampp/htdocs/code/template/$template_num.mid $pinyin $gecicount /home/root/music/wav/$name.wav /opt/lampp/htdocs/code/scripts/sing/voice/$source/inf.n /opt/lampp/htdocs/code/scripts/sing/voice/$source/voice.n 1
/usr/bin/sox /opt/lampp/htdocs/code/template/$template_num.wav -c1 /home/root/music/accwav/${template_num}_c1.wav
/usr/bin/sox -m /home/root/music/accwav/${template_num}_c1.wav /home/root/music/wav/${name}.wav /home/root/music/mixwav/$name.wav
/usr/bin/lame /home/root/music/mixwav/$name.wav /home/root/music/mp3/$name.mp3

