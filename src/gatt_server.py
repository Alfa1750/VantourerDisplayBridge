#!/usr/bin/env python3
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import os
import signal
from collections import deque
from tcp_client import NodeRedTcpClient

BLUEZ='org.bluez'
OM='org.freedesktop.DBus.ObjectManager'
PROP='org.freedesktop.DBus.Properties'
GATT_MANAGER='org.bluez.GattManager1'
ADV_MANAGER='org.bluez.LEAdvertisingManager1'
SERVICE_IFACE='org.bluez.GattService1'
CHAR_IFACE='org.bluez.GattCharacteristic1'
ADV_IFACE='org.bluez.LEAdvertisement1'
SERVICE_UUID='8f7a0001-6d5b-4c3a-9e2f-1a0b2c3d4e5f'
TX_UUID='8f7a0002-6d5b-4c3a-9e2f-1a0b2c3d4e5f'
RX_UUID='8f7a0003-6d5b-4c3a-9e2f-1a0b2c3d4e5f'
mainloop=None

# Application-level BLE framing: 20-byte values work with the minimum ATT MTU
# of 23 bytes (20-byte notification payload), independent of MTU negotiation.
BLE_FRAME_MAGIC = b"VD"
BLE_FRAME_VERSION = 1
BLE_NOTIFICATION_VALUE_MAX = 20
BLE_FRAME_HEADER_SIZE = 6
BLE_FRAME_DATA_SIZE = BLE_NOTIFICATION_VALUE_MAX - BLE_FRAME_HEADER_SIZE
BLE_MAX_MESSAGE_SIZE = BLE_FRAME_DATA_SIZE * 255
BLE_FRAGMENT_INTERVAL_MS = 10

