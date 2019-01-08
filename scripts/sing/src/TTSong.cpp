
#include "TTSong.h"
#include "Midi.h"
#define M_PI 3.14159265358979323846
/* 初始化voice bank各种参数 */
void initVoiceBank( VOICE_bank *bank )
{ 
	bank->inf_ver = 100;
	bank->num_pinyin = 0; 
  
	bank->path_inf = new char[MAX_BUFF_SIZE];
	bank->path_voice = new char[MAX_BUFF_SIZE]; 

	bank->stop = false; 
}

/* 载入voice bank */
int loadVoiceBank( VOICE_bank *bank, char *fn_inf, char *fn_voice ) 
{
	/*  错误代码：
		0: 参数错误
		-1: 打开voice.d失败
		-2: 打开inf.d失败
		-3: 读取inf.d第一行失败 
	*/
	// 变量
	FILE *fp_inf, *fp_voice;
	char buff1[MAX_BUFF_SIZE]; 
	char token[MAX_BUFF_SIZE]; 
	char *p;
	int ti; 
	int i, j, buff_len;
	 
	strcpy( bank->path_inf, fn_inf );
	strcpy( bank->path_voice, fn_voice );
	 
	// 检查指针
	if (bank == NULL || fn_inf == NULL || fn_voice == NULL )
		// 初始化失败返回0
		return 0;
 
	// 尝试打开voice.d
	fp_voice = fopen(fn_voice, "rb");
	if (fp_voice == NULL) { 
		return -1; // 打开voice.d失败
	}
	fclose(fp_voice);

	// 打开inf.d, 读取信息
	fp_inf = fopen(fn_inf, "rb");
	if (fp_inf == NULL) {
		return -2;
	} 
	/* 读取inf.n第一行 */
	buff_len = get_token_from_fp_with_separator(fp_inf, buff1, '\n');
	if ( buff_len <= 0) { 
		 return -3;
	}
	// 解析第一行字符串  
	bank->num_pinyin = atoi(buff1);		// 拼音个数
 
	/* 读取inf.n第二行：各拼音的片段数 */ 
	bank->pinyin_info_list = new INF_pinyin_info[bank->num_pinyin];
	for ( i = 0; i< bank->num_pinyin; i++ )
	{
		// 先读取一整行
		buff_len = get_token_from_fp_with_separator(fp_inf, buff1, '\n');
		if ( buff_len <= 0) { 
			 return -5;
		} 
		// 再分别读取信息
		p = buff1;
		j = get_token_from_string_with_separator(p, token, ' ');
		if (strchr(token, '_') != NULL)
			get_token_from_string_with_separator(token, token, '_');
		bank->pinyin_info_list[i].pinyin = new char[strlen(token) + 1];
		strcpy(bank->pinyin_info_list[i].pinyin, token);
		p += (j+1);
		j = get_token_from_string_with_separator(p, token, ' ');
		bank->pinyin_info_list[i].voice_file_offset = atoi(token);
		p += (j+1);
		j = get_token_from_string_with_separator(p, token, ' ');
		bank->pinyin_info_list[i].voice_file_len = atoi(token);
		p += (j+1);
		j = get_token_from_string_with_separator(p, token, ' ');
		bank->pinyin_info_list[i].vowel_sample = atoi(token);
		p += (j+1);
		j = get_token_from_string_with_separator(p, token, ' ');
		bank->pinyin_info_list[i].tail_sample = atoi(token);
		p += (j+1);
		j = get_token_from_string_with_separator(p, token, ' ');
		bank->pinyin_info_list[i].pitch = atof(token);
		p += (j+1);
		j = get_token_from_string_with_separator(p, token, ' ');
		bank->pinyin_info_list[i].amp_part = atoi(token);
		p += (j+1); 
		bank->pinyin_info_list[i].amp_all = atoi(p); 
		// 16bit: 
		bank->pinyin_info_list[i].len_sample = bank->pinyin_info_list[i].voice_file_len / 2;
	}
 
	// 关闭文件
	fclose(fp_inf); 
  
	// 返回 true
	return 1; 
}

void clearVoiceBank( VOICE_bank *bank )
{
	/* 释放 voice bank */
	int i, j;

	if ( bank->path_inf != NULL ) delete bank->path_inf;
	if ( bank->path_voice != NULL ) delete bank->path_voice; 
	if ( bank->pinyin_info_list != NULL )
	{
		for ( i = 0; i < bank->num_pinyin; i++ )
		{
			if ( bank->pinyin_info_list[i].pinyin != NULL ) 
				delete bank->pinyin_info_list[i].pinyin; 
		} 
		delete[] bank->pinyin_info_list;
	}    
}
  
