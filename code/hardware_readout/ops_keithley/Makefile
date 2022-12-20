
#ANY LINKED LIBRARIES MUST BE INCLUDED in VSYSTEM.RC FILE"

lib_path_standard=/lib64/
lib_path_local=/usr/local/lib/

#Add Full path to library names
lib_standard=$(patsubst %.so,${lib_path_standard}%.so, libpthread.so)
lib_local=$(patsubst %.so,${lib_path_local}%.so, libmodbus.so)

lib=${lib_standard} ${lib_local}

#Make Rules
all: ${lib} ATLAS_Native_Serial_Test

ATLAS_Native_Serial_Test: ATLAS_Native_Serial_Test.c libATLAS_Native_Serial_Handlers.so
	gcc -fPIC -Wall -g -O0 -g ATLAS_Native_Serial_Test.c ATLAS_Native_Generic_Serial.o \
	-o ATLAS_Native_Serial_Test  ${lib} \
	./libATLAS_Native_Serial_Handlers.so

libATLAS_Native_Serial_Handlers.so: ${lib} ATLAS_Native_Generic_Serial.o 
	gcc -shared -g -fPIC -o libATLAS_Native_Serial_Handlers.so ATLAS_Native_Generic_Serial.o \
        -lc -lm -lcrypt ${lib}
	#Issue 'make release' to copy library to /atlas/lib
	

ATLAS_Native_Generic_Serial.o: ATLAS_Native_Generic_Serial.c ATLAS_Native_Generic_Serial.h
	gcc -c -fPIC -Wall -O0 -DMULTITHREADED -g ATLAS_Native_Generic_Serial.c -o ATLAS_Native_Generic_Serial.o


clean:
	rm -rf *o ATLAS_Native_Serial_Test


