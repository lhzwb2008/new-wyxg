
#define sSIL "sil"
#define sSP "sp"
#define sXX "xx"
#define sLYFH "-"   // 连音符号
#define sER "er"
#define sA "a"
#define sO "o"
#define sE "e"
#define sGER "ger"
#define sGA "ga"
#define sGO "go"
#define sGE "ge"
#define sZHI "zhi"
#define sCHI "chi"
#define sSHI "shi"
#define sRI "ri"
#define sZH "zh"
#define sCH "ch"
#define sSH "sh"
#define sR "r"
#define sIB "ib"
#define sZI "zi"
#define sCI "ci"
#define sSI "si"
#define sIF "if" 
#define sZ "z"
#define sC "c"
#define sS "s"
#define sJU "ju"
#define sQU "qu"
#define sXU "xu"
#define sYU "yu"
#define sV "v"
#define sJ "j"
#define sQ "q"
#define sX "x"
#define sY "y"
#define sI "i"
#define sYE "ye"
#define sYAN "yan"
#define sYANG "yang"
#define sYA "ya"
#define sYAO "yao"
#define sYONG "yong"
#define sYOU "you"
#define sIU "iu"
#define sW "w"
#define sU "u"
#define sWEN "wen"
#define sUN "un"
#define sWEI "wei"
#define sUI "ui"
#define sWA "wa"
#define sWAI "wai"
#define sWAN "wan"
#define sWANG "wang"
#define sWENG "weng"
#define sWO "wo"
#define sH "h"
#define sM "m"
#define sN "n"
#define sL "l"
#define sR "r"
#define sB "b"
#define sP "p"
#define sD "d"
#define sT "t"
#define sG "g"
#define sK "k"
#define sF "f"
#define sIB "ib"
#define sIF "if"
#define sEI "ei"
#define sIE "ie"
#define sVE "ve"
#define sAI "ai"
#define sBRE "br"


// 声母类型 
#define SM_TYPE_0 0  //  ('sp', 'sil')
#define SM_TYPE_1 1  //  ('ga', 'go', 'ge','ger', 'a','o','e','er','i', 'u', 'v', 'w', 'y')
#define SM_TYPE_2 2  //  ('m', 'n', 'l', 'r')
#define SM_TYPE_3 3  //  ('b', 'p', 'd', 't', 'g', 'k')
#define SM_TYPE_4 4  //  ('f', 'h', 'j', 'q', 'x')
#define SM_TYPE_5 5  //  ('zh', 'ch', 'sh', 'z', 'c', 's')

// 韵母类型  终止字母
#define YM_TYPE_0 0  //  ('sil', 'sp')
#define YM_TYPE_1 1  //  ('a', ) 
#define YM_TYPE_2 2  //  ('o', ) 
#define YM_TYPE_3 3  //  ('e', 'r')
#define YM_TYPE_4 4  //  ('i', 'b', 'f', ) 
#define YM_TYPE_5 5  //  ('u', ) 
#define YM_TYPE_6 6  //  ('v', ) 
#define YM_TYPE_7 7  //  ('n', 'g') 

// 韵母类型  起始字母
#define YM_INIT_TYPE_0 0  //  ('sil', 'sp')
#define YM_INIT_TYPE_1 1  //  ('a', ) 
#define YM_INIT_TYPE_2 2  //  ('o', ) 
#define YM_INIT_TYPE_3 3  //  ('e')
#define YM_INIT_TYPE_4 4  //  ('i', ) 
#define YM_INIT_TYPE_5 5  //  ('u', ) 
#define YM_INIT_TYPE_6 6  //  ('v', )  

// methods

/* 拼音->音素（声母+韵母） */
int pinyin2mono( char *pin_str, char *sm_str, char *ym_str);

/* 声母分类序号*/
int smtype(char *sm_str);

/* 韵母分类序号*/
int ymtype(char *ym_str);

/* 韵母结尾字符 */
int ymendchr(char *ym_str, char *end_str);

/* 韵母起始字符 */
int ymstartchr(char *ym_str, char *start_str);

/* 韵母起始字符分类 */
int yminittype( char *ym_str );

/* 当前拼音是sil sp ?  */
bool isPinyinSilSp( char *pinyin_str );
 
/* 当前拼音是连音符号- ?  */
bool isPinyinLy( char *pinyin_str );

/* 当前拼音是连音符号- ?  */
bool isPinyinBre( char *pinyin_str );

/* 声母是否有音高 */
bool smHasPitch( int smtype );

/* 汉字->拼音 */
int c2p(char *charactor_str, char *pinyin_str);

static int char2hex(char c);