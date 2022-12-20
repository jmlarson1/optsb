//    Function Name:        ATLAS_Native_Generic_Serial
//    Directory Name:
//    File Name:            ATLAS_Native_Generic_Serial.c
//
//    Associated Files:
//
//    Linking Procedure:
//
//    Related Documents:
//    
//    Installation:         Argonne National Laboratory
//                          Physics Division
//                          ATLAS Facility
//
//    Author(s):            J. Dreher (C. Peters)
//    Date:                 12-Feb-2013
//
//    Revisions:            
//
//                          C. Peters
//                          28-Aug-2018
//
//                          There is an apparent bug wherein if there is
//                          an error with writing or reading to/from the
//                          serial port, the error is returned in the
//                          ATLAS_Native_SendCommand() function, but that
//                          information is not passed to the last phase
//                          of ATLAS_Native_CloseRelease_Port().  So this
//                          means that the CloseRelease will NEVER close
//                          the port even if there is an error.  The 
//                          result is that unplugging and replugging a 
//                          USB connection may get renamed to ttyUSB1
//                          or such, and will not get closed and 
//                          re-opened to the new port number. Therefore,
//                          added a parameter to the CloseRelease function
//                          to pass on the iReturn information. 
//
//                          C. Peters
//    						13-Nov-2017
//
//    						Added code to disable the ICANON mode which 
//    						returns strings based on newlines, to the
//    						section of code which ignores newlines.  This
//    						way we can handle a device which uses local
//    						echo to echo back the command before sending
//    						the response on a new line.  Also changed 
//    						several printfs to syslog LOG_DEBUGs.
//
//    						C. Peters
//    						13-Nov-2017
//
//    						On the same day as the above change, realized
//    						that the struct flock 'pstSTLock' which was 
//    						being used to facilitate multi process file 
//    						locking was esentially static, therefore
//    						hardcoded this as a global setting and only
//    						the "WRLCK" or "UNLCK" parameter changes.
//
//    						Also fixed a timing bug where the iWaitTime
//    						passed in was being treated in seconds.  IE,
//    						'50' was causing a 50 SECOND delay.  Whomever
//    						wrote that (me) should be ashamed!
//    						
//    						M. Power
//                          18-Sept-2017
//
//                          As was done in the ATLAS_Hytec_Handlers version,
//                          Modularized the functions so that if specific 
//                          semaphore handling (for mulitiple commands
//                          like in BK_Precision and Genesys handlers) 
//                          is needed they can be called directly.
//
//	Description:            
//
//  Notes(s):              
//
//  						Setting all the interface attributes for each and every
//  						device is.....not fun.  We have made some assumptions
//  						to make this easier.  Since the development of this code
//  						we have moved to an asyncrounous model where there is 
//  						no blocking.  Therefore, HParam[3] below is not used.
//  						It could be used for some other HParam like "Newlines"
//  						but that may break some other handler.  Leaving it 
//  						for now.   
//
//  						The IgnoreNewlines Hparam[4] is particularly interesting.
//  						This affects both a disabling of 'Canocial' mode where the
//  						kernel performs transactions based on newlines and also 
//  						causes the handler to actually return non-printable values
//  						for \n and \r instead of trimming them off.  This is
//  						useful for binary devices and non-ASCII devices, or devices
//  						which return MORE THAN one line at a time.
//
//                          HParams Index:
//                              0:  PortID		- Usually 0, gets filled by handler
//                              1:  BaudRate	- 9600, 19200, etc
//                              2:  Parity		- 0 for no parity, 1 for odd
//                              3:  BlockFlag	- 0 for no blocking (not used)
//                              4:  Ignore Newlines - See note above.
//******************************************************************************

#include "ATLAS_Native_Generic_Serial.h"
#include <semaphore.h>
#include <unistd.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/types.h>
#include <sys/syscall.h>
#include <sys/time.h>

//#define DEBUG_NATIVE_SERIAL
#define SHM_SIZE    256

// Set the global syslog logging options
#ifndef DEBUG_NATIVE_SERIAL
static const int G_iSyslogOptions = (LOG_CONS | LOG_PID);
//static int G_iSyslogPriority = LOG_WARNING;
#else
static const int G_iSyslogOptions = (LOG_CONS | LOG_PID | LOG_PERROR);
//static int G_iSyslogPriority = LOG_ERR;
#endif

static int G_iSyslogFacility = LOG_LOCAL0;

// 13-Nov-2017 C. Peters - Hardcoded a global version of the lock structure
// A write lock on the first byte of the port
static struct flock G_stLock = {0, .l_start = 0, .l_whence = SEEK_SET, .l_len = 1} ;

// Create structure for shared variables
struct stSharedMemVars
{
    pthread_mutex_t mutex;
    pthread_cond_t conditionVar;
    sem_t semHighPriority;
};
struct stSharedMemVars *G_pstSharedMem;
void   *G_pSharedMem = ((void *)-1);

// Every process which calls this handler is only allowed
// a certain number of file descriptors to use.
// We will link EACH fd to a certain ttyUSB port IN ORDER.
// Keep track of them in this global array, so we don't
// have to keep closing-and-re-opening them.
// These are defaulted to -1, but if the array size is
// changed, this initialization will also have to change.
int G_iSerialPortDescriptor[MAXOPENPORTS] =
{-1, -1, -1, -1, -1, -1, -1, -1, -1, -1};

