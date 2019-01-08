#include <stdio.h>
#include <string.h>
#include "pinyinConverter.h"
#include "gbunicode.h"


/* 拼音->音素（声母+韵母） */
int pinyin2mono( char *pin_str, char *sm_str,  char *ym_str) 
/*			
	返回值：
		0=错误
		1=只有声母
		2=有声母 有韵母 
 */
{ 
	if ( pin_str == NULL || sm_str == NULL || ym_str == NULL ) 
		return 0;
	// 检查非拼音的情况
	if ( strcmp(pin_str, sSIL) == 0 ){
		strcpy(sm_str, sSIL);
		strcpy(ym_str, "");
		return 1;
	}else if ( strcmp(pin_str, sSP) == 0 ){
		strcpy(sm_str, sSP);
		strcpy(ym_str, "");
		return 1; 
	}else if ( strcmp(pin_str, sLYFH) == 0 ){
		strcpy(sm_str, sLYFH);
		strcpy(ym_str, "");
		return 1;
	}
	// 拆分拼音
	// 无声母
	if ( strncmp(pin_str, sER, 2) == 0 ){
		//strcpy(sm_str, sGER);
		strcpy(sm_str, sER);
		strcpy(ym_str, pin_str);
		return 2;
	}else if ( strncmp(pin_str, sA, 1) == 0 ){
		//strcpy(sm_str, sGA);
		strcpy(sm_str, sA);
		strcpy(ym_str, pin_str);
		return 2;
	}else if ( strncmp(pin_str, sO, 1) == 0 ){
		//strcpy(sm_str, sGO);
		strcpy(sm_str, sO);
		strcpy(ym_str, pin_str);
		return 2;
	}else if ( strncmp(pin_str, sE, 1) == 0 || strncmp(pin_str, sEI, 2) == 0 ){
		//strcpy(sm_str, sGE);
		strcpy(sm_str, sE);
		strcpy(ym_str, pin_str);
		return 2;
	}
	// zhi chi shi ri
	else if ( strcmp(pin_str, sZHI) == 0 ){
		strcpy(sm_str, sZH);
		strcpy(ym_str, sIB);
		return 2;
	}else if ( strcmp(pin_str, sCHI) == 0 ){
		strcpy(sm_str, sCH);
		strcpy(ym_str, sIB);
		return 2;
	}else if ( strcmp(pin_str, sSHI) == 0 ){
		strcpy(sm_str, sSH);
		strcpy(ym_str, sIB);
		return 2;
	}else if ( strcmp(pin_str, sRI) == 0 ){
		strcpy(sm_str, sR );
		strcpy(ym_str, sIB);
		return 2;
	}
	// zi ci si
	else if ( strcmp(pin_str, sZI) == 0 ){
		strcpy(sm_str, sZ );
		strcpy(ym_str, sIF);
		return 2;
	}else if ( strcmp(pin_str, sCI) == 0 ){
		strcpy(sm_str, sC );
		strcpy(ym_str, sIF);
		return 2;
	}else if ( strcmp(pin_str, sSI) == 0 ){
		strcpy(sm_str, sS );
		strcpy(ym_str, sIF);
		return 2;
	} 
	// ju qu xu yu
	else if ( strncmp(pin_str, sJU, 2) == 0 ){
		strcpy(sm_str, sJ );
		strcpy(ym_str, pin_str+1);
		strncpy(ym_str, sV, 1); 
		return 2;
	}else if ( strncmp(pin_str, sQU, 2) == 0 ){
		strcpy(sm_str, sQ );
		strcpy(ym_str, pin_str+1);
		strncpy(ym_str, sV, 1); 
		return 2;
	}else if ( strncmp(pin_str, sXU, 2) == 0 ){
		strcpy(sm_str, sX );
		strcpy(ym_str, pin_str+1);
		strncpy(ym_str, sV, 1); 
		return 2;
	}else if ( strncmp(pin_str, sYU, 2) == 0 ){
		strcpy(sm_str, sY );
		strcpy(ym_str, pin_str+1);
		strncpy(ym_str, sV, 1); 
		return 2;
	} 
	// y+i e an ang a ao ong
	else if ( strcmp(pin_str, sYE) == 0 || strcmp(pin_str, sYAN) == 0 || strcmp(pin_str, sYANG) == 0 || 
				strcmp(pin_str, sYA) == 0  || strcmp(pin_str, sYAO) == 0 || strcmp(pin_str, sYONG) == 0 ){
		strcpy(sm_str, sY );
		strcpy(ym_str, pin_str);
		strncpy(ym_str, sI, 1); 
		return 2;
	} 
	// you = y + iu(iou)
	else if ( strcmp(pin_str, sYOU) == 0 ){
		strcpy(sm_str, sY );
		strcpy(ym_str, sIU); 
		return 2;
	} 
	// wen = w + un(uen)
	else if ( strcmp(pin_str, sWEN) == 0 ){
		strcpy(sm_str, sW );
		strcpy(ym_str, sUN); 
		return 2;
	} 
	// wei = w + ui(uei)
	else if ( strcmp(pin_str, sWEI) == 0 ){
		strcpy(sm_str, sW );
		strcpy(ym_str, sUI); 
		return 2;
	} 
	// w+u a ai an ang eng o
	else if ( strcmp(pin_str, sWA) == 0 || strcmp(pin_str, sWAI) == 0 || strcmp(pin_str, sWAN) == 0 || 
				strcmp(pin_str, sWANG) == 0  || strcmp(pin_str, sWENG) == 0 || strcmp(pin_str, sWO) == 0 ){
		strcpy(sm_str, sW );
		strcpy(ym_str, pin_str); 
		strncpy(ym_str, sU, 1); 
		return 2;
	} 

	// 拆分普通无变化的拼音
	if ( strncmp( pin_str+1 ,sH, 1) == 0 ){
		strcpy(sm_str, pin_str );
		sm_str[2] = '\0';
		strcpy(ym_str, pin_str+2 );
	}
	else{
		strcpy(sm_str, pin_str );
		sm_str[1] = '\0';
		strcpy(ym_str, pin_str+1 ); 
	}
	return 2;

}

 
/* 声母分类序号*/
int smtype(char *sm_str)
{
	if ( strcmp(sm_str, sSIL) == 0 || strcmp(sm_str, sSP) == 0 )
		return SM_TYPE_0;
	else if ( strncmp(sm_str, sGA, 2) == 0 || strncmp(sm_str, sGO, 2) == 0 || strncmp(sm_str, sGE, 2) == 0 || strncmp(sm_str, sGER, 3) == 0 ||
			  strncmp(sm_str, sA, 1) == 0 || strncmp(sm_str, sO, 1) == 0 || strncmp(sm_str, sE, 1) == 0 || strncmp(sm_str, sER, 2) == 0 ||
		      strncmp(sm_str, sI, 1) == 0 || strncmp(sm_str, sU, 1) == 0 || strncmp(sm_str, sV, 1) == 0 || strncmp(sm_str, sW, 1) == 0 || 
			  strncmp(sm_str, sY, 1) == 0 )
		return SM_TYPE_1;
	else if ( strncmp(sm_str, sM, 1) == 0 || strncmp(sm_str, sN, 1) == 0 || strncmp(sm_str, sL, 1) == 0 || strncmp(sm_str, sR, 1) == 0 )
		return SM_TYPE_2;
	else if ( strncmp(sm_str, sB, 1) == 0 || strncmp(sm_str, sP, 1) == 0 || strncmp(sm_str, sD, 1) == 0 || 
			  strncmp(sm_str, sT, 1) == 0 || strncmp(sm_str, sG, 1) == 0 || strncmp(sm_str, sK, 1) == 0)
		return SM_TYPE_3;
	else if ( strncmp(sm_str, sF, 1) == 0 || strncmp(sm_str, sH, 1) == 0 || strncmp(sm_str, sJ, 1) == 0 || 
			  strncmp(sm_str, sQ, 1) == 0 || strncmp(sm_str, sX, 1) == 0 )
		return SM_TYPE_4;
	else if ( strncmp(sm_str, sZH, 2) == 0 || strncmp(sm_str, sCH, 2) == 0 || strncmp(sm_str, sSH, 2) == 0 || 
			  strncmp(sm_str, sZ, 1) == 0 || strncmp(sm_str, sC, 1) == 0 || strncmp(sm_str, sS, 1) == 0)
		return SM_TYPE_5;  

	return -1;
}

