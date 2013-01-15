/******************************************************************************
 *
 * Filename:
 *    ${filename}
 *
 * Description:
 *    ${description}
 *
 ******************************************************************************
 *
 * Copyright 2010 by Cortina Systems. All text contained within remains property
 * of Cortina Sytems corporation and may not be modified, distributed, or
 * reproduced without the express written permission of Cortina Systems
 *
 *****************************************************************************/

%module leeds
%{
    typedef int (*READFUNC)(unsigned int addr, unsigned short* data, void*);
    typedef int (*WRITEFUNC)(unsigned int addr, unsigned short data, void*);
    
    READFUNC  g_callback_read[4];
    void*     g_callback_read_clientdata[4];
    WRITEFUNC g_callback_write[4];
    void*     g_callback_write_clientdata[4];

%}