// Private Function Prototypes
static void ATLAS_Serial_HandleErrorMessage(int, const char*, int);
static int ATLAS_Serial_SetInterfaceAttributes(int, int, int, int);
//static void ATLAS_Serial_SetBlocking (int, int);
static int ATLAS_Serial_ConvertBaudRate (int *);

//******************************************************************************
//      Function Name:      catch_alarm
//
//      Inputs:             int - SignalNo
//
//      Description:       
//                         
//******************************************************************************
static void catch_alarm (int iSignalNo)
{
  // This just keeps the program from exiting due to the alarm
  syslog(LOG_ERR, "Alarm Timeout!!! - PID = %d\n", getpid());
  return;
}


//******************************************************************************
//      Function Name:      ATLAS_Serial_HandleErrorMessage
//
//      Inputs:             int 		iLogLevel
//      					const char  csErrorMessage[MAXERRORLENGTH]
//                          int         ErrorNum
//
//      Description:       prints error number to syslog
//                         
//******************************************************************************
static void ATLAS_Serial_HandleErrorMessage(int iLogLevel, const char *csErrorMessage, int iErrorNum)
{
    syslog(iLogLevel, "%s - Error no %d - %s\n", csErrorMessage, iErrorNum, strerror(errno));
    return;
}

//******************************************************************************
//      Function Name:      ATLAS_Serial_SetInterfaceAttributes
//
//      Inputs:             int     iTerminalFileDesc
//                          int     iBaudRate
//                          int     iParity
//                          int     iIgnoreNewlines
//
//      Outputs:
//
//      Return Value:       int     Success = 1, Failure = 0
//
//      Description:        Sets the terminal device's attributes
//                         
//******************************************************************************
static int ATLAS_Serial_SetInterfaceAttributes(int iTerminalFileDesc, int iBaudRate, int iParity, int iIgnoreNewlines)
{
    // Structure for terminal device to set interface attributes for
    struct termios stTTYDevice;
    
    // Integer for return value
    int iReturn = SUCCESS;
    
    // Clear the terminal device's structure's memory
    memset(&stTTYDevice, 0, sizeof(stTTYDevice));
    
    // Get the terminal device's parameters
    if (tcgetattr (iTerminalFileDesc, &stTTYDevice) != 0)
    {
        ATLAS_Serial_HandleErrorMessage(LOG_ERR, "ATLAS_Serial_SetInterfaceAtrributes -- Error %d from tcgetattr\n",
                                        errno);
        return FAILURE;
    }
    
    // Set the output baud rate of the terminal device
    if (cfsetospeed (&stTTYDevice, iBaudRate) != 0)
    {
        ATLAS_Serial_HandleErrorMessage(LOG_ERR, "ATLAS_Serial_SetInterfaceAtrributes -- Error %d from cfsetospeed\n",
                                        errno);
    }
    
    // Set the input baud rate of the terminal device
    if (cfsetispeed (&stTTYDevice, iBaudRate) != 0)
    {
        ATLAS_Serial_HandleErrorMessage(LOG_ERR, "ATLAS_Serial_SetInterfaceAtrributes -- Error %d from cfsetispeed\n",
                                        errno);
    }
 
    // Setting these options has been a relative pain. 
    // For now, default to 8N1.  Need to test with laser.
    if (iParity)
    {
        stTTYDevice.c_cflag &= PARENB;
    }
    else
    {
        stTTYDevice.c_cflag &= ~PARENB; // No Parity
    }
    
    stTTYDevice.c_cflag &= ~CSTOPB; // 1 Stop bit
    stTTYDevice.c_cflag &= ~CSIZE;  // Size mask....
    stTTYDevice.c_cflag |= CS8;     // ...is 8 bits
    
 
    // JESS'S TRIUMPH! 
    // Make sure we ignore any Newline 0xa in the stream
    if (iIgnoreNewlines)
    {
        stTTYDevice.c_iflag &= ~(IXON | IXOFF | IXANY);
        stTTYDevice.c_iflag |= (INLCR | ICRNL);
 		// 13-Nov-2017 C. Peters
   		// If we're ignoring newlines, then also disable CONICAL mode (on by default)
		stTTYDevice.c_lflag &= ~ICANON; 
        //stTTYDevice.c_cc[VTIME] = 1; 
        //stTTYDevice.c_cc[VMIN] =  0; 
    }
    else
    {
        // Then we ARE using CONICAL mode
        stTTYDevice.c_lflag |= ICANON;  
        stTTYDevice.c_iflag &= ~(INLCR | ICRNL);
    }
   
    // Set the terminal device's attributes where the changes will be made
    // immediately
    if (tcsetattr (iTerminalFileDesc, TCSANOW, &stTTYDevice) != 0)
    {
        ATLAS_Serial_HandleErrorMessage(LOG_ERR, "ATLAS_Serial_SetInterfaceAtrributes -- Error %d from tcsetattr\n",
                                        errno);
        iReturn = FAILURE;
    }
    
    return iReturn;   
}