/*  根据用户输入的音符信息和参数，合成歌声
	Parameter:
		bank : 音源对象指针
		pinyin_list : 每个音符的歌词（拼音）字符串 (包括sil sp等, 首尾必须为sil)
		start_sample_list : 每个音符的起始sample
		len_sample_list : 每个音符的长度(sample)
		midi_no_list : 每个音符的音高(0~127)
		num_all_note : 音符的个数 
		cle_list : 声母与前音重叠的长度(0~1.0~2.0倍声母长度)
		vel_list : 声母伸缩的倍数(0~1.0~2.0倍)
		num_voiced_note : 有音音符的个数
		pit_list : 音高曲线pit的值（每frame对应一个值）
		vol_list : 音量曲线pit的值（每frame对应一个值） 
		len_frame : 一共有多少个frame（就是前面2个数组的长度）(1frame=10ms?)
	return:
		rtn_code : 1 or 错误代码 -1=首尾不是sil或sp -2= -3=找不到发音 -4=取出发音出错  -5=合成f0时出错  (已舍弃：拆分拼音出错)
*/
int makeVoice(VOICE_bank *bank, char **pinyin_list, 
				int *in_start_sample_list, int *in_len_sample_list, int *midi_no_list,
				float *cle_list, float *vel_list, int num_all_note,
				float *pit_list, float *vol_list, int len_frame, 
				short *wave_data, int out_len_sample,
				float volume, 
				int (*play_callback)( short *wave_data, int len_sample, int cur_sample, int total_sample ) )
{    
	// 变量
	int i,j,k;
	float target_midino;
	int target_len_sample;
	int start_sample, len_sample, sm_sample, overlap_sample, last_overlap_sample = 0;
	int cur_sample = 0;
	bool has_trans_info;
	int next_index;
	   
	int error_code = 1; // 若为负，则出错 
	
	int *start_sample_list, *len_sample_list;
	int *sm_sample_list;
	char **sm_str_list, **ym_str_list; // 韵母存储结尾音 
	int *num_ly_list;  
	INF_pinyin_info *pinyin_info_list;
	float *target_f0_list;
	float *target_vol_list;
	int target_start_frame, target_len_frame;
	INF_pinyin_info *trans_info;
	char *trans_pinyin;

	// 检查首尾字符必须是sil或sp
	if ( !isPinyinSilSp( pinyin_list[0] ) || !isPinyinSilSp( pinyin_list[num_all_note-1] ) )
	{
		error_code = -1; 
	}
	 
	// 初始化
	start_sample_list = new int[num_all_note];
	len_sample_list = new int[num_all_note];
	sm_sample_list = new int[num_all_note];
	memset(sm_sample_list, 0, sizeof(int) * num_all_note);
	sm_str_list = new char*[num_all_note];
	ym_str_list = new char*[num_all_note];
	for( i = 0 ; i < num_all_note; i++ )
	{
		sm_str_list[i] = new char[10];
		ym_str_list[i] = new char[10];
	} 
	num_ly_list = new int[num_all_note]; 
	memset(num_ly_list, 0, sizeof(int) * num_all_note);
	pinyin_info_list = new INF_pinyin_info[num_all_note];
	trans_info = new INF_pinyin_info;
	trans_pinyin = new char[10];
 
	// 第1次循环：根据sm信息，重新计算音符起止; 读取pinyin在voice.d中的位置 
	if ( error_code > 0 )
	{
		for ( i = 0; i < num_all_note; i++ )
		{
			// **** 修正len_frame，填充空白
			//HTS_error (0, " i=%d 1. start_frame_list[i]=%d len_frame_list[i]=%d ",  i ,start_frame_list[i], len_frame_list[i]);
			if ( i + 1 < num_all_note )
				len_sample_list[i] = in_start_sample_list[i+1] - in_start_sample_list[i] ;
			else
				len_sample_list[i] = in_len_sample_list[i];
			start_sample_list[i] = in_start_sample_list[i];

			// **** 计算声母
			if ( !isPinyinSilSp( pinyin_list[i] ) && !isPinyinLy( pinyin_list[i] )  ) // 静音，-，没有声母
			{ 
				// ====== 求出上下文信息 ====== 
				// 尝试解析声母韵母，如果不能解析，报错
				if ( pinyin2mono( pinyin_list[i], sm_str_list[i], ym_str_list[i]) != 2){ 
					// 拆音出错
					// todo?pass?
				}
				ymendchr(ym_str_list[i], ym_str_list[i]); // 取出结尾字符
				// 求连音个数
				num_ly_list[i] = 0;
				while ( i + num_ly_list[i] + 1 < num_all_note && isPinyinLy( pinyin_list[i + num_ly_list[i] + 1] ) ){
					num_ly_list[i] ++ ; 
				}
				// 从inf.d中寻找合适的发音info
				target_midino = midi_no_list[i];
				target_len_sample = len_sample_list[i];
				if (num_ly_list[i] > 0)
				{
					target_len_sample = 0;
					target_midino = 0;
					for ( j = 0; j < num_ly_list[i]; j ++ )
					{
						target_midino += midi_no_list[i+j+1];
						target_len_sample += len_sample_list[i+j+1];
					}
					target_midino /= (num_ly_list[i] + 1);
				} 
				// 开找
				if ( 0 == getPinyinInfoInInf( bank, pinyin_list[i], target_midino, target_len_sample, &pinyin_info_list[i]))
				{
					// 音源库中没有
					strcpy(pinyin_list[i], "sp");
					continue;
				} 

				// 声母长度(带vel参数), 不能超过前音的30%
				sm_sample_list[i] = pinyin_info_list[i].vowel_sample * vel_list[i];
				if (isPinyinSilSp(pinyin_list[i - 1]))
				{
					if (sm_sample_list[i] > PRE_SIL_PERCENT * len_sample_list[i-1])
						sm_sample_list[i] = PRE_SIL_PERCENT * len_sample_list[i-1];
				}else{ 
					if (sm_sample_list[i] > PRE_YM_PERCENT *(len_sample_list[i-1] - sm_sample_list[i-1]))
						sm_sample_list[i] = PRE_YM_PERCENT *(len_sample_list[i-1] - sm_sample_list[i-1]);
				}

				// 修正前音len_sample
				len_sample_list[i-1] -= sm_sample_list[i];
				// 修正当前音的start_sample
				start_sample_list[i] -= sm_sample_list[i];
				len_sample_list[i] += sm_sample_list[i]; 
			}
			else if ( isPinyinLy( pinyin_list[i] ) )
			{   // 连音 
			}
			else
			{	// 静音  
			} 
		}
	}

	// 第2次循环：计算开始合成
	if ( error_code > 0 )
	{
		// printf(" ============ prepare parameter === total %d notes ===", num_all_note);
		
		// callback
		play_callback( NULL, 0, 0, out_len_sample);

		// loop
		for ( i = 0; i < num_all_note && !(bank->stop); i++ )
		{   
			start_sample = start_sample_list[i];
			len_sample = len_sample_list[i];
			if ( !isPinyinSilSp( pinyin_list[i] ) && !isPinyinLy( pinyin_list[i] ) ) // 静音和- 不合成
			{  
				
				// **** 1. 如果有-，计算长度 
				for (j = 0; j < num_ly_list[i] ; j++ )
				{
					len_sample += len_sample_list[i+j+1];
				}

				// **** 2. 计算overlap, 检查是否有过渡音
				next_index = i + num_ly_list[i] + 1;
				if (!isPinyinSilSp( pinyin_list[next_index] ))
				{
					// 有后续音
					sprintf(trans_pinyin, "%s-%s", ym_str_list[i], sm_str_list[next_index]);

					// 检查过渡音
					if ( 0 == getPinyinInfoInInf( bank, trans_pinyin, midi_no_list[next_index - 1], 0, trans_info))
					{
						// 木有过渡音
						has_trans_info = false;
					}else
					{
						// 有过渡音
						has_trans_info = true;  
					} 
					// 合成长度也变长
					overlap_sample = cle_list[next_index] * sm_sample_list[next_index];
					// overlap下一个声母
					len_sample += overlap_sample;
				}  
				else
				{
					// 没有后续音
					has_trans_info = false;
					//overlap_sample =  pinyin_info_list[i].len_sample - pinyin_info_list[i].tail_sample;  // 这里可能不对 应该用output的值
					overlap_sample = (float)(pinyin_info_list[i].len_sample - pinyin_info_list[i].tail_sample) / pinyin_info_list[i].len_sample * len_sample;
				}  

				// **** 3. 合成
				sm_sample = sm_sample_list[i];

				target_start_frame = (start_sample + sm_sample) / SAMPLE_PER_FRAME;
				target_f0_list = pit_list + target_start_frame; 
				target_vol_list = vol_list + target_start_frame; 

				// check stop 
				if ( bank->stop )
					break;

				// synthesis
				if( -1 == synthesizeSingleVoice(bank, &pinyin_info_list[i], sm_sample, len_sample, target_f0_list, target_vol_list,
								overlap_sample, last_overlap_sample, has_trans_info, trans_info, 
								wave_data + start_sample) )
				{
					// 忽略合成错误
					// error_code = -2
				}

				last_overlap_sample = overlap_sample;
				// 更新index 
				cur_sample += (len_sample - overlap_sample);
				// callback
				play_callback(wave_data + start_sample, (len_sample - overlap_sample), cur_sample, out_len_sample);
			}
			else if ( isPinyinLy( pinyin_list[i] ) )
			{
				// 连音符号
				//last_overlap_sample = 0; 
			}
			else
			{	// 静音  
				cur_sample = start_sample + len_sample;
				// callback
				play_callback(wave_data + start_sample - last_overlap_sample, len_sample + last_overlap_sample, cur_sample, out_len_sample);
				last_overlap_sample = 0;
			}   
		} // end for 
	}
	// 将指示游标移动到最后
	if ( cur_sample < out_len_sample )
	{
		cur_sample = out_len_sample; 
		// callback 
		play_callback(NULL, 0, cur_sample, out_len_sample);
	}

	// free 
	delete[] start_sample_list;
	delete[] len_sample_list;
	delete[] sm_sample_list;
	delete[] sm_str_list;
	delete[] ym_str_list;
	delete[] num_ly_list;
	delete[] pinyin_info_list;   

	return error_code; 
}
 
