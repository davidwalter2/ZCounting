#!/bin/bash
export PATH=$HOME/.local/bin:/afs/cern.ch/cms/lumi/brilconda-1.1.7/bin:$PATH
DATE=`date '+%m/%d/%y'`
DATE2=`date '+%m_%d_%y'`
TIME=`date '+%H:%M:%S'`
echo $DATE
echo $TIME

brilcalc lumi --begin "04/20/18 13:54:51" --end "$DATE $TIME" -b "STABLE BEAMS" --byls -o /eos/cms/store/group/comm_luminosity/ZCounting/brilcalcFile2018/briloutByLS_${DATE2}.csv --hltpath="HLT_IsoMu27_v*"