//******************************************************************************
//      Function Name:      ATLAS_Serial_ConvertBaudRate
//
//      Inputs:             int     *iBaudRate
//
//      Outputs:
//
//      Return Value:       int     Success = 1, Failure = 0
//
//      Description:        changes to Baudrate definition in ???
//                         
//******************************************************************************
static int ATLAS_Serial_ConvertBaudRate (int *iBaudRate)
{
    int iReturn = SUCCESS;
    
    // Begin switch case for the baud rate
    // Baud rates for serial ports begin with a 'B' (i.e. B115200), so 
    // numerical value needs to be converted to corresponding 'B' value
    // (defined in termios.h)
    switch (*iBaudRate)
        {
            // Hang up
            case 0:
            {
                *iBaudRate = B0;
                break;
            }
            // 50 baud
            case 50:
            {
                *iBaudRate = B50;
                break;
            }
            // 75 baud
            case 75:
            {
                *iBaudRate = B75;
                break;
            }
            // 110 baud
            case 110:
            {
                *iBaudRate = B110;
                break;
            }
            // 134.5 baud
            case 134:
            {
                *iBaudRate = B134;
                break;
            }
            // 150 baud
            case 150:
            {
                *iBaudRate = B150;
                break;
            }
            // 200 baud
            case 200:
            {
                *iBaudRate = B200;
                break;
            }
            // 300 baud
            case 300:
            {
                *iBaudRate = B300;
                break;
            }
            // 600 baud
            case 600:
            {
                *iBaudRate = B600;
                break;
            }
            // 1200 baud
            case 1200:
            {
                *iBaudRate = B1200;
                break;
            }
            // 1800 baud
            case 1800:
            {
                *iBaudRate = B1800;
                break;
            }
            // 2400 baud
            case 2400:
            {
                *iBaudRate = B2400;
                break;
            }
            // 4800 baud
            case 4800:
            {
                *iBaudRate = B4800;
                break;
            }
            // 9600 baud
            case 9600:
            {
                *iBaudRate = B9600;
                break;
            }
            // 19200 baud
            case 19200:
            {
                *iBaudRate = B19200;
                break;
            }
            // 38400 baud
            case 38400:
            {
                *iBaudRate = B38400;
                break;
            }
            // 57600 baud
            case 57600:
            {
                *iBaudRate = B57600;
                break;
            }
            // 115200 baud
            case 115200:
            {
                *iBaudRate = B115200;
                break;
            }
            default:
            {
                syslog(LOG_ERR, "ATLAS_Serial_ConvertBaudRate -- Invalid baud rate of %d "
                        "given\n", *iBaudRate);
                iReturn = FAILURE;
                break;
            }
        }
    
    return iReturn;
}
//******************************************************************************
//      Function Name:      ATLAS_Native_ReserveOpen_Port
//
//      Description:        This function will create and book the semaphore 
//                          and open the serial port
//
//      Inputs/Outputs:     int *piHparams - pointer to hParam array sent to main handler,
//                                           not modified
//
//      Return value:       VSYS_SUCCESS (1) if successful, LOCAL_VSYSERROR (0) if failure
//******************************************************************************
#ifdef MULTITHREADED
int ATLAS_Native_ReserveOpen_Port (int *piHparams, int iPriority)
#else
int ATLAS_Native_ReserveOpen_Port (int *piHparams)
#endif
{
    int iReturn = SUCCESS;
    int iPortID;
    char csPortID[2] = {'\0', '\0'};
    char csSerialPortName[MAXNAMELENGTH];
    unsigned int uiOldTimeout;
    struct sigaction stAction, stOld_Action;

#ifdef MULTITHREADED
    int iSharedMemKey, iSharedMemID;
    pthread_mutexattr_t mutexAttr;
    pthread_condattr_t conditionAttr;
    struct shmid_ds stSharedMemParams;
    int iMutexWaitTime = 10;
    int iSemValue;
#endif

    // structure for holding hparam values
    struct NativeSerialParameters stHParams;

    int iWriteCheck;
    char cWaiting = 0;

#ifdef DEBUG_NATIVE_SERIAL
    printf("***** ATLAS_Native_ReserveOpen_Port -- starting, pid = %d, tid = %li... *****\n", getpid (), syscall(SYS_gettid));
#endif  
  
   	// -- Set the name of the serial port --
   
    // Use a local variable for convienience
    iPortID = piHparams[0];
 
    // Check if this is a 'test' call to the non-USB serial port
    if (iPortID != 99)
    {
        // Make sure we are using a port lower than the array can fit
        if (iPortID < MAXOPENPORTS)
        {
                // Convert the first hParam to a Char
                csPortID[0] = (char)(iPortID + 0x30);
                strncpy(csSerialPortName, "/dev/ttyUSB", MAXNAMELENGTH);
				strcat(csSerialPortName, csPortID);
        }
        else
        {
            printf("ERROR: Cannot fit ports beyond: tty[%i]!\n", iPortID);
           	iPortID = 0;
            iReturn = FAILURE;
        }
    }
    else
    {
        // This is a test
        strncpy(csSerialPortName, "/home/controlsys/IAMLASER.txt", MAXNAMELENGTH);
    
         // Remember to set the fd location as if we are talking to USB0
        iPortID = 0;
        G_iSerialPortDescriptor[0] = -1;
    }
    
    // This is an attempt to implement file locking on this port.
    // This should ensure that only one process is writing/reading
    // to this port at a time
    
    // Cancel any existing alarm
    uiOldTimeout = alarm(0);

    // Establish signal handler for a lock timeout
    stAction.sa_handler = catch_alarm;
    sigemptyset (&stAction.sa_mask);
    stAction.sa_flags = SA_SIGINFO;
    sigaction (SIGALRM, &stAction, &stOld_Action);

    // Check if we have already opened the port
    if (G_iSerialPortDescriptor[iPortID] < 0)
    {        
        // Get hparams values
        stHParams.iBaudRate     	= piHparams[1];
        stHParams.iParity       	= piHparams[2];
        stHParams.iBlockFlag    	= piHparams[3];
        stHParams.iIgnoreNewlines  	= piHparams[4];
        
        // Create open file description for serial port (return is checked below)
        G_iSerialPortDescriptor[iPortID] = open (csSerialPortName, O_RDWR | O_NOCTTY | O_SYNC);
        if (-1 == G_iSerialPortDescriptor[iPortID])
        {
            syslog(LOG_WARNING, "Error Opening port! %s\n", csSerialPortName); 

#ifdef DEBUG_NATIVE_SERIAL
            perror("Open failed!");
#endif
            // Return immediatley
            return(FAILURE);
        }
        else
        {
            syslog(LOG_DEBUG, "Opened port %s: using fd[%i]\n", csSerialPortName, G_iSerialPortDescriptor[iPortID]);
        }
        
		// Decide if we are setting the interface attributes here (not for tests)
		if (iPortID != 99)
        {
            // Send baud rate to conversion function 
            iReturn = ATLAS_Serial_ConvertBaudRate(&stHParams.iBaudRate);        
        }

        if (SUCCESS == iReturn)
        {
            if (piHparams[0] != 99)
            {
                // Set baud rate and parity
               iReturn = ATLAS_Serial_SetInterfaceAttributes(G_iSerialPortDescriptor[piHparams[0]],
                                                             stHParams.iBaudRate, stHParams.iParity,
                                                             stHParams.iIgnoreNewlines);
			}
			// else do nothing, let error fall thru
        }
        else
        {
            syslog(LOG_ERR, "Error converting baud rate %i", stHParams.iBaudRate);
            iReturn = FAILURE;
        }
    }
    else if (-1 == G_iSerialPortDescriptor[iPortID])
    {
		// This is a warning only, could just be that user unplugged it.
        ATLAS_Serial_HandleErrorMessage(LOG_WARNING, "ATLAS_Native_Serial_Handlers -- Error opening serial port\n", errno);
        iReturn = FAILURE;       
    }  
    // else, we have already opened it.
    
    // Check for success opening the port
    if (SUCCESS == iReturn)
    {

        // ** The file locking version ** //
       
#ifndef MULTITHREADED

        // Set the file lock timeout in seconds
        alarm(SERIAL_PORT_LOCK_TIMEOUT);

        // This is a blocking call to lock.  If the alarm timeout occurs,
        // the signal handler will cancel the lock
     
        // Check to see if the port is busy already and print status if so
    	G_stLock.l_type = F_WRLCK;
	   	iWriteCheck = fcntl(G_iSerialPortDescriptor[iPortID], F_GETLK, &G_stLock);
        if (G_stLock.l_pid != 0)
        {
            // Flag that we are waiting on another process, so we can delay later on
            cWaiting = 1;
            syslog(LOG_DEBUG, "OpenReserve_Port: Waiting for Process %i to finish...\n", 
                   G_stLock.l_pid);
        }

        // Get in line to write to the file and wait
        G_stLock.l_type = F_WRLCK;
        iWriteCheck = fcntl(G_iSerialPortDescriptor[iPortID], F_SETLKW, &G_stLock);
        if (iWriteCheck < 0)
        {
            // If the lock failed, it either timed out or was inturrupted by a signal
            // We will return here (carefully) and report an error.
            syslog(LOG_ERR, "Write Lock timeout pid: %d - %s\n", G_stLock.l_pid, strerror(errno));
            alarm(0);            
            // Let the error fall thru so the port is unlocked
            iReturn = FAILURE;
        }
        else if (iWriteCheck > 0)
        {
            syslog(LOG_ERR, "Lock call returned nonzero error");
        }
        else
        {
            syslog(LOG_DEBUG, "ReserveOpen_Port, File <%i>Locked!\n", G_iSerialPortDescriptor[iPortID]); 
        }    


        // ** The system wide shared memory version **i ----------------------------------------- //
#else
        // This is an attempt at system-wide, shared memory based, priorty, resource locking
        // Remember, file locking doesn't work multithreaded because it's the same PID!

        // Create key for shared memory
        iSharedMemKey = ftok(csSerialPortName, 'R');
        if(iSharedMemKey != -1)
        {
            // Create ID for shared memory
            iSharedMemID = shmget(iSharedMemKey, SHM_SIZE, IPC_CREAT | 0777);
            if(iSharedMemID != -1)
            {
                // Copy info from the kernel data structure associated with shmid
                // into the shmid_ds structure pointed to by stSharedMemParams
                shmctl(iSharedMemID, IPC_STAT, &stSharedMemParams);
                
#ifdef DEBUG_NATIVE_SERIAL
                printf("THE NUM OF PROCESSES ATTACHED IS:\t%i\n", (int)stSharedMemParams.shm_nattch);
                printf("THE PID OF THE LAST SHMAT/SHMDT IS:\t%i\n", stSharedMemParams.shm_lpid);
#endif
                // Check if we have already attached to the shared memory for this process
                if (G_pSharedMem == (void *)-1)
                {
                    // Assign the address of the shared memory segment to pointer
                    G_pSharedMem = shmat(iSharedMemID, (void *)0, 0); 

                    // If shared memory was allocated correctly, convert pointer into
                    // structure so we don't have to continue de-referencing it and
                    // have access to the shared vars in the structure
                    if(G_pSharedMem != (void *)-1)
                    {
                        // Assign pointer to the location of the shared memory
                        G_pstSharedMem = (struct stSharedMemVars*) G_pSharedMem;

                        // If this was the first attach, check if any one else is attached 
                        if (stSharedMemParams.shm_nattch == 0)
                        {
                            syslog(LOG_WARNING, "Initializing shared memory!....\n");

                            // Mutex initialization and declaration of attributes
                            pthread_mutexattr_init(&mutexAttr);
                            pthread_mutexattr_setpshared(&mutexAttr, PTHREAD_PROCESS_SHARED);
                            pthread_mutex_init(&G_pstSharedMem->mutex, &mutexAttr);

                            // Declare and initialize condition variable & attributes
                            pthread_condattr_init(&conditionAttr);
                            pthread_condattr_setpshared(&conditionAttr, PTHREAD_PROCESS_SHARED);
                            pthread_cond_init(&G_pstSharedMem->conditionVar, &conditionAttr);

                            // Initialize the semaphore which will indicate a high-priorty thread is waiting
                            sem_init(&G_pstSharedMem->semHighPriority, 1, 1); // The first '1' indicates shared memory
                        }
                        // else, someone else it attached and already init'ed shared variables
                    }
                    else
                    {
                        perror("Shared memory not attached!");
                        iReturn = LOCAL_VSYSERROR;
                    }
                }
                // else, it was already mapped, do nothing

                // Check to make sure everything is OK with the shared memory above
                if (VSYS_SUCCESS == iReturn)
                {
                    // Ok, now we actually get in line to access the resource
                    if (iPriority > 0)
                    {
                        // High Priority
                        
                        // Lock semaphore to indicate that a high priority thread is waiting
                        sem_wait(&G_pstSharedMem->semHighPriority);

    #ifdef DEBUG_NATIVE_SERIAL
                        printf("Thread is a high priority thread and has locked semaphore\n");
    #endif
                        // Lock mutex
                        pthread_mutex_lock(&G_pstSharedMem->mutex);

    #ifdef DEBUG_NATIVE_SERIAL
                        printf("Thread %li is a high priority thread and has locked mutex %p\n",syscall(SYS_gettid), &G_pstSharedMem->mutex);
    #endif
                        // Unlock semaphore to indicate that a high priority thread is no longer waiting
                        sem_post(&G_pstSharedMem->semHighPriority);

    #ifdef DEBUG_NATIVE_SERIAL
                        printf("Thread is a high priority thread and has unlocked semaphore\n");
    #endif
                        // We now have locked the resource
                    }
                    else
                    {
                        // Low priority
                        
                        // Lock mutex and get value of the semaphore here
                        pthread_mutex_lock(&G_pstSharedMem->mutex);

                        #ifdef DEBUG_NATIVE_SERIAL
                        printf("----Thread %li is a low priority thread and has locked mutex %p\n", syscall(SYS_gettid), &G_pstSharedMem->mutex);
                        #endif

                        sem_getvalue(&G_pstSharedMem->semHighPriority, &iSemValue);
                        #ifdef DEBUG_NATIVE_SERIAL
                        printf("----Low Priority Wait SEM value: '%d'\n", iSemValue);
                        #endif

                        // While there is a high priority thread waiting,
                        // call wait on condition variable and put thread
                        // to sleep
                        while(iSemValue < 1)
                        {
                            #ifdef DEBUG_NATIVE_SERIAL
                            printf("\n----SLEEPING INSIDE COND WAIT...\n");
                            #endif
        
                            printf("WARNING - Thread %x sleeping inside Cond. Wait...\n", pthread_self()); 
 
                            pthread_cond_wait(&G_pstSharedMem->conditionVar, &G_pstSharedMem->mutex);
                            sem_getvalue(&G_pstSharedMem->semHighPriority, &iSemValue);

                            // If the value of the semaphore greater than one
                            // then a high priority thread is not waiting
                            // but penalize the low priority by making it sleep
                            // and check sem value once more
                            if(iSemValue >= 1)
                            {
                                //sleep(1);
                                sem_getvalue(&G_pstSharedMem->semHighPriority, &iSemValue);
                                if (iSemValue >= 1)
                                {
                                    syslog(LOG_DEBUG, "WARNING - Thread %li is AWAKE!  Continuing...\n", syscall(SYS_gettid));
                                }
                            }
                            // else, no one else is waiting, move along
                        }
                        // end while iSemValue < 1 loop
                    }
                    // endif High Priority
                }
                // endif Success getting shared memory, let error fall thru 
            }
            else
            {
                syslog(LOG_ERR, "Shared memory ID not created successfully\n");
                perror("shmget");
                iReturn = LOCAL_VSYSERROR;
            }
        }
        else
        {
            perror("ftok");

            //iReturn = ERROR;
        }

#endif  // The file-locking version vs. the System-wide shared memory version  ----------------


        // Cancel the alarm if we made it to here
        alarm(0);

        // We now have the port, but if we were waiting on another process,
        // we don't want to execute immediatley.  Give the device a chance
        // to finish the previous transaction
        if (cWaiting)
        {
            //vdb_wait_ms(&iMutexWaitTime);
        }
    }
	// else, let the error from opening bad fall thru

    if (VSYS_SUCCESS == iReturn)
    {
        syslog(LOG_DEBUG, "Successfully locked mutex fd: %i., pid = %d, tid = %li\n", G_iSerialPortDescriptor[iPortID], getpid(), syscall(SYS_gettid));
    }

#ifdef DEBUG_NATIVE_SERIAL
    printf("***** ATLAS_Native_ReserveOpen_Port -- pid %d, tid %li, returing with %d... *****\n", 
           getpid (), syscall(SYS_gettid), iReturn);
#endif  

    return (iReturn);
}