/* 
	停止播放
*/
void stopSynthesis( VOICE_bank *bank, bool is_stop)
{
	bank->stop = is_stop;
}

/* 
	读取曲谱文件
*/
int readSongFile(char *fn_song, char ***pinyin_list, int **start_sample_list, int **len_sample_list,
				int **midi_no_list, float **cle_list, float **vel_list, int *num_all_note,
				float **pit_list, float **vol_list, int *len_frame, short **wave_data, int *len_sample,
                int need_autoconfig )
{ 
	/*  返回代码： 
		 1：正确
		-1: 打开.mid文件失败 
	*/
	// 变量
	FILE *fp_song;
	char buff1[MAX_BUFF_SIZE]; 
	char token[MAX_BUFF_SIZE]; 
	char *p; 
	int i, j, k, buff_len;
	float bpm_float, tick_per_32note, tmp_vibdep, tmp_vibrat, tmp_midino;
	int num_voiced_note = 0, num_track = 0, selected_track = 0,tmp_last_end = 0, tmp_start, tmp_len, tmp_viblen;
	int *start_32note_list, *len_32note_list, *tmp_midino_list;
	char **tmp_pinyin_list;
	int *tmp_cle_list, *tmp_vel_list, *tmp_por_list, *tmp_vib_len_list, *tmp_vib_dep_list, *tmp_vib_rat_list;
	int **tmp_pit_list, **tmp_vol_list, *tmp_pbs_list;
	MIDINOTE *midiNoteList;

	/* 一. 尝试打开.mid文件 */
	Midi *pMidi = new Midi();//初始化midi类
	//打开midi  
	if (! pMidi->OpenMidi(fn_song)) { 
		return -1; // 打开.mid文件失败
	} 
	// 读取曲速 
	bpm_float = pMidi->getBpmFloat();  
  
	// 读取轨道数 
	num_track = pMidi->getTrackCount();
	// 默认选中第一个有音符的轨道
	selected_track = 0;
	for ( i = 0; i < num_track; i++)
	{
		if ( pMidi->getNoteCountByTrack(i) > 0 )
		{
			selected_track = i;
			break;
		}
	}

	// 读取音符个数  
	num_voiced_note = pMidi->getNoteCountByTrack(selected_track);  

	// 初始化临时变量
	tmp_pinyin_list = new char*[num_voiced_note];
	for( i = 0; i < num_voiced_note; i++ )
		tmp_pinyin_list[i] = new char[PINYIN_LEN];
	start_32note_list = new int[num_voiced_note];
	len_32note_list = new int[num_voiced_note];
	tmp_midino_list = new int[num_voiced_note];
	tmp_cle_list = new int[num_voiced_note];
	tmp_vel_list = new int[num_voiced_note];
	tmp_por_list = new int[num_voiced_note];
	tmp_vib_len_list = new int[num_voiced_note];
	tmp_vib_dep_list = new int[num_voiced_note];
	tmp_vib_rat_list = new int[num_voiced_note];
	tmp_pit_list = new int*[num_voiced_note];
	tmp_vol_list = new int*[num_voiced_note]; 
	for ( i = 0; i < num_voiced_note; i++ )
	{
		tmp_pit_list[i] = new int[100];
		tmp_vol_list[i] = new int[100];
	}
	tmp_pbs_list = new int[num_voiced_note];
	midiNoteList = new MIDINOTE[num_voiced_note];
	 
	/* 读取各音符的参数 */ 
	pMidi->getMidiNote(selected_track, midiNoteList);
	tick_per_32note = pMidi->getTickUnit() / 8;// getTickUnit() = 1个4分音符的tick  

	// 循环每个音符
	for ( i = 0; i < num_voiced_note; i++ )
	{ 
		// 音符信息 
		strcpy(tmp_pinyin_list[i], "a"); 
		start_32note_list[i] = midiNoteList[i].miTime / tick_per_32note; // 音符起始（32分音符） 
		len_32note_list[i] = midiNoteList[i].miLen / tick_per_32note; ; // 音符长度（32分音符） 
		tmp_midino_list[i] = midiNoteList[i].miNo; // 音高
		tmp_cle_list[i] = 50;// CLE 
		tmp_vel_list[i] = 50;// VEL  
		tmp_por_list[i] = 0;  // POR    
		tmp_vib_len_list[i] = 0; // VIB_len 
		tmp_vib_dep_list[i] = 0; // VIB_dep 
		tmp_vib_rat_list[i] = 0;  // VIB_rat 
		for( k = 0; k < 100; k++ ) // 循环100个dyn值
		{  
			tmp_vol_list[i][k] = 50;
		}   
		for( k = 0; k < 100; k++ ) // 循环100个pit值
		{ 
			tmp_pit_list[i][k] = 50;
		} 
		// PBS
		tmp_pbs_list[i] = 0; 
	} 

	/* 二. 将曲谱文件的内容，转换为song结构数据 */
	if ( num_voiced_note <= 0)
	{
		// 处理特殊情况：没有音符
		*num_all_note = 2;
		*pinyin_list = new char*[2];
		for(i = 0; i < 2; i++)
			(*pinyin_list)[i] = new char[PINYIN_LEN];
		*start_sample_list = new int[2];
		memset(*start_sample_list, 0, sizeof(int)*2);
		*len_sample_list = new int[2];
		memset(*len_sample_list, 0, sizeof(int)*2);
		*midi_no_list = new int[2];
		memset(*midi_no_list, 0, sizeof(int)*2);
		*cle_list = new float[2];
		*vel_list = new float[2]; 
		*len_frame = 0;
	}
	else
	{
		// 有音符的情况 
		// 1. 统计音符个数：前后要加入静音音符'sil', 音符间的静音区间要加入静音音符'sp'
		*num_all_note = 1; // 起始加入一个静音音符sil
		tmp_last_end = start_32note_list[0];
		for ( i = 0; i< num_voiced_note; i++ )
		{ 
			if (start_32note_list[i] > tmp_last_end)
				// 需要插入一个静音音符sp
				(*num_all_note)++;
			// 记数一个有音音符
			(*num_all_note)++;
			// 更新位置
			tmp_last_end = start_32note_list[i] + len_32note_list[i];
		}
		// 结尾加入一个静音音符sil
		(*num_all_note)++;
		// 2. 初始化数据
		*pinyin_list = new char*[*num_all_note];
		for(i = 0; i < *num_all_note; i++)
			(*pinyin_list)[i] = new char[PINYIN_LEN];
		*start_sample_list = new int[*num_all_note]; 
		*len_sample_list = new int[*num_all_note]; 
		*midi_no_list = new int[*num_all_note];
		memset(*midi_no_list, 0, sizeof(int) * (*num_all_note));
		*cle_list = new float[*num_all_note];
		memset(*cle_list, 0, sizeof(float) * (*num_all_note));
		*vel_list = new float[*num_all_note]; 
		memset(*vel_list, 0, sizeof(float) * (*num_all_note));
		
		*len_frame = (int)len32note2frame(tmp_last_end + LAST_SIL_FRAME, bpm_float);
		*pit_list = new float[*len_frame]; 
		memset(*pit_list, 0, sizeof(float) * (*len_frame));
		*vol_list = new float[*len_frame];
		memset(*vol_list, 0, sizeof(float) * (*len_frame));
		*len_sample = len32note2sample(tmp_last_end + LAST_SIL_FRAME, bpm_float);
		*wave_data = new short[*len_sample];
		memset(*wave_data, 0, sizeof(short) * (*len_sample));
		// 3. 计算所需数据
		tmp_last_end = start_32note_list[0];
		// 第1个音符是静音sil
		(*start_sample_list)[0] = 0;
		(*len_sample_list)[0] = len32note2sample(start_32note_list[0], bpm_float);
		strcpy((*pinyin_list)[0], "sil");
		k = 1;	// 指示当前有声音符在总音符列表中的位置
		// 循环音符进行计算
		for ( i = 0; i < num_voiced_note; i++ )
		{ 
			if (start_32note_list[i] > tmp_last_end)
			{
				// 需要插入一个静音音符sp
				(*start_sample_list)[k] = len32note2sample(tmp_last_end, bpm_float);
				(*len_sample_list)[k] =  len32note2sample(start_32note_list[i], bpm_float) - len32note2sample(tmp_last_end, bpm_float);
				strcpy((*pinyin_list)[k], "sp");
				k++;
			}
			// 有音音符 
			(*start_sample_list)[k] = len32note2sample(start_32note_list[i], bpm_float);
			(*len_sample_list)[k] = len32note2sample(len_32note_list[i], bpm_float);
			tmp_midino = tmp_midino_list[i];//47 - tmp_midino_list[i] + 24 ;
			(*midi_no_list)[k] = (int)tmp_midino;
			(*cle_list)[k] = tmp_cle_list[i] / 50.;
			(*vel_list)[k] = tmp_vel_list[i] / 50.;
			strcpy((*pinyin_list)[k], tmp_pinyin_list[i]);
			// pit vol
			tmp_start = (int)len32note2frame(start_32note_list[i], bpm_float);
			tmp_len = (int)len32note2frame(len_32note_list[i], bpm_float) + 1;
			for( j = tmp_start; j < tmp_start + tmp_len && j < (*len_frame); j++)
			{
				// pit
				tmp_midino = (*midi_no_list)[k] + (float)(tmp_pit_list[i][(int)(( (float)(j - tmp_start)/tmp_len ) * 100)] - 50)/ 50. * (tmp_pbs_list[i] + 1); 
				tmp_viblen = (1.0 - (float)tmp_vib_len_list[i] / 100) * tmp_len;
				if( j > tmp_start + tmp_viblen )
				{
					// 进入颤音范围 
					tmp_vibdep = float(tmp_vib_dep_list[i]) / 100 * 1.0;
					tmp_vibrat = (1  - float(tmp_vib_rat_list[i]) / 100) * (25 - 20) + 20;
					tmp_midino += tmp_vibdep * sin( (2 * M_PI / tmp_vibrat ) * ((j - tmp_start - tmp_viblen)) ); 
				}
				(*pit_list)[j] = midino2freq(tmp_midino);
				// vol
				(*vol_list)[j] = (float)(tmp_vol_list[i][(int)(( (float)(j - tmp_start)/tmp_len ) * 100)])/ 50.; 
			}
			
			// 自动调教
            if ( need_autoconfig > 0 )
            {
                // 如果有后音，80%处开始滑音
                // 如果有前音，且差距>=2个半音, 前滑音至max(30%处, sm + 10)
                if ( i < num_voiced_note && start_32note_list[i+1] == start_32note_list[i] + len_32note_list[i])
                {
                    for( j = tmp_start + tmp_len*0.8; j < tmp_start + tmp_len && j < (*len_frame); j++)
                    {
                        tmp_midino = tmp_midino_list[i] + (((float)(tmp_midino_list[i+1] - tmp_midino_list[i])/2) / (tmp_len*0.2) * (j - tmp_start - tmp_len*0.8)); 
                        (*pit_list)[j] = midino2freq(tmp_midino);
                    }
                }
                if ( i > 0 && start_32note_list[i] == start_32note_list[i-1] + len_32note_list[i-1] )
                {
                    if ( tmp_midino_list[i] - tmp_midino_list[i - 1] >= 2 )
                    {
                        for( j = tmp_start; j < tmp_start + tmp_len*0.3 && j < tmp_start + 20; j++)
                        {
                            tmp_midino = tmp_midino_list[i] - 2 + (2. / (tmp_len*0.3<20?tmp_len*0.3:20) * (j - tmp_start)); 
                            (*pit_list)[j] = midino2freq(tmp_midino);
                        }
                    }
                }
            }
			// 更新位置
			tmp_last_end = start_32note_list[i] + len_32note_list[i];
			k++;
		} 
		// 最后一个音符sil
		(*start_sample_list)[k] = len32note2sample(tmp_last_end, bpm_float);
		(*len_sample_list)[k] = len32note2sample(LAST_SIL_FRAME, bpm_float);
		strcpy((*pinyin_list)[k], "sil");

	}
	 
	// 释放
	for(i=0; i < num_voiced_note; i++)
		delete tmp_pinyin_list[i];
	delete[] tmp_pinyin_list;
	delete[] start_32note_list;
	delete[] len_32note_list;
	delete[] tmp_midino_list;
	delete[] tmp_cle_list;
	delete[] tmp_vel_list;
	delete[] tmp_por_list;
	delete[] tmp_vib_len_list;
	delete[] tmp_vib_dep_list;
	delete[] tmp_vib_rat_list;
	delete[] midiNoteList;

	// 返回 true
	return 1;  
}

