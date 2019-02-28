#!/bin/bash

runNum=$1

workdir="/afs/cern.ch/work/d/dwalter/CMSSW_9_2_8/src/ZCounting"

CMSSW_BASE="/afs/cern.ch/work/d/dwalter/CMSSW_9_2_8/src/"
TOP="$PWD"

cd $CMSSW_BASE
eval `scramv1 runtime -sh`
cd $TOP

cp -r ${workdir}/Utils $TOP
cp -r ${workdir}/.rootlogon.C $TOP
cp ${workdir}/calculateDataEfficiency.C $TOP
cp ${workdir}/calculateZEfficiency.C $TOP
cp ${workdir}/ZCounting.py $TOP

python ZCounting.py -b $runNum -e $(($runNum + 1)) -d $2 -f $3 -g $4 -t $5 -a $6 -x $7  

