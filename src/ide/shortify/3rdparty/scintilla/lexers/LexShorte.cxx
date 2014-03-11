// Scintilla source code edit control
// @file LexShorte.cxx
// Lexer for Shorte
// by Brad Elliott
//
// Changes:
// March 28, 2004 - Added the standard Folding code
//
// Copyright for Scintilla: 1998-2001 by Neil Hodgson <neilh@scintilla.org>
// The License.txt file describes the conditions under which this software may be distributed.
// Scintilla source code edit control

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdarg.h>
#include <assert.h>
#include <ctype.h>

#include "ILexer.h"
#include "Scintilla.h"
#include "SciLexer.h"

#include "WordList.h"
#include "LexAccessor.h"
#include "Accessor.h"
#include "StyleContext.h"
#include "CharacterSet.h"
#include "LexerModule.h"

#ifdef SCI_NAMESPACE
using namespace Scintilla;
#endif

static inline bool IsTypeCharacter(const int ch)
{
    return ch == '$';
}
static inline bool IsAWordChar(const int ch)
{
    return (ch < 0x80) && (isalnum(ch) || ch == '_');
}

static inline bool IsAWordStart(const int ch)
{
    return (ch < 0x80) && (isalnum(ch) || ch == '_' || ch == '@' || ch == '#' || ch == '$' || ch == '.');
}

static inline bool IsAOperator(char ch) {
    return false;
	if (isascii(ch) && isalnum(ch))
		return false;
	if (ch == '+' || ch == '-' || ch == '*' || ch == '/' ||
	    ch == '&' || ch == '^' || ch == '=' || ch == '<' || ch == '>' ||
	    ch == '(' || ch == ')' || ch == '[' || ch == ']' || ch == ',' )
		return true;
	return false;
}

///////////////////////////////////////////////////////////////////////////////
// GetSendKey() filters the portion before and after a/multiple space(s)
// and return the first portion to be looked-up in the table
// also check if the second portion is valid... (up,down.on.off,toggle or a number)
///////////////////////////////////////////////////////////////////////////////

static int GetSendKey(const char *szLine, char *szKey)
{
	int		nFlag	= 0;
	int		nStartFound	= 0;
	int		nKeyPos	= 0;
	int		nSpecPos= 0;
	int		nSpecNum= 1;
	int		nPos	= 0;
	char	cTemp;
	char	szSpecial[100];

	// split the portion of the sendkey in the part before and after the spaces
	while ( ( (cTemp = szLine[nPos]) != '\0'))
	{
		// skip leading Ctrl/Shift/Alt state
		if (cTemp == '{') {
			nStartFound = 1;
		}
		//
		if (nStartFound == 1) {
			if ((cTemp == ' ') && (nFlag == 0) ) // get the stuff till first space
			{
				nFlag = 1;
				// Add } to the end of the first bit for table lookup later.
				szKey[nKeyPos++] = '}';
			}
			else if (cTemp == ' ')
			{
				// skip other spaces
			}
			else if (nFlag == 0)
			{
				// save first portion into var till space or } is hit
				szKey[nKeyPos++] = cTemp;
			}
			else if ((nFlag == 1) && (cTemp != '}'))
			{
				// Save second portion into var...
				szSpecial[nSpecPos++] = cTemp;
				// check if Second portion is all numbers for repeat fuction
				if (isdigit(cTemp) == false) {nSpecNum = 0;}
			}
		}
		nPos++;									// skip to next char

	} // End While


	// Check if the second portion is either a number or one of these keywords
	szKey[nKeyPos] = '\0';
	szSpecial[nSpecPos] = '\0';
	if (strcmp(szSpecial,"down")== 0    || strcmp(szSpecial,"up")== 0  ||
		strcmp(szSpecial,"on")== 0      || strcmp(szSpecial,"off")== 0 ||
		strcmp(szSpecial,"toggle")== 0  || nSpecNum == 1 )
	{
		nFlag = 0;
	}
	else
	{
		nFlag = 1;
	}
	return nFlag;  // 1 is bad, 0 is good

} // GetSendKey()

//
// Routine to check the last "none comment" character on a line to see if its a continuation
//
static bool IsContinuationLine(unsigned int szLine, Accessor &styler)
{
	int nsPos = styler.LineStart(szLine);
	int nePos = styler.LineStart(szLine+1) - 2;
	//int stylech = styler.StyleAt(nsPos);
	while (nsPos < nePos)
	{
		//stylech = styler.StyleAt(nePos);
		int stylech = styler.StyleAt(nsPos);
		if (!(stylech == SCE_SHORTE_COMMENT)) {
			char ch = styler.SafeGetCharAt(nePos);
			if (!isspacechar(ch)) {
				if (ch == '_')
					return true;
				else
					return false;
			}
		}
		nePos--; // skip to next char
	} // End While
	return false;
} // IsContinuationLine()

