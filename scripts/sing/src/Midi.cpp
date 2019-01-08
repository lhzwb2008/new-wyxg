// Midi.cpp: implementation of the Midi class.
//
//////////////////////////////////////////////////////////////////////
 
#include "Midi.h"
#include <string.h>
#include <stdlib.h>
#include <math.h>
 
//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

Midi::Midi()
{
}

Midi::~Midi()
{
	fclose(m_midFile);
}

//=============================�����ķֽ���==============================//
inline void Midi::revert_unsigned_short(unsigned short *a) //2�ֽ�little endian->big endian
{ 
	unsigned short left,right; 
	left= right = *a; 
	*a = ((left&0x00ff) << 8) | ((right&0xff00) >> 8); 
} 

inline void Midi::revert_unsigned_int(unsigned int *a)  //4�ֽ�little endian->big endian
{ 
	unsigned int first, second, third, forth; 
	first = second = third = forth = *a; 
	*a = ((first & 0x000000ff) << 24) | ((second & 0x0000ff00) << 8) | 
		((third & 0x00ff0000) >> 8) | ((forth & 0xff000000) >> 24); 
} 

inline bool Midi::IsBigger128(char ch)//�ж�2�ֽ����λ: 1-true; 0-false
{
	if((ch & 0x80) == 0x80) 
		return true;
	return false;
}

inline int Midi::getTime(int *p, int i)//�õ�delta-time
{	
	int t = 0, buf = 0;
	while(IsBigger128(m_midi.mTrack[i].mtData[(*p)++])){//�ж�delta-time����
		t++;
	}
	for(; t >= 0; t--){//����delta-time
		buf += pow(128., t) * (m_midi.mTrack[i].mtData[*p - 1 - t] & 0x7F);
	}
	return buf;
}

inline void Midi::ReadMidiInfo()//��ȡmidi��ϸ��Ϣ
{
	fread(&m_midi.mHeader.mhType, 1, sizeof(char)*4 + sizeof(unsigned int) + sizeof(unsigned short)*3, m_midFile); //��ȡHeader Chunk
    revert_unsigned_int(&m_midi.mHeader.mhSize);//ת��header size
    revert_unsigned_short(&m_midi.mHeader.mhFormat);//ת��header format
    revert_unsigned_short(&m_midi.mHeader.mhNumTracks);//ת��track number
    revert_unsigned_short(&m_midi.mHeader.mhDivision);//ת��header division
	
	int i = 0, j = 0;
	// ѭ����ȡÿ1�����Ϣ
	for( ; i < m_midi.mHeader.mhNumTracks && i < MAX_TRACK; i++ )
	{
		// ��ȡ��Ϣ
		fread(&m_midi.mTrack[i].mtType, 1, 4, m_midFile);//��ȡTrack Chunk����
		fread(&m_midi.mTrack[i].mtSize, 1, sizeof(unsigned int), m_midFile);//��ȡTrack Chunk���� 
		revert_unsigned_int(&m_midi.mTrack[i].mtSize);
		m_midi.mTrack[i].mtData = new unsigned char[m_midi.mTrack[i].mtSize]; 
		fread(m_midi.mTrack[i].mtData, 1, m_midi.mTrack[i].mtSize, m_midFile);//��ȡTrack Chunk����
	
		//����midi���� ���������Ϣ
		int p = 0, ip = 0, now = 0, bytelen = 0;
		char event = 0;
		while(p <= m_midi.mTrack[i].mtSize)
		{
			now += getTime(&p, i);//�õ�delta-time
			if(IsBigger128(m_midi.mTrack[i].mtData[p])){//�����¼�
				event = m_midi.mTrack[i].mtData[p];
				p++;
			}
			if(event >= (char)0x80 && event <= (char)0x8f){
				p = p + 2;
			}else if(event >= (char)0x90 && event <= (char)0x9f){//��������
				if(m_midi.mTrack[i].mtData[p + 1] != 0x00){//�Ǿ���
					//m_midiinfo[ip].miHeight = m_midi.mTrack[i].mtData[p];
					//m_midiinfo[ip].miTime = now;
					ip++;
				}
				p = p + 2;
			}else if(event >= (char)0xa0 && event <= (char)0xaf){
				p = p + 2;
			}else if(event >= (char)0xb0 && event <= (char)0xbf){
				p = p + 2;
			}else if(event >= (char)0xc0 && event <= (char)0xcf){
				p = p + 1;
			}else if(event >= (char)0xd0 && event <= (char)0xdf){
				p = p + 1;
			}else if(event >= (char)0xe0 && event <= (char)0xef){
				p = p + 2;
			}else if(event == (char)0xf0){
				p += getTime(&p, i);
			}else if(event == (char)0xf7){
				p += getTime(&p, i);
			}else if(event == (char)0xff){
				switch(m_midi.mTrack[i].mtData[p++]){
					case 0x00 : p = p + 3; break;
					case 0x2F : p = p + 2; break;
					case 0x51 : // ����   FF 51 03 xx xx xx
						// m_midi.mTrack[i].mtData[p] ��Ϊ03
						m_fBpm = 60000000.f / (
							(m_midi.mTrack[i].mtData[p+1]& 0xFF) * 65536 +
							(m_midi.mTrack[i].mtData[p+2]& 0xFF) * 256 +
							(m_midi.mTrack[i].mtData[p+3]& 0xFF) );
						p = p + 4; break;
					case 0x58 : p = p + 5; break;
					case 0x59 : p = p + 3; break;
					case 0x03 : // �����
						bytelen = getTime(&p, i);  
						p = p + bytelen; break; 
					default : p = p + getTime(&p, i);
				}		
			}
		}
		// ��¼��������
		m_nNoteCount[i] = ip;
	} 
}

