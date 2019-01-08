
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "ncore.h" 

#include "TTSong.h" 
#include "pinyinConverter.h" 
 
///////////////////////////////
/////    音源API
///////////////////////////////

/* 创建合成引擎，设置音源
	Parameter: 
	@fn_inf : inf文件的路径
	@fn_voice : voice文件的路径
*/ 
void* createVoice( char *fn_inf, char *fn_voice )
{  
	int rtn_code = 0;
	  
	/* new a voice bank */
    VOICE_bank *bank = new VOICE_bank ;
 
	/* initialize voice bank */ 
	initVoiceBank( bank );
  
	/* load voice bank */
	rtn_code = loadVoiceBank(bank, fn_inf, fn_voice);
	if ( rtn_code != 1) {
		// 失败：路径错误，格式错误等等
		//fprintf(stderr, "Error: Voice bank cannot be loaded.\n");  
		return NULL;
	}
 
	return bank;
}
 
/* 释放音源 */
void clearVoice( void *bank )
{
	clearVoiceBank((VOICE_bank *)bank);
}


///////////////////////////////
/////    字音转换API
///////////////////////////////

/*   字音转换，输入汉字转成拼音，若无法转换，则直接返回charactor_str
	返回：1 
		-1: 字符串为null
		-2: 找不到字典
*/
int charactor2pinyin(char *charactor_str, char *pinyin_str)

{
	return c2p(charactor_str, pinyin_str);
}



///////////////////////////////
/////    合成引擎
///////////////////////////////

/* 创建歌曲结构 */
void* createSong(char *fn_song, int need_autoconfig)
{
	Song_Info *song_info = new Song_Info;

	// 读取曲谱文件
	if ( 0 > readSongFile(fn_song, 
							&(song_info->pinyin_list),
							&(song_info->start_sample_list),
							&(song_info->len_sample_list),
							&(song_info->midi_no_list),
							&(song_info->cle_list),
							&(song_info->vel_list),
							&(song_info->num_all_note),
		
							&(song_info->pit_list),
							&(song_info->vol_list),
							&(song_info->len_frame),
							&(song_info->wave_data),
							&(song_info->len_sample),
                            need_autoconfig ) )
	{
		// 读取曲谱文件错误
		clearSong(song_info);
		return NULL;
	}

	return song_info;
}

/* 初始化歌曲 
   返回：1 - 正确
		-1 - song为NULL
		-2 - bank为NULL
*/
int initSong( void * song, void *bank, float volume, 
			char **pinyin_list, int num_pinyin, 
			int (*play_callback)( short *wave_data, int len_sample, int cur_sample, int total_sample )  )
{
	Song_Info *song_info = (Song_Info *)song; 
	int i, j;

	// check song
	if ( song == NULL )
		return -1;	
	//check bank
	if ( bank == NULL )
		return -2;

	song_info->bank = (VOICE_bank *)bank;
	song_info->volume = volume; 
	
	for(i = 0, j = 0; i < song_info->num_all_note; i++)
	{
		if( !isPinyinSilSp( song_info->pinyin_list[i] ) && !isPinyinLy( song_info->pinyin_list[i] ) ) 
		{
			// 如果不是静音，赋值拼音
			if ( j < num_pinyin)
				strcpy( song_info->pinyin_list[i], pinyin_list[j]);
			else 
				strcpy( song_info->pinyin_list[i], "sp");
			j++;
		} 
	} 
	song_info->callback = play_callback;

	memset(song_info->wave_data, 0, sizeof(short)*song_info->len_sample);

	return 1;
}

/* 播放 */ 
void playSong( void *song )
{
	Song_Info *song_info = (Song_Info *)song;
	// reset stop
	song_info->is_stop = false;
	stopSynthesis(song_info->bank, false);
	// 播放
	makeVoice( song_info->bank, song_info->pinyin_list, 
				song_info->start_sample_list, song_info->len_sample_list, song_info->midi_no_list, 
				song_info->cle_list, song_info->vel_list, song_info->num_all_note,
				song_info->pit_list, song_info->vol_list, song_info->len_frame, 
				song_info->wave_data, song_info->len_sample,
				song_info->volume, song_info->callback );
}

/* 暂停 */ 
void stopSong( void *song )
{
	// 暂停
	Song_Info *song_info = (Song_Info *)song;
	song_info->is_stop = true;
	stopSynthesis(song_info->bank, true);
}
 
/* 释放歌曲 */ 
void clearSong( void *song )
{
	Song_Info *song_info = (Song_Info *)song;
	// clear song_info 
	int i, j;  
	
	if (song_info != NULL)
	{
		//if ( song_info->bank != NULL )
		//	clearVoiceBank(song_info->bank);
	
		if ( song_info->pinyin_list != NULL )
		{ 
			for ( i = 0; i < song_info->num_all_note; i++ )
			{
				if ( song_info->pinyin_list[i] != NULL )
				{ 
					delete[] song_info->pinyin_list[i];
				}
			}
			delete[] song_info->pinyin_list;
		}
	 
		if ( song_info->start_sample_list != NULL ) 
			delete[] song_info->start_sample_list; 
		if ( song_info->len_sample_list != NULL ) 
			delete[] song_info->len_sample_list; 
		if ( song_info->midi_no_list != NULL ) 
			delete[] song_info->midi_no_list; 
		if ( song_info->cle_list != NULL ) 
			delete[] song_info->cle_list; 
		if ( song_info->vel_list != NULL ) 
			delete[] song_info->vel_list; 
		if ( song_info->pit_list != NULL ) 
			delete[] song_info->pit_list; 
		if ( song_info->vol_list != NULL ) 
			delete[] song_info->vol_list; 
		if ( song_info->wave_data != NULL ) 
			delete[] song_info->wave_data; 
	 
		delete song_info; 
	}
}


////////////////////////////////////////////////////
 
/* 打印debug信息 */
void printDebug(char *debug_file, char *debug_str, int char_len)
{
	FILE *fp;
	fp = fopen(debug_file, "a");
	if ( fp != NULL)
	{
		fwrite(debug_str, char_len, 1, fp);
		fclose(fp);
	}
}
