#!/bin/sh
name=$1
zhugecount=$2
fugecount=$3
melody_range_a=$4
melody_range_b=$5
emotion=$6
velocity=$7
zhugesize=$8
fugesize=$9
chord=`/usr/bin/python /opt/lampp/htdocs/core/Public/getchord.py -1`
/usr/bin/python /opt/lampp/htdocs/core/Public/main.py /home/admin/auto-compose-php/music/mid/$name.mid $zhugecount $fugecount $chord $velocity $melody_range_a $melody_range_b $emotion $zhugesize $fugesize
