from BluetoothService import *
    
if __name__ == '__main__':
    bt = BluetoothService()
    toConnect = '20:14:04:24:11:95'
    if bt.connect(toConnect):
	try:
	    while(True):
                # Enter as a list, in the format "[1, 2, 3, ...]"
	        vals = input("Enter motor number + Enter 3 [1-255] Values: ")
#                vals=[4,220,220,10]
	        toSend = ''
                toSend += chr(vals[0] + ord('0'))
                toSend += chr(ord('d'))
                toSend += chr(vals[1])
                toSend += chr(vals[2])
                toSend += chr(vals[3])
                toSend += chr(0)
                bt.send(toConnect,toSend)
#                print (bt.read(toConnect,1000))
#                print (bt.read(toConnect,1000))
#                print (bt.read(toConnect,1000))
	except:
    	    bt.disconnect(toConnect)
