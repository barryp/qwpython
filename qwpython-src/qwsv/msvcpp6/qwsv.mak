# Microsoft Developer Studio Generated NMAKE File, Based on qwsv.dsp
!IF "$(CFG)" == ""
CFG=qwsv - Win32 Release
!MESSAGE No configuration specified. Defaulting to qwsv - Win32 Release.
!ENDIF 

!IF "$(CFG)" != "qwsv - Win32 Release" && "$(CFG)" != "qwsv - Win32 Debug"
!MESSAGE Invalid configuration "$(CFG)" specified.
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
!ERROR An invalid configuration is specified.
!ENDIF 

!IF "$(OS)" == "Windows_NT"
NULL=
!ELSE 
NULL=nul
!ENDIF 

CPP=cl.exe
MTL=midl.exe
RSC=rc.exe

!IF  "$(CFG)" == "qwsv - Win32 Release"

OUTDIR=.\Release
INTDIR=.\Release
# Begin Custom Macros
OutDir=.\Release
# End Custom Macros

ALL : "..\..\qwsv.pyd" "$(OUTDIR)\qwsv.bsc"


CLEAN :
	-@erase "$(INTDIR)\cmd.obj"
	-@erase "$(INTDIR)\cmd.sbr"
	-@erase "$(INTDIR)\common.obj"
	-@erase "$(INTDIR)\common.sbr"
	-@erase "$(INTDIR)\crc.obj"
	-@erase "$(INTDIR)\crc.sbr"
	-@erase "$(INTDIR)\cvar.obj"
	-@erase "$(INTDIR)\cvar.sbr"
	-@erase "$(INTDIR)\mathlib.obj"
	-@erase "$(INTDIR)\mathlib.sbr"
	-@erase "$(INTDIR)\md4.obj"
	-@erase "$(INTDIR)\md4.sbr"
	-@erase "$(INTDIR)\model.obj"
	-@erase "$(INTDIR)\model.sbr"
	-@erase "$(INTDIR)\net_chan.obj"
	-@erase "$(INTDIR)\net_chan.sbr"
	-@erase "$(INTDIR)\net_wins.obj"
	-@erase "$(INTDIR)\net_wins.sbr"
	-@erase "$(INTDIR)\pmove.obj"
	-@erase "$(INTDIR)\pmove.sbr"
	-@erase "$(INTDIR)\pmovetst.obj"
	-@erase "$(INTDIR)\pmovetst.sbr"
	-@erase "$(INTDIR)\pr_edict.obj"
	-@erase "$(INTDIR)\pr_edict.sbr"
	-@erase "$(INTDIR)\qwp_entity.obj"
	-@erase "$(INTDIR)\qwp_entity.sbr"
	-@erase "$(INTDIR)\qwp_vector.obj"
	-@erase "$(INTDIR)\qwp_vector.sbr"
	-@erase "$(INTDIR)\sv_ccmds.obj"
	-@erase "$(INTDIR)\sv_ccmds.sbr"
	-@erase "$(INTDIR)\sv_ents.obj"
	-@erase "$(INTDIR)\sv_ents.sbr"
	-@erase "$(INTDIR)\sv_init.obj"
	-@erase "$(INTDIR)\sv_init.sbr"
	-@erase "$(INTDIR)\sv_main.obj"
	-@erase "$(INTDIR)\sv_main.sbr"
	-@erase "$(INTDIR)\sv_move.obj"
	-@erase "$(INTDIR)\sv_move.sbr"
	-@erase "$(INTDIR)\sv_nchan.obj"
	-@erase "$(INTDIR)\sv_nchan.sbr"
	-@erase "$(INTDIR)\sv_phys.obj"
	-@erase "$(INTDIR)\sv_phys.sbr"
	-@erase "$(INTDIR)\sv_send.obj"
	-@erase "$(INTDIR)\sv_send.sbr"
	-@erase "$(INTDIR)\sv_user.obj"
	-@erase "$(INTDIR)\sv_user.sbr"
	-@erase "$(INTDIR)\sys_python.obj"
	-@erase "$(INTDIR)\sys_python.sbr"
	-@erase "$(INTDIR)\vc60.idb"
	-@erase "$(INTDIR)\world.obj"
	-@erase "$(INTDIR)\world.sbr"
	-@erase "$(INTDIR)\zone.obj"
	-@erase "$(INTDIR)\zone.sbr"
	-@erase "$(OUTDIR)\qwsv.bsc"
	-@erase "$(OUTDIR)\qwsv.exp"
	-@erase "..\..\qwsv.pyd"

