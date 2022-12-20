//	Function Name:          <Several>
//	Directory Name:
//	File Name:              ATLAS_Native_Generic_Serial.h
//
//	Associated Files:
//
//  Compiling Procedure:	
//
//	Linking Procedure:
//	Related Documents:
//	
//	Installation:           Argonne National Laboratory
//                          Physics Division
//                          ATLAS Facility
//
//	Author(s):              J. Dreher (C. Peters)
//	Date:                   12-Feb-2013
//
//	Revisions:
//
//	Description:

//#ifndef ATLAS_NATIVE_GENERIC_SERIAL_H
#define	ATLAS_NATIVE_GENERIC_SERIAL_H

#define SUCCESS 1
#define FAILURE 0

#define MAXOPENPORTS		    	10

#define MAXNAMELENGTH               256
#define MAXLENGTH                   512
#define MAXCOMMANDSIZE              200
#define REPETITIONRATEMAXSIZE       4
#define ATTENUATIONRATIOMAXSIZE     3

#ifndef LOCAL_VSYSERROR
#define LOCAL_VSYSERROR                  FAILURE
#endif

#define SERIAL_PORT_LOCK_TIMEOUT    30 // seconds



#include "/vsys/include/vdb_class.h"
#include "/vsys/include/vdb_convert.h"
#include "/vsys/include/vdb_descrip.h"
#include "/vsys/include/vdb_routines.h"
#include "/vsys/include/vdb_structure.h"
#include "/vsys/include/vdb_hardware.h"
#include "/vsys/include/comand.h"
  

#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <termios.h>
#include <unistd.h>
#include <string.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/time.h>
#include <signal.h>
#include <syslog.h>


#ifdef MULTITHREADED       
int ATLAS_Native_ReserveOpen_Port (int *piHparams, int iPriority);
#else
int ATLAS_Native_ReserveOpen_Port (int *piHparams);
#endif 

int ATLAS_Native_CloseRelease_Port (int *piHparams, int iReturn);
int ATLAS_Native_SendCommand (char *pcReadBuffer, char *pcWriteBuffer,
                              int *piHparams, int iReadBuffLength,
                              int iWriteBuffLength, int iWaitTime,
                              int *piNumBytesRead);
    
int ATLAS_Native_Generic_Serial
(
    char *pcReadBuffer,
    char *pcWriteBuffer,
    int  *piHparams,
    int  iReadBuffLength,
    int  iWriteBuffLength,
    int  iWaitTime,
    int  *piNumBytesRead
);

struct NativeSerialParameters
{
    int iTTYID;
    int iBaudRate;
    int iParity;
    int iBlockFlag;
    int iIgnoreNewlines;
};

//#endif	/* ATLAS_NATIVE_GENERIC_SERIAL_H */
