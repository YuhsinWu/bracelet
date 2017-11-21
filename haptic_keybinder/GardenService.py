from BluetoothService import *
    
class GardenService:
    
    def __init__(self, numTiles = 16, enablePrint=True, flowersPerTile=8, stripsPerFlower=3, ledsPerStrip=5):
        self._bt = BluetoothService()
        self._numTiles = numTiles
        self._tiles = [None]*numTiles # List of addresses of each tile (tile 0 is at index 0, etc)
        self._flowersPerTile = flowersPerTile
        self._stripsPerFlower = stripsPerFlower
        self._ledsPerStrip = ledsPerStrip
        time.clock() # start clock (needed on Windows)
        self.setPrint(enablePrint)

    def setPrint(self, enablePrint):
        self._print = enablePrint

    def tileName(self, tileNum):
        """
        Converts a tile number to a tile name.  This convention should be implemented on the Arduinos.

        @param tileNum: The 0-indexed number of the tile.
        @type tileNum: int

        @return: The bluetooth name that tile should have.
        @rtype: str
        """
        return 'tile_' + ('0' if tileNum < 10 else '') + str(tileNum)
        
    def setAddress(self, tileNum, address):
        """
        Sets the address of the Bluetooth module for the given tile

        @param tileNum: The 0-indexed number of the tile.
        @type tileNum: int

        @param address: The Bluetooth address of the tile (format 'XX:XX:XX:XX:XX:XX')
        @type address: str
        """
        self._tiles[tileNum] = address
        self._bt.addDevice(address, self.tileName(tileNum))

    def connectTiles(self, tileNum = None):
        """
        Connects to the given tiles, or to all tiles if none are supplied.

        @param tileNum: The 0-indexed tile numbers to connect
        @type tileNum: list or tuple of int or an int
        """
        if tileNum is None:
            tileNum = list(range(self._numTiles))
        if not isinstance(tileNum, (list, tuple)):
            tileNum = [tileNum]
        if self._print:
            print('\nConnecting to tiles', tileNum)
        unknown = []
        for tile in tileNum:
            if self._tiles[tile] is None:
                unknown.append(tile)
        if len(unknown) > 0:
            """
            print('No address is known for tiles ', unknown, end='... ')
            print('trying to discover devices')
            discovered = self._bt.discoverDevices()
            for tile in unknown[:]:
                if self.tileName(tile) in discovered.values():
                    for (address, name) in discovered:
                        if name == self.tileName(tile):
                            self.setAddress(tile, address)
                            unknown.remove(tile)
                            break
            """
            if len(unknown) > 0:
                print('No address is known for tiles ', unknown, end='... ')
                print('Will not connect to these tiles')
        for tile in tileNum:
            if tile not in unknown:
                self._bt.connect(self._tiles[tile])

    def disconnectTiles(self, tileNum = None):
        """
        Disconnects from the given tiles, or from all tiles if none are supplied.

        @param tileNum: The 0-indexed tile numbers to disconnect
        @type tileNum: list or tuple of int or an int
        """
        if tileNum is None:
            tileNum = list(range(self._numTiles))
        if not isinstance(tileNum, (list, tuple)):
            tileNum = [tileNum]
        if self._print:
            print('\nDisconnecting from tiles', tileNum)
        for tile in tileNum:
            self._bt.disconnect(self._tiles[tile])

    def sendToTiles(self, message, tileNum = None, waitForAck = True):
        """
        Send a message to the given tiles, or all if none are provided.

        The tiles should be already connected (see L{connectTiles}).

        @param message: The data to send.  If it doesn't already end in '\0', '\0' will be appended.
        @type message: str or something which can be cast to str

        @param tileNum: The 0-indexed tile numbers to disconnect
        @type tileNum: list or tuple of int or an int

        @param waitForAck: Whether it should wait for an acknowledgement of receipt of the data from each tile.
        Not waiting will make this call return very fast, but then be cautious about flooding the bluetooth connection with too frequent calls.
        Also, if waitForAck is False then there is no way to know for sure if the Arduino actually got the message.
        @type waitForAck: boolean
        
        @return: Whether the data was sent to all desired tiles.
        @rtype: boolean
        """
        waitForAck = False
        if tileNum is None:
            tileNum = list(range(self._numTiles))
        if not isinstance(tileNum, (list, tuple)):
            tileNum = [tileNum]
        if self._print:
            print('\nSending <%s> to tiles %s' % (message, str(tileNum)))
        success = True
        acks = []
        for tile in tileNum:
            #if a tile number doesn't have an address (i.e. tiles that are not parents)
            #if self._tiles[tile] is None:
                #continue
            haveAck = False
            tries = 0
            while(not haveAck and tries < 7):
                if tries > 0:
                    print('\tRetrying send data to %d' % tile)
                #I added in the tile number at the beginning of every message here and the if statements
                #if tile==0 or tile==1 or tile==6 or tile==7 or tile==10 or tile==11:
                print (str(tile) +"_" + message)
                if not self._bt.send(self._tiles[0], str(tile) + "_" + message, enablePrint=False):
                    success = False
                    print('Could not send %s to tile %d' % (message, tile))
                '''
                elif tile==2 or tile==3 or tile==12 or tile==13:
                    if not self._bt.send(self._tiles[2], str(tile) + "_" + message, enablePrint=False):
                        success = False
                        print('Could not send %s to tile %d' % (message, tile))
                elif tile==4 or tile==5 or tile==8 or tile==9 or tile==14 or tile==15:
                    if not self._bt.send(self._tiles[4], str(tile) + "_" + message, enablePrint=False):
                        success = False
                        print('Could not send %s to tile %d' % (message, tile))
                #This is the end of what I cahnged/added
                '''
                if waitForAck:
                    ack = self.readFromTiles(tileNum=tileNum, timeout=2000)[0]
                    haveAck = (ack == 'OK')
                    tries += 1
                    if haveAck:
                        acks.append(ack)
                        if tries > 1:
                            print('Received acknowledgement from tile %d for <%s>' % (tile, message))
                    else:
                        print('Did not receive acknowledgement from tile %d for <%s>' % (tile, message))
                else:
                    break
            time.sleep(0.1)
            
        for ack in acks:
            if len(ack) == 0 or (ack != 'OK'):
                success = False
                #print('Send <%> to %d might have failed: did not receive acknowledgement' % (message, tile))
        return success or not waitForAck

    def readFromTiles(self, tileNum = None, timeout=1000):
        """
        Read data from the given tiles, or all if none are provided.

        The tiles must be already connected (see L{connectTiles}).

        @param tileNum: The 0-indexed tile numbers to disconnect
        @type tileNum: list or tuple of int or an int

        @param timeout: The time to wait for a character before giving up, in milliseconds.  Default is 1000.
        @type timeout: int
        
        @return: The data received from the tiles.
        The data from tile numbered i is in the ith position of the returned list.
        If no data was read from tile i (error or didn't try), that position contains an empty string
        @rtype: list of str
        """
        if tileNum is None:
            tileNum = list(range(self._numTiles))
        if not isinstance(tileNum, (list, tuple)):
            tileNum = [tileNum]
        if self._print:
            print('\nReading from tiles %s' % str(tileNum))
        data = ['']*self._numTiles
        for tile in tileNum:
            data[tile] = self._bt.read(self._tiles[tile], timeout, enablePrint=False)
            if self._print:
                print('\tReceived <%s> from tile %s' % (data[tile], str(tile)))
        return data
        

    def setColor(self, color, tileNum=None, flower=None, strip=None, led=None, waitForAck=True):
        """
        Sets the color of some RGB LEDs.
        Can specify at level of tile, flower, strip, or individual led.
        Will send the same command to each specified tile.

        @param color: A tuple/list of (red, green, blue) values.  Each value is between 0 and 255.
        If a single number is given, will set all channels to that value.
        @type color: tuple/list of int or an int

        @param tileNum: The 0-indexed tile numbers to control.
        Will control all tiles if omitted.
        @type tileNum: list or tuple of int or an int

        @param flower: The 0-indexed flower to control on each desired tile.
        Will control all flowers on desired tiles if omitted.
        @type flower: int or list/tuple of int

        @param strip: The 0-indexed strip to control on each desired flower.
        If strip is provided, led should be provided as well (or led will default to 0).
        Will control given strip on each desired flower if an int is given.
        If a list/tuple is given, there should be one element for each desired flower (will match them up).
        If omitted:
          Will control all leds on all strips of each desired flower if leds is also omitted.
          Will control the given led on each strip of desired flower if leds is provided.
        @type strip: int or list/tuple of int

        @param led: The 0-indexed led to control on each desired strip.
        Will control given led on each desired strip if an int is given.
        If a list/tuple is given, there should be one element for each desired strip (will match them up).
        If omitted:
          Will control all leds of all strips if strips is also omitted.
          Will control 0th led of each desired strip if strips is provided.
        @type led: int or list/tuple of int

        @param waitForAck: Whether it should wait for an acknowledgement of receipt of the data from each tile.
        Not waiting will make this call return very fast, but then be cautious about flooding the bluetooth connection with too frequent calls.
        Also, if waitForAck is False then there is no way to know for sure if the Arduino actually got the message.
        @type waitForAck: boolean
        
        @return: Whether the data was successfully sent and received to/from all desired tiles.
        @rtype: boolean
        """
        if not isinstance(color, (list, tuple)):
            color = (color, color, color)
        if tileNum is None:
            tileNum = list(range(self._numTiles))
        if not isinstance(tileNum, (list, tuple)):
            tileNum = [tileNum]
        color = list(color)
        temp = color[0]
        color[0] = color[1]
        color[1] = temp
        command = str('SET_COLOR<%d-%d-%d>' % (color[0], color[1], color[2]))
        if not(flower is None and strip is None and led is None):
            if flower is None:
                flower = list(range(self._flowersPerTile))
            if not isinstance(flower, (list, tuple)):
                flower = [flower]
            for i in range(len(flower)):
                command += str('<%d' % flower[i])
                if strip is not None:
                    if isinstance(strip, (list, tuple)):
                        command += str('-%d' % strip[i])
                    else:
                        command += str('-%d' % strip)
                if led is not None:
                    if isinstance(led, (list, tuple)):
                        command += str('-%d' % led[i])
                    else:
                        command += str('-%d' % led)
                elif strip is not None:
                    command += '-0'
                command += str('>')
        return self.sendToTiles(command, tileNum, waitForAck)

    def actuate(self, inflate=True, tileNum=None, flower=None, valve=None, waitForAck=True):
        """
        Actuates some valves.
        Can specify at level of tile, flower, or valve.
        Will send the same command to each specified tile.

        @param inflate: Whether the desired valves should be inflated or deflated.
        @type inflate: boolean

        @param tileNum: The 0-indexed tile numbers to control.
        Will control all tiles if omitted.
        @type tileNum: list or tuple of int or an int

        @param flower: The 0-indexed flower to control on each desired tile.
        Will control all flowers on desired tiles if omitted.
        @type flower: int or list/tuple of int

        @param valve: The 0-indexed valve to control on each desired flower.
        Will control given valve on each desired flower if an int is given.
        If a list/tuple is given, there should be one element for each desired flower (will match them up).
        If omitted, will control all valves on each desired flower.
        @type valve: int or list/tuple of int

        @param waitForAck: Whether it should wait for an acknowledgement of receipt of the data from each tile.
        Not waiting will make this call return very fast, but then be cautious about flooding the bluetooth connection with too frequent calls.
        Also, if waitForAck is False then there is no way to know for sure if the Arduino actually got the message.
        @type waitForAck: boolean
        
        @return: Whether the data was sent to all desired tiles.
        @rtype: boolean
        """
        if tileNum is None:
            tileNum = list(range(self._numTiles))
        if not isinstance(tileNum, (list, tuple)):
            tileNum = [tileNum]
        command = str('%s' % 'INFLATE' if inflate else 'DEFLATE')
        if not(flower is None and valve is None):
            if flower is None:
                flower = list(range(self._flowersPerTile))
            if not isinstance(flower, (list, tuple)):
                flower = [flower]
            for i in range(len(flower)):
                command += str('<%d' % flower[i])
                if valve is not None:
                    if isinstance(valve, (list, tuple)):
                        command += str('-%d' % valve[i])
                    else:
                        command += str('-%d' % valve)
                command += str('>')
        return self.sendToTiles(command, tileNum, waitForAck)

    def inflate(self, tileNum=None, flower=None, valve=None, waitForAck=True):
        """
        Inflates some valves.
        Can specify at level of tile, flower, or valve.
        Will send the same command to each specified tile.

        @param tileNum: The 0-indexed tile numbers to control.
        Will control all tiles if omitted.
        @type tileNum: list or tuple of int or an int

        @param flower: The 0-indexed flower to control on each desired tile.
        Will control all flowers on desired tiles if omitted.
        @type flower: int or list/tuple of int

        @param valve: The 0-indexed valve to control on each desired flower.
        Will control given valve on each desired flower if an int is given.
        If a list/tuple is given, there should be one element for each desired flower (will match them up).
        If omitted, will control all valves on each desired flower.
        @type valve: int or list/tuple of int

        @param waitForAck: Whether it should wait for an acknowledgement of receipt of the data from each tile.
        Not waiting will make this call return very fast, but then be cautious about flooding the bluetooth connection with too frequent calls.
        Also, if waitForAck is False then there is no way to know for sure if the Arduino actually got the message.
        @type waitForAck: boolean
        
        @return: Whether the data was sent to all desired tiles.
        @rtype: boolean
        """
        return self.actuate(inflate=True, tileNum=tileNum, flower=flower, valve=valve, waitForAck=waitForAck)

    def deflate(self, tileNum=None, flower=None, valve=None, waitForAck=True):
        """
        Inflates some valves.
        Can specify at level of tile, flower, or valve.
        Will send the same command to each specified tile.

        @param tileNum: The 0-indexed tile numbers to control.
        Will control all tiles if omitted.
        @type tileNum: list or tuple of int or an int

        @param flower: The 0-indexed flower to control on each desired tile.
        Will control all flowers on desired tiles if omitted.
        @type flower: int or list/tuple of int

        @param valve: The 0-indexed valve to control on each desired flower.
        Will control given valve on each desired flower if an int is given.
        If a list/tuple is given, there should be one element for each desired flower (will match them up).
        If omitted, will control all valves on each desired flower.
        @type valve: int or list/tuple of int

        @param waitForAck: Whether it should wait for an acknowledgement of receipt of the data from each tile.
        Not waiting will make this call return very fast, but then be cautious about flooding the bluetooth connection with too frequent calls.
        Also, if waitForAck is False then there is no way to know for sure if the Arduino actually got the message.
        @type waitForAck: boolean
        
        @return: Whether the data was sent to all desired tiles.
        @rtype: boolean
        """
        return self.actuate(inflate=False, tileNum=tileNum, flower=flower, valve=valve, waitForAck=waitForAck)

    def setInflateTime(self, tileNum=None, flower=None, time=3000, waitForAck=True):
        """
        Sets the inflation time for the flowers.
       
        @param tileNum: The 0-indexed tile numbers to control.
        Will control all tiles if omitted.
        @type tileNum: list or tuple of int or an int

        @param flower: The 0-indexed flower to control on each desired tile.
        Will control all flowers on desired tiles if omitted.
        @type flower: int or list/tuple of int

        @param time: The time, in ms, to inflate.  If time is a list, it should be the same length as flower (they will be matched up).
        @type time: list or tuple of int, or int

        @param waitForAck: Whether it should wait for an acknowledgement of receipt of the data from each tile.
        Not waiting will make this call return very fast, but then be cautious about flooding the bluetooth connection with too frequent calls.
        Also, if waitForAck is False then there is no way to know for sure if the Arduino actually got the message.
        @type waitForAck: boolean
        
        @return: Whether the data was sent to all desired tiles.
        @rtype: boolean
        """
        if tileNum is None:
            tileNum = list(range(self._numTiles))
        if not isinstance(tileNum, (list, tuple)):
            tileNum = [tileNum]
        command = str('INFLATE_TIME')
        if flower is None:
            if isinstance(time, (list, tuple)):
                command += str('<%d>' % time[0])
            else:
                command += str('<%d>' % time)
        else:
            if not isinstance(flower, (list,tuple)):
                flower = [flower]
            if not isinstance(time, (list, tuple)):
                time = [time]
            if len(time) < len(flower):
                time += [time[-1]] * (len(flower) - len(time))
            for flowerNum in range(len(flower)):
                command += str('<%d-%d>' % (flower[flowerNum], time[flowerNum]))
        return self.sendToTiles(command, tileNum, waitForAck)
    
    def setAutonomous(self, tileNum=None, waitForAck=True):
        """
        Switches the given tile(s) into autonomous mode.
        Autonomous mode will be exited whenever another command is received.

        @param tileNum: The 0-indexed tile numbers to control.
        Will control all tiles if omitted.
        @type tileNum: list or tuple of int or an int

        @param waitForAck: Whether it should wait for an acknowledgement of receipt of the data from each tile.
        Not waiting will make this call return very fast, but then be cautious about flooding the bluetooth connection with too frequent calls.
        Also, if waitForAck is False then there is no way to know for sure if the Arduino actually got the message.
        @type waitForAck: boolean
        
        @return: Whether the data was sent to all desired tiles.
        @rtype: boolean
        """
        if tileNum is None:
            tileNum = list(range(self._numTiles))
        if not isinstance(tileNum, (list, tuple)):
            tileNum = [tileNum]
        command = str('AUTO')
        return self.sendToTiles(command, tileNum, waitForAck)

    
    def flood(self, waitForAck=True):
        command = str('FLOOD')
        
        return self.sendToTiles(command, 0, waitForAck)

    def graphColoring(self, waitForAck=True):
        command = str('COLOR')

        return self.sendToTiles(command, 0, waitForAck)

