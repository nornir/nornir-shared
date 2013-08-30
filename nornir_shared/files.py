'''
Created on Jul 11, 2012

@author: Jamesan
'''
import os
import prettyoutput;
import glob

DownsampleFormat = '%03d';
DefaultLevels = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024];


def NewestFile(fileA, fileB):
    '''Returns parameter which is the newest, or none if equal.'''
    if(fileA is None):
        return None;
    if(fileB is None):
        return None;

    if not os.path.exists(fileA):
        return None;
    if not os.path.exists(fileB):
        return None;

    AStats = os.stat(fileA);
    BStats = os.stat(fileB);

    if(AStats.st_mtime > BStats.st_mtime):
        return fileA;
    elif(AStats.st_mtime < BStats.st_mtime):
        return fileB;
    else:
        return None;

def OutdatedFile(ReferenceFilename, TestFilename):
    '''Return true if ReferenceFilename modified time is newer than the TestFilename'''
    return NewestFile(ReferenceFilename, TestFilename) == ReferenceFilename;

def RemoveOutdatedFile(ReferenceFilename, TestFilename):
    '''Takes a ReferenceFilename and TestFilename.  Removes TestFilename if it is newer than the reference'''
    if(OutdatedFile(ReferenceFilename, TestFilename)):
        try:
            PrettyOutput.Log('Removing outdated file: ' + TestFilename);
            os.remove(TestFilename);
            return True;
        except:
            PrettyOutput.Log('Exception removing outdated file: ' + TestFilename);
            pass;

 #   [name, ext] = os.path.splitext(TestFilename);
    return False;


def RecurseSubdirectories(Path,
                          RequiredFiles = None,
                          ExcludedFiles = None,
                          MatchNames = None,
                          ExcludeNames = None,
                          ExcludedDownsampleLevels = None):
    '''Recurse Subdirectories adds Path and every subdirectory to a list
       If MatchNames is not null we add the matching directory, but do not recurse subdirectories underneath
       If ExcludeNames  is not null we do not add the directory to the list and do not recurse subdirectories/
       if RequiredFiles is not null the directory must contain the required file before we add it.  No subdirectories are searched.
       if ExcludeFiles is not null and the directory contains the a matching file we do not add it or search subdirectories
       ExcludedDownsampleLevels and ExcludeNames must be an empty list to avoid population with default values.
       RequiredFiles and ExcludeFiles can be either a regular expression string or a list of specific filenames.
       Excluded files take priority over RequiredFiles
       '''

    if not os.path.exists(Path):
        PrettyOutput.LogErr("RecurseSubdirectories passed path parameter which does not exist: " + Path)

    if ExcludedDownsampleLevels is None:
        ExcludedDownsampleLevels = DefaultLevels;

    if ExcludeNames is None:
        ExcludeNames = ["clahe", "mbproj", "8-bit", "16-bit", "blob", "mosaic", "tem", "temp", "bruteresults", "gridresults", "results", "registered"];
    else:
        if ExcludeNames.__class__ != list:
            if not MatchNames is None:
                ExcludeNames = [MatchNames];
            else:
                ExcludeNames = [];

        for i in range(0, len(ExcludeNames)):
            ExcludeNames[i] = ExcludeNames[i].lower();

    for level in ExcludedDownsampleLevels:
        ExcludeNames.append(DownsampleFormat % level);

    if MatchNames is not None:
        if MatchNames.__class__ != list:
            MatchNames = [MatchNames];

        for i in range(0, len(MatchNames)):
            MatchNames[i] = MatchNames[i].lower();

    if(not RequiredFiles is None):
        if(RequiredFiles.__class__ != list):
            RequiredFiles = [RequiredFiles];

    Dirlist = list();

    # Exclude takes priority over included files
    if ExcludedFiles is not None:
        if(ExcludedFiles.__class__ != list):
            # If not a list then it should be a regular expression string
            files = glob.glob(os.path.join(Path, ExcludedFiles));
            if(len(files) > 0):
                # We found a match, do not add this directory to the list and search no further
                return Dirlist;
        else:
            for filename in ExcludedFiles:
                if os.path.exists(os.path.join(Path, filename)):
                    # We found a match, do not add this directory to the list and search no further
                    return Dirlist;

    if RequiredFiles is not None:
        for filename in RequiredFiles:
            if os.path.exists(os.path.join(Path, filename)):
                # We found a match, add this directory to the list but search no further
                Dirlist.append(Path);
                return Dirlist;
            elif '*' in filename or '?' in filename:
                files = glob.glob(os.path.join(Path, filename));
                if(len(files) > 0):
                    # We found a match, add this directory to the list but search no further
                    Dirlist.append(Path);
                    return Dirlist;

        # If we do not return it means the directory did not contain the required file, but we continue the search of subdirectories
    elif MatchNames is None:
        # Include directory if no required file specified
        Dirlist.append(Path);

    # If we made it this far we did not match either Required or Excluded Files

    # Recursively list the subdirectories, catch any exceptions.  This can occur if we don't have permissions
    dirs = [];
    try:
    #    PrettyOutput.Log( os.path.join(Path, '*[!png]');
        dirs = os.listdir(Path);
    except:
        prettyoutput.Log("RecurseSubdirectories could not enumerate " + str(Path));
        return [];

    for d in dirs:
        if os.path.isfile(d):
            continue;

        # Skip if it contains a .
        if d.find('.') > -1:
            continue;

        # Skip if it contains words from the exclude list
        name = os.path.basename(d);
        name = name.lower();

        if MatchNames is not None:
            if name in MatchNames:
                Dirlist.append(os.path.join(Path, d));
                continue;

        if (name in ExcludeNames):
            continue;

        # Add directory tree to list and keep looking
        fullpath = os.path.join(Path, d);
        if os.path.isdir(os.path.join(Path, d)):
            Dirlist = Dirlist + RecurseSubdirectories(fullpath,
                                                      RequiredFiles = RequiredFiles,
                                                      ExcludedFiles = ExcludedFiles,
                                                      MatchNames = MatchNames,
                                                      ExcludeNames = ExcludeNames,
                                                      ExcludedDownsampleLevels = ExcludedDownsampleLevels);
    return Dirlist;