/* 韵母结尾分类序号*/
int ymtype(char *ym_str)
{	
	if ( strcmp(ym_str, sSIL) == 0 || strcmp(ym_str, sSP) == 0 )
		return YM_TYPE_0;
	int last_index = 0;

	while (ym_str[last_index] != '\0')
	{
		last_index++ ; 
	}
	last_index-- ;	 
	
	if ( strcmp(ym_str + last_index, sA) == 0 )
		return YM_TYPE_1;
	else if ( strcmp(ym_str + last_index, sO) == 0 )
		return YM_TYPE_2;
	else if ( strcmp(ym_str + last_index, sE) == 0 || strcmp(ym_str + last_index, sR) == 0 )
		return YM_TYPE_3;
	else if ( strcmp(ym_str + last_index, sI) == 0 || strcmp(ym_str + last_index, sB) == 0 || strcmp(ym_str + last_index, sF) == 0 )
		return YM_TYPE_4;
	else if ( strcmp(ym_str + last_index, sU) == 0 )
		return YM_TYPE_5;
	else if ( strcmp(ym_str + last_index, sV) == 0 )
		return YM_TYPE_6;
	else if ( strcmp(ym_str + last_index, sN) == 0 || strcmp(ym_str + last_index, sG) == 0 )
		return YM_TYPE_7;
 
	return -1; 
}

