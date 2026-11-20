#!/usr/bin/env python3

import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import signal

BLUEZ = 'org.bluez'
OM = 'org.freedesktop.DBus.ObjectManager'
PROP = 'org.freedesktop.DBus.Properties'
GATT_MANAGER = 'org.bluez.GattManager1'
ADV_MANAGER = 'org.bluez.LEAdvertisingManager1'
SERVICE_IFACE = 'org.bluez.GattService1'
CHAR_IFACE = 'org.bluez.GattCharacteristic1'
ADV_IFACE = 'org.bluez.LEAdvertisement1'

SERVICE_UUID = '8f7a0001-6d5b-4c3a-9e2f-1a0b2c3d4e5f'
TX_UUID = '8f7a0002-6d5b-4c3a-9e2f-1a0b2c3d4e5f'
RX_UUID = '8f7a0003-6d5b-4c3a-9e2f-1a0b2c3d4e5f'

mainloop = None


class Characteristic(dbus.service.Object):

    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.path + '/char' + str(index)
        self.uuid = uuid
        self.flags = flags
        self.service = service
        self.value = []
        self.notifying = False
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_properties(self):
        return {
            CHAR_IFACE: {
                'Service': self.service.get_path(),
                'UUID': self.uuid,
                'Flags': dbus.Array(self.flags, signature='s'),
                'Descriptors': dbus.Array([], signature='o')
            }
        }

    @dbus.service.method(PROP, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != CHAR_IFACE:
            raise dbus.exceptions.DBusException('Invalid interface')
        return self.get_properties()[CHAR_IFACE]

    @dbus.service.method(CHAR_IFACE, in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        return dbus.Array(self.value, signature='y')

    @dbus.service.method(CHAR_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        data = bytes(value)
        print('ESP32 -> Pi:', data.hex(), repr(data), flush=True)

    @dbus.service.method(CHAR_IFACE)
    def StartNotify(self):
        self.notifying = True
        print('ESP32 heeft notifications ingeschakeld', flush=True)

    @dbus.service.method(CHAR_IFACE)
    def StopNotify(self):
        self.notifying = False
        print('ESP32 heeft notifications uitgeschakeld', flush=True)

    @dbus.service.signal(PROP, signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass

    def send(self, data):
        self.value = [dbus.Byte(b) for b in data]
        if self.notifying:
            self.PropertiesChanged(
                CHAR_IFACE, {'Value': self.value}, [])

class Service(dbus.service.Object):

    def __init__(self, bus, index):
        self.path = '/com/vantourer/bridge/service' + str(index)
        self.uuid = SERVICE_UUID
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

        self.tx = Characteristic(bus, 0, TX_UUID, ['notify'], self)
        self.rx = Characteristic(bus, 1, RX_UUID, ['write'], self)
        self.characteristics.extend([self.tx, self.rx])

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_characteristics(self):
        return self.characteristics

    def get_properties(self):
        return {
            SERVICE_IFACE: {
                'UUID': self.uuid,
                'Primary': dbus.Boolean(True),
                'Characteristics': dbus.Array(
                    [c.get_path() for c in self.characteristics],
                    signature='o')
            }
        }

    @dbus.service.method(PROP, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != SERVICE_IFACE:
            raise dbus.exceptions.DBusException('Invalid interface')
        return self.get_properties()[SERVICE_IFACE]


class Application(dbus.service.Object):

    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        self.services.append(Service(bus, 0))

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(OM, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        result = {}
        for service in self.services:
            result[service.get_path()] = service.get_properties()
            for characteristic in service.get_characteristics():
                result[characteristic.get_path()] = (
                    characteristic.get_properties())
        return result


class Advertisement(dbus.service.Object):

    def __init__(self, bus):
        self.path = '/com/vantourer/bridge/advertisement0'
        dbus.service.Object.__init__(self, bus, self.path)

    @dbus.service.method(PROP, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != ADV_IFACE:
            raise dbus.exceptions.DBusException('Invalid interface')
        return {
            'Type': 'peripheral',
            'ServiceUUIDs': dbus.Array([SERVICE_UUID], signature='s'),
            'LocalName': 'VantourerBridge'
        }

    @dbus.service.method(ADV_IFACE)
    def Release(self):
        print('BLE-advertentie vrijgegeven', flush=True)


def find_adapter(bus):
    manager = dbus.Interface(bus.get_object(BLUEZ, '/'), OM)
    for path, interfaces in manager.GetManagedObjects().items():
        if GATT_MANAGER in interfaces and ADV_MANAGER in interfaces:
            return path
    raise RuntimeError('Geen geschikte Bluetooth-adapter gevonden')


def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    adapter = find_adapter(bus)

    print('Bluetooth-adapter:', adapter, flush=True)

    app = Application(bus)
    advertisement = Advertisement(bus)

    gatt = dbus.Interface(
        bus.get_object(BLUEZ, adapter), GATT_MANAGER)
    advertising = dbus.Interface(
        bus.get_object(BLUEZ, adapter), ADV_MANAGER)

    mainloop = GLib.MainLoop()

    def advertising_registered():
        print('BLE-advertising actief: VantourerBridge', flush=True)

    def gatt_registered():
        print('GATT-service geregistreerd', flush=True)
        advertising.RegisterAdvertisement(
            advertisement.path, {},
            reply_handler=advertising_registered,
            error_handler=lambda e: print('Advertising-fout:', e, flush=True))

    def registration_error(error):
        print('GATT-registratiefout:', error, flush=True)
        mainloop.quit()

    gatt.RegisterApplication(
        app.get_path(), {},
        reply_handler=gatt_registered,
        error_handler=registration_error)

    signal.signal(signal.SIGINT, lambda s, f: mainloop.quit())
    signal.signal(signal.SIGTERM, lambda s, f: mainloop.quit())

    print('Vantourer Display Bridge start...', flush=True)
    mainloop.run()


if __name__ == '__main__':
    main()