class Characteristic(dbus.service.Object):
    def __init__(self,bus,index,uuid,flags,service):
        self.path=service.path+'/char'+str(index)
        self.uuid,self.flags,self.service=uuid,flags,service
        self.value=[]
        self.notifying=False
        self.on_write=None
        self._tx_fragments=deque()
        self._tx_timer_id=0
        self._tx_message_id=0
        dbus.service.Object.__init__(self,bus,self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {CHAR_IFACE:{'Service':self.service.get_path(),'UUID':self.uuid,
            'Flags':dbus.Array(self.flags,signature='s'),'Descriptors':dbus.Array([],signature='o')}}

    @dbus.service.method(PROP,in_signature='s',out_signature='a{sv}')
    def GetAll(self,interface):
        if interface!=CHAR_IFACE:
            raise dbus.exceptions.DBusException('Invalid interface')
        return self.get_properties()[CHAR_IFACE]

    @dbus.service.method(CHAR_IFACE,in_signature='a{sv}',out_signature='ay')
    def ReadValue(self,options):
        return dbus.Array(self.value,signature='y')

    @dbus.service.method(CHAR_IFACE,in_signature='aya{sv}')
    def WriteValue(self,value,options):
        data=bytes(value)
        print('ESP32 -> Pi:',data.hex(),repr(data),flush=True)
        if self.on_write is not None:
            self.on_write(data)

    @dbus.service.method(CHAR_IFACE)
    def StartNotify(self):
        self.notifying=True
        print('ESP32 heeft notifications ingeschakeld',flush=True)

    @dbus.service.method(CHAR_IFACE)
    def StopNotify(self):
        self.notifying=False
        self._tx_fragments.clear()
        print('ESP32 heeft notifications uitgeschakeld',flush=True)

    @dbus.service.signal(PROP,signature='sa{sv}as')
    def PropertiesChanged(self,interface,changed,invalidated):
        pass

    def send(self,data):
        data=bytes(data)
        if not self.notifying:
            print('Pi -> ESP32: notification niet actief; bericht overgeslagen',flush=True)
            return
        if not data or len(data)>BLE_MAX_MESSAGE_SIZE:
            print('Pi -> ESP32: berichtlengte ongeldig ({} bytes; maximum {}); verworpen'.format(
                len(data),BLE_MAX_MESSAGE_SIZE),flush=True)
            return

        self._tx_message_id=(self._tx_message_id+1)&0xff
        fragment_count=(len(data)+BLE_FRAME_DATA_SIZE-1)//BLE_FRAME_DATA_SIZE
        for index in range(fragment_count):
            start=index*BLE_FRAME_DATA_SIZE
            payload=data[start:start+BLE_FRAME_DATA_SIZE]
            frame=(BLE_FRAME_MAGIC+bytes((BLE_FRAME_VERSION,self._tx_message_id,
                                          index,fragment_count))+payload)
            self._tx_fragments.append(frame)

        print('Pi -> ESP32: {} bytes in {} BLE-fragmenten (bericht {})'.format(
            len(data),fragment_count,self._tx_message_id),flush=True)
        if not self._tx_timer_id:
            self._tx_timer_id=GLib.timeout_add(
                BLE_FRAGMENT_INTERVAL_MS,self._send_next_fragment)

    def _send_next_fragment(self):
        if not self.notifying:
            self._tx_fragments.clear()
            self._tx_timer_id=0
            return False
        if not self._tx_fragments:
            self._tx_timer_id=0
            return False

        frame=self._tx_fragments.popleft()
        self.value=[dbus.Byte(b) for b in frame]
        self.PropertiesChanged(CHAR_IFACE,{'Value':self.value},[])
        return True

class Service(dbus.service.Object):
    def __init__(self,bus,index):
        self.path='/com/vantourer/bridge/service'+str(index)
        self.uuid=SERVICE_UUID
        self.characteristics=[]
        dbus.service.Object.__init__(self,bus,self.path)
        self.tx=Characteristic(bus,0,TX_UUID,['notify'],self)
        self.rx=Characteristic(bus,1,RX_UUID,['write'],self)
        self.characteristics.extend([self.tx,self.rx])

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_characteristics(self):
        return self.characteristics

    def get_properties(self):
        return {SERVICE_IFACE:{'UUID':self.uuid,'Primary':dbus.Boolean(True),
            'Characteristics':dbus.Array([c.get_path() for c in self.characteristics],signature='o')}}

    @dbus.service.method(PROP,in_signature='s',out_signature='a{sv}')
    def GetAll(self,interface):
        if interface!=SERVICE_IFACE:
            raise dbus.exceptions.DBusException('Invalid interface')
        return self.get_properties()[SERVICE_IFACE]

class Application(dbus.service.Object):
    def __init__(self,bus):
        self.path='/'
        self.services=[]
        dbus.service.Object.__init__(self,bus,self.path)
        self.services.append(Service(bus,0))

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(OM,out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        result={}
        for service in self.services:
            result[service.get_path()]=service.get_properties()
            for characteristic in service.get_characteristics():
                result[characteristic.get_path()]=characteristic.get_properties()
        return result

class Advertisement(dbus.service.Object):
    def __init__(self,bus):
        self.path='/com/vantourer/bridge/advertisement0'
        dbus.service.Object.__init__(self,bus,self.path)

    @dbus.service.method(PROP,in_signature='s',out_signature='a{sv}')
    def GetAll(self,interface):
        if interface!=ADV_IFACE:
            raise dbus.exceptions.DBusException('Invalid interface')
        return {'Type':'peripheral','ServiceUUIDs':dbus.Array([SERVICE_UUID],signature='s'),
            'LocalName':'VantourerBridge'}

    @dbus.service.method(ADV_IFACE)
    def Release(self):
        print('BLE-advertentie vrijgegeven',flush=True)

def find_adapter(bus):
    manager=dbus.Interface(bus.get_object(BLUEZ,'/'),OM)
    for path,interfaces in manager.GetManagedObjects().items():
        if GATT_MANAGER in interfaces and ADV_MANAGER in interfaces:
            return path
    raise RuntimeError('Geen geschikte Bluetooth-adapter gevonden')

def main():
    global mainloop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus=dbus.SystemBus()
    adapter=find_adapter(bus)
    print('Bluetooth-adapter:',adapter,flush=True)
    app=Application(bus)
    advertisement=Advertisement(bus)
    host=os.environ.get('VDB_NODE_RED_HOST','127.0.0.1')
    port=int(os.environ.get('VDB_NODE_RED_PORT','5005'))
    retry=float(os.environ.get('VDB_TCP_RECONNECT_SECONDS','3'))

    def node_red_message(data):
        # D-Bus/GLib operations must run on the GLib main-loop thread.
        GLib.idle_add(app.services[0].tx.send,data)

    tcp=NodeRedTcpClient(host,port,node_red_message,reconnect_seconds=retry)
    app.services[0].rx.on_write=tcp.send
    gatt=dbus.Interface(bus.get_object(BLUEZ,adapter),GATT_MANAGER)
    advertising=dbus.Interface(bus.get_object(BLUEZ,adapter),ADV_MANAGER)
    mainloop=GLib.MainLoop()

    def advertising_registered():
        print('BLE-advertising actief: VantourerBridge',flush=True)

    def gatt_registered():
        print('GATT-service geregistreerd',flush=True)
        advertising.RegisterAdvertisement(advertisement.path,{},
            reply_handler=advertising_registered,
            error_handler=lambda e:print('Advertising-fout:',e,flush=True))

    def registration_error(error):
        print('GATT-registratiefout:',error,flush=True)
        mainloop.quit()

    gatt.RegisterApplication(app.get_path(),{},reply_handler=gatt_registered,
        error_handler=registration_error)

    def shutdown(signum,frame):
        print('Vantourer Display Bridge stopt...',flush=True)
        tcp.stop()
        mainloop.quit()

    signal.signal(signal.SIGINT,shutdown)
    signal.signal(signal.SIGTERM,shutdown)
    print('Vantourer Display Bridge start...',flush=True)
    print('Node-RED TCP-doel: {}:{}'.format(host,port),flush=True)
    tcp.start()
    try:
        mainloop.run()
    finally:
        tcp.stop()

if __name__=='__main__':
    main()
