#!/usr/local/bin/python
"""
Library for reading Quake-style PAK files, and loading
resources from those files and regular directories

   Barry Pederson <bpederson@geocities.com> 2001-04-09

(Interface is similar to the standard Python "zipfile" module)
"""

import os, os.path, struct

class BadPakFile(Exception): 
    """
    Exception that will be raised from the constructor
    of instances of the PakFile class, if the specified
    file is not a valid PAK file.
    """
    pass


class PakInfo:
    """
    Hold information on a single member of a Pak file, is returned by 
    the getinfo() and infolist() methods of PakFile objects.  The
    properties held are:
    
        filename:       name of the item in the Pak file
        file_offset:    position within the Pak file
        file_size:      size of the item
        
    (Based on the standard Python ZipInfo class)
    """
    def __init__(self, name, offset, size):
        self.filename = name
        self.file_offset = offset
        self.file_size = size


class PakFile:
    """
    Provides read-access to a Quake-style PAK file.  
    (Based on the standard Python ZipFile class)
    
    """
    def __init__(self, filename):
        f = open(filename, 'rb')
        
        # 
        # Header is 3 little-endian 4-byte integers, a 
        # signature, an offset to the directory block, and
        # the size of the directory block (which should be a 
        # multiple of 64 bytes).
        #    
        try:
            header = struct.unpack('<iii', f.read(12))
        except:
            raise BadPakFile, 'Error reading PAK file header'
            
        if header[0] != 0x4b434150:
            raise BadPakFile, 'PAK file header has wrong signature'
            
        if (header[2] % 64) != 0:
            raise BadPakFile, 'Corrupt PAK directory length, not a multiple of 64 bytes'

        #
        # Each Pak directory entry is 64 bytes total.  A 56-byte 
        # null terminated string holding the name of the item, 4 bytes
        # indication the position of the item within the pak file, 
        # and 4 bytes indicating the length of the item.
        #
        f.seek(header[1])        
        infodict = {}
        for i in range(header[2] / 64):
            info = struct.unpack('<56sii', f.read(64))
            name = info[0].split('\000', 1)[0]
            infodict[name] = PakInfo(name, info[1], info[2])

        # everything's groovy, save what we found, let the file close itself
        self.__filename = filename
        self.__info = infodict


    def getinfo(self, name):
        """
        Fetch the PakInfo object for an item with the given name.
        """
        return self.__info[name]


    def has_key(self, name):
        """ 
        Check if the pak file has an item with the given name
        """
        return self.__info.has_key(name)


    def infolist(self):
        """
        Return a list of PakInfo objects, representing the contents of the PAK file.
        """
        return self.__info.values()


    def namelist(self):
        """
        Return a list of names of the members of the PAK file.
        """
        return self.__info.keys()


    def read(self, name):
        """
        Read the entire contents of a particular member of the PAK file, 
        returned as a string.
        """
        pi = self.__info[name]
        f = open(self.__filename, 'rb')
        f.seek(pi.file_offset)
        return f.read(pi.file_size)


class ResourceDir:
    """
    Gives a plain directory an interface similar to the PakFile class, for
    the convenience of the PakLoader class.  Hides files with names 
    ending in .pak, so the server won't attempt to load or download them    
    """
    def __init__(self, dirname):
        self.dirname = [dirname]
        
        
    def __real_path(self, name):
        return apply(os.path.join, self.dirname + name.split('/'))
        
        
    def has_key(self, name):
        """
        Check if the directory has an item with
        the given name.  
        """
        if name.lower().endswith('.pak'):
            return 0
            
        return os.access(self.__real_path(name), os.R_OK)        

        
    def read(self, name):
        """ 
        Read the entire contents of a file with the given name.
        """
        return open(self.__real_path(name), 'rb').read()            


class PakLoader:
    """
    Read from multiple PAK files and directories.  The search order
    is: last added == first searched
    """
    def __init__(self):
        self._paklist = []


    def add_file(self, filename):        
        """ 
        Add a single PAK file to the list. Last added
        will be first searched.
        """
        self._paklist.insert(0, PakFile(filename))


    def add_directory(self, dirname):
        """ 
        add all PAK files in a directory to the list, and then
        add the directory itself.  The directory will end up
        being searched, then the contents of the pak files
        (in alphabetical order).
        """
        files = os.listdir(dirname)
        files.sort()
        for f in files:
            if f.lower().endswith('.pak'):
                try:
                    self.add_file(os.path.join(dirname, f))
                except:
                    pass
        self._paklist.insert(0, ResourceDir(dirname))


    def has_key(self, name):
        """
        Check if any of the pak files or directories has the given name
        """
        for p in self._paklist:
            if p.has_key(name):
                return 1
        return 0


    def read(self, name):
        """
        Search the list of PAK files and directories for a named 
        resource, and read it. Raises a KeyError if it can't find 
        the named item.
        """
        for p in self._paklist:
            if p.has_key(name):
                return p.read(name)
                
        raise KeyError, '%s not found' % (name)
        

#
# Test code, run while in the quake/quakeworld directory
#
if __name__ == '__main__':
    loader = PakLoader()
    loader.add_directory('id1')
    sound1 = loader.read('sound/player/axhit1.wav')  #should come from pak0.pak 
    sound2 = loader.read('sound/boss2/pop2.wav')     #should come from pak1.pak 
    if loader.has_key('maps/dm1.bsp'):
        print 'seems ok'
    else:
        print 'doesn\'t have expected map'