/* 韵母起始字符 */
int ymstartchr(char *ym_str, char *start_str)
{ 
	if ( strcmp(ym_str, sSIL) == 0 || strcmp(ym_str, sSP) == 0 )
	{
		strcpy(start_str, sSP);
		return 1;
	}
 
	if ( strncmp(ym_str, sA, 1) == 0 ){
		strcpy(start_str, sA);
		return 1;
	}else if ( strncmp(ym_str, sO, 1) == 0 ){
		strcpy(start_str, sO);
		return 1; 
	}else if ( strncmp(ym_str, sER, 2) == 0 ){
		strcpy(start_str, sER);
		return 1; 
	}else if ( strncmp(ym_str, sU, 1) == 0 ){
		strcpy(start_str, sU);
		return 1; 
	}else if ( strncmp(ym_str, sV, 1) == 0 ){
		strcpy(start_str, sV);
		return 1; 
	}else if ( strncmp(ym_str, sEI, 2) == 0 ){
		strcpy(start_str, sEI);
		return 1; 
	}else if ( strncmp(ym_str, sE, 1) == 0 ){
		strcpy(start_str, sE);
		return 1; 
	}else if ( strncmp(ym_str, sI, 1) == 0 ){
		strcpy(start_str, sI);
		return 1;
	}
 
	return -1; 
}


/* 韵母起始字符分类 */
int yminittype( char *ym_str )
{ 
	if ( strcmp(ym_str, sSIL) == 0 || strcmp(ym_str, sSP) == 0 )
	{ 
		return YM_INIT_TYPE_0;
	}
 
	if ( strncmp(ym_str, sA, 1) == 0 ){ 
		return YM_INIT_TYPE_1;
	}else if ( strncmp(ym_str, sO, 1) == 0 ){ 
		return YM_INIT_TYPE_2; 
	}else if ( strncmp(ym_str, sE, 1) == 0 ){ 
		return YM_INIT_TYPE_3; 
	}else if ( strncmp(ym_str, sI, 1) == 0 ){ 
		return YM_INIT_TYPE_4;
	}else if ( strncmp(ym_str, sU, 1) == 0 ){ 
		return YM_INIT_TYPE_5; 
	}else if ( strncmp(ym_str, sV, 1) == 0 ){ 
		return YM_INIT_TYPE_6; 
	}
 
	return -1; 
}

