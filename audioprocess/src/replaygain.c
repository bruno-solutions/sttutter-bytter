#define _REPLAYGAIN_BUILD_DLL

#include "replaygain.h"


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


int ReplayGain_init(replaygain_ReplayGain *self){
    int  i;

    /* zero out initial values*/
    for (i = 0; i < MAX_ORDER; i++ )
        self->linprebuf[i] =
        self->lstepbuf[i] =
        self->loutbuf[i] =
        self->rinprebuf[i] =
        self->rstepbuf[i] =
        self->routbuf[i] = 0.;

    self->freqindex = 1; //Sample Rate Set 44100

    self->sampleWindow = (int)ceil(44100 * RMS_WINDOW_TIME);

    self->lsum         = 0.;
    self->rsum         = 0.;
    self->totsamp      = 0;

    memset (self->A, 0, sizeof(self->A));

    self->linpre       = self->linprebuf + MAX_ORDER;
    self->rinpre       = self->rinprebuf + MAX_ORDER;
    self->lstep        = self->lstepbuf  + MAX_ORDER;
    self->rstep        = self->rstepbuf  + MAX_ORDER;
    self->lout         = self->loutbuf   + MAX_ORDER;
    self->rout         = self->routbuf   + MAX_ORDER;

    memset (self->B, 0, sizeof(self->B));

    self->title_peak = self->album_peak = 0.0;

    return 0;
}

_REPLAYGAIN_EXPORTS int __stdcall replaygain_wip(){
    printf("Replaygain Function PENDING IMPLEMENTATION\n");
    return -1;
}
