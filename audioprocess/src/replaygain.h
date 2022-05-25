#ifndef _AUDIOPROCESS_REPLAYGAIN_H_INCLUDED
#define _AUDIOPROCESS_REPLAYGAIN_H_INCLUDED

#ifndef _REPLAYGAIN_EXPORTS
    #ifdef _REPLAYGAIN_BUILD_DLL
        #define _REPLAYGAIN_EXPORTS __declspec(dllexport)
    #endif
#endif

_REPLAYGAIN_EXPORTS void __stdcall replaygain_test();

#endif //End of file _AUDIOPROCESS_REPLAYGAIN_H_INCLUDED