//******************************************************************************
//      Function Name:      ATLAS_Native_CloseRelease_Port
//
//
//      Inputs/Outputs:     int *piHparams - pointer to hParam array sent to main handler,
//                                           not modified
//                          int iReturn    - This function needs to know if there was
//                                           an error during a previous operation so
//                                           we know if the port needs to be closed.
//
//      Outputs:            no outputs
//
//      Description:        This function will close the port and release the
//                          semaphore
//
//      Return value:       VSYS_SUCCESS (1) if successful, LOCAL_VSYSERROR (0) if failure
//
//******************************************************************************
int ATLAS_Native_CloseRelease_Port (int *piHparams, int iReturn)
{
    // NOTE: iReturn is passed in as a parameter
    int iPortID;
    int iWriteCheck;

#ifdef DEBUG_NATIVE_SERIAL
    printf("\tCloseRelease_Port: Unlocking File., pid = %d, tid = %li\n", getpid(), syscall(SYS_gettid));
#endif

    // Use a local variable for convienience
    iPortID = piHparams[0];

#ifndef MULTITHREADED
    // Regardless of what happened above, remember to unlock the file descriptor
    G_stLock.l_type = F_UNLCK;
	iWriteCheck = fcntl(G_iSerialPortDescriptor[iPortID], F_SETLK, &G_stLock);
    if (-1 == iWriteCheck)
    {
        syslog(LOG_ERR, "Error unlocking file descriptor: <%i>!\n", G_iSerialPortDescriptor[iPortID]);
        perror("Error on unlock!:");
		iReturn = FAILURE;
    }
	else
	{
    	syslog(LOG_DEBUG, "Successfully unlocked file fd: %i., pid = %d\n", G_iSerialPortDescriptor[iPortID], getpid());
	}

#else
    struct shmid_ds stSharedMemParams;
    int iSharedMemKey, iSharedMemID;
    char csSerialPortName[MAXNAMELENGTH];
    
    // Awaken all other threads and unlock mutex
    pthread_cond_broadcast(&G_pstSharedMem->conditionVar);
    pthread_mutex_unlock(&G_pstSharedMem->mutex);

    syslog(LOG_DEBUG, "Successfully unlocked mutex fd: %i., pid = %d, tid = %li\n", G_iSerialPortDescriptor[iPortID], getpid(), syscall(SYS_gettid));

    // If there was an error anywhere, invalidate the global fd
    // Otherwise, we think closing the port isn't necessary.  It will close when process stops.
    if (iReturn != SUCCESS)
    {
        close(G_iSerialPortDescriptor[iPortID]);
        G_iSerialPortDescriptor[iPortID] = -1;
    }

    // Get the path of the shared memory (file name)
    snprintf(csSerialPortName, MAXNAMELENGTH, "/dev/ttyS%c", (char)(iPortID + 0x30));
    
    // Create key for shared memory
    iSharedMemKey = ftok(csSerialPortName, 'R');
    if(iSharedMemKey != -1)
    {
        // Create ID for shared memory
        iSharedMemID = shmget(iSharedMemKey, SHM_SIZE, IPC_CREAT | 0777);
        if(iSharedMemID != -1)
        {
            // Check if another program is still attached to shared memory
            shmctl(iSharedMemID, IPC_STAT, &stSharedMemParams);
            
            // If only one process is attached, then we can
            // delete the shared variables
            if(stSharedMemParams.shm_nattch == 0)
            {
                //printf("Destroying shared variables......\n");
                pthread_mutex_destroy(&G_pstSharedMem->mutex);
                pthread_cond_destroy(&G_pstSharedMem->conditionVar);
                sem_destroy(&G_pstSharedMem->semHighPriority);
            }
        }
        else
        {
            perror("shmget");
        }
    }   
    else
    {
        syslog(LOG_ERR, "ATLAS_Native_Serial - ERRROR Could not retreive shared memory!\n");
        iReturn = LOCAL_VSYSERROR;
    }
 
#endif
       
    return (iReturn);
}