//
// syntax highlighting logic
static void ColouriseShorteDoc(unsigned int startPos,
							int length, int initStyle,
							WordList *keywordlists[],
							Accessor &styler) {

    WordList &keywords = *keywordlists[0];
    WordList &keywords2 = *keywordlists[1];
    WordList &keywords3 = *keywordlists[2];
    WordList &keywords4 = *keywordlists[3];
    WordList &keywords5 = *keywordlists[4];
    WordList &keywords6 = *keywordlists[5];
    WordList &keywords7 = *keywordlists[6];
    WordList &keywords8 = *keywordlists[7];
	// find the first previous line without continuation character at the end
	int lineCurrent = styler.GetLine(startPos);
	int s_startPos = startPos;
	// When not inside a Block comment: find First line without _
	if (!(initStyle==SCE_SHORTE_COMMENTBLOCK)) {
		while ((lineCurrent > 0 && IsContinuationLine(lineCurrent,styler)) ||
			   (lineCurrent > 1 && IsContinuationLine(lineCurrent-1,styler))) {
			lineCurrent--;
			startPos = styler.LineStart(lineCurrent); // get start position
			initStyle =  0;                           // reset the start style to 0
		}
	}
	// Set the new length to include it from the start and set the start position
	length = length + s_startPos - startPos;      // correct the total length to process
    styler.StartAt(startPos);

    StyleContext sc(startPos, length, initStyle, styler);
	char si;     // string indicator "=1 '=2
	char ni;     // Numeric indicator error=9 normal=0 normal+dec=1 hex=2 Enot=3
	char ci;     // comment indicator 0=not linecomment(;)
	char s_save[100];
	si=0;
	ni=0;
	ci=0;
	//$$$
    for (; sc.More(); sc.Forward()) {
		char s[100];
		sc.GetCurrentLowered(s, sizeof(s));

        if(sc.ch == '\\')
        {
			sc.SetState(SCE_SHORTE_DEFAULT);
            sc.Forward(2);
            continue;
        }
		// **********************************************
		// save the total current word for eof processing
		if (IsAWordChar(sc.ch) || sc.ch == '}')
		{
			strcpy(s_save,s);
			int tp = static_cast<int>(strlen(s_save));
			if (tp < 99) {
				s_save[tp] = static_cast<char>(tolower(sc.ch));
				s_save[tp+1] = '\0';
			}
		}
		// **********************************************
		//
		switch (sc.state)
        {
            case SCE_SHORTE_COMMENTBLOCK:
            {
                printf("In comment block!\n");
                if(sc.chPrev == '?' && sc.ch == '>')
                {
                    sc.ForwardSetState(SCE_SHORTE_DEFAULT);
                    break;
                }
                break;
            }
            case SCE_SHORTE_CONDITIONAL_EVAL:
            {
                if(sc.chPrev == '?' && sc.ch == '>'){
                    sc.ForwardSetState(SCE_SHORTE_DEFAULT);
                }
                break;
            }
            case SCE_SHORTE_CODE_BLOCK:
            {
                //if((sc.chPrev == '\n' || sc.chPrev == '\r') && (sc.ch == '@') && (sc.chNext != '{'))
                if((sc.ch == '@') && (sc.chNext != '{'))
                {
                    sc.SetState(SCE_SHORTE_DEFAULT);
                }
                break;
            }
            case SCE_SHORTE_LINK:
            {
                if((sc.chPrev == ']') && (sc.ch == ']'))
                {
                    sc.ForwardSetState(SCE_SHORTE_DEFAULT);
                }
                break;
            }
            case SCE_SHORTE_INLINE_TAG:
            {
                if(sc.ch == '}')
                {
                    sc.ForwardSetState(SCE_SHORTE_DEFAULT);
                }
                break;
            }
            case SCE_SHORTE_COMMENT:
            {
                if (sc.atLineEnd) {sc.SetState(SCE_SHORTE_DEFAULT);}
                break;
            }
            case SCE_SHORTE_OPERATOR:
            {
                // check if its a COMobject
				if (sc.chPrev == '.' && IsAWordChar(sc.ch)) {
					sc.SetState(SCE_SHORTE_COMOBJ);
				}
				else {
					sc.SetState(SCE_SHORTE_DEFAULT);
				}
                break;
            }
            case SCE_SHORTE_SPECIAL:
            {
                if (sc.ch == '#') {sc.SetState(SCE_SHORTE_COMMENT);}
				if (sc.atLineEnd) {sc.SetState(SCE_SHORTE_DEFAULT);}
                break;
            }
            case SCE_SHORTE_KEYWORD:
            {
                if (!(IsAWordChar(sc.ch) || (sc.ch == '-' && (strcmp(s, "#comments") == 0 || strcmp(s, "#include") == 0))))
                {
                    if (!IsTypeCharacter(sc.ch))
                    {
						//if (strcmp(s, "#cs")== 0 || strcmp(s, "#comments-start")== 0 )
						//{
						//	sc.ChangeState(SCE_SHORTE_COMMENTBLOCK);
						//	sc.SetState(SCE_SHORTE_COMMENTBLOCK);
						//	break;
						//}
						if (keywords.InList(s)) {
							sc.ChangeState(SCE_SHORTE_KEYWORD);
							sc.SetState(SCE_SHORTE_DEFAULT);
						}
						else if (keywords2.InList(s)) {
							sc.ChangeState(SCE_SHORTE_FUNCTION);
							sc.SetState(SCE_SHORTE_DEFAULT);
						}
						else if (keywords3.InList(s)) {
                            if(keywords4.InList(s))
                            {
                                sc.ChangeState(SCE_SHORTE_CODE_BLOCK);
                                sc.SetState(SCE_SHORTE_CODE_BLOCK);
                                sc.Forward(strlen(s));
                            }
                            else
                            {
							    sc.ChangeState(SCE_SHORTE_MACRO);
							    sc.SetState(SCE_SHORTE_DEFAULT);
                            }
						}
						else if (keywords5.InList(s)) {
							sc.ChangeState(SCE_SHORTE_PREPROCESSOR);
							sc.SetState(SCE_SHORTE_DEFAULT);
							if (strcmp(s, "#include")== 0)
							{
								si = 3;   // use to determine string start for #inlude <>
							}
						}
						else if (keywords6.InList(s)) {
							sc.ChangeState(SCE_SHORTE_SPECIAL);
							sc.SetState(SCE_SHORTE_SPECIAL);
						}
						else if ((keywords7.InList(s)) && (!IsAOperator(static_cast<char>(sc.ch)))) {
							sc.ChangeState(SCE_SHORTE_EXPAND);
							sc.SetState(SCE_SHORTE_DEFAULT);
						}
						else if (keywords8.InList(s)) {
							sc.ChangeState(SCE_SHORTE_UDF);
							sc.SetState(SCE_SHORTE_DEFAULT);
						}
						else if (strcmp(s, "_") == 0) {
							sc.ChangeState(SCE_SHORTE_OPERATOR);
							sc.SetState(SCE_SHORTE_DEFAULT);
						}
						else if (!IsAWordChar(sc.ch)) {
							sc.ChangeState(SCE_SHORTE_DEFAULT);
							sc.SetState(SCE_SHORTE_DEFAULT);
						}
					}
				}
                if (sc.atLineEnd) {
					sc.SetState(SCE_SHORTE_DEFAULT);}
                break;
            }
			case SCE_SHORTE_NUMBER:
            {
				// Numeric indicator error=9 normal=0 normal+dec=1 hex=2 E-not=3
				//
				// test for Hex notation
				if (strcmp(s, "0") == 0 && (sc.ch == 'x' || sc.ch == 'X') && ni == 0)
				{
					ni = 2;
					break;
				}
				// test for E notation
				if (IsADigit(sc.chPrev) && (sc.ch == 'e' || sc.ch == 'E') && ni <= 1)
				{
					ni = 3;
					break;
				}
				//  Allow Hex characters inside hex numeric strings
				if ((ni == 2) &&
					(sc.ch == 'a' || sc.ch == 'b' || sc.ch == 'c' || sc.ch == 'd' || sc.ch == 'e' || sc.ch == 'f' ||
					 sc.ch == 'A' || sc.ch == 'B' || sc.ch == 'C' || sc.ch == 'D' || sc.ch == 'E' || sc.ch == 'F' ))
				{
					break;
				}
				// test for 1 dec point only
				if (sc.ch == '.')
				{
					if (ni==0)
					{
						ni=1;
					}
					else
					{
						ni=9;
					}
					break;
				}
				// end of numeric string ?
				if (!(IsADigit(sc.ch)))
				{
					if (ni==9)
					{
						sc.ChangeState(SCE_SHORTE_DEFAULT);
					}
					sc.SetState(SCE_SHORTE_DEFAULT);
				}
				break;
			}
			case SCE_SHORTE_VARIABLE:
			{
				// Check if its a COMObject
				if (sc.ch == '.' && !IsADigit(sc.chNext)) {
					sc.SetState(SCE_SHORTE_OPERATOR);
				}
				else if (!IsAWordChar(sc.ch)) {
					sc.SetState(SCE_SHORTE_DEFAULT);
				}
				break;
            }
			case SCE_SHORTE_COMOBJ:
			{
				if (!(IsAWordChar(sc.ch))) {
					sc.SetState(SCE_SHORTE_DEFAULT);
				}
				break;
            }
            case SCE_SHORTE_STRING:
            {
				// check for " to end a double qouted string or
				// check for ' to end a single qouted string
	            if ((si == 1 && sc.ch == '\"') || (si == 2 && sc.ch == '\'') || (si == 3 && sc.ch == '>'))
				{
					sc.ForwardSetState(SCE_SHORTE_DEFAULT);
					si=0;
					break;
				}
                if (sc.atLineEnd)
				{
					si=0;
					// at line end and not found a continuation char then reset to default
					int lineCurrent = styler.GetLine(sc.currentPos);
					if (!IsContinuationLine(lineCurrent,styler))
					{
						sc.SetState(SCE_SHORTE_DEFAULT);
						break;
					}
				}
				// find Sendkeys in a STRING
				if (sc.ch == '{' || sc.ch == '+' || sc.ch == '!' || sc.ch == '^' || sc.ch == '#' ) {
                    sc.SetState(SCE_SHORTE_SENT);}
				break;
            }

            case SCE_SHORTE_SENT:
            {
				// Send key string ended
				if (sc.chPrev == '}' && sc.ch != '}')
				{
					// set color to SENDKEY when valid sendkey .. else set back to regular string
					char sk[100];
					// split {111 222} and return {111} and check if 222 is valid.
					// if return code = 1 then invalid 222 so must be string
					if (GetSendKey(s,sk))
					{
						sc.ChangeState(SCE_SHORTE_STRING);
					}
					// if single char between {?} then its ok as sendkey for a single character
					else if (strlen(sk) == 3)
					{
						sc.ChangeState(SCE_SHORTE_SENT);
					}
					// if sendkey {111} is in table then ok as sendkey
					//else if (keywords4.InList(sk))
					//{
					//	sc.ChangeState(SCE_SHORTE_SENT);
					//}
					else
					{
						sc.ChangeState(SCE_SHORTE_STRING);
					}
					sc.SetState(SCE_SHORTE_STRING);
				}
				else
				{
					// check if the start is a valid SendKey start
					int		nPos	= 0;
					int		nState	= 1;
					char	cTemp;
					while (!(nState == 2) && ((cTemp = s[nPos]) != '\0'))
					{
						if (cTemp == '{' && nState == 1)
						{
							nState = 2;
						}
						if (nState == 1 && !(cTemp == '+' || cTemp == '!' || cTemp == '^' || cTemp == '#' ))
						{
							nState = 0;
						}
						nPos++;
					}
					//Verify characters infront of { ... if not assume  regular string
					if (nState == 1 && (!(sc.ch == '{' || sc.ch == '+' || sc.ch == '!' || sc.ch == '^' || sc.ch == '#' ))) {
						sc.ChangeState(SCE_SHORTE_STRING);
						sc.SetState(SCE_SHORTE_STRING);
					}
					// If invalid character found then assume its a regular string
					if (nState == 0) {
						sc.ChangeState(SCE_SHORTE_STRING);
						sc.SetState(SCE_SHORTE_STRING);
					}
				}
				// check if next portion is again a sendkey
				if (sc.atLineEnd)
				{
					sc.ChangeState(SCE_SHORTE_STRING);
					sc.SetState(SCE_SHORTE_DEFAULT);
					si = 0;  // reset string indicator
				}
				//* check in next characters following a sentkey are again a sent key
				// Need this test incase of 2 sentkeys like {F1}{ENTER} but not detect {{}
				if (sc.state == SCE_SHORTE_STRING && (sc.ch == '{' || sc.ch == '+' || sc.ch == '!' || sc.ch == '^' || sc.ch == '#' )) {
					sc.SetState(SCE_SHORTE_SENT);}
				// check to see if the string ended...
				// Sendkey string isn't complete but the string ended....
				if ((si == 1 && sc.ch == '\"') || (si == 2 && sc.ch == '\''))
				{
					sc.ChangeState(SCE_SHORTE_STRING);
					sc.ForwardSetState(SCE_SHORTE_DEFAULT);
				}
				break;
            }
        }  //switch (sc.state)

        // Determine if a new state should be entered:
		if (sc.state == SCE_SHORTE_DEFAULT)
        {
            if (sc.ch == '#')
            {
                sc.SetState(SCE_SHORTE_COMMENT);
            }
            else if(sc.ch == '<' && sc.chNext == '!') {sc.SetState(SCE_SHORTE_COMMENTBLOCK);}
            else if (sc.ch == '<' && sc.chNext == '?') {sc.SetState(SCE_SHORTE_CONDITIONAL_EVAL);}
            else if (sc.ch == '[' && sc.chNext == '[') {sc.SetState(SCE_SHORTE_LINK);}
            //else if (sc.ch == '#') {sc.SetState(SCE_SHORTE_KEYWORD);}
            //else if (sc.ch == '$') {sc.SetState(SCE_SHORTE_VARIABLE);}
            //else if (sc.ch == '.' && !IsADigit(sc.chNext)) {sc.SetState(SCE_SHORTE_OPERATOR);}
            else if (sc.ch == '@')
            {
                if(sc.chNext == '{')
                {
                    sc.SetState(SCE_SHORTE_INLINE_TAG);
                    sc.Forward(2);
                }
                else
                {
                    sc.SetState(SCE_SHORTE_KEYWORD);
                }
            }
            //else if (sc.ch == '_') {sc.SetState(SCE_SHORTE_KEYWORD);}
            //else if (sc.ch == '<' && si==3) {sc.SetState(SCE_SHORTE_STRING);}  // string after #include
            else if (sc.ch == '\"') {
				sc.SetState(SCE_SHORTE_STRING);
				si = 1;	}
            /*else if (sc.ch == '\'') {
				sc.SetState(SCE_SHORTE_STRING);
				si = 2;	}*/
            /*else if ((IsASpace(sc.chPrev) || IsAOperator(sc.chPrev)) && (IsADigit(sc.ch) || (sc.ch == '.' && IsADigit(sc.chNext))))
			{
				sc.SetState(SCE_SHORTE_NUMBER);
				ni = 0;
            }*/
            else if (IsAWordStart(sc.ch)) {sc.SetState(SCE_SHORTE_KEYWORD);}
            //else if (IsAOperator(static_cast<char>(sc.ch))) {sc.SetState(SCE_SHORTE_OPERATOR);}
			else if (sc.atLineEnd) {sc.SetState(SCE_SHORTE_DEFAULT);}
        }
    }      //for (; sc.More(); sc.Forward())

	//*************************************
	// Colourize the last word correctly
	//*************************************
	if (sc.state == SCE_SHORTE_KEYWORD)
		{
		//if (strcmp(s_save, "#cs")== 0 || strcmp(s_save, "#comments-start")== 0 )
		//{
		//	sc.ChangeState(SCE_SHORTE_COMMENTBLOCK);
		//	sc.SetState(SCE_SHORTE_COMMENTBLOCK);
		//}
		if (keywords.InList(s_save)) {
			sc.ChangeState(SCE_SHORTE_KEYWORD);
			sc.SetState(SCE_SHORTE_KEYWORD);
		}
		else if (keywords2.InList(s_save)) {
			sc.ChangeState(SCE_SHORTE_FUNCTION);
			sc.SetState(SCE_SHORTE_FUNCTION);
		}
		else if (keywords3.InList(s_save)) {
			sc.ChangeState(SCE_SHORTE_MACRO);
			sc.SetState(SCE_SHORTE_MACRO);
		}
		else if (keywords5.InList(s_save)) {
			sc.ChangeState(SCE_SHORTE_PREPROCESSOR);
			sc.SetState(SCE_SHORTE_PREPROCESSOR);
		}
		else if (keywords6.InList(s_save)) {
			sc.ChangeState(SCE_SHORTE_SPECIAL);
			sc.SetState(SCE_SHORTE_SPECIAL);
		}
		else if (keywords7.InList(s_save) && sc.atLineEnd) {
			sc.ChangeState(SCE_SHORTE_EXPAND);
			sc.SetState(SCE_SHORTE_EXPAND);
		}
		else if (keywords8.InList(s_save)) {
			sc.ChangeState(SCE_SHORTE_UDF);
			sc.SetState(SCE_SHORTE_UDF);
		}
		else {
			sc.ChangeState(SCE_SHORTE_DEFAULT);
			sc.SetState(SCE_SHORTE_DEFAULT);
		}
	}
	if (sc.state == SCE_SHORTE_SENT)
    {
		// Send key string ended
		if (sc.chPrev == '}' && sc.ch != '}')
		{
			// set color to SENDKEY when valid sendkey .. else set back to regular string
			char sk[100];
			// split {111 222} and return {111} and check if 222 is valid.
			// if return code = 1 then invalid 222 so must be string
			if (GetSendKey(s_save,sk))
			{
				sc.ChangeState(SCE_SHORTE_STRING);
			}
			// if single char between {?} then its ok as sendkey for a single character
			else if (strlen(sk) == 3)
			{
				sc.ChangeState(SCE_SHORTE_SENT);
			}
			// if sendkey {111} is in table then ok as sendkey
			//else if (keywords4.InList(sk))
			//{
			//	sc.ChangeState(SCE_SHORTE_SENT);
			//}
			else
			{
				sc.ChangeState(SCE_SHORTE_STRING);
			}
			sc.SetState(SCE_SHORTE_STRING);
		}
		// check if next portion is again a sendkey
		if (sc.atLineEnd)
		{
			sc.ChangeState(SCE_SHORTE_STRING);
			sc.SetState(SCE_SHORTE_DEFAULT);
		}
    }
	//*************************************
	sc.Complete();
}

