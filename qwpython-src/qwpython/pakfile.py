#!/usr/local/bin/python
"""Read Quake-style PAK files.  

   Barry Pederson <bpederson@geocities.com> 2000-11-05

(Interface is similar to the standard Python "zipfile" module)"""

import os, os.path, string, struct

class BadPakFile(Exception): pass

class PakInfo:
    """Instances of PakInfo are returned by the getinfo() and infolist()
       methods of PakFile objects.  Each object stores information about
       a single member of the Pak file.
       (Based on the standard Python ZipInfo class)"""
    def __init__(self, name, offset, size):
        self.filename = name
        self.file_offset = offset
        self.file_size = size

class PakFile:
    """Provides read-access to a Quake-style PAK file.  (Based on the 
       standard Python ZipFile class)"""
    def __init__(self, filename):
        f = open(filename, 'rb')
        try:
            header = struct.unpack('<iii', f.read(12))
        except:
            raise BadPakFile, 'Error reading PAK file header'
        if header[0] != 0x4b434150:
            raise BadPakFile, 'PAK file header has wrong signature'
        f.seek(header[1])
        if (header[2] % 64) != 0:
            raise BadPakFile, 'Corrupt PAK directory length, not a multiple of 64 bytes'

        namelist = []
        infodict = {}
        for i in range(header[2] / 64):
            info = struct.unpack('<56sii', f.read(64))
            name = info[0][:string.find(info[0], '\000')]
            pi = PakInfo(name, info[1], info[2])
            namelist.append(name)
            infodict[name] = pi

        # everything's groovy, save what we found
        self._file = f
        self._names = namelist    
        self._info = infodict

    def close(self):
        """Close the underlying file, the name and info lists are still available."""
        self._file.close()
        self._file = None

    def getinfo(self, name):
        """Fetch the PakInfo object for a given name"""
        return self._info[name]

    def has_key(self, name):
        """ Check if the pak file has the given name"""
        return self._info.has_key(name)

    def infolist(self):
        """Return a list of PakInfo objects, representing the contents of the PAK file."""
        result = []
        for n in self._names:
            result.append(self._info[n])
        return result

    def namelist(self):
        """Return a list of names of the members of the PAK file."""
        return self._names[:]

    def read(self, name):
        """Read the contents of a particular member of the PAK file."""
        pi = self._info[name]
        self._file.seek(pi.file_offset)
        return self._file.read(pi.file_size)

class ResourceDir:
    def __init__(self, dirname):
        self.dirname = [dirname]
    def _real_path(self, name):
        return apply(os.path.join, self.dirname + string.split(name, '/'))
    def has_key(self, name):
        return os.access(self._real_path(name), os.R_OK)        
    def read(self, name):
        return open(self._real_path(name), 'rb').read()            

class PakLoader:
    """Read from multiple PAK files"""
    def __init__(self):
        self._paklist = []

    def add_file(self, filename):        
        """ add a single PAK file to the list"""
        self._paklist.append(PakFile(filename))

    def add_directory(self, dirname):
        """ add all PAK files in a directory to the list"""
        self._paklist.append(ResourceDir(dirname))
        for f in os.listdir(dirname):
            if string.lower(f[-4:]) == '.pak':
                try:
                    self.add_file(os.path.join(dirname, f))
                except:
                    pass

    def has_key(self, name):
        """Check if any of the pak files has the given name"""
        for p in self._paklist:
            if p.has_key(name):
                return 1
        return 0

    def read(self, name):
        """Search the list of PAK files for a named resource, and read it
           Raises a KeyError if it can't find the named item"""
        for p in self._paklist:
            try:
                return p.read(name)
            except:
                pass
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