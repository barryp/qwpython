# Microsoft Developer Studio Project File - Name="qwsv" - Package Owner=<4>
# Microsoft Developer Studio Generated Build File, Format Version 6.00
# ** DO NOT EDIT **

# TARGTYPE "Win32 (x86) Dynamic-Link Library" 0x0102

CFG=qwsv - Win32 Release
!MESSAGE This is not a valid makefile. To build this project using NMAKE,
!MESSAGE use the Export Makefile command and run
!MESSAGE 
!MESSAGE NMAKE /f "qwsv.mak".
!MESSAGE 
!MESSAGE You can specify a configuration when running NMAKE
!MESSAGE by defining the macro CFG on the command line. For example:
!MESSAGE 
!MESSAGE NMAKE /f "qwsv.mak" CFG="qwsv - Win32 Release"
!MESSAGE 
!MESSAGE Possible choices for configuration are:
!MESSAGE 
!MESSAGE "qwsv - Win32 Release" (based on "Win32 (x86) Dynamic-Link Library")
!MESSAGE "qwsv - Win32 Debug" (based on "Win32 (x86) Dynamic-Link Library")
!MESSAGE 

# Begin Project
# PROP AllowPerConfigDependencies 0
# PROP Scc_ProjName ""
# PROP Scc_LocalPath ""
CPP=cl.exe
MTL=midl.exe
RSC=rc.exe

!IF  "$(CFG)" == "qwsv - Win32 Release"

# PROP BASE Use_MFC 0
# PROP BASE Use_Debug_Libraries 0
# PROP BASE Output_Dir "Release"
# PROP BASE Intermediate_Dir "Release"
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 0
# PROP Output_Dir "Release"
# PROP Intermediate_Dir "Release"
# PROP Ignore_Export_Lib 1
# PROP Target_Dir ""
# ADD BASE CPP /nologo /W3 /GX /O2 /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_MBCS" /D "_USRDLL" /D "DLL_EXPORTS" /YX /FD /c
# ADD CPP /nologo /MD /W3 /GX /O2 /I "g:\python20\include" /I ".." /D "NDEBUG" /D "_USRDLL" /D "SERVERONLY" /D "WIN32" /D "_WINDOWS" /D "_MBCS" /FR /YX /FD /c
# ADD BASE MTL /nologo /D "NDEBUG" /mktyplib203 /win32
# ADD MTL /nologo /D "NDEBUG" /mktyplib203 /win32
# ADD BASE RSC /l 0x409 /d "NDEBUG"
# ADD RSC /l 0x409 /d "NDEBUG"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LINK32=link.exe
# ADD BASE LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib /nologo /dll /machine:I386
# ADD LINK32 wsock32.lib kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib winmm.lib /nologo /dll /machine:I386 /out:"..\..\..\qwpython\qwsv.pyd" /libpath:"g:\python20\libs" /export:initqwsv
# SUBTRACT LINK32 /pdb:none

!ELSEIF  "$(CFG)" == "qwsv - Win32 Debug"

# PROP BASE Use_MFC 0
# PROP BASE Use_Debug_Libraries 1
# PROP BASE Output_Dir "Debug"
# PROP BASE Intermediate_Dir "Debug"
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 1
# PROP Output_Dir "Debug"
# PROP Intermediate_Dir "Debug"
# PROP Ignore_Export_Lib 1
# PROP Target_Dir ""
# ADD BASE CPP /nologo /MTd /W3 /Gm /GX /ZI /Od /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "_MBCS" /D "_USRDLL" /D "DLL_EXPORTS" /YX /FD /GZ /c
# ADD CPP /nologo /MT /W3 /Gm /GX /ZI /Od /I "g:\python20\include" /I ".." /D "_DEBUG" /D "DLL_EXPORTS" /D "_USRDLL" /D "SERVERONLY" /D "WIN32" /D "_WINDOWS" /D "_MBCS" /FR /YX /FD /GZ /c
# ADD BASE MTL /nologo /D "_DEBUG" /mktyplib203 /win32
# ADD MTL /nologo /D "_DEBUG" /mktyplib203 /win32
# ADD BASE RSC /l 0x409 /d "_DEBUG"
# ADD RSC /l 0x409 /d "_DEBUG"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LINK32=link.exe
# ADD BASE LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib /nologo /dll /debug /machine:I386 /pdbtype:sept
# ADD LINK32 winmm.lib wsock32.lib kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib /nologo /dll /debug /machine:I386 /out:"..\..\..\qwpython\qwsv_d.pyd" /pdbtype:sept /libpath:"g:\python-2.0\PCBuild" /export:initqwsv
# SUBTRACT LINK32 /pdb:none /incremental:no

