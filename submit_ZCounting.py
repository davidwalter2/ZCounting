#!/usr/bin/env python
import os
import subprocess
import commands

#for runnum in range(1,11):
for runnum in [302026]:
        cmd = "/afs/cern.ch/work/x/xniu/public/CMSSW_9_2_8/src/ZCountHarvest/CloneJob/runZCountingOnBatch.sh "+str(runnum) 
	print cmd
	bsubs_cmd = "bsub -q 8nh -R 'pool > 4000' -C 0 -o" + \
		"/afs/cern.ch/work/x/xniu/public/CMSSW_9_2_8/src/ZCountHarvest/CloneJob/output "+cmd
	status,output=commands.getstatusoutput(bsubs_cmd)
	print output