////////////////////////////
//  Private methods
////////////////////////////

/*   
	合成单音
	输入的out_ori_f0_list/out_ori_vol_list  每441个sample_per_frame对应1个frame
	返回：正确返回1 
		-1：取出voice失败
*/
int synthesizeSingleVoice(VOICE_bank *bank, INF_pinyin_info *pinyin_info, 
					int out_sm_sample, int out_len_sample, float *out_ori_f0_list, float *out_ori_vol_list, 
					int overlap_sample, int last_overlap_sample, 
					bool has_trans_info, INF_pinyin_info *trans_info,
					short *syn_data )
{ 
	int i, j;
	float *ori  = NULL, *trans_wave_data = NULL;
	int in_len_sample, trans_len_sample, ori_len_sample, trans_vowel_sample;
	int out_tail_len_sample; // 输出tail长度
	float *ou = new float[out_len_sample];
	int f0_sample_per_frame = 1;  // 1效果最好，441的话 无音高声母和韵母交界处效果不好
	int out_num_frame = out_len_sample / f0_sample_per_frame + 1;
	int out_sm_frame = out_sm_sample / f0_sample_per_frame;
	float *in_f0_list;
	bool sm_has_pitch;
	int in_num_frame;
	int num_sec;
	int *in_sec_start_sample_list, *in_sec_len_sample_list;
	int *out_sec_start_sample_list, *out_sec_len_sample_list;
	float *f0_frame_list = new float[out_num_frame];
	float *vol_frame_list = new float[out_num_frame];
	int tmp_amplitude_end = 0, tmp_amplitude_trans = 0; float ratio_amplitude; // 用于修整过渡音振幅
	// 特殊处理：是否是呼吸音
	bool is_bre = isPinyinBre(pinyin_info->pinyin);
	if ( is_bre ) has_trans_info = false;  // 呼吸音不能有过渡音

	// 先从voice.d中取出过渡音
	if ( has_trans_info)
	{
		trans_len_sample = trans_info->len_sample;  
		trans_vowel_sample = trans_len_sample / 2;			// 过渡音分割线暂定为一半
		trans_wave_data = new float[trans_len_sample];
		memset(trans_wave_data, 0, sizeof(float)*trans_len_sample);
		if( 1 != extractWaveFromVoice( bank, trans_info->voice_file_offset, trans_info->voice_file_len, trans_wave_data, trans_len_sample ) )
		{
			printf ( "Error: cannot extract trans-wave from voice:%s)", trans_info->pinyin);
			has_trans_info = false;
			//return -2; 
		}
	}

	// 根据有无过渡音，初始化in_wave_data, section_info
	ori_len_sample = pinyin_info->len_sample;	 
	if ( has_trans_info)
	{
		// 输入长度
		//in_len_sample = ori_len_sample + (trans_len_sample - trans_vowel_sample);
		in_len_sample = ori_len_sample;
		// 计算num_sec 
		num_sec = 4;
	} 
	else
	{ 
		in_len_sample = ori_len_sample;
		num_sec = 3;
	}
	// 计算输出的tail长度(如果长度够长，采用in_tail_sample, 否则按%) 
	if (out_len_sample - out_sm_sample >= in_len_sample - pinyin_info->vowel_sample)
		out_tail_len_sample = in_len_sample - pinyin_info->tail_sample;
	else
		out_tail_len_sample = (in_len_sample - pinyin_info->tail_sample) * (float(out_len_sample - out_sm_sample)/float(in_len_sample - pinyin_info->vowel_sample));

	// 初始化变量
	ori = new float[in_len_sample];
	memset(ori, 0, sizeof(float) * in_len_sample);
	in_sec_start_sample_list = new int[num_sec];
	in_sec_len_sample_list = new int[num_sec];
	out_sec_start_sample_list = new int[num_sec];
	out_sec_len_sample_list = new int[num_sec];

	// 从voice.d中取出in_len_sample
	if ( 1 != extractWaveFromVoice( bank, pinyin_info->voice_file_offset, pinyin_info->voice_file_len, ori, ori_len_sample))
	{ 
		printf ( "Error: cannot extract wave from voice:%s)", pinyin_info->pinyin);
		return -1;
	}

	// 根据有无过渡音，处理波形，计算波形伸缩的区域   // TODO: 这里定义分段延长
	if( has_trans_info )
	{
		// 变变变
		d_(trans_wave_data, trans_len_sample, trans_info->pitch, SRATE, pinyin_info->pitch, f0_sample_per_frame);
		// 根据原音结尾的振幅, 调整过渡音振幅 
		for ( i = ori_len_sample - trans_vowel_sample - 100,j = -100; i < ori_len_sample; i++, j++)
		{
			if ( i > 0 && ori[i] > tmp_amplitude_end)
				tmp_amplitude_end = ori[i];
			if ( j > 0 && j < trans_vowel_sample/2 && trans_wave_data[j] > tmp_amplitude_trans)
				tmp_amplitude_trans = trans_wave_data[j];
		}
		if(tmp_amplitude_trans > 0 && tmp_amplitude_end > 0)
		{
			ratio_amplitude = (float)tmp_amplitude_end / tmp_amplitude_trans;
			for ( i = 0; i < trans_len_sample; i++)
			{
				trans_wave_data[i] *= ratio_amplitude;
			}
		}
		// 拼接过渡音
		appendList1(ori, ori_len_sample, trans_wave_data, trans_len_sample, trans_len_sample);        // new : all overlap
		// 计算in伸缩区域
		calculateStrentchSec( in_sec_start_sample_list, in_sec_len_sample_list, num_sec,
								pinyin_info->vowel_sample, pinyin_info->tail_sample, 
								in_len_sample - trans_vowel_sample > pinyin_info->tail_sample ? in_len_sample - trans_vowel_sample : pinyin_info->tail_sample, 
								in_len_sample);  
		// 计算out伸缩区域
		calculateStrentchSec( out_sec_start_sample_list, out_sec_len_sample_list, num_sec,
							out_sm_sample, out_len_sample - out_tail_len_sample, 
							out_len_sample - overlap_sample > out_len_sample - out_tail_len_sample ? out_len_sample - overlap_sample : out_len_sample - out_tail_len_sample, 
							out_len_sample);
	}
	else
	{ 
		// 计算in伸缩区域
		calculateStrentchSec( in_sec_start_sample_list, in_sec_len_sample_list, num_sec,
								pinyin_info->vowel_sample, pinyin_info->tail_sample, in_len_sample); 
		// 计算out伸缩区域
		calculateStrentchSec( out_sec_start_sample_list, out_sec_len_sample_list, num_sec, 
								out_sm_sample, out_len_sample - out_tail_len_sample, out_len_sample);
	}
	// 计算输入f0，考虑声母是否有声母
	in_num_frame = in_len_sample / f0_sample_per_frame + 1;
	in_f0_list = new float[in_num_frame]; 
	sm_has_pitch = smHasPitch(smtype( pinyin_info->pinyin));
	for( i = 0; i < in_num_frame; i++)
	{
		if ( is_bre || (! sm_has_pitch && i * f0_sample_per_frame < pinyin_info->vowel_sample) )
		{
			// 是呼吸音 || 声母没音高，且当前frame为声母帧
			in_f0_list[i] = 0;
		}
		else
		{
			in_f0_list[i] = pinyin_info->pitch;
		}
	}
	// 计算输出f0，输出vol
	memset(f0_frame_list, 0, sizeof(float)*out_num_frame);
	memset(vol_frame_list, 0, sizeof(float)*out_num_frame); 
	if ( is_bre )
	{
		// 是呼吸音,音量按比例拷贝
		for(i = 0; i < out_num_frame; i++ )
		{
			f0_frame_list[i] = 0;
			vol_frame_list[i] = 1.0; //out_ori_vol_list[ (int)(((float)i / out_num_frame) * (out_num_frame - out_sm_frame) / SAMPLE_PER_FRAME) ];
		}

	}
	else if ( ! sm_has_pitch )
	{ 
		// 声母无音高, 韵母按比例拷贝
		for(i = out_sm_frame; i < out_num_frame; i++ )
		{
			f0_frame_list[i] = out_ori_f0_list[ (int)((i - out_sm_frame) / SAMPLE_PER_FRAME) ]; 
		} 
		// 音量按比例拷贝
		for(i = 0; i < out_num_frame; i++ )
		{ 
			vol_frame_list[i] = out_ori_vol_list[ (int)(((float)i / out_num_frame) * (out_num_frame - out_sm_frame) / SAMPLE_PER_FRAME) ];
		}
	}
	else
	{
		// 声母有音高, 按比例拷贝
		for(i = 0; i < out_num_frame; i++ )
		{
			f0_frame_list[i] = out_ori_f0_list[ (int)(((float)i / out_num_frame) * (out_num_frame - out_sm_frame) / SAMPLE_PER_FRAME) ];
			vol_frame_list[i] = out_ori_vol_list[ (int)(((float)i / out_num_frame) * (out_num_frame - out_sm_frame) / SAMPLE_PER_FRAME) ];
		}
	}

	// 变变变
	memset(ou, 0, sizeof(float) * out_len_sample);
	if ( is_bre )
		db(ori, in_len_sample, in_f0_list, in_num_frame, SRATE, 
					   ou, out_len_sample, f0_frame_list, out_num_frame, f0_sample_per_frame);
	else
		_(ori, in_len_sample, in_f0_list, in_num_frame, SRATE, 
					   ou, out_len_sample, f0_frame_list, out_num_frame, f0_sample_per_frame,
					   in_sec_start_sample_list, in_sec_len_sample_list,
					   out_sec_start_sample_list, out_sec_len_sample_list, num_sec );
	 
	// 复制到wave中, 考虑fade in & out，考虑音量
	// fade in
	for ( i = 0; i < last_overlap_sample && i < out_len_sample; i++)
	{
		syn_data[i] += cosFunc2(i,last_overlap_sample) * ou[i] * vol_frame_list[i/f0_sample_per_frame] * MAX_AMP;
	}
	// copy middle
	if (out_len_sample - overlap_sample - last_overlap_sample > 0)
	{
		for ( i = last_overlap_sample; i < out_len_sample - overlap_sample; i++)
		{
			syn_data[i] = ou[i] * vol_frame_list[i/f0_sample_per_frame] * MAX_AMP;
		}
	}
	// fade out
	for ( i = out_len_sample - overlap_sample > 0 ? out_len_sample - overlap_sample : 0, j = 0; 
			i < out_len_sample; i++, j++)
	{
		syn_data[i] += cosFunc1(j, overlap_sample) * ou[i] * vol_frame_list[i/f0_sample_per_frame] * MAX_AMP; 
	} 
	  
	// free
	delete[] ori;
	delete[] ou;
	delete[] in_f0_list;
	delete[] in_sec_start_sample_list;
	delete[] in_sec_len_sample_list;
	delete[] out_sec_start_sample_list;
	delete[] out_sec_len_sample_list;
	delete[] f0_frame_list;
	delete[] vol_frame_list;
	if(trans_wave_data != NULL) delete[] trans_wave_data;

	return 1;
}