//******************************************************************************
//      Function Name:      ATLAS_Native_SendCommand
//
//      Description:        This function does the write/read to the port
//
//      Inputs/Outputs:     same as ATLAS_Hytec_Generic_Handler 
//      					See comments at top of file for HParam notes
//
//      Outputs:            no outputs
//
//      Return value:       VSYS_SUCCESS (1) if successful, LOCAL_VSYSERROR (0) if failure
//
//      Notes:              It must be assumed that ReserveOpen port is called
//                          BEFORE this function, in order to reserve both the
//                          port AND any shared memory between threads.
//                                                      
//******************************************************************************
int ATLAS_Native_SendCommand (char *pcReadBuffer, char *pcWriteBuffer,
                              int *piHparams, int iReadBuffLength,
                              int iWriteBuffLength, int iWaitTime,
                              int *piNumBytesRead)
{
    int iReturn = SUCCESS;
    int iPortID;
    int iWriteCheck;
    char csTempReadBuffer[MAXLENGTH];
    fd_set fdSet;
    int iSelectCheck;
    int iNumCharsRead;
	// We default to wait time being in ms, similar to vdb_wait_ms
    struct timeval stTimeout;
    
//#ifdef DEBUG_NATIVE_SERIAL
    struct timeval tv;
    struct timeval start_tv;
    double dElapsed = 0.0;
//#endif
        
    // Use a local variable for convienience
    iPortID = piHparams[0];

    // Check if someone closed the port while we were waiting on another thread
    if (G_iSerialPortDescriptor[iPortID] != 0)
    {
        // Check to see if we are writing
        if (pcWriteBuffer != NULL)
        {

#ifdef DEBUG_NATIVE_SERIAL
           printf("ATLAS_Native_Serial_Handlers - Writing Command[%i]: <%s>\n", 
                    iWriteBuffLength, pcWriteBuffer);
#endif
            // Send command
            iWriteCheck = write (G_iSerialPortDescriptor[iPortID], pcWriteBuffer, iWriteBuffLength);

            // Make sure it was successful
            if (iWriteCheck == iWriteBuffLength)
            {
#ifdef DEBUG_NATIVE_SERIAL           
            int iIndex;

                printf("SUCCESS! (Starting Timer...) Hex->");

                for (iIndex = 0; iIndex < iWriteBuffLength; iIndex++)
                {
                    printf("%x:", (unsigned char)pcWriteBuffer[iIndex]);
                }
                printf("\n\n");
#endif
                // Start timer between write and read
                gettimeofday(&start_tv, NULL);

                if (iPortID == 99)
                {
                    // Move the read position back to the beginning of the file
                    lseek(G_iSerialPortDescriptor[iPortID], 0, SEEK_SET);
                }
            
                // Wait between send and receive in MS only if not in CANOLICAL mode
                if (1 == piHparams[4])
                {
                    //vdb_wait_ms(&iWaitTime);
                }
            }
            else
            {
                // This is just a warning, could be that user unplugged device.
                ATLAS_Serial_HandleErrorMessage(LOG_WARNING, "ATLAS_Native_Serial_Handlers -- Error writing command, wrong # bytes\n", errno);
                iReturn = FAILURE;
            }
        }
        else
        {
#ifdef DEBUG_NATIVE_SERIAL    
            printf("ATLAS_Native_Generic_Serial -- Do not need to do write.\n");
            printf("Write Buffer set to NULL\n");
#endif
        }
        
        if (pcReadBuffer != NULL)
        {
            // Clear out temporary read buffer and caller's read buffer
            memset(csTempReadBuffer, 0, MAXLENGTH);  	 // This is our buffer
            memset(pcReadBuffer, 	 0, iReadBuffLength);// This is the caller's buffer

            // Calculate our timeout structure based on ms passed in
            
            // If less than 1000ms = 1sec
            if (iWaitTime < 1000) 		
            {
                stTimeout.tv_sec = 0;
                stTimeout.tv_usec = iWaitTime * 1000; // Can hold up to 1,000,000 useconds, which is 1sec
            }
            else
            {
                // Lets round to the second level above 1000msec
                stTimeout.tv_sec = iWaitTime / 1000;
                stTimeout.tv_usec = 0;
            }
            
            // Now set up our list of file descriptors upon which to wait.    
            if (iPortID != 99)
            {
                // Check if there is any data on the input line
                FD_ZERO(&fdSet); /* clear the set */
                FD_SET(G_iSerialPortDescriptor[iPortID], &fdSet); /* add our file descriptor to the set */
                iSelectCheck = select(G_iSerialPortDescriptor[iPortID] + 1, &fdSet, NULL, NULL, &stTimeout);
            }
            else
            {
                // For testing, just move on
                iSelectCheck = 1;
            }

            // Check if the select worked
            if (iSelectCheck > 0)
            {                                                        
                // Read characters if ready to read
                iNumCharsRead = read (G_iSerialPortDescriptor[iPortID], csTempReadBuffer, sizeof(csTempReadBuffer));
#ifdef DEBUG_NATIVE_SERIAL
            
                printf("ATLAS_Native_Serial_Handlers - Read Back[%i]: <%s> into csTempReadBuffer (size:%d)\n", 
                        iNumCharsRead, csTempReadBuffer, sizeof(csTempReadBuffer));

                int iIndex;
                for (iIndex = 0; iIndex < iNumCharsRead; iIndex++)
                {
                    printf("%x:", (unsigned char)csTempReadBuffer[iIndex]);
                }
#endif
                if (iNumCharsRead > 0)
                {
                    // Set the caller's number of bytes read to number read
                    *piNumBytesRead = iNumCharsRead;

                    // Determine if the readback was bigger than the user's buffer
                    if (iNumCharsRead > iReadBuffLength)
                    {
                        ATLAS_Serial_HandleErrorMessage(LOG_WARNING, 
                        "ATLAS_Native_Serial_Handlers -- WARNING: Read back more bytes than users supplied %d size buffer!\n",iReadBuffLength);
                        // Limit the memcpy below
                        iNumCharsRead = iReadBuffLength;

                    }

                    // Copy temp read buffer's value into caller's buffer, only what was read
                    memcpy(pcReadBuffer, csTempReadBuffer, iNumCharsRead);

                    // Wait a second time between commands, perhaps not necessary....
                    //vdb_wait_ms(&iWaitTime);
            
                    // Clear the buffer
                    tcflush(G_iSerialPortDescriptor[iPortID], TCIOFLUSH);
                }
                else
                {
                    // This is just a warning, could be that user unplugged device
                    ATLAS_Serial_HandleErrorMessage(LOG_WARNING, "ATLAS_Native_Serial_Handlers -- Error: 0 or Negative # of bytes read\n", errno);
                    iReturn = FAILURE;
                }
            }
            else if (0 == iSelectCheck)
            {
                // This is just a warning, user could have unplugged the device
                syslog(LOG_WARNING, "ERROR - Timeout occured on Read from Command %s\n", pcWriteBuffer);
                iReturn = FAILURE;
            }
            else
            {
                // This is an ERROR, that should not happen
                syslog(LOG_ERR, "Error on Select for Read! ");
                iReturn = FAILURE;
            }  
        }
        else
        {
            // Flush the buffer in case there was a reply from the write we don't want
            //tcflush(G_iSerialPortDescriptor[iPortID], TCIOFLUSH); // clear buffer


#ifdef DEBUG_NATIVE_SERIAL
            printf("ATLAS_Native_Generic_Serial -- Read Buffer set to NULL, "
                    "Do not need to do read.\n");
#endif
        }
    }
    else
    {
        // The file desciptor in the global array was zero!
        syslog(LOG_WARNING, "WARNING - Native Serial handler called with a closed port!  Returning...\n");
        iReturn = LOCAL_VSYSERROR;
    }           

                //vdb_wait_ms(&iWaitTime);
#ifdef DEBUG_NATIVE_SERIAL
    gettimeofday(&tv, NULL);
    dElapsed = (tv.tv_sec - start_tv.tv_sec) +
               (tv.tv_usec - start_tv.tv_usec) / 1000000.0;

    printf("\t%f seconds for command %s\n", dElapsed, pcWriteBuffer);
#endif

    return (iReturn);   
}

