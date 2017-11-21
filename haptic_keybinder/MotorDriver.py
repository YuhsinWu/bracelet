from BluetoothService import *
    
class GardenService:
    
    def __init__(self):
        bt = BluetoothService()
        time.clock() # start clock (needed on Windows)
        
   

"""
Some test code...
"""
if __name__ == '__main__':
    bt = BluetoothService()
    #bt.discoverDevices()
    
    #devices = bt.getDevices()
    #print('\nFound devices: ')
    #for (name, address) in devices.items():
    #    print("  <%s> at <%s>" % (name, address))

    #robots = bt.getDevices(('robot', 'hc-', 'linvor','haptic','20:13:11:29:04:20'))
    #print('\nFound robot devices: ')
    toConnect = '20:14:04:24:11:95'
    #for (address, name) in robots.items():
    #    print("  <%s> at <%s>" % (name, address))
    #    toConnect = address

    #ticker=10
    if bt.connect(toConnect):
        #b = 0
	try:
	    while(True):
                # Enter as a list, in the format "[1, 2, 3, ...]"
                # or as [10]*8
	        vals = input("Enter 8 Values: ")
                #while(b < 10):
                #s = 'z'
                #if(b < 9):
	        toSend = ''
	        for val in vals:
                    toSend += chr(val)
                bt.send(toConnect,toSend)
                #else:
                #bt.send(toConnect,'\0')
            #b = b + 1
            #delay(10)
	except:
    #delay(3000)
    	    bt.disconnect(toConnect)
