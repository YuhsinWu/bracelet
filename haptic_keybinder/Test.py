#/usr/bin/python
import sys
from BluetoothService import *

def looper(bt, vals, silent = False):
    toConnect = '20:14:04:24:11:95'
#    if silent:
#        print(vals)
    toSend = ''
    toSend += vals[0]
    toSend += vals[1]
    for x in range(2,len(vals)):
	toSend += chr(vals[x])
    toSend += chr(0)
#    if silent:
#        print(toSend)
    bt.send(toConnect,toSend)
    return

def allOff(bt):
    looper(bt,['0','a',1], True)
    looper(bt,['1','a',1], True)
    looper(bt,['2','a',1], True)
    looper(bt,['3','a',1], True)
    looper(bt,['4','a',1], True)
    looper(bt,['5','a',1], True)
    looper(bt,['6','a',1], True)
    looper(bt,['7','a',1], True)

if __name__ == '__main__':
    bt = BluetoothService()
    toConnect = '20:14:04:24:11:95'
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        print "Opening file " + sys.argv[1]
    else:
        filename = 'config'

    if  bt.connect(toConnect):
        allOff(bt)
        with open(filename) as f:
            lines = f.readlines()
        raw_input("Press enter to continue") #1
        allOff(bt)
        for line in lines:
            if line == "\n":
                raw_input("Press enter to continue") #1
                allOff(bt)
                continue
            print line
            if line[0] == 'r':
                sleeper = 0.2
                looper(bt,['6','d',255,255,010],True)
                time.sleep(sleeper)
                looper(bt,['6','d',1,255,010],True)
                looper(bt,['5','a',255,255,010],True)
                time.sleep(sleeper)
                looper(bt,['5','d',1,255,010],True)
                looper(bt,['4','a',255,255,010],True)
                time.sleep(sleeper)
                looper(bt,['4','d',1,255,010],True)
                looper(bt,['3','a',255,255,010],True)
                time.sleep(sleeper)
                looper(bt,['3','d',1,255,010],True)
                looper(bt,['2','a',255,255,010],True)
                time.sleep(sleeper)
                looper(bt,['2','d',1,255,010],True)
                looper(bt,['1','a',255,255,010],True)
                time.sleep(sleeper)
                looper(bt,['1','d',1,255,010],True)
                looper(bt,['0','a',255,255,010],True)
                time.sleep(sleeper)
                looper(bt,['0','a',1,255,010],True)
                continue
            elif line[0] == 'l':
                sleeper = 0.2
                looper(bt,['0','d',255,255,010],True)
                time.sleep(sleeper)
                looper(bt,['0','d',1,255,010],True)
                looper(bt,['1','a',255,255,010],True)
                time.sleep(sleeper)
                looper(bt,['1','d',1,255,010],True)
                looper(bt,['2','a',255,255,010],True)
                time.sleep(sleeper)
                looper(bt,['2','d',1,255,010],True)
                looper(bt,['3','a',255,255,010],True)
                time.sleep(sleeper)
                looper(bt,['3','d',1,255,010],True)
                looper(bt,['4','a',255,255,010],True)
                time.sleep(sleeper)
                looper(bt,['4','d',1,255,010],True)
                looper(bt,['5','a',255,255,010],True)
                time.sleep(sleeper)
                looper(bt,['5','d',1,255,010],True)
                looper(bt,['6','a',255,255,010],True)
                time.sleep(sleeper)
                looper(bt,['6','a',1,255,010],True)
                continue
            elif len(line) == 8:
                vals = [line[0], line[2] , int(line[4] + line[5] + line[6])]
            elif len(line) == 16:
                vals = [line[0], line[2] ,int(line[4] + line[5] + line[6]), int(line[8] + line[9] + line[10]), int(line[12] + line[13] + line[14]) ]
            else:
                print("INVALID INPUT SIZE")
                continue
            looper(bt,vals,True)

        raw_input("All done, Press enter to close")
        allOff(bt)
    print("All done!")