"$(OUTDIR)" :
    if not exist "$(OUTDIR)/$(NULL)" mkdir "$(OUTDIR)"

CPP_PROJ=/nologo /MD /W3 /GX /O2 /I "g:\python20\include" /I ".." /D "NDEBUG" /D "_USRDLL" /D "SERVERONLY" /D "WIN32" /D "_WINDOWS" /D "_MBCS" /FR"$(INTDIR)\\" /Fp"$(INTDIR)\qwsv.pch" /YX /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 
MTL_PROJ=/nologo /D "NDEBUG" /mktyplib203 /win32 
BSC32=bscmake.exe
BSC32_FLAGS=/nologo /o"$(OUTDIR)\qwsv.bsc" 
BSC32_SBRS= \
	"$(INTDIR)\cmd.sbr" \
	"$(INTDIR)\common.sbr" \
	"$(INTDIR)\crc.sbr" \
	"$(INTDIR)\cvar.sbr" \
	"$(INTDIR)\mathlib.sbr" \
	"$(INTDIR)\md4.sbr" \
	"$(INTDIR)\model.sbr" \
	"$(INTDIR)\net_chan.sbr" \
	"$(INTDIR)\net_wins.sbr" \
	"$(INTDIR)\pmove.sbr" \
	"$(INTDIR)\pmovetst.sbr" \
	"$(INTDIR)\pr_edict.sbr" \
	"$(INTDIR)\qwp_entity.sbr" \
	"$(INTDIR)\qwp_vector.sbr" \
	"$(INTDIR)\sv_ccmds.sbr" \
	"$(INTDIR)\sv_ents.sbr" \
	"$(INTDIR)\sv_init.sbr" \
	"$(INTDIR)\sv_main.sbr" \
	"$(INTDIR)\sv_move.sbr" \
	"$(INTDIR)\sv_nchan.sbr" \
	"$(INTDIR)\sv_phys.sbr" \
	"$(INTDIR)\sv_send.sbr" \
	"$(INTDIR)\sv_user.sbr" \
	"$(INTDIR)\sys_python.sbr" \
	"$(INTDIR)\world.sbr" \
	"$(INTDIR)\zone.sbr"

"$(OUTDIR)\qwsv.bsc" : "$(OUTDIR)" $(BSC32_SBRS)
    $(BSC32) @<<
  $(BSC32_FLAGS) $(BSC32_SBRS)
<<

LINK32=link.exe
LINK32_FLAGS=wsock32.lib kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib winmm.lib /nologo /dll /incremental:no /pdb:"$(OUTDIR)\qwsv.pdb" /machine:I386 /out:"..\..\qwsv.pyd" /implib:"$(OUTDIR)\qwsv.lib" /libpath:"g:\python20\libs" /export:initqwsv 
LINK32_OBJS= \
	"$(INTDIR)\cmd.obj" \
	"$(INTDIR)\common.obj" \
	"$(INTDIR)\crc.obj" \
	"$(INTDIR)\cvar.obj" \
	"$(INTDIR)\mathlib.obj" \
	"$(INTDIR)\md4.obj" \
	"$(INTDIR)\model.obj" \
	"$(INTDIR)\net_chan.obj" \
	"$(INTDIR)\net_wins.obj" \
	"$(INTDIR)\pmove.obj" \
	"$(INTDIR)\pmovetst.obj" \
	"$(INTDIR)\pr_edict.obj" \
	"$(INTDIR)\qwp_entity.obj" \
	"$(INTDIR)\qwp_vector.obj" \
	"$(INTDIR)\sv_ccmds.obj" \
	"$(INTDIR)\sv_ents.obj" \
	"$(INTDIR)\sv_init.obj" \
	"$(INTDIR)\sv_main.obj" \
	"$(INTDIR)\sv_move.obj" \
	"$(INTDIR)\sv_nchan.obj" \
	"$(INTDIR)\sv_phys.obj" \
	"$(INTDIR)\sv_send.obj" \
	"$(INTDIR)\sv_user.obj" \
	"$(INTDIR)\sys_python.obj" \
	"$(INTDIR)\world.obj" \
	"$(INTDIR)\zone.obj"

