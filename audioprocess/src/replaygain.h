#ifndef _AUDIOPROCESS_REPLAYGAIN_H_INCLUDED
#define _AUDIOPROCESS_REPLAYGAIN_H_INCLUDED

#ifndef _REPLAYGAIN_EXPORTS
    #ifdef _REPLAYGAIN_BUILD_DLL
        #define _REPLAYGAIN_EXPORTS __declspec(dllexport)
    #endif
#endif

#include <stdio.h>
#include <math.h>
#include <stdint.h>
#include <string.h>


/*
 *  ReplayGainAnalysis - analyzes input samples and give the recommended dB change
 *  Copyright (C) 2001 David Robinson and Glen Sawyer
 *  Modified 2010 by Brian Langenberger for use in Python Audio Tools
 *  Modified 2022 by Yake Wang for use in Sttutter Audio Bot
 *
 *  This library is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU Lesser General Public
 *  License as published by the Free Software Foundation; either
 *  version 2.1 of the License, or (at your option) any later version.
 *
 *  This library is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *  Lesser General Public License for more details.
 *
 *  You should have received a copy of the GNU Lesser General Public
 *  License along with this library; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 *  concept and filter values by David Robinson (David@Robinson.org)
 *    -- blame him if you think the idea is flawed
 *  coding by Glen Sawyer (mp3gain@hotmail.com) 735 W 255 N, Orem, UT 84057-4505 USA
 *    -- blame him if you think this runs too slowly, or the coding is otherwise flawed
 *
 *  For an explanation of the concepts and the basic algorithms involved, go to:
 *    http://www.replaygain.org/
 */


#define GAIN_NOT_ENOUGH_SAMPLES  -24601

#define YULE_ORDER         10
#define BUTTER_ORDER       2
#define YULE_FILTER        filterYule
#define BUTTER_FILTER      filterButter
#define RMS_PERCENTILE     0.95          /* percentile which is louder than the proposed level */
#define MAX_SAMP_FREQ      192000.       /* maximum allowed sample frequency [Hz] */
#define RMS_WINDOW_TIME    0.050         /* Time slice size [s] */
#define STEPS_per_dB       100.          /* Table entries per dB */
#define MAX_dB             120.          /* Table entries for 0...MAX_dB (normal max. values are 70...80 dB) */

#define MAX_ORDER 10                     /* MAX(YULE_ORDER, BUTTER_ORDER) */
#define MAX_SAMPLES_PER_WINDOW   2205    /* max. Samples per Time slice */
#define PINK_REF           64.82         /* calibration value */

typedef enum {GAIN_ANALYSIS_ERROR, GAIN_ANALYSIS_OK} gain_calc_status;


typedef struct{
    double          linprebuf [MAX_ORDER * 2];
    double*         linpre;  /* left input samples, with pre-buffer */
    double          lstepbuf  [MAX_SAMPLES_PER_WINDOW + MAX_ORDER];
    double*         lstep;   /* left "first step" (i.e. post first filter) samples */
    double          loutbuf   [MAX_SAMPLES_PER_WINDOW + MAX_ORDER];
    double*         lout;    /* left "out" (i.e. post second filter) samples */
    double          rinprebuf [MAX_ORDER * 2];
    double*         rinpre;  /* right input samples ... */
    double          rstepbuf  [MAX_SAMPLES_PER_WINDOW + MAX_ORDER];
    double*         rstep;
    double          routbuf   [MAX_SAMPLES_PER_WINDOW + MAX_ORDER];
    double*         rout;
    long            sampleWindow; /* number of samples required to reach number of milliseconds required for RMS window */
    long            totsamp;
    double          lsum;
    double          rsum;
    int             freqindex;
    int             first;
    uint32_t  A [12000];
    uint32_t  B [12000];

    double title_peak;
    double album_peak;
}replaygain_ReplayGain;


int ReplayGain_init(replaygain_ReplayGain *self);

_REPLAYGAIN_EXPORTS int __stdcall replaygain_wip();


#endif //End of file _AUDIOPROCESS_REPLAYGAIN_H_INCLUDED