def RemoveDirectorySpaces(Path):
    '''
    Remove spaces from the path and any immediate subdirectories under that path replacing spaces with '_'
    '''
    import shutil

    if os.path.exists(Path) == False:
        prettyoutput.Log("No valid path provided as first argument")
        return;

    Dirlist = list();
    Dirlist.append(Path);

    # Recursively list the subdirectories, catch any exceptions.  This can occur if we don't have permissions
    dirs = [];
    try:
    #    PrettyOutput.Log( os.path.join(Path, '*[!png]'))
        dirs = glob.glob(os.path.join(Path, '*'));
    except:
        prettyoutput.Log("RecurseSubdirectories could not enumerate " + Path)
        return [];

    for d in dirs:
        if os.path.isfile(d):
            continue;

        # Skip if it contains a .
        if d.find('.') > -1:
            continue;

        # Skip if it contains words from the exclude list
        name = os.path.basename(d);
        parentDir = os.path.dirname(d);
        nameNoSpaces = name.replace(' ', '_');
        if(name != nameNoSpaces):
            fullnameNoSpace = os.path.join(parentDir, nameNoSpaces);
            shutil.move(d, fullnameNoSpace);

def RemoveFilenameSpaces(Path, ext):
    '''Replaces spaces in filenames with _'''
    import shutil

    if os.path.exists(Path) == False:
        prettyoutput.Log("No valid path provided as first argument")
        return;

    if(ext[0] != '.'):
        ext = '.' + ext;

    globext = '*' + ext;

    prettyoutput.Log(os.path.join(Path, ext))

    # List all of the .mrc files in the path
    files = glob.glob(os.path.join(Path, globext));

    # We expect .mrc files to be named ####_string.mrc
    # #### is a section number
    # string is anything the users chooses to add

    prettyoutput.Log(files)
    for f in files:
        filename = os.path.basename(f);
        dirname = os.path.dirname(f);

        # Remove spaces if they are found
        filenameNoSpaces = filename.replace(' ', '_');
        filePathNoSpaces = os.path.join(dirname, filenameNoSpaces);
        shutil.move(f, filePathNoSpaces);

if __name__ == '__main__':
    pass