"..\..\qwsv.pyd" : "$(OUTDIR)" $(DEF_FILE) $(LINK32_OBJS)
    $(LINK32) @<<
  $(LINK32_FLAGS) $(LINK32_OBJS)
<<

!ELSEIF  "$(CFG)" == "qwsv - Win32 Debug"

OUTDIR=.\Debug
INTDIR=.\Debug
# Begin Custom Macros
OutDir=.\Debug
# End Custom Macros

ALL : "..\..\qwsv_d.pyd" "$(OUTDIR)\qwsv.bsc"


CLEAN :
	-@erase "$(INTDIR)\cmd.obj"
	-@erase "$(INTDIR)\cmd.sbr"
	-@erase "$(INTDIR)\common.obj"
	-@erase "$(INTDIR)\common.sbr"
	-@erase "$(INTDIR)\crc.obj"
	-@erase "$(INTDIR)\crc.sbr"
	-@erase "$(INTDIR)\cvar.obj"
	-@erase "$(INTDIR)\cvar.sbr"
	-@erase "$(INTDIR)\mathlib.obj"
	-@erase "$(INTDIR)\mathlib.sbr"
	-@erase "$(INTDIR)\md4.obj"
	-@erase "$(INTDIR)\md4.sbr"
	-@erase "$(INTDIR)\model.obj"
	-@erase "$(INTDIR)\model.sbr"
	-@erase "$(INTDIR)\net_chan.obj"
	-@erase "$(INTDIR)\net_chan.sbr"
	-@erase "$(INTDIR)\net_wins.obj"
	-@erase "$(INTDIR)\net_wins.sbr"
	-@erase "$(INTDIR)\pmove.obj"
	-@erase "$(INTDIR)\pmove.sbr"
	-@erase "$(INTDIR)\pmovetst.obj"
	-@erase "$(INTDIR)\pmovetst.sbr"
	-@erase "$(INTDIR)\pr_edict.obj"
	-@erase "$(INTDIR)\pr_edict.sbr"
	-@erase "$(INTDIR)\qwp_entity.obj"
	-@erase "$(INTDIR)\qwp_entity.sbr"
	-@erase "$(INTDIR)\qwp_vector.obj"
	-@erase "$(INTDIR)\qwp_vector.sbr"
	-@erase "$(INTDIR)\sv_ccmds.obj"
	-@erase "$(INTDIR)\sv_ccmds.sbr"
	-@erase "$(INTDIR)\sv_ents.obj"
	-@erase "$(INTDIR)\sv_ents.sbr"
	-@erase "$(INTDIR)\sv_init.obj"
	-@erase "$(INTDIR)\sv_init.sbr"
	-@erase "$(INTDIR)\sv_main.obj"
	-@erase "$(INTDIR)\sv_main.sbr"
	-@erase "$(INTDIR)\sv_move.obj"
	-@erase "$(INTDIR)\sv_move.sbr"
	-@erase "$(INTDIR)\sv_nchan.obj"
	-@erase "$(INTDIR)\sv_nchan.sbr"
	-@erase "$(INTDIR)\sv_phys.obj"
	-@erase "$(INTDIR)\sv_phys.sbr"
	-@erase "$(INTDIR)\sv_send.obj"
	-@erase "$(INTDIR)\sv_send.sbr"
	-@erase "$(INTDIR)\sv_user.obj"
	-@erase "$(INTDIR)\sv_user.sbr"
	-@erase "$(INTDIR)\sys_python.obj"
	-@erase "$(INTDIR)\sys_python.sbr"
	-@erase "$(INTDIR)\vc60.idb"
	-@erase "$(INTDIR)\vc60.pdb"
	-@erase "$(INTDIR)\world.obj"
	-@erase "$(INTDIR)\world.sbr"
	-@erase "$(INTDIR)\zone.obj"
	-@erase "$(INTDIR)\zone.sbr"
	-@erase "$(OUTDIR)\qwsv.bsc"
	-@erase "$(OUTDIR)\qwsv_d.exp"
	-@erase "$(OUTDIR)\qwsv_d.pdb"
	-@erase "..\..\qwsv_d.ilk"
	-@erase "..\..\qwsv_d.pyd"

