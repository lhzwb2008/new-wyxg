#!/bin/sh
name=$1
zhugecount=$2
fugecount=$3
gecicount=$4
geci=$5
velocity=$6
source=$7
melody_range_a=$8
melody_range_b=$9
genre=${10}
emotion=${11}
zhugesize=${12}
fugesize=${13}
chord=`/usr/bin/python2.6 /opt/lampp/htdocs/code/scripts/getchord.py $emotion`
/usr/bin/python2.6 /opt/lampp/htdocs/code/scripts/main.py /home/root/music/mid/$name.mid $zhugecount $fugecount $chord $velocity $melody_range_a $melody_range_b $emotion $zhugesize $fugesize -1
cd /opt/lampp/htdocs/code/scripts/acc
if [ $zhugesize -eq 8 ]
then 
zhugesize0=8
zhugesize1=8
else
zhugesize0=$(( $zhugesize * 2 ))
zhugesize1=0
fi
if [ $fugesize -eq 8 ]
then 
fugesize0=8
fugesize1=8
else
fugesize0=$(( $fugesize * 2 ))
fugesize1=0
fi
/usr/bin/python2.6 /opt/lampp/htdocs/code/scripts/acc/main.py $chord /home/root/music/accmid/$name.mid $velocity $emotion $genre $zhugesize0 $zhugesize1 $fugesize0 $fugesize1
cd /opt/lampp/htdocs/code/scripts/sing
pinyin=`/usr/bin/python2.6 /opt/lampp/htdocs/code/scripts/sing/pinyin.py $geci` 
/opt/lampp/htdocs/code/scripts/sing/testcallso /home/root/music/mid/$name.mid $pinyin $gecicount /home/root/music/wav/$name.wav /opt/lampp/htdocs/code/scripts/sing/voice/$source/inf.n /opt/lampp/htdocs/code/scripts/sing/voice/$source/voice.n 1
/usr/local/bin/timidity -Ow -o /home/root/music/accwav/$name.wav /home/root/music/accmid/$name.mid
/usr/bin/sox /home/root/music/accwav/$name.wav -c1 /home/root/music/accwav/${name}_c1.wav
if [ $genre -eq 0 ];then
/usr/bin/sox -v 0.8 /home/root/music/accwav/${name}_c1.wav /home/root/music/accwav/${name}_v.wav
elif [ $genre -eq 1 ];then
/usr/bin/sox -v 0.5 /home/root/music/accwav/${name}_c1.wav /home/root/music/accwav/${name}_v.wav
elif [ $genre -eq 2 ];then
/usr/bin/sox -v 0.7 /home/root/music/accwav/${name}_c1.wav /home/root/music/accwav/${name}_v.wav
elif [ $genre -eq 3 ];then
/usr/bin/sox -v 0.7 /home/root/music/accwav/${name}_c1.wav /home/root/music/accwav/${name}_v.wav
fi
/usr/bin/sox -m /home/root/music/accwav/${name}_v.wav /home/root/music/wav/${name}.wav /home/root/music/mixwav/$name.wav
/usr/bin/lame /home/root/music/mixwav/$name.wav /home/root/music/mp3/$name.mp3
rm /home/root/music/accwav/$name.wav /home/root/music/accwav/${name}_v.wav  /home/root/music/accwav/${name}_c1.wav /home/root/music/mixwav/$name.wav
