// Midi.h: interface for the Midi class.
//
//////////////////////////////////////////////////////////////////////

#include <stdio.h>

#ifndef MIDI_H 
#define MIDI_H 

#define MAX_SIZE 1000
#define MAX_TRACK 32

#pragma pack(1)//C������������n���ֽڶ���

typedef struct tagMIDIHEADER{
	char mhType[4];//chunk��־"MThd"
	unsigned int mhSize;// Chunk���ݲ��ֵĳ���,����һ��32λ��������,MSB first,�涨Ϊ6
	unsigned short mhFormat;//MIDI�ļ��ĸ�ʽ.����һ��16λ��������,MSB first.��Ч�ĸ�ʽ��:0,1��2
	unsigned short mhNumTracks;//track chunk������.����һ��16λ��������,MSB first
	unsigned short mhDivision;//MIDI �ļ���(һ��)��λ��delta-time��.����һ��16λ��������,MSB first
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
	int miTime;	// ʱ��
	int miLen;	// ʱ��
	int miNo;   // ����
}MIDINOTE;

#pragma pack() // ȡ��1�ֽڶ��뷽ʽ

class Midi  
{
public:
	Midi();
	virtual ~Midi();

private:
	FILE *m_midFile;		//midi�ļ�
	MIDI m_midi;			//midi���� 
	int m_nNoteCount[MAX_TRACK];			// ÿ����������
	float m_fBpm;			//midi���� 

	/* �������ֽ�˳��ı亯�� */ 
	inline void revert_unsigned_short(unsigned short *a);
	inline void revert_unsigned_int(unsigned int *a);
	inline bool IsBigger128(char ch);
	inline int getTime(int *p, int i);			//�õ�delta-time
	inline void ReadMidiInfo();			//��ȡmidi��ϸ��Ϣ
public:
	bool OpenMidi(char* sFilename);	//��Midi�ļ�

	int getTrackCount();	// �������
	int getNoteCountByTrack(int iTrack);  // ������������� 
	int getTickUnit();	// ���tick�ĵ�λ
	float getBpmFloat();		// �������

	int getMidiNote(int iTrack, MIDINOTE *midiNoteList);	//���note����
};


#endif  
