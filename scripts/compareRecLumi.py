#This script compares triggerpath dependent deadtime and general deadtime, and print out different points and write into a csv file
import csv
import os,sys

f1 = file('/eos/cms/store/group/comm_luminosity/ZCounting/2017LumiByLS_trig.csv', 'r')
f2 = file('/eos/cms/store/group/comm_luminosity/ZCounting/2017LumiByLS_notrig_PU.csv', 'r')
f3 = file('difflumirec.csv', 'w')

c1 = csv.reader(f1, delimiter=",")
c2 = csv.reader(f2, delimiter=",")
c3 = csv.writer(f3, delimiter=",")

notriggerlist = list(c2)
diff_row = []

for trigger_row in c1:
    if trigger_row[0] == '#Data tag : v1 ':
        continue;
    if trigger_row[0] == '#run:fill':
        continue; 
    found = False
    for notrigger_row in notriggerlist:
        if notrigger_row[0] == trigger_row[0] and notrigger_row[1] == trigger_row[1]:
            if float(notrigger_row[6]) != float(trigger_row[5]):
		print float(notrigger_row[6]) - float(trigger_row[5])
                diff_row.append(float(notrigger_row[6]) - float(trigger_row[5]))
                c3.writerow(diff_row)
            found = True
            break

f1.close()
f2.close()
f3.close()
