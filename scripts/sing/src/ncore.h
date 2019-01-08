#include "TTSong.h" 

// data 
/* struct ----------------------------------------------------------- */

#ifndef NCORE_H
#define NCORE_H
 
#define PINYIN_LEN 10 // 歌词发音的字符串的长度
 
// 回调函数
typedef int (*play_callback)( short *wave_data, int len_sample, int cur_sample, int total_sample );

// 数据结构
typedef struct _song_info {
	VOICE_bank *bank;	// 音源 
	float volume; 
	char **pinyin_list;
	int *start_sample_list;
	int *len_sample_list;
	int *midi_no_list;
	float *cle_list;
	float *vel_list;
	int num_all_note;  
	// 歌声参数
	float *pit_list;
	float *vol_list; 
	int len_frame; 
	// 波形
	short *wave_data;
	int len_sample;
 
	bool is_stop;
	 
	play_callback callback;

	bool is_debug;

} Song_Info;

 
// 打印错误信息
void printDebug(char *debug_file, char *debug_str, int char_len);
 
	/* 音源API */
	// 创建歌声音源
	void* createVoice( char *fn_inf, char *fn_voice );
	// 释放歌声音源
	void clearVoice( void *bank );
	
	/* 字音转换API */
	// 汉字转拼音
	int charactor2pinyin(char *charactor_str, char *pinyin_str); 

	/* 合成引擎 */
	// 创建歌曲
	void* createSong(char *fn_song, int need_autoconfig );
	// 初始化歌曲 
	int initSong( void *song, void *bank, float volume, 
									char **pinyin_list, int num_pinyin, 
									int (*play_callback)( short *wave_data, int len_sample, int cur_sample, int total_sample )); 
	// 播放歌曲
	void playSong( void *song );
	// 停止播放
	void stopSong( void *song );
	// 释放歌曲
	void clearSong( void *song );
 

#endif                          /* !NCORE_H */
