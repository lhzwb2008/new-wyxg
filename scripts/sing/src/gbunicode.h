#ifndef _GB_CODE_H_
#define _GB_CODE_H_

/*
 * hz2py.c
 *   	convert chinese character to pinyin string
 *
 * luhmily@hotmail.com @dsoundsoft
 * date: March 19 15:23:00 2013
 */
 
#include <stdio.h>
#include <string.h>

typedef struct h2p {
    char *py;
    char *py_shengdiao;
    unsigned shengdiao;
    char *hz;
} pyhz_tab;
 
int getcnchar(char *cnChar, char *pinyinChar)
{
	/* 返回单汉字的拼音 */
	int PY_CNT = 0;
	int CHINESE_CHARACTER_LEN = 3;
	char query[] = "°?";
	char *curHzString;
	char curHz[4] = "";
	int i, j;
	int found = 0;
	char *gotChar; 
	for ( i = 0; i < CHINESE_CHARACTER_LEN; i++)
	{
		query[i] = cnChar[i];
	}
	query[CHINESE_CHARACTER_LEN] = '\0';
     
	if (!found)
		return 0;
	else
		return 1;
}

#endif









 
