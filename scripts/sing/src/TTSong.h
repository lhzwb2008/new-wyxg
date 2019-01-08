
#ifndef TTSONG_H
#define TTSONG_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include "pinyinConverter.h" 


#define MAX_BEND_FRAME 50	// 弯曲部分最长100
#define MAX_BAND_MIDINO 2	// 弯曲部分最大幅度 2音高

#define PRE_YM_PERCENT 0.3 // 声母占用前拼音的最大%
#define PRE_SIL_PERCENT 0.7 // 声母占用前静音的最大%

#define P_SIL_SAMPLE 100 // 静音时tm长度
#define MAX_BUFF_SIZE 1024 

#define SRATE 44100
#define FRAME_MS 10									   // 1frame = 10ms
#define SAMPLE_PER_FRAME (SRATE / (1000 / FRAME_MS))   // 1个frame=10ms
#define LAST_SIL_FRAME 10			// 最后一个音符结束后，加入多长的静音： 10frame 
#define PINYIN_LEN 10 // 歌词发音的字符串的长度:10个char

#define MAX_AMP 32767.0
#define MIN_AMP -32768.0

/*  voice文件  */
typedef struct _INF_pinyin_info { 
	char *pinyin;				/* current pinyinn */
	int voice_file_offset;      /* start pos in voice.d */
	int voice_file_len;			/* file length in voice.d */  
	int vowel_sample;			/* vowel_sample */
	int tail_sample;			/* tail_sample */
	float pitch;				/* pitch */ 
	int amp_part;				/* amp_part */
	int amp_all;				/* amp_all */ 
	int len_sample;				/* 16bit: voice_file_len / 2 */ 
} INF_pinyin_info;

/*  inf文件 */
typedef struct _VOICE_bank {
	char *path_inf;							/* path of inf file */
	char *path_voice;						/* path of voice file */
 
	INF_pinyin_info *pinyin_info_list;		/* information of voice.d */

	int inf_ver;
	int num_pinyin;

	bool stop;

} VOICE_bank;

/* public methods */
void initVoiceBank( VOICE_bank *bank );
 
int loadVoiceBank( VOICE_bank *bank, char *fn_inf, char *fn_voice );

void clearVoiceBank( VOICE_bank *bank );

int checkPinyinList(VOICE_bank *bank, char **pinyin_list, int num_pinyin, int *wrong_index_list);
 
int makeVoice(VOICE_bank *bank, char **pinyin_list,
				int *start_sample_list, int *len_sample_list, int *midi_no_list, 
				float *cle_list, float *vel_list, int num_all_note,
				float *pit_list, float *vol_list, int len_frame, 
				short *wave_data, int out_len_sample,
				float volume, 
				int (*play_callback)( short *wave_data, int len_sample, int cur_sample, int total_sample ) );
 
void stopSynthesis( VOICE_bank *bank, bool is_stop);

int readSongFile(char *fn_nn, char ***pinyin_list, int **start_sample_list, int **len_sample_list,
				int **midi_no_list,	float **cle_list, float **vel_list,	int *num_all_note,		
				float **pit_list, float **vol_list,	int *len_frame, short **wave_data,int *len_sample,
                int need_autoconfig  
		);

/* private methods */
int synthesizeSingleVoice(VOICE_bank *bank, INF_pinyin_info *pinyin_info, 
					int out_sm_sample, int out_len_sample, float *out_ori_f0_list, float *out_ori_vol_list, 
					int overlap_sample, int last_overlap_sample, 
					bool has_trans_info, INF_pinyin_info *trans_info,
					short *syn_data );
 
void calculateStrentchSec( int *sec_start_list, int *sec_end_list, int num_sec, int s1, int s2, int s3, int s4 = 0);

void d_(float *__, int aa, float ii_, float amplitude, float _______, int pspf);

void db(float *__, int aa, float *___, int aaa , float amplitude, 
					   float *___a, int a_, float *_a_, int o, int pspf );

void _(float *__, int __a, float *_______, int day, float amplitude, 
					   float *___, int ___a, float *________, int night, int pspf,
					   int *ii, int *jjj,
					   int *jj, int *iii, int hz );

int getPinyinInfoInInf( VOICE_bank *bank, char *pinyin_str, int midi_no, int len_sample, 
							   INF_pinyin_info *found_pinyin_info);

/* static methods */
static int extractWaveFromVoice( VOICE_bank *bank, int voice_file_offset, int voice_file_len, 
									float *wave_data, int len_sample);

static float hummingWin(int n, int win_size) ;

static float cosFunc1(int i, int overlap_sample);
static float cosFunc2(int i, int overlap_sample);  
static void crossFading(float *syn_list, int num_frame, int pre_overlap_frame, int next_overlap_frame);
static float cosFuncFull(int i, int duration, float A, float yoff);

static int appendList1(float *list1, int len_list1, float *list2, int len_list2, int overlap_frame);
static int appendList2(float *list1, int len_list1, float *list2, int len_list2, int overlap_frame);

static int hasPinyin( VOICE_bank *bank, char *pin_str );

static float midino2freq( float midi_no );
static float freq2midino( float freq );

static float len32note2frame( int len32_note, float bpm_float);
static int len32note2sample( int len32_note, float bpm_float);

static int get_token_from_fp_with_separator(FILE *fp, char *buff, char separator);
static int get_token_from_string_with_separator(char *buff, char *token, char separator);

#endif                          /* !TTSONG_H */
