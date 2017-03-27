/**
 * STM32 specific code
 **/

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <time.h>
#include <signal.h>
#include <stdlib.h>


//	#include <native/task.h>
//	#include <native/timer.h>
//	#include <native/mutex.h>
//	#include <native/sem.h>
//	#include <native/pipe.h>

unsigned int PLC_state = 0;
#define PLC_STATE_TASK_CREATED                 1
#define PLC_STATE_DEBUG_FILE_OPENED            2 
#define PLC_STATE_DEBUG_PIPE_CREATED           4 
#define PLC_STATE_PYTHON_FILE_OPENED           8 
#define PLC_STATE_PYTHON_PIPE_CREATED          16   
#define PLC_STATE_WAITDEBUG_FILE_OPENED        32   
#define PLC_STATE_WAITDEBUG_PIPE_CREATED       64
#define PLC_STATE_WAITPYTHON_FILE_OPENED       128
#define PLC_STATE_WAITPYTHON_PIPE_CREATED      256

#define WAITDEBUG_PIPE_DEVICE        "/dev/rtp0"
#define WAITDEBUG_PIPE_MINOR         0
#define DEBUG_PIPE_DEVICE            "/dev/rtp1"
#define DEBUG_PIPE_MINOR             1
#define WAITPYTHON_PIPE_DEVICE       "/dev/rtp2"
#define WAITPYTHON_PIPE_MINOR        2
#define PYTHON_PIPE_DEVICE           "/dev/rtp3"
#define PYTHON_PIPE_MINOR            3
#define PIPE_SIZE                    1 

/**********************************************************************************
*				externs
**********************************************************************************/
extern unsigned long long getRtosTime (void);
/* provided by POUS.C */
//extern unsigned long common_ticktime__;
extern void PLC_SetTimer(unsigned long long next, unsigned long long period);
extern void initPlcTask (void);
/**********************************************************************************
*				vars
**********************************************************************************/
int WaitDebug_pipe_fd;
int WaitPython_pipe_fd;
int Debug_pipe_fd;
int Python_pipe_fd;
const unsigned char ucMACAddress[ 6 ] = { 0x1E, 0x30, 0x6C, 0xA2, 0x45, 0x44 };
/**********************************************************************************
*				funs
**********************************************************************************/

long AtomicCompareExchange(long* atomicvar,long compared, long exchange)
{
    return __sync_val_compare_and_swap(atomicvar, compared, exchange);
}
long long AtomicCompareExchange64(long long* atomicvar, long long compared, long long exchange)
{
    //return __sync_val_compare_and_swap(atomicvar, compared, exchange);
    return 1;
}

void PLC_GetTime(IEC_TIME *CURRENT_TIME)
{
    unsigned long long current_time = getRtosTime();
	CURRENT_TIME->tv_sec = current_time / 1000;
	CURRENT_TIME->tv_nsec = current_time * 1000000;
}

extern int PLC_shutdown;


void PLC_task_proc (void)
{
	PLC_GetTime(&__CURRENT_TIME);
	__run();
}

static unsigned long __debug_tick;

int stopPLC()
{
	/* stop plc polling task */
	PLC_shutdown = 1;

	__cleanup();
	__debug_tick = -1;
	return 0;
}

//
void catch_signal(int sig)
{
    //stopPLC();
//  signal(SIGTERM, catch_signal);
    signal(SIGINT, catch_signal);
    printf("Got Signal %d\n",sig);
    exit(0);
}

#define max_val(a,b) ((a>b)?a:b)
int startPLC (void)
{
	
    PLC_SetTimer(common_ticktime__, common_ticktime__);
	//signal(SIGINT, catch_signal);

	//Ttick = 1;
	PLC_shutdown = 0;
//	
//	 /*** RT Pipes creation and opening ***/
//	 /* create Debug_pipe */
//	 if(rt_pipe_create(&Debug_pipe, "Debug_pipe", DEBUG_PIPE_MINOR, PIPE_SIZE)) 
//	     goto error;
	 PLC_state |= PLC_STATE_DEBUG_PIPE_CREATED;
//	
//	 /* open Debug_pipe*/
//	 if((Debug_pipe_fd = open(DEBUG_PIPE_DEVICE, O_RDWR)) == -1) goto error;
	 PLC_state |= PLC_STATE_DEBUG_FILE_OPENED;
//	
//	 /* create Python_pipe */
//	 if(rt_pipe_create(&Python_pipe, "Python_pipe", PYTHON_PIPE_MINOR, PIPE_SIZE)) 
//	     goto error;
	 PLC_state |= PLC_STATE_PYTHON_PIPE_CREATED;
//	
//	 /* open Python_pipe*/
//	 if((Python_pipe_fd = open(PYTHON_PIPE_DEVICE, O_RDWR)) == -1) goto error;
	 PLC_state |= PLC_STATE_PYTHON_FILE_OPENED;
//	
//	 /* create WaitDebug_pipe */
//	 if(rt_pipe_create(&WaitDebug_pipe, "WaitDebug_pipe", WAITDEBUG_PIPE_MINOR, PIPE_SIZE))
//	     goto error;
	 PLC_state |= PLC_STATE_WAITDEBUG_PIPE_CREATED;
//	
//	 /* open WaitDebug_pipe*/
//	 if((WaitDebug_pipe_fd = open(WAITDEBUG_PIPE_DEVICE, O_RDWR)) == -1) goto error;
	 PLC_state |= PLC_STATE_WAITDEBUG_FILE_OPENED;
//	
//	 /* create WaitPython_pipe */
//	 if(rt_pipe_create(&WaitPython_pipe, "WaitPython_pipe", WAITPYTHON_PIPE_MINOR, PIPE_SIZE))
//	     goto error;
	 PLC_state |= PLC_STATE_WAITPYTHON_PIPE_CREATED;
//	
//	 /* open WaitPython_pipe*/
//	 if((WaitPython_pipe_fd = open(WAITPYTHON_PIPE_DEVICE, O_RDWR)) == -1) goto error;
	 PLC_state |= PLC_STATE_WAITPYTHON_FILE_OPENED;
//	
	/*** create PLC task ***/
	initPlcTask();
	PLC_state |= PLC_STATE_TASK_CREATED;

	__init(0,(char**)NULL);
	return 0;
//error:

//	  return 1;
}

