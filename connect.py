# ble_scan_connect.py:
from bluepy.btle import Peripheral, UUID
from bluepy.btle import Scanner, DefaultDelegate
import struct
ls=[0,0,0]
IF=True
def mv():
    global IF
    IF=True
    Notif(dev)
    if ls[2]>930:
        return 0
    elif ls[1]<-300 :
        return 1
    elif ls[0]>300:
        return 2
    elif ls[0]<-300:
        return 3
    elif ls[1]>300:
        return 4
    else:
        return 0
class ScanDelegate(DefaultDelegate):
        def __init__(self):
                DefaultDelegate.__init__(self)
        def handleNotification(self, cHandle, data):
#            print ('Data received')
#            print (cHandle)    #use this to check the  handle value of each characteristic
            if cHandle < 19:
                print ("HeartRate is %d bpm" %data[1])
            else:
                if data[0]:
                    k=struct.unpack('!Bh',data)
                    out=k[1]
                else:
                    out=int(data[1])
                if cHandle < 22:
                    ls[0]=out
                elif cHandle < 25:
                    ls[1]=out
                else:
                    ls[2]=out
                    global IF
                    IF=False
scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(3.0)

print ("Connecting...")
dev = Peripheral('e1:b2:60:72:64:aa', 'random')
dev.setDelegate(ScanDelegate())
def Notif(dev):
        accnoService = dev.getServiceByUUID(UUID(0x2AA1))
        accX = accnoService.getCharacteristics(UUID(0xfff0))
        accY = accnoService.getCharacteristics(UUID(0xfff1))
        accZ = accnoService.getCharacteristics(UUID(0xfff2))
        dev.writeCharacteristic(accX[0].valHandle + 1, b'\x01\x00')
        dev.writeCharacteristic(accY[0].valHandle + 1, b'\x01\x00')
        dev.writeCharacteristic(accZ[0].valHandle + 1, b'\x01\x00')
        while IF:
            if dev.waitForNotifications(0.1):
                 continue
