'''
Created on Jul 11, 2012

@author: Jamesan

Functions that are broadly used in Python programs but don't have a specific category
'''
import atexit
import logging
import os
import sys
import time


logging_setup = False

def RunWithProfiler(functionStr, outputpath=None):
    import cProfile
    import pstats
    import sys

    if outputpath is None:
        outputpath = "C:\\Temp"

    ProfilePath = os.path.join(outputpath, 'BuildProfile.pr')

    ProfileDir = os.path.dirname(ProfilePath)
    if not os.path.exists(ProfileDir):
        os.makedirs(ProfileDir)

    logger = logging.getLogger(__name__ + '.RunWithProfiler')


    logger.info("Profiling: " + functionStr)

    try:
        cProfile.run(functionStr, ProfilePath)
    finally:
        if not os.path.exists(ProfilePath):
            logger.error("No profile file found" + ProfilePath)
            sys.exit()

        pr = pstats.Stats(ProfilePath)
        if not pr is None:
            pr.sort_stats('time')
            print(str(pr.print_stats(.1)))
            logger.info(str(pr.print_stats(0.1)))

    pr.print_callers(.1)

def SetupLogging(OutputPath=None, Level=None):
    
    global logging_setup
    if(logging_setup):
        return 
    
    logging_setup = True

    if(Level is None):
        Level = logging.INFO

    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')

    if not OutputPath is None:
        OutputPath = "C:\\Temp"

        LogPath = os.path.join(OutputPath, 'Logs')

        if not os.path.exists(LogPath):
            os.makedirs(LogPath)

        logFileName = time.strftime('log-%M.%d.%y_%H.%M.txt', time.localtime())
        logFileName = os.path.join(LogPath, logFileName)
        errlogFileName = time.strftime('log-%M.%d.%y_%H.%M-Errors.txt', time.localtime())
        errlogFileName = os.path.join(LogPath, errlogFileName)

        logging.basicConfig(filename=logFileName, level=Level, format='%(levelname)s - %(name)s - %(message)s')

        eh = logging.FileHandler(errlogFileName)
        eh.setLevel(logging.ERROR)
        eh.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(eh)
    else:
        logging.basicConfig(level=Level, format='%(levelname)s - %(name)s - %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(Level)
    ch.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(ch)

    # Automatically shutdown logging when our process ends
    atexit.register(logging.shutdown)


def lowpriority():
    """ Set the priority of the process to below-normal.
        Copied from: http://stackoverflow.com/questions/1023038/change-process-priority-in-python-cross-platform"""

    try:
        sys.getwindowsversion()
    except:
        isWindows = False
    else:
        isWindows = True

    try:
        if isWindows:
            # Based on:
            #   "Recipe 496767: Set Process Priority In Windows" on ActiveState
            #   http://code.activestate.com/recipes/496767/
            import win32api, win32process, win32con
            pid = os.getpid()
            handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
            win32process.SetPriorityClass(handle, win32process.BELOW_NORMAL_PRIORITY_CLASS)
            win32api.CloseHandle(handle)
        else:
            # Unix and Mac should have a nice function
            os.nice(1)
    except:
        logger = logging.getLogger(__name__ + '.lowpriority')
        if not logger is None:
            logger.warn("Could not lower process priority")
            if isWindows:
                logger.warn("Are you missing Win32 extensions for python? http://sourceforge.net/projects/pywin32/")
        pass


def enum(*sequential, **named):
    '''Generates a dictionary of names to number values used as an enumeration'''
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


def ArgumentsFromDict(dictObj):
    '''Generates an argument string for a command line program from a dictionary
    Takes a dictionary and returns a string with '-' prepended to the entry name, a space, and the entry string verbatim'''

    outstr = " "

    for entry in dictObj.iteritems():
        assert(isinstance(entry[0], str))
        outstr = outstr + " -" + entry[0] + " " + str(entry[1]) + " "

    return outstr

def GenNameFromDict(dictObj):
    '''Creates a mangled name unique to the contents of a dictionary.
       Take the first three letters from each entry name, append the value, and build a mangled name'''
    outstr = ""
    
    sorted_keys = sorted(dictObj.keys())

    for key in sorted_keys:
        value = dictObj[key]
        assert(isinstance(key, str))
        nameMangle = key
        if(len(nameMangle) > 3):
            nameMangle = nameMangle[0:3]

        ValueStr = ""
        if value is None:
            ValueStr = "None"
        elif(isinstance(value, list)):
            ValueStr = str(value[0])
            for e in value[1:-1]:
                ValueStr = 'x' + str(e)
        else:
            ValueStr = str(value)

        outstr = outstr + "_" + nameMangle + ValueStr

    return outstr

def ListFromDelimited(value, delimiter=None):
    if delimiter is None:
        delimiter = ','

    ValueList = value
    if isinstance(value, str):
        ValueList = []
        Values = str(value).strip().split(delimiter)
        ValueList = list()
        for Value in  Values:
            try:
                floatVal = float(Value)
                try:
                    intVal = int(Value)
                    ValueList.append(intVal)
                except:
                    ValueList.append(floatVal)
            except:
                if len(Value) > 0:
                    ValueList.append(Value)
                    
    elif not isinstance(value, list):
        ValueList = [value]

    return ValueList

def SortedListFromDelimited(value, delimiter=None):
    ValueList = ListFromDelimited(value, delimiter)
    ValueList.sort()
    return ValueList

def ListFromAttribute(attrib):
    return ListFromDelimited(attrib, delimiter=',')

def IsSequence(arg):
    '''Return true if arg is iterable and not a string'''
    return (not hasattr(arg, "strip") and
            hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__"))


if __name__ == '__main__':
    pass