//
static bool IsStreamCommentStyle(int style) {
    return style == SCE_SHORTE_COMMENT || style == SCE_SHORTE_COMMENTBLOCK;
}

//
// Routine to find first none space on the current line and return its Style
// needed for comment lines not starting on pos 1
static int GetStyleFirstWord(unsigned int szLine, Accessor &styler)
{
	int nsPos = styler.LineStart(szLine);
	int nePos = styler.LineStart(szLine+1) - 1;
	while (isspacechar(styler.SafeGetCharAt(nsPos)) && nsPos < nePos)
	{
		nsPos++; // skip to next char

	} // End While
	return styler.StyleAt(nsPos);

} // GetStyleFirstWord()


//
static void FoldShorteDoc(unsigned int startPos, int length, int, WordList *[], Accessor &styler)
{
	int endPos = startPos + length;
	// get settings from the config files for folding comments and preprocessor lines
    bool foldComment = 1; //styler.GetPropertyInt("fold.comment") != 0;
	bool foldInComment = styler.GetPropertyInt("fold.comment") == 2;
	bool foldCompact = styler.GetPropertyInt("fold.compact", 1) != 0;
	bool foldpreprocessor = styler.GetPropertyInt("fold.preprocessor") != 0;
	// Backtrack to previous line in case need to fix its fold status
	int lineCurrent = styler.GetLine(startPos);
	if (startPos > 0) {
		if (lineCurrent > 0) {
			lineCurrent--;
			startPos = styler.LineStart(lineCurrent);
		}
	}
	// vars for style of previous/current/next lines
	int style = GetStyleFirstWord(lineCurrent,styler);
	int stylePrev = 0;
	// find the first previous line without continuation character at the end
	while ((lineCurrent > 0 && IsContinuationLine(lineCurrent,styler)) ||
	       (lineCurrent > 1 && IsContinuationLine(lineCurrent-1,styler))) {
		lineCurrent--;
		startPos = styler.LineStart(lineCurrent);
	}
	if (lineCurrent > 0) {
		stylePrev = GetStyleFirstWord(lineCurrent-1,styler);
	}
	// vars for getting first word to check for keywords
	bool FirstWordStart = false;
	bool FirstWordEnd = false;
	char szKeyword[11]="";
	int	 szKeywordlen = 0;
	char szThen[5]="";
	int	 szThenlen = 0;
	bool ThenFoundLast = false;
	// var for indentlevel
	int levelCurrent = SC_FOLDLEVELBASE;
	if (lineCurrent > 0)
		levelCurrent = styler.LevelAt(lineCurrent-1) >> 16;
	int levelNext = levelCurrent;
	//
	int	visibleChars = 0;
	char chNext = styler.SafeGetCharAt(startPos);
	char chPrev = ' ';
    bool in_block = false;

	//
	for (int i = startPos; i < endPos; i++) {
		char ch = chNext;
		chNext = styler.SafeGetCharAt(i + 1);
        chPrev = styler.SafeGetCharAt(i - 1);
		if (IsAWordChar(ch)) {
			visibleChars++;
		}
		// get the syle for the current character neede to check in comment
		int stylech = styler.StyleAt(i);
		// get first word for the line for indent check max 9 characters
		if (FirstWordStart && (!(FirstWordEnd))) {
			if (!IsAWordChar(ch)) {
				FirstWordEnd = true;
				szKeyword[szKeywordlen] = '\0';
			}
			else {
				if (szKeywordlen < 10) {
				szKeyword[szKeywordlen++] = static_cast<char>(tolower(ch));
				}
			}
		}
		// start the capture of the first word
		if (!(FirstWordStart)) {
			if (IsAWordChar(ch) || IsAWordStart(ch) || ch == '#') {
				FirstWordStart = true;
				szKeyword[szKeywordlen++] = static_cast<char>(tolower(ch));
			}
		}
		// only process this logic when not in comment section
		if (!(stylech == SCE_SHORTE_COMMENT)) {
			if (ThenFoundLast) {
				if (IsAWordChar(ch)) {
					ThenFoundLast = false;
				}
			}
			// find out if the word "then" is the last on a "if" line
			if (FirstWordEnd && strcmp(szKeyword,"if") == 0) {
				if (szThenlen == 4) {
					szThen[0] = szThen[1];
					szThen[1] = szThen[2];
					szThen[2] = szThen[3];
					szThen[3] = static_cast<char>(tolower(ch));
					if (strcmp(szThen,"then") == 0 ) {
						ThenFoundLast = true;
					}
				}
				else {
					szThen[szThenlen++] = static_cast<char>(tolower(ch));
					if (szThenlen == 5) {
						szThen[4] = '\0';
					}
				}
			}
		}


#if 0
        if(ch == '@' && (i == 0 || chPrev == '\n'))
        {
            if(in_block)
            {
                levelNext--;
                i-=1;
                in_block=false;
            }
            else
            {
                levelNext++;
                in_block=true;
            }
        }
#endif

		// End of Line found so process the information
        if ((ch == '\r' && chNext != '\n') || (ch == '\n') || (i == endPos))
        {


#if 0
            // **************************
			// Folding logic for Keywords
			// **************************
			// if a keyword is found on the current line and the line doesn't end with _ (continuation)
			//    and we are not inside a commentblock.
			if (szKeywordlen > 0 && (!(chPrev == '_')) &&
				((!(IsStreamCommentStyle(style)) || foldInComment)) ) {
				szKeyword[szKeywordlen] = '\0';
				// only fold "if" last keyword is "then"  (else its a one line if)
				if (strcmp(szKeyword,"if") == 0  && ThenFoundLast) {
						levelNext++;
				}
				// create new fold for these words
				if (strcmp(szKeyword,"do") == 0   || strcmp(szKeyword,"for") == 0 ||
					strcmp(szKeyword,"func") == 0 || strcmp(szKeyword,"while") == 0||
					strcmp(szKeyword,"with") == 0 || strcmp(szKeyword,"#region") == 0 ) {
						levelNext++;
				}
				// create double Fold for select&switch because Case will subtract one of the current level
				if (strcmp(szKeyword,"select") == 0 || strcmp(szKeyword,"switch") == 0) {
						levelNext++;
						levelNext++;
				}
				// end the fold for these words before the current line
				if (strcmp(szKeyword,"endfunc") == 0 || strcmp(szKeyword,"endif") == 0 ||
					strcmp(szKeyword,"next") == 0    || strcmp(szKeyword,"until") == 0 ||
					strcmp(szKeyword,"endwith") == 0 ||strcmp(szKeyword,"wend") == 0){
						levelNext--;
						levelCurrent--;
				}
				// end the fold for these words before the current line and Start new fold
				if (strcmp(szKeyword,"case") == 0      || strcmp(szKeyword,"else") == 0 ||
					strcmp(szKeyword,"elseif") == 0 ) {
						levelCurrent--;
				}
				// end the double fold for this word before the current line
				if (strcmp(szKeyword,"endselect") == 0 || strcmp(szKeyword,"endswitch") == 0 ) {
						levelNext--;
						levelNext--;
						levelCurrent--;
						levelCurrent--;
				}
				// end the fold for these words on the current line
				if (strcmp(szKeyword,"#endregion") == 0 ) {
						levelNext--;
				}
			}
#endif

			// Preprocessor and Comment folding
			int styleNext = GetStyleFirstWord(lineCurrent + 1,styler);
			// *************************************
			// Folding logic for preprocessor blocks
			// *************************************
			// process preprosessor line
#if 0
            if (foldpreprocessor && style == SCE_SHORTE_PREPROCESSOR) {
				if (!(stylePrev == SCE_SHORTE_PREPROCESSOR) && (styleNext == SCE_SHORTE_PREPROCESSOR)) {
				    levelNext++;
				}
				// fold till the last line for normal comment lines
				else if (stylePrev == SCE_SHORTE_PREPROCESSOR && !(styleNext == SCE_SHORTE_PREPROCESSOR)) {
					levelNext--;
				}
			}
#endif
/*
            if(style == SCE_SHORTE_MACRO)
            {
                if (!(styleNext != SCE_SHORTE_MACRO) && (styleNext == SCE_SHORTE_MACRO)) {
                    levelNext++;
                }
                #if 0
                // fold till the last line for normal comment lines
                else if (stylePrev == SCE_SHORTE_MACRO && !(styleNext == SCE_SHORTE_MACRO)) {
                    levelNext--;
                }
                #endif
            }
*/

/*
            if(style == SCE_SHORTE_CODE_BLOCK)
            {
                static bool is_code_block = false;

                if (!(styleNext != SCE_SHORTE_CODE_BLOCK) && (styleNext == SCE_SHORTE_CODE_BLOCK)) {
                    if(!is_code_block)
                    {
                        levelNext++;
                        is_code_block = true;
                    }
                }
                // fold till the last line for normal comment lines
                else if (stylePrev == SCE_SHORTE_CODE_BLOCK && !(styleNext == SCE_SHORTE_CODE_BLOCK)) {
                    if(is_code_block)
                    {
                        levelNext--;
                        is_code_block = false;
                    }
                }
            }
*/

			// *********************************
			// Folding logic for Comment blocks
			// *********************************
			if (foldComment && IsStreamCommentStyle(style)) {
				// Start of a comment block
				if (!(stylePrev==style) && IsStreamCommentStyle(styleNext) && styleNext==style) {
				    levelNext++;
				}
				// fold till the last line for normal comment lines
				else if (IsStreamCommentStyle(stylePrev)
						&& !(styleNext == SCE_SHORTE_COMMENT)
						&& stylePrev == SCE_SHORTE_COMMENT
						&& style == SCE_SHORTE_COMMENT) {
					levelNext--;
				}
                #if 0
				// fold till the one but last line for Blockcomment lines
				else if (IsStreamCommentStyle(stylePrev)
						&& !(styleNext == SCE_SHORTE_COMMENTBLOCK)
						&& style == SCE_SHORTE_COMMENTBLOCK) {
					levelNext--;
					levelCurrent--;
				}
                #endif
			}

            if(style == SCE_SHORTE_CODE_BLOCK)
            {
                // Start of a code block
                if (!(stylePrev==style) && styleNext==style) {
                    levelNext++;
                }
                else if (!(styleNext == SCE_SHORTE_CODE_BLOCK)
                        && stylePrev == SCE_SHORTE_CODE_BLOCK
                        && style == SCE_SHORTE_CODE_BLOCK) {
                    levelNext--;
                }
            }
            else if(chNext == '@')
            {
                if(in_block)
                {
                    levelNext=0;
                    levelCurrent=0;
                    in_block=false;
                }
                else
                {
                    levelNext=1;
                    levelCurrent=1;
                    in_block=true;
                }
            }

			int levelUse = levelCurrent;
			int lev = levelUse | levelNext << 16;
			if (visibleChars == 0 && foldCompact)
				lev |= SC_FOLDLEVELWHITEFLAG;
			if (levelUse < levelNext) {
				lev |= SC_FOLDLEVELHEADERFLAG;
			}
			if (lev != styler.LevelAt(lineCurrent)) {
				styler.SetLevel(lineCurrent, lev);
			}
			// reset values for the next line
			lineCurrent++;
			stylePrev = style;
			style = styleNext;
			levelCurrent = levelNext;
			visibleChars = 0;
			// if the last character is an Underscore then don't reset since the line continues on the next line.
			if (!(chPrev == '_')) {
				szKeywordlen = 0;
				szThenlen = 0;
				FirstWordStart = false;
				FirstWordEnd = false;
				ThenFoundLast = false;
			}
		}
		// save the last processed character
		if (!isspacechar(ch)) {
			chPrev = ch;
			visibleChars++;
		}
	}
}


//

static const char * const ShorteWordLists[] = {
    "#shorte keywords",
    "#shorte functions",
    "#shorte macros",
    "#shorte Sent keys",
    "#shorte Pre-processors",
    "#shorte Special",
    "#shorte Expand",
    "#shorte UDF",
    0
};

LexerModule lmShorte(SCLEX_SHORTE, ColouriseShorteDoc, "tpl", NULL /* FoldShorteDoc*/ , ShorteWordLists);
