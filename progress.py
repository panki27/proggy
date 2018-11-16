#!/usr/bin/env python3
""" Displays progress of various operations. """

def get_terminal_size():
    """ return size of terminal as rows, columns  """
    import os
    import platform
    currentOS = platform.system()
    if currentOS == 'Windows':
        # shoutout to stackoverflow <3
        from ctypes import windll, create_string_buffer
        import struct
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom,
             maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            columns = right - left + 1
            rows = bottom - top + 1
            return rows, columns
    else:
        # and it's that simple on linux...
        return os.popen('stty size', 'r').read().split()

def print_progress(position, target, clear=False):
    """ 
    Print a bar the width of the terminal, filled according to position/target
    Args:
      position (int):
        The current "step" your process is at, i.e. bytes copied
      target (int):
        The goal your process is trying to reach, i.e. total amount of bytes
    """
    # [=====    30       ]
    import math
    import platform
    rows, columns = get_terminal_size()
    
    currentOS = platform.system()
    # account for [] at the edges
    if currentOS == 'Windows':
        maximumBarLength = int(columns) - 3 # and 1 more because FUCKING WINDOWS
    else:
        maximumBarLength = int(columns) - 2
    
    percentage = ( position / target )*100
    # calculate how many percents of progress mean 1 bar is printed
    stepPercentage = ( 100 / maximumBarLength )
    numBars = math.floor( percentage / stepPercentage )
    # create string filled with '====' at the beginning and '    ' at the back
    barstring = ''.join('=' for i in range( numBars )) + ''.join(' ' for i in range( maximumBarLength - numBars ))
    
    half = round(maximumBarLength/2)
    digitValue = ' {:3.2f}% '.format( round( percentage, 4 )).zfill( 5 )

    # no jiggly positioning
    if len( digitValue ) % 2 == 0:
        digitOffsetStart = round( len( digitValue ) /2 )
    else:
        digitOffsetStart = math.floor( len( digitValue ) /2 ) + 1
    digitOffsetEnd = math.floor( len( digitValue ) /2 )

    # replace the middle with percentage
    barstring = '{}{}{}'.format(barstring[:half-digitOffsetStart], digitValue, barstring[half+digitOffsetEnd:])
    print( '[' + barstring + ']', end='\r' )
    if( position == target ):
        # make sure we print a newline when 100% is reached
        #if not clear:
        print('\n')

def print_progress_percent(percentage):
    """ Wrapper to print just a percentage value """
    print_progress( percentage, 100 )

def get_file_size(filepath):
    """ Takes a path to a file and returns its size in bytes"""
    import os
    return os.stat( filepath ).st_size

def get_folder_size(folderPath):
    """ Returns the size of files in a folder including any subdirectories """
    import os
    size = 0
    for file in os.listdir( folderPath ):
        if os.path.isfile( folderPath + file ):
            size += get_file_size( os.path.join( folderPath, file ))
        else:
            size += get_folder_size( os.path.join( folderPath, file, '' ))
    return size

def copy_file_with_progress(src, dst, length=16*1024):
    """ Copies a single file from src to dst (paths) and prints the progress"""
    copied = 0
    totalsize = get_file_size(src)
    with open(src, 'rb') as fsrc:
      with open(dst, 'wb') as fdst:
        while True:
            buf = fsrc.read(length)
            if not buf:
                break
            fdst.write(buf)
            copied += len(buf)
            print_progress(copied, totalsize)

def copy_folder_with_progress(srcFolder, destFolder):
    """ Copy a folder with all its subdirectories and files and show the progress """
    #TODO: count bytez instead of files
    import os
    import shutil
    copied = 0
    files = os.listdir( srcFolder )
    total = get_folder_size( srcFolder )
    for file in files:
        if os.path.isfile( os.path.join( srcFolder, file )):
            copied += get_file_size( os.path.join( srcFolder, file ))
            shutil.copy(os.path.join( srcFolder, file ), os.path.join( destFolder, file ))
        else:
            copied += get_folder_size( os.path.join( srcFolder, file, '' ))
            shutil.copytree( os.path.join( srcFolder, file, '', os.path.join( destFolder, file, '')))
        print_progress( copied, total )

def main():
    helpStr = """Usage: progress [ percentage | { position target } | --demo ]"""
    # TODO: If no arguments are given, read std in.
    import sys
    argLen = len(sys.argv)
    #sys.exit(0)
    if argLen == 2:
        print_progress_percent(int(sys.argv[1]))
    elif argLen == 3:
        print_progress(int(sys.argv[1]), int(sys.argv[2]))
      #elif argLen == 4:
      #  print_progress(int(sys.argv[2]), int(sys.argv[3]))
    else:
      print(helpStr)
if __name__ == '__main__':
    import sys
    if sys.argv[1] == '--demo':
        print('Copying file...')
        for i in range(1, 500):
            print_progress(i, 499)
    else:
        main()