int Midi::getTrackCount()
{
	// �������
	return m_midi.mHeader.mhNumTracks;
}
int Midi::getNoteCountByTrack(int iTrack)  
{
	// ������������� 
	return m_nNoteCount[iTrack];
} 
int Midi::getTickUnit()  
{
	// ������� 
	return (int)(m_midi.mHeader.mhDivision);
}
float Midi::getBpmFloat()
{
	// ����
	return m_fBpm;
}

bool Midi::OpenMidi(char* sFilename)//��Midi�ļ�
{
	m_midFile = fopen(sFilename, "rb");
	if(!m_midFile)
	{
		return false;
	}
	ReadMidiInfo();//��ȡmidi��ϸ��Ϣ
	return true;
}


int Midi::getMidiNote(int i, MIDINOTE *midiNoteList)	//���note����
{
	if ( i >= m_midi.mHeader.mhNumTracks )
		return 0;

	//����midi���� ���������Ϣ
	int j, p = 0, ip = 0, now = 0;
	char event = 0;
	while(p <= m_midi.mTrack[i].mtSize)
	{
		now += getTime(&p, i);//�õ�delta-time
		if(IsBigger128(m_midi.mTrack[i].mtData[p])){//�����¼�
			event = m_midi.mTrack[i].mtData[p];
			p++;
		}
		if(event >= (char)0x80 && event <= (char)0x8f){
			// �ɿ�����
			int midino = m_midi.mTrack[i].mtData[p];
			int vel = m_midi.mTrack[i].mtData[p + 1];
			// ����-�����ͬ����������������
			for ( j = ip - 1; j >= 0; j-- )
			{
				if ( midiNoteList[j].miNo == midino && midiNoteList[j].miLen == 0)
				{
					midiNoteList[j].miLen = now - midiNoteList[j].miTime;
					break;
				}
			}
			p = p + 2;
		}else if(event >= (char)0x90 && event <= (char)0x9f){
			//��������
			int midino = m_midi.mTrack[i].mtData[p];
			int vel = m_midi.mTrack[i].mtData[p + 1];
			if( vel != 0x00){
				//�Ǿ���
				midiNoteList[ip].miNo = midino;
				midiNoteList[ip].miTime = now;
				midiNoteList[ip].miLen = 0;
				ip++;
			}
			else{
				for ( j = ip - 1; j >= 0; j-- )
				{
					if ( midiNoteList[j].miNo == midino && midiNoteList[j].miLen == 0)
					{
						midiNoteList[j].miLen = now - midiNoteList[j].miTime;
						break;
					}
				}
			} 
			p = p + 2;
		}else if(event >= (char)0xa0 && event <= (char)0xaf){
			p = p + 2;
		}else if(event >= (char)0xb0 && event <= (char)0xbf){
			p = p + 2;
		}else if(event >= (char)0xc0 && event <= (char)0xcf){
			p = p + 1;
		}else if(event >= (char)0xd0 && event <= (char)0xdf){
			p = p + 1;
		}else if(event >= (char)0xe0 && event <= (char)0xef){
			p = p + 2;
		}else if(event == (char)0xf0){
			p += getTime(&p, i);
		}else if(event == (char)0xf7){
			p += getTime(&p, i);
		}else if(event == (char)0xff){
			switch(m_midi.mTrack[i].mtData[p++]){
			case 0x00 : p = p + 3; break;
			case 0x2F : p = p + 2; break;
			case 0x51 : p = p + 4; break;
			case 0x58 : p = p + 5; break;
			case 0x59 : p = p + 3; break;
			default : p = p + getTime(&p, i);
			}		
		}
	} 

}