#define DEBUG_FREE 0
#define DEBUG_BUSY 1
static long debug_state = DEBUG_FREE;

int TryEnterDebugSection(void)
{
    return 0;
}

#define DEBUG_UNLOCK 1
void LeaveDebugSection(void)
{
//	 if(AtomicCompareExchange( &debug_state, 
//	     DEBUG_BUSY, DEBUG_FREE) == DEBUG_BUSY){
//	     char msg = DEBUG_UNLOCK;
//	     /* signal to NRT for wakeup */
//	     rt_pipe_write(&Debug_pipe, &msg, sizeof(msg), P_NORMAL);
//	 }
}

extern unsigned long __tick;

#define DEBUG_PENDING_DATA 1
int WaitDebugData(unsigned long *tick)
{
    char cmd;
    int res;
    if (PLC_shutdown) return -1;
    /* Wait signal from PLC thread */
    res = read(WaitDebug_pipe_fd, &cmd, sizeof(cmd));
    if (res == sizeof(cmd) && cmd == DEBUG_PENDING_DATA){
        *tick = __debug_tick;
        return 0;
    }
    return -1;
}

/* Called by PLC thread when debug_publish finished
 * This is supposed to unlock debugger thread in WaitDebugData*/
void InitiateDebugTransfer()
{
    char msg = DEBUG_PENDING_DATA;
    /* remember tick */
    __debug_tick = __tick;
    /* signal debugger thread it can read data */
    //rt_pipe_write(&WaitDebug_pipe, &msg, sizeof(msg), P_NORMAL);
}

int suspendDebug(int disable)
{
    char cmd = DEBUG_UNLOCK;
    if (PLC_shutdown) return -1;
    while(AtomicCompareExchange(
            &debug_state,
            DEBUG_FREE,
            DEBUG_BUSY) != DEBUG_FREE &&
            cmd == DEBUG_UNLOCK){
       if(read(Debug_pipe_fd, &cmd, sizeof(cmd)) != sizeof(cmd)){
           return -1;
       }
    }
    __DEBUG = !disable;
    if (disable)
        AtomicCompareExchange( &debug_state, DEBUG_BUSY, DEBUG_FREE);
    return 0;
}

void resumeDebug(void)
{
    AtomicCompareExchange( &debug_state, DEBUG_BUSY, DEBUG_FREE);
}

#define PYTHON_PENDING_COMMAND 1

#define PYTHON_FREE 0
#define PYTHON_BUSY 1
static long python_state = PYTHON_FREE;

int WaitPythonCommands(void)
{ 
    char cmd;
    if (PLC_shutdown) return -1;
    /* Wait signal from PLC thread */
    if(read(WaitPython_pipe_fd, &cmd, sizeof(cmd))==sizeof(cmd) && cmd==PYTHON_PENDING_COMMAND){
        return 0;
    }
    return -1;
}

/* Called by PLC thread on each new python command*/
void UnBlockPythonCommands(void)
{
    char msg = PYTHON_PENDING_COMMAND;
//    rt_pipe_write(&WaitPython_pipe, &msg, sizeof(msg), P_NORMAL);
}

int TryLockPython(void)
{
    return AtomicCompareExchange(
        &python_state,
        PYTHON_FREE,
        PYTHON_BUSY) == PYTHON_FREE;
}

#define UNLOCK_PYTHON 1
void LockPython(void)
{
    char cmd = UNLOCK_PYTHON;
    if (PLC_shutdown) return;
    while(AtomicCompareExchange(
            &python_state,
            PYTHON_FREE,
            PYTHON_BUSY) != PYTHON_FREE &&
            cmd == UNLOCK_PYTHON){
       read(Python_pipe_fd, &cmd, sizeof(cmd));
    }
}

void UnLockPython(void)
{
    if(AtomicCompareExchange(
            &python_state,
            PYTHON_BUSY,
            PYTHON_FREE) == PYTHON_BUSY){
//        if(rt_task_self()){/*is that the real time task ?*/
//           char cmd = UNLOCK_PYTHON;
//           rt_pipe_write(&Python_pipe, &cmd, sizeof(cmd), P_NORMAL);
//        }/* otherwise, no signaling from non real time */
    }    /* as plc does not wait for lock. */
}

