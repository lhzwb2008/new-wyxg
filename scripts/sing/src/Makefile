CC = g++

# testniaolib is a sample code to call ncore.h
testniaolib:  pinyinConverter.cpp TTSong.cpp ncore.cpp testNiaoLib.cpp pinyinConverter.h TTSong.h ncore.h gbunicode.h Wave.h Midi.h Midi.cpp
	$(CC) -o testNiaoLib Midi.cpp pinyinConverter.cpp TTSong.cpp ncore.cpp testNiaoLib.cpp


# libniaoso is a shared .so library
libniaoso: pinyinConverter.cpp TTSong.cpp ncore.cpp pinyinConverter.h TTSong.h ncore.h gbunicode.h  Wave.h Midi.h Midi.cpp
	$(CC) Midi.cpp pinyinConverter.cpp TTSong.cpp ncore.cpp -fPIC -shared -o libniao.so

test: testNiaoLib 
	./testNiaoLib ./song/test.mid 一闪一闪亮晶晶 7 ./out.wav ./voice/niaotest/inf.n ./voice/niaotest/voice.n 0
