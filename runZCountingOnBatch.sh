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

python ZCounting.py -b $runNum -e $(($runNum + 1)) -m True -l $2 -s $3 -d $4 -f $5 -g $6 -t $7 -a $8 -x $9  