/* 韵母结尾字符 */
int ymendchr(char *ym_str, char *end_str)
{	
	if ( strcmp(ym_str, sSIL) == 0 || strcmp(ym_str, sSP) == 0 )
	{
		strcpy(end_str, sSP);
		return 1;
	}

	int last_index = 0;

	while (ym_str[last_index] != '\0')
	{
		last_index++ ; 
	}
	last_index-- ;	 
	
	if ( strcmp(ym_str + last_index, sA) == 0 ){
		strcpy(end_str, sA);
		return 1;
	}else if ( strcmp(ym_str + last_index, sO) == 0 ){
		strcpy(end_str, sO);
		return 1;
	}else if ( strcmp(ym_str + last_index, sR) == 0 ){
		strcpy(end_str, sER);
		return 1;
	}else if ( last_index > 0 && ( strcmp(ym_str + last_index - 1, sEI) == 0 || strcmp(ym_str + last_index - 1, sUI) == 0 
				|| strcmp(ym_str + last_index - 1, sIE) == 0 || strcmp(ym_str + last_index - 1, sVE) == 0    ) ){
		strcpy(end_str, sEI);
		return 1;
	}else if ( strcmp(ym_str + last_index, sE) == 0 ){
		strcpy(end_str, sE);
		return 1;
	}else if ( last_index > 0 && ( strcmp(ym_str + last_index - 1, sAI) == 0  ) ){
		//strcpy(end_str, sEI);
		strcpy(end_str, sI);
		return 1;
	}else if ( strcmp(ym_str + last_index, sB) == 0 ){
		//strcpy(end_str, sIB);
		strcpy(end_str, sRI);
		return 1;
	}else if ( strcmp(ym_str + last_index, sF) == 0 ){
		//strcpy(end_str, sIF);
		strcpy(end_str, sZI);
		return 1;
	}else if ( strcmp(ym_str + last_index, sI) == 0 ){
		strcpy(end_str, sI);
		return 1;
	}else if ( strcmp(ym_str + last_index, sN) == 0 ){
		strcpy(end_str, sN);
		return 1;
	}else if ( strcmp(ym_str + last_index, sG) == 0 ){
		strcpy(end_str, sG);
		return 1;
	}else if ( strcmp(ym_str + last_index, sV) == 0 ){
		strcpy(end_str, sV);
		return 1;
	}else if ( strcmp(ym_str + last_index, sU) == 0 ){
		strcpy(end_str, sU);
		return 1;
	}
 
	return -1; 
}


/* 当前拼音是sil sp ?  */
bool isPinyinSilSp( char *pinyin_str )
{
	return ( strcmp( pinyin_str, sSIL ) == 0 || strcmp( pinyin_str, sSP ) == 0 );
}

/* 当前拼音是连音符号- ?  */
bool isPinyinLy( char *pinyin_str )
{
	return ( strcmp( pinyin_str, sLYFH ) == 0 );
}

/* 当前拼音是呼吸音bre ?  */
bool isPinyinBre( char *pinyin_str )
{
	return ( strncmp( pinyin_str, sBRE, 2 ) == 0 );
}

/* 声母是否有音高 */
bool smHasPitch( int smtype )
{
	return smtype == SM_TYPE_1 || smtype == SM_TYPE_2;
}

 
/* 汉字->拼音 
	返回：1
		-1: 字符串为null
*/
int c2p(char *charactor_str, char *pinyin_str)
{	
	int rtn_code;

	if ( charactor_str == NULL || pinyin_str == NULL )
		return -1;

	// 计算gbk_code
	//unsigned int gb_code = 0; 
	//gb_code = charactor_str[0] & 0x000000FF;   
	//gb_code = gb_code << 8;   
	//gb_code |=  charactor_str[1] & 0x000000FF;   
	//gb_code = gb_code & 0x0000FFFF;
	// gb -> unicode
	//uni_code = gb_uni(gb_code, pinyin_str);
	// 2016-01-01 : use new method 
	rtn_code = getcnchar(charactor_str, pinyin_str);

	// 没找到, 则原路返回
	if (rtn_code <= 0)
	{
		strcpy(pinyin_str, "a"); 
	} 

	return 1;

}


static int char2hex(char c)
{
#define SWAP(A) (A&0x01)<<7 | (A&0x02) <<6 | \
	(A&0x04)<<5 | (A&0x08)<<4 | \
	(A&0x10)>>1 | (A&0x20)>>2 | \
	(A&0x40)>>3 | (A&0x80)>>4
	return 1;
}