#/usr/bin/python
import sys
from BluetoothService import *
    
if __name__ == '__main__':
    bt = BluetoothService()
    toConnect = '20:14:04:24:11:95'
    print str(sys.argv)
    if bt.connect(toConnect):
	try:
	    while(True):
                # Enter as a list, in the format "[1, 2, 3, ...]"
#		vals = [5,'a',10]
	        vals = input("Enter motor number + ('a'=Intensity 'b'= On Period 'c'=Total Period 'd'=All) + Enter up to 3 [1-255] Values: ")
	        toSend = ''
                toSend += chr(vals[0] + ord('0'))
                #toSend += chr(ord(val[1]))
                toSend += chr(ord(vals[1]))
		for x in range(2,len(vals)):
			toSend += chr(vals[x])
		print toSend
                toSend += chr(0)
                bt.send(toConnect,toSend)
	except:
    	    bt.disconnect(toConnect)