/* 给定3-4个点，计算起始
	返回：无
*/
void calculateStrentchSec( int *sec_start_list, int *sec_end_list, int num_sec, int s1, int s2, int s3, int s4)
{
	sec_start_list[0] = 0;
	sec_end_list[0] = s1;
	sec_start_list[1] = s1;
	sec_end_list[1] = s2 - s1; 
	sec_start_list[2] = s2;
	sec_end_list[2] = s3 - s2; 
	
	if ( num_sec == 4 && s4 != 0)
	{
		sec_start_list[3] = s3;
		sec_end_list[3] = s4 - s3;  
	} 
}
 
/* 
	返回：无
*/
void d_(float *__, int aa, float ii_, float amplitude, float _______, int pspf)
{
	int i;
	float *___ = new float[aa];
	memset(___, 0, sizeof(float)* aa );
	int day = aa /pspf + 1;
	float *aaa = new float[day];
	float *aaa_ = new float[day];
	for( i = 0; i < day; i++)
	{
		aaa[i] = ii_;
		aaa_[i] = _______;
	}
	int hz = 1;
	int *jj = new int[hz];
	int *ii = new int[hz];
	int *iii = new int[hz];
	int *jjj = new int[hz];
	jj[0] = 0;
	ii[0] = aa;
	iii[0] = 0;
	jjj[0] = aa;

	_(__, aa , aaa, day, amplitude, 
					   ___, aa , aaa_, day, pspf,
					   jj, ii,
					   iii, jjj, hz );

	memcpy(__, ___, sizeof(float) * aa );

	// free
	delete[] ___;
	delete[] aaa;
	delete[] aaa_;
	delete[] jj;
	delete[] ii;
	delete[] iii;
	delete[] jjj;
}
 
