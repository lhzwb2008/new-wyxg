// Wave.h: interface for the Wave.
//
//////////////////////////////////////////////////////////////////////
  
#ifndef WAVE_H
#define WAVE_H
  
typedef struct tagWAVEHEADER{
	char dID[4];	//"RIFF"
	unsigned long dSize;	//数据大小
	char dType[4];	//数据类型"WAVE"
}WAVEHEADER;

typedef struct tagPCMWAVEFORMAT{ 
	unsigned short wFormatTag;//记录着此声音的格式代号，例如WAVE_FORMAT_PCM，WAVE_F0RAM_ADPCM等等
	unsigned short nChannels;//记录声音的频道数 
	unsigned long  nSamplesPerSec;//记录每秒取样数 
	unsigned long  nAvgBytesperSec;//记录每秒的数据量 
	unsigned short nBlockAlign; //记录区块的对齐单位(每个采样需要的字节数)
	unsigned short wBitsPerSample;//记录每个取样所需的位元数(bit)
	char bAdd[2];//附加内容
}PCMWAVE_FORMAT;

typedef struct tagFMTCHUNK{
	char dId[4];  //块标志"fmt "
	unsigned long  dSize;  //块大小sizeof(PCMWAVEFORMAT)16或18
	PCMWAVE_FORMAT pcmwaveformat; //块内容
}FMTCHUNK;

typedef struct tagFACTCHUNK{
	char dId[4];  //块标志"fact"
	unsigned long  dSize;  //块大小(4)
	char bFact[4]; //块内容
}FACTCHUNK;

typedef struct tagDATACHUNK{
	char dId[4];  //块标志"data"
	unsigned long  dSize;  //块大小
	char *bData; //块内容
	/*ChunkData中所包含的数据是以字(WORD)为单位排列的，如果数据长度是奇数，则在最后添加一个空(NULL)字节*/
}DATACHUNK;

typedef struct tagWAVE{
	WAVEHEADER header;
	FMTCHUNK fmt;
	FACTCHUNK fact;
	DATACHUNK data;
}WAVE;


////////////////////////////////////////
//	methods
////////////////////////////////////////
 
/* 写入wave信息 */
int writeWaveHeader( FILE *fp, int rawfile_size )
{  
	char RIFF[] = "RIFF";
    char WAVE[] = "WAVE";
	int file_size = rawfile_size + 36;
	char fmt_chunk[] = "fmt ";
	char data_chunk[] = "data";

	int chunk_size = 16;
	short formatID = 1;
	short channel = 1;           /* mono:1·stereo:2 */
	int fs = 44100;
	int data_speed;
	short block_size = 2;            /* 16bit, mono => 16bit*1=2byte */
	short bit = 16;

	/* RIFF header */
	fwrite(RIFF, sizeof(char), 4, fp);
	/* file size */
	fwrite(&file_size, sizeof(int), 1, fp);
	/* WAVE header */
	fwrite(WAVE, sizeof(char), 4, fp);
	/* fmt chunk */
	fwrite(fmt_chunk, sizeof(char), 4, fp);
	/* chunk size */
	fwrite(&chunk_size, sizeof(int), 1, fp);
	/* formatID */
	fwrite(&formatID, sizeof(short), 1, fp);
	/* channel (mono:1·stereo:2) */
	fwrite(&channel, sizeof(short), 1, fp);
	/* sampling frequency */
	fwrite(&fs, sizeof(int), 1, fp);
	/* data speed */
	data_speed = fs * bit / 8 * formatID;
	fwrite(&data_speed, sizeof(int), 1, fp);
	/* block size */
	block_size = bit / 8 * formatID;
	fwrite(&block_size, sizeof(short), 1, fp);
	/* bit number */ 
	fwrite(&bit, sizeof(short), 1, fp);

	/* data chunk */
	fwrite(data_chunk, sizeof(char), 4, fp);
	/* file size of data */
	fwrite(&rawfile_size, sizeof(int), 1, fp);
 
	return 1;
}

#endif                          /* !WAVE_H */