"""
Some test code...
"""
if __name__ == '__main__':
    garden = GardenService(1)
    garden.setPrint(False)

    garden.setAddress(0, '98:D3:31:B3:0C:7D')    
    
    garden.connectTiles()
    delay(1000)
    """
    for i in range(200):
        print('\n------%d--------' %i)
        garden.setColor(color=(100,0,0))
        delay(100)
        garden.setColor(color=(0,100,0))
        delay(100)
        garden.setColor(color=(0,0,100))
        delay(100)
        garden.setColor(color=(10,10,10))
        delay(100)
    garden.setAutonomous()
    """
    garden.setInflateTime(tileNum=0, time=3000)
    delay(1000)
    garden.setColor(tileNum=0, color=(100,101,102))
    delay(1000)
    garden.setColor(tileNum=0, color=(0,0,102))
    delay(5000)
    """
    for i in range(1):
        print('\n--------------------')
        start = time.clock()
        a = time.clock()
        #garden.setColor(tileNum=0, color=(100,101,102))
        garden.deflate(tileNum=0)
        print(time.clock() - a)
        a = time.clock()
        #garden.setColor(tileNum=0, color=(100,101,102), flower=[3,4])
        garden.actuate(tileNum=0, inflate=True, flower=0)
        print(time.clock() - a)
        a = time.clock()
        #garden.setColor(tileNum=0, color=(100,101,102), flower=[3,4], led=[7,5])
        garden.actuate(tileNum=0, inflate=True, flower=0, valve=1)
        print(time.clock() - a)
        a = time.clock()
        #garden.setColor(tileNum=0, color=(100,101,102), flower=[3,4], strip=[9,8])
        garden.deflate(tileNum=0, flower=[0,1])
        print(time.clock() - a)
        a = time.clock()
        #garden.setColor(tileNum=0, color=(100,101,102), flower=[3,4], strip=9, led=[7,5])
        garden.actuate(tileNum=0, inflate=True, flower=[1,3], valve=[5,6])
        print(time.clock() - a)
        print('\n', time.clock()-start, (time.clock()-start)/15)
        delay(3000)
        """
    garden.disconnectTiles()
    










