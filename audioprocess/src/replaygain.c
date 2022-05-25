#define _REPLAYGAIN_BUILD_DLL

#include "replaygain.h"
#include <stdio.h>

_REPLAYGAIN_EXPORTS void __stdcall replaygain_test(){
    printf("Replaygain function test-call success");
}