/*  
	返回：无
*/ 
void db(float *__, int aa, float *___, int aaa , float amplitude, 
					   float *___a, int a_, float *_a_, int o, int pspf )
{
	int i;    
	int z = 1;
	int *jjj = new int[z];
	int *ii = new int[z];
	int *iii = new int[z];
	int *jj = new int[z];
	float *s;

	if ( aa >= a_)
	{ 
		jjj[0] = 0;
		ii[0] = aa;
		iii[0] = 0;
		jj[0] = a_;  
		_(__, aa, ___, aaa , amplitude, 
						   ___a, a_, _a_, a_, pspf,
						   jjj, ii,
						   iii, jj, z ); 
	} 
	else
	{ 
		jjj[0] = 0;
		ii[0] = aa;
		iii[0] = 0;
		jj[0] = aa;  
		s = ___a + (a_ - aa); 
		_(__, aa, ___, aaa , amplitude, 
						   ___a + (a_ - aa), aa, _a_, aaa , pspf,
						   jjj, ii,
						   iii, jj, z ); 
	} 


	// free
	delete[] jjj;
	delete[] ii;
	delete[] iii;
	delete[] jj;
}
	

void _(float *__, int __a, float *_______, int day, float amplitude, 
					   float *___, int ___a, float *________, int night, int pspf,
					   int *ii, int *jjj,
					   int *jj, int *iii, int hz )
{
	int i, j, k;
	int *____, *_____, a, aa;
	int ______a, _a_;
	int aaa, __a__ = 0;
	float *aaa_;
	float ______a_;
	int a_a, aaa__, ______;
	float _a__;
	int __a_;
	  
	a = 0;
	_a_ = 0;
	while(_a_ < __a)
	{ 
		______a_ = _______[ (int)(_a_ / pspf) ];  
		______a = (______a_ <= 50)? P_SIL_SAMPLE : (int)(amplitude / ______a_); 
		
		_a_ += ______a;
		a++;	  
		__a__ = ______a * 2 > __a__ ? ______a * 2:__a__;
	} 
	a--; 
	____ = new int[a]; 
	_a_ = 0;
	for ( i = 0 ; i < a; i++)
	{ 
		______a_ = _______[(int)(_a_ / pspf) ]; 
		______a = (______a_ <= 50)? P_SIL_SAMPLE : (int)(amplitude / ______a_);  
		_a_ += ______a; 
		____[i] = _a_;
	}    
	aa = 0;
	_a_ = 0;
	while(_a_ < ___a)
	{   
		______a_ = ________[ (int)(_a_ / pspf) ];  
		______a = (______a_ <= 50)? P_SIL_SAMPLE : (int)(amplitude / ______a_); 
		_a_ += ______a; 
		aa++;
	} 
	_____ = new int[aa]; 
	_a_ = 0;
	for(i = 0; i < aa; i++)
	{ 
		______a_ = ________[ (int)(_a_ / pspf) ];
		______a = (______a_ <= 50)? P_SIL_SAMPLE : (int)(amplitude / ______a_); 
		_a_ += ______a;  
		_____[i] = _a_;
	} 
	aaa_ = new float[__a__]; 
	a_a = 0;  
	aaa__ = 0; 
	______  = -1;  
	for(i = 0; i < aa; i++)
	{ 
		while (_____[i] > jj[aaa__] + iii[aaa__])
		{
			if (aaa__ >= hz - 1)
				break;
			aaa__ ++;
		} 
		_a_ = (int)( ((float)( _____[i] - jj[aaa__] )/iii[aaa__])
					* jjj[aaa__] + ii[aaa__]);
		while ( a_a < a - 1 && ____[a_a + 1] < _a_)
		{
			a_a ++;
		}
		aaa = (a_a > 0 )? (____[a_a] - ____[a_a - 1]) : ____[0]; 
		aaa = (____[a_a] + aaa > __a?__a - ____[a_a] - 1:aaa )* 2;
		memcpy(aaa_, __ + ____[a_a] - aaa / 2, aaa * sizeof(float));  
		if ( ______ == a_a)
		{ 
			_a__ = (float)((rand() % 40) + 60) / 100.;
			for(j = 0; j < aaa; j++) 
				aaa_[j] *= _a__;
		}  
		for(j = 0; j < aaa; j++) 
		{ 
			if(_____[i] - aaa / 2 + j >= 0 && _____[i] - aaa / 2 + j < ___a )
				___[_____[i] - aaa / 2 + j] += (_____[i] - aaa / 2 + j >= 0 && _____[i] - aaa / 2 + j < ___a ? aaa_[j] * hummingWin(j, aaa):0);
		} 
	}   
	delete[] ____;
	delete[] _____;
	delete[] aaa_; 
}