!ENDIF 

# Begin Target

# Name "qwsv - Win32 Release"
# Name "qwsv - Win32 Debug"
# Begin Group "Source Files"

# PROP Default_Filter "cpp;c;cxx;rc;def;r;odl;hpj;bat;for;f90"
# Begin Source File

SOURCE=..\cmd.c
# End Source File
# Begin Source File

SOURCE=..\common.c
# End Source File
# Begin Source File

SOURCE=..\crc.c
# End Source File
# Begin Source File

SOURCE=..\cvar.c
# End Source File
# Begin Source File

SOURCE=..\mathlib.c
# End Source File
# Begin Source File

SOURCE=..\md4.c
# End Source File
# Begin Source File

SOURCE=..\model.c
# End Source File
# Begin Source File

SOURCE=..\net_chan.c
# End Source File
# Begin Source File

SOURCE=..\net_wins.c
# End Source File
# Begin Source File

SOURCE=..\pmove.c
# End Source File
# Begin Source File

SOURCE=..\pmovetst.c
# End Source File
# Begin Source File

SOURCE=..\pr_edict.c
# End Source File
# Begin Source File

SOURCE=..\qwp_entity.c
# End Source File
# Begin Source File

SOURCE=..\qwp_vector.c
# End Source File
# Begin Source File

SOURCE=..\sv_ccmds.c
# End Source File
# Begin Source File

SOURCE=..\sv_ents.c
# End Source File
# Begin Source File

SOURCE=..\sv_init.c
# End Source File
# Begin Source File

SOURCE=..\sv_main.c
# End Source File
# Begin Source File

SOURCE=..\sv_move.c
# End Source File
# Begin Source File

SOURCE=..\sv_nchan.c
# End Source File
# Begin Source File

SOURCE=..\sv_phys.c
# End Source File
# Begin Source File

SOURCE=..\sv_send.c
# End Source File
# Begin Source File

SOURCE=..\sv_user.c
# End Source File
# Begin Source File

SOURCE=..\sys_python.c
# End Source File
# Begin Source File

SOURCE=..\world.c
# End Source File
# Begin Source File

SOURCE=..\zone.c
# End Source File
# End Group
# Begin Group "Header Files"

# PROP Default_Filter "h;hpp;hxx;hm;inl;fi;fd"
# Begin Source File

SOURCE=..\bothdefs.h
# End Source File
# Begin Source File

SOURCE=..\bspfile.h
# End Source File
# Begin Source File

SOURCE=..\cmd.h
# End Source File
# Begin Source File

SOURCE=..\common.h
# End Source File
# Begin Source File

SOURCE=..\crc.h
# End Source File
# Begin Source File

SOURCE=..\cvar.h
# End Source File
# Begin Source File

SOURCE=..\mathlib.h
# End Source File
# Begin Source File

SOURCE=..\model.h
# End Source File
# Begin Source File

SOURCE=..\modelgen.h
# End Source File
# Begin Source File

SOURCE=..\net.h
# End Source File
# Begin Source File

SOURCE=..\pmove.h
# End Source File
# Begin Source File

SOURCE=..\progdefs.h
# End Source File
# Begin Source File

SOURCE=..\progs.h
# End Source File
# Begin Source File

SOURCE=..\protocol.h
# End Source File
# Begin Source File

SOURCE=..\quakedef.h
# End Source File
# Begin Source File

SOURCE=..\qwpython.h
# End Source File
# Begin Source File

SOURCE=..\qwsvdef.h
# End Source File
# Begin Source File

SOURCE=..\server.h
# End Source File
# Begin Source File

SOURCE=..\sys.h
# End Source File
# Begin Source File

SOURCE=..\world.h
# End Source File
# Begin Source File

SOURCE=..\zone.h
# End Source File
# End Group
# Begin Group "Resource Files"

# PROP Default_Filter "ico;cur;bmp;dlg;rc2;rct;bin;cnt;rtf;gif;jpg;jpeg;jpe"
# End Group
# End Target
# End Project