//******************************************************************************
//      Function Name:      ATLAS_Native_Generic_Serial
//
//      Description:        A generic interface to the Hytec Serial module.
//      
//                          HParams Index:
//                              0:  PortID
//                              1:  BaudRate
//                              2:  Parity
//                              3:  BlockFlag
//                              4:  Ignore Newlines
//
//      Notes(s):   This function utilizes file locking to control access
//                  to the ports.  This means that this function
//                  must not 'return' without first releasing contro, even if
//                  there was an error.
//                  The variable iReturn is used to store the progress
//                  of the function, and this function must never
//                  return other than the last line.
//******************************************************************************
int ATLAS_Native_Generic_Serial(char *pcReadBuffer,
                                char *pcWriteBuffer,
                                int *piHparams,
                                int iReadBuffLength,
                                int iWriteBuffLength,
                                int iWaitTime,
                                int *piNumBytesRead)
{
    int iReturn = SUCCESS;
    int iLocalLogOptions = G_iSyslogOptions;
    
    // First, make sure the hparams is not a null pointer
    if (NULL == piHparams)
    {
        printf("ATLAS_Native_Generic_Serial -- Handler called with a null pointer....\n");
        return FAILURE;
    }
        
    // Check if read and write buffer lengths are greater than max length
    if ( (iReadBuffLength  > MAXLENGTH) || (iWriteBuffLength > MAXLENGTH) )
    {
        printf("ATLAS_Native_Generic_Serial -- Buffer lengths past max length....\n");
        return FAILURE;
    }
    
    // Open a syslog instance once we have passed all the programming checks
    openlog("ATLAS_Native_Generic_Serial", iLocalLogOptions, G_iSyslogFacility);
   
    // Wait in line to lock the port
#ifdef MULTITHREADED
    iReturn = ATLAS_Native_ReserveOpen_Port (piHparams, 0); // Default priority for now
#else
    iReturn = ATLAS_Native_ReserveOpen_Port (piHparams);
#endif
    if (iReturn)
    {                
        // now send the command
        iReturn = ATLAS_Native_SendCommand (pcReadBuffer, pcWriteBuffer, piHparams, 
                                             iReadBuffLength, iWriteBuffLength, 
                                             iWaitTime, piNumBytesRead);

        // If sucessful in locking, then unlock and close the port based on iReturn
        ATLAS_Native_CloseRelease_Port (piHparams, iReturn);
    }

    return iReturn;
}