/* Get pinyin info according to context, return pinyin_info in inf.d
	返回：
		找到的candidate个数
		失败 -1 
*/
int getPinyinInfoInInf( VOICE_bank *bank, char *pinyin_str, int midi_no, int len_sample, 
							   INF_pinyin_info *found_pinyin_info)  
{ 
	// 局部变量
	int i;
	int num_candidate = 0;
	int max_num_candidate = 20;
	INF_pinyin_info *candidate_info_list = new INF_pinyin_info[max_num_candidate];

	float inf_midino;
	float this_penality = 0;
	float min_penality = 999999;
	int min_index = 0;
	 
	// 在inf.d中寻找所有的info
	for ( i = 0 ; i < bank->num_pinyin; i++)
	{
		if ( strcmp(bank->pinyin_info_list[i].pinyin, pinyin_str) == 0 )
		{
			memcpy(&candidate_info_list[num_candidate], &(bank->pinyin_info_list[i]), sizeof(INF_pinyin_info));
			num_candidate ++;
		}
	}

	// 寻找最合适的info
	if(num_candidate == 1)
	{
		// 如果只找到1个，直接使用
		memcpy(found_pinyin_info, &candidate_info_list[0], sizeof(INF_pinyin_info));
	}
	else if (num_candidate > 1)
	{
		// 找到多个，选出最合适的 (与目标音高最接近的发音)
		for ( i = 0 ; i < num_candidate; i++)
		{
			// 计算得分 : 相差1音高=扣10分，相差44100sample=3分
			inf_midino = freq2midino(candidate_info_list[i].pitch);
			this_penality = abs(inf_midino - midi_no)*10. + 
							abs(candidate_info_list[i].len_sample - len_sample)/44100. * 3.;
			// 记录惩罚值最低的
			if ( this_penality < min_penality)
			{
				min_penality = this_penality;
				min_index = i;
			}
		}
		// 找到惩罚值最小的
		memcpy(found_pinyin_info, &candidate_info_list[min_index], sizeof(INF_pinyin_info)); 
	}

	delete[] candidate_info_list;
 
	return num_candidate;  
}
 

