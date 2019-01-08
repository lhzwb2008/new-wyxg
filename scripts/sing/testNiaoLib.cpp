// testNiaoLib.cpp : 定义控制台应用程序的入口点。
//

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "ncore.h"
#include "Wave.h"

// 输出wav路径
char out_path[1024];

// 回调函数
int callback_func( short *wave_data, int len_sample, int cur_sample, int total_sample )
{
	// 如果cur_sample == 0 : 刚刚开始播放
	// 如果cur_sample == total_sample: 已经结束播放

	printf( "\n>> CALLBACK - played sample: %d / %d ", cur_sample, total_sample);
	
	FILE *fp; 
	int i; 
	
	// 第一次进入callback，创建wav文件
	if ( cur_sample == 0 && total_sample != 0 )
	{
		// 准备开始保存wav格式
		fp = fopen(out_path, "wb");
		if( fp != NULL )
		{
			writeWaveHeader(fp, (total_sample * 2 )); // 每个sample占2个字节 
			fclose(fp);
		} else
		{
			printf( "\n >> Error initilizing wave file ");
		}
	}

	// 写入wav文件
	if( wave_data != NULL && len_sample > 0)
	{  
		fp = fopen(out_path, "ab");
		if ( fp )
		{ 
			for(i = 0; i < len_sample; i++)
			{
				fwrite(wave_data + i, sizeof(short), 1, fp);
			}
			fclose(fp);
		} else
		{
			printf( "\n >> Error writing to wave file ");
		}

	} 

	return 1;
}

 /* 
 * Get the character code type. (UTF-8 or GB18030) 
 * @param s the string to be operator. 
 * @return return the code type. (1 means UTF-8, 0 for GB18030, -1 for error) 
 */  
int get_character_code_type(const char* s)  
{  
    if (NULL == s)
        return -1;
    int i = 0;  
    for(; s[i] != '\0'; i++)  
    {  
        // ASCII character.  
        if (!(s[i] & 0x80))  
        {  
            continue;  
        }  
        // Hanzi utf-8 code possiable.  
        else if(!( (s[i] & 0xF0) ^ 0xE0)   
                && s[i+1]   
                && !( (s[i+1] & 0xC0) ^ 0x80)   
                && s[i+2]   
                && !( (s[i+2] & 0xC0) ^ 0x80))  
        {  
            return 1;  
        }  
        // Not a UTF-8 code.  
        else  
        {  
            return 0;  
        }  
    }
    return -1;  
}  


/* 输入值：midi_path   char_lyric  num_lyric  out_path  inf_path  voice_path need_autoconfig*/
int main(int argc, char* argv[])
{
	/* 变量 */
	int i, n;
	void *bank;           // 音源对象指针 
	void *song;           // 歌曲对象指针
	char *pinyin;
	char *fn_inf;		  // 音源inf路径
	char *fn_voice;		  // 音源voice路径 
	char *fn_song;  // 曲谱路径
	int is_utf8;	// 是否是utf8编码 
	int need_autoconfig;	// 是否需要自动滑音 
	FILE *fp;
    
	float volume = 1.0;		// 音量：表示倍数
	char **pinyin_list;         // 歌词对应的拼音，每个拼音最长占10个char  

	// 读取变量
	if ( argc < 8 )
	{
		printf("Need at least 7 parameters! current is %d.", argc - 1);
		return -1;
	}
	fn_song = argv[1]; // 记录midi地址
	pinyin = argv[2];   // 记录歌词拼音
	n = atoi(argv[3]); //记录歌词字数 
	memset(out_path, 0, 1024);	// 输出路径
	strcpy(out_path, argv[4]);
	fn_inf = argv[5];		// 音源inf路径
	fn_voice = argv[6];		// 音源voice路径
	need_autoconfig = atoi(argv[7]);		// 是否自动滑音
	 	
	
	// 检查midi路径
	if ( !(fp = fopen(fn_song,"rb")))
	{
		// error open  inf 
		printf("Cannot open midi : %s.", fn_song);
		return -3;
	}
	// 检查音源路径
	if ( !(fp = fopen(fn_inf,"rb")))
	{
		// error open  inf 
		printf("Cannot open inf : %s.", fn_inf);
		return -4;
	}
	fclose(fp);
	if ( !(fp = fopen(fn_voice,"rb")))
	{
		// error open voice
		printf("Cannot open voice : %s.", fn_voice);
		return -5;
	}
	fclose(fp);

	// 初始化拼音
	pinyin_list = new char*[n]; 	
	for( i = 0; i < n; i++)
	{
		pinyin_list[i] = new char[10];
	}

	/* 第一步：初始化音源，载入音源 */
	bank = createVoice(fn_inf, fn_voice);

	/* 第二步：拼音 */
	const char * split = ","; 
	char * p; 
	i=0;
	p = strtok (pinyin,split); 
	while(p!=NULL&&i<n) {
	pinyin_list[i++] = p;		
	p = strtok(NULL,split); 
	} 
	 
	/* 第三步：初始化歌曲，载入.song曲谱文件 */
	song = createSong(fn_song, need_autoconfig);
	initSong( song, bank, volume, pinyin_list, n, callback_func); 
	 
	/* 第四步：播放 */
	playSong(song);
	 
	// 也可以多次播放，每次播放前调用initSong
	if(false)
	{
		initSong( song, bank, volume, pinyin_list, n, callback_func); 
		playSong(song);
	}
	/* 第五步：播放完毕，释放资源 */
	clearVoice(bank);
	clearSong(song);  


	// end
	char ch = getc(stdin);
	return 0;
}