"$(OUTDIR)" :
    if not exist "$(OUTDIR)/$(NULL)" mkdir "$(OUTDIR)"

CPP_PROJ=/nologo /MT /W3 /Gm /GX /ZI /Od /I "g:\python20\include" /I ".." /D "_DEBUG" /D "DLL_EXPORTS" /D "_USRDLL" /D "SERVERONLY" /D "WIN32" /D "_WINDOWS" /D "_MBCS" /FR"$(INTDIR)\\" /Fp"$(INTDIR)\qwsv.pch" /YX /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /GZ /c 
MTL_PROJ=/nologo /D "_DEBUG" /mktyplib203 /win32 
BSC32=bscmake.exe
BSC32_FLAGS=/nologo /o"$(OUTDIR)\qwsv.bsc" 
BSC32_SBRS= \
	"$(INTDIR)\cmd.sbr" \
	"$(INTDIR)\common.sbr" \
	"$(INTDIR)\crc.sbr" \
	"$(INTDIR)\cvar.sbr" \
	"$(INTDIR)\mathlib.sbr" \
	"$(INTDIR)\md4.sbr" \
	"$(INTDIR)\model.sbr" \
	"$(INTDIR)\net_chan.sbr" \
	"$(INTDIR)\net_wins.sbr" \
	"$(INTDIR)\pmove.sbr" \
	"$(INTDIR)\pmovetst.sbr" \
	"$(INTDIR)\pr_edict.sbr" \
	"$(INTDIR)\qwp_entity.sbr" \
	"$(INTDIR)\qwp_vector.sbr" \
	"$(INTDIR)\sv_ccmds.sbr" \
	"$(INTDIR)\sv_ents.sbr" \
	"$(INTDIR)\sv_init.sbr" \
	"$(INTDIR)\sv_main.sbr" \
	"$(INTDIR)\sv_move.sbr" \
	"$(INTDIR)\sv_nchan.sbr" \
	"$(INTDIR)\sv_phys.sbr" \
	"$(INTDIR)\sv_send.sbr" \
	"$(INTDIR)\sv_user.sbr" \
	"$(INTDIR)\sys_python.sbr" \
	"$(INTDIR)\world.sbr" \
	"$(INTDIR)\zone.sbr"

"$(OUTDIR)\qwsv.bsc" : "$(OUTDIR)" $(BSC32_SBRS)
    $(BSC32) @<<
  $(BSC32_FLAGS) $(BSC32_SBRS)
<<

LINK32=link.exe
LINK32_FLAGS=winmm.lib wsock32.lib kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib /nologo /dll /incremental:yes /pdb:"$(OUTDIR)\qwsv_d.pdb" /debug /machine:I386 /out:"..\..\qwsv_d.pyd" /implib:"$(OUTDIR)\qwsv_d.lib" /pdbtype:sept /libpath:"g:\python-2.0\PCBuild" /export:initqwsv 
LINK32_OBJS= \
	"$(INTDIR)\cmd.obj" \
	"$(INTDIR)\common.obj" \
	"$(INTDIR)\crc.obj" \
	"$(INTDIR)\cvar.obj" \
	"$(INTDIR)\mathlib.obj" \
	"$(INTDIR)\md4.obj" \
	"$(INTDIR)\model.obj" \
	"$(INTDIR)\net_chan.obj" \
	"$(INTDIR)\net_wins.obj" \
	"$(INTDIR)\pmove.obj" \
	"$(INTDIR)\pmovetst.obj" \
	"$(INTDIR)\pr_edict.obj" \
	"$(INTDIR)\qwp_entity.obj" \
	"$(INTDIR)\qwp_vector.obj" \
	"$(INTDIR)\sv_ccmds.obj" \
	"$(INTDIR)\sv_ents.obj" \
	"$(INTDIR)\sv_init.obj" \
	"$(INTDIR)\sv_main.obj" \
	"$(INTDIR)\sv_move.obj" \
	"$(INTDIR)\sv_nchan.obj" \
	"$(INTDIR)\sv_phys.obj" \
	"$(INTDIR)\sv_send.obj" \
	"$(INTDIR)\sv_user.obj" \
	"$(INTDIR)\sys_python.obj" \
	"$(INTDIR)\world.obj" \
	"$(INTDIR)\zone.obj"