// ===========================================
//             static methods
// ===========================================
 
/* extract mgc&bap from voice.d 
	返回：
		成功 1
		打开失败 -1 
		seek失败 -2
*/
static int extractWaveFromVoice( VOICE_bank *bank, int voice_file_offset, int voice_file_len, 
									float *wave_data, int len_sample)  
{
	// 变量
	int i, j; 
	float tf;
	short* tmp_wav = new short[len_sample];
	FILE *fp;
	 
	// 从voice.d文件中读取wave信息 
	fp = fopen(bank->path_voice, "rb");
	if (fp == NULL) { 
		return -1; // 打开voice.d失败
	} 
	// 找到voice所在位置
	if ( fseek( fp, voice_file_offset, SEEK_SET ) == -1 ){
		fclose(fp);
		return -2;
	}
	// 读取 
	fread( tmp_wav, sizeof(char), voice_file_len, fp ); 
	for ( i = 0; i < len_sample; i++ )
	{ 
		wave_data[i] = (float)tmp_wav[i] / MAX_AMP;
	}
	// 关闭
	fclose(fp);

	delete[] tmp_wav;

	return 1;
} 

/* 
	汉明窗
*/  
static float hummingWin(int n, int win_size) 
{
	return 0.54 - 0.46 * cos(2 * M_PI * n / (win_size - 1));
}


/* 
	将波形  开头和结尾处  渐入渐出 
	// math.h中宏定义的是M_PI #define M_PI 3.14159265358979323846
*/ 
static float cosFunc1(int i, int overlap_sample)
{	// 减弱
	return ( 1.0 + cos( (float)i * M_PI / (float)overlap_sample ) )/ 2 ;
}

static float cosFunc2(int i, int overlap_sample)
{	// 渐强
	return 1.0 - ( 1.0 + cos( (float)i * M_PI / (float)overlap_sample ) )  / 2 ; 
}

static void crossFading(float *syn_list, int num_frame, int pre_overlap_frame, int next_overlap_frame)
{
	int i, j; 
	float f;
	if (next_overlap_frame > num_frame) next_overlap_frame = num_frame;
	for ( i = 0; i < next_overlap_frame; i++ )
	{
		f = cosFunc1(i, next_overlap_frame);    // 减弱
		syn_list[ num_frame - next_overlap_frame + i ] *= f; 		
	} 
	if (pre_overlap_frame > num_frame) pre_overlap_frame = num_frame;
	for ( i = 0; i < pre_overlap_frame ; i++ )
	{
		f = cosFunc2(i, pre_overlap_frame);   // 减强
		syn_list[i] *= f;
	} 		
}

static float cosFuncFull(int i, int duration, float A, float yoff)
{	// 渐变
	return A* ( 1.0 + cos( (float)i * M_PI / (float)duration ) )/ 2 + (float) yoff ;
}


/* 
	将2个波形 叠加
	appendList1  list1更新重叠部分
	appendList2	 list2更新重叠部分
*/ 
static int appendList1(float *list1, int len_list1, float *list2, int len_list2, int overlap_frame)
{
	int i, j;
	crossFading(list1, len_list1, 0, overlap_frame );
	crossFading(list2, len_list2, overlap_frame, 0 );  

	if (overlap_frame > len_list1) overlap_frame=len_list1;
	if (overlap_frame > len_list2) overlap_frame=len_list2;
	
	for ( i = 0; i < overlap_frame; i++ )
	{ 
		list1[len_list1 - overlap_frame + i ] += list2[ i ];   
	} 
	for ( i = overlap_frame; i < len_list2; i++ )
	{ 
		list1[len_list1 - overlap_frame + i ] += list2[ i ];   
	} 
	return overlap_frame;
}

static int appendList2(float *list1, int len_list1, float *list2, int len_list2, int overlap_frame)
{
	int i, j;
	crossFading(list1, len_list1, 0, overlap_frame );
	crossFading(list2, len_list2, overlap_frame, 0 );  

	if (overlap_frame > len_list1) overlap_frame=len_list1;
	if (overlap_frame > len_list2) overlap_frame=len_list2;

	for ( i = 0; i < overlap_frame; i++ )
	{ 
		list2[i] += list1[len_list1 - overlap_frame + i]; 
	} 
	return overlap_frame;
}


/* Check whether pinyin_str in dict 	
	返回：
		成功 pos in dict   
		失败 -1: 解析拼音失败 
*/
static int hasPinyin( VOICE_bank *bank, char *pin_str )
{ 
	int i;

	for ( i = 0; i < bank->num_pinyin; i++)
	{
		if ( strcmp( bank->pinyin_info_list[i].pinyin, pin_str) == 0 ) 
			return i;
	}
	return -1;
}
 
static float midino2freq( float midi_no )
{
    // formula from wikipedia on "pitch"
    if ( midi_no <= 0 ) return 0.;
    return 440.0 * ( pow(2.0, ((midi_no - 69.0+12) / 12.0) ) );
}

static float freq2midino( float freq )
{  
	return log(freq / 440.0) * 12 +69-12; 
}

/* 32分音符，根据曲速，转换为frame长度 */
static float len32note2frame( int len32_note, float bpm_float)
{
	return  (float)len32_note / ((bpm_float / 60.) *2*2*2) *(1000 / FRAME_MS);
}
/* 32分音符，根据曲速，转换为sample长度 */
static int len32note2sample( int len32_note, float bpm_float)
{
	float frame = len32note2frame(len32_note, bpm_float);
	int sample = frame * SAMPLE_PER_FRAME;
	return sample;
}

/* get_token_with_separator: get token from file pointer with specified separator */
static int get_token_from_fp_with_separator(FILE * fp, char *buff, char separator)
{
   char c; 
   int i;

   if (fp == NULL || feof(fp))
      return 0;
   c = fgetc(fp);
   while (c == separator) {
      if (feof(fp))
         return 0;
      c = fgetc(fp);
      if (c == EOF)
         return 0;
   }

   for (i = 0; c != separator;) {
      buff[i++] = c;
      if (feof(fp))
         break;
      c = fgetc(fp);
      if (c == EOF)
         break;
   }

   buff[i] = '\0';
   return i;
} 

/* get_token_with_separator: get token from file pointer with specified separator */
static int get_token_from_string_with_separator(char *buff, char *token, char separator)
{
	char c;
	int i = 0, j = 0;

	c = buff[i++];
	while (c == separator) { 
		c = buff[i++]; 
	} 

	for (j = 0; c != separator;) {
		token[j++] = c; 
		c = buff[i++];  
	}

	token[j] = '\0';
	return j;
}
