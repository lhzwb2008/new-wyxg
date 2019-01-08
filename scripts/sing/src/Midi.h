// Midi.h: interface for the Midi class.
//
//////////////////////////////////////////////////////////////////////

#include <stdio.h>

#ifndef MIDI_H 
#define MIDI_H 

#define MAX_SIZE 1000
#define MAX_TRACK 32

#pragma pack(1)//C编译器将按照n个字节对齐

typedef struct tagMIDIHEADER{
	char mhType[4];//chunk标志"MThd"
	unsigned int mhSize;// Chunk数据部分的长度,这是一个32位二进制数,MSB first,规定为6
	unsigned short mhFormat;//MIDI文件的格式.这是一个16位二进制数,MSB first.有效的格式是:0,1和2
	unsigned short mhNumTracks;//track chunk的数量.这是一个16位二进制数,MSB first
	unsigned short mhDivision;//MIDI 文件中(一个)单位的delta-time数.这是一个16位二进制数,MSB first
}MIDIHEADER;

typedef struct tagMIDITRACK{
    /* Here's the 8 byte header that all chunks must have */
    char mtType[4];   /* This will be 'M','T','r','k' */
	unsigned int mtSize;  /* This will be the actual size of Data[] */
    /* Here are the data bytes */
	unsigned char *mtData;  /* Its actual size is Data[mtSize] */
}MIDITRACK;

typedef struct tagMIDI{
	MIDIHEADER mHeader;
	MIDITRACK mTrack[MAX_TRACK];
}MIDI;

typedef struct tagMIDINOTE{
	int miTime;	// 时间
	int miLen;	// 时长
	int miNo;   // 音高
}MIDINOTE;

#pragma pack() // 取消1字节对齐方式

class Midi  
{
public:
	Midi();
	virtual ~Midi();

private:
	FILE *m_midFile;		//midi文件
	MIDI m_midi;			//midi内容 
	int m_nNoteCount[MAX_TRACK];			// 每轨音符个数
	float m_fBpm;			//midi曲速 

	/* 整形数字节顺序改变函数 */ 
	inline void revert_unsigned_short(unsigned short *a);
	inline void revert_unsigned_int(unsigned int *a);
	inline bool IsBigger128(char ch);
	inline int getTime(int *p, int i);			//得到delta-time
	inline void ReadMidiInfo();			//读取midi详细信息
public:
	bool OpenMidi(char* sFilename);	//打开Midi文件

	int getTrackCount();	// 轨道个数
	int getNoteCountByTrack(int iTrack);  // 轨道的音符个数 
	int getTickUnit();	// 轨道tick的单位
	float getBpmFloat();		// 轨道曲速

	int getMidiNote(int iTrack, MIDINOTE *midiNoteList);	//获得note数据
};


#endif  