"..\..\qwsv_d.pyd" : "$(OUTDIR)" $(DEF_FILE) $(LINK32_OBJS)
    $(LINK32) @<<
  $(LINK32_FLAGS) $(LINK32_OBJS)
<<

!ENDIF 

.c{$(INTDIR)}.obj::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cpp{$(INTDIR)}.obj::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cxx{$(INTDIR)}.obj::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.c{$(INTDIR)}.sbr::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cpp{$(INTDIR)}.sbr::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cxx{$(INTDIR)}.sbr::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<


!IF "$(NO_EXTERNAL_DEPS)" != "1"
!IF EXISTS("qwsv.dep")
!INCLUDE "qwsv.dep"
!ELSE 
!MESSAGE Warning: cannot find "qwsv.dep"
!ENDIF 
!ENDIF 


!IF "$(CFG)" == "qwsv - Win32 Release" || "$(CFG)" == "qwsv - Win32 Debug"
SOURCE=..\cmd.c

"$(INTDIR)\cmd.obj"	"$(INTDIR)\cmd.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\common.c

"$(INTDIR)\common.obj"	"$(INTDIR)\common.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\crc.c

"$(INTDIR)\crc.obj"	"$(INTDIR)\crc.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\cvar.c

"$(INTDIR)\cvar.obj"	"$(INTDIR)\cvar.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\mathlib.c

"$(INTDIR)\mathlib.obj"	"$(INTDIR)\mathlib.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\md4.c

"$(INTDIR)\md4.obj"	"$(INTDIR)\md4.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\model.c

"$(INTDIR)\model.obj"	"$(INTDIR)\model.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\net_chan.c

"$(INTDIR)\net_chan.obj"	"$(INTDIR)\net_chan.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\net_wins.c

"$(INTDIR)\net_wins.obj"	"$(INTDIR)\net_wins.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\pmove.c

"$(INTDIR)\pmove.obj"	"$(INTDIR)\pmove.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\pmovetst.c

"$(INTDIR)\pmovetst.obj"	"$(INTDIR)\pmovetst.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\pr_edict.c

"$(INTDIR)\pr_edict.obj"	"$(INTDIR)\pr_edict.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\qwp_entity.c

"$(INTDIR)\qwp_entity.obj"	"$(INTDIR)\qwp_entity.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\qwp_vector.c

"$(INTDIR)\qwp_vector.obj"	"$(INTDIR)\qwp_vector.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\sv_ccmds.c

"$(INTDIR)\sv_ccmds.obj"	"$(INTDIR)\sv_ccmds.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\sv_ents.c

"$(INTDIR)\sv_ents.obj"	"$(INTDIR)\sv_ents.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\sv_init.c

"$(INTDIR)\sv_init.obj"	"$(INTDIR)\sv_init.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\sv_main.c

"$(INTDIR)\sv_main.obj"	"$(INTDIR)\sv_main.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\sv_move.c

"$(INTDIR)\sv_move.obj"	"$(INTDIR)\sv_move.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\sv_nchan.c

"$(INTDIR)\sv_nchan.obj"	"$(INTDIR)\sv_nchan.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\sv_phys.c

"$(INTDIR)\sv_phys.obj"	"$(INTDIR)\sv_phys.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\sv_send.c

"$(INTDIR)\sv_send.obj"	"$(INTDIR)\sv_send.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\sv_user.c

"$(INTDIR)\sv_user.obj"	"$(INTDIR)\sv_user.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\sys_python.c

"$(INTDIR)\sys_python.obj"	"$(INTDIR)\sys_python.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\world.c

"$(INTDIR)\world.obj"	"$(INTDIR)\world.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)


SOURCE=..\zone.c

"$(INTDIR)\zone.obj"	"$(INTDIR)\zone.sbr" : $(SOURCE) "$(INTDIR)"
	$(CPP) $(CPP_PROJ) $(SOURCE)



!ENDIF 

