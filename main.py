import wifimgr
import machine
import network
import ubinascii
import utime
import json
from umqtt.simple import MQTTClient
import bme280

def get_ip():
    sta_if = network.WLAN(network.STA_IF)
    return sta_if.ifconfig()[0]

while True:

    print("Network...")

    connected = False

    # Ensure Wifi is connected

    try:
        wlan = wifimgr.get_connection()
    
        connected = True

    except Exception as ex:
        print(ex)
        connected = False

    if connected:

        try:
    
            # Create an I2C object out of our SDA and SCL pin objects

            print("Initializing i2c...")

            i2c = machine.I2C(sda=machine.Pin(21), scl=machine.Pin(22))

            print("Getting bme280 values...")

            bme = bme280.BME280(i2c=i2c, address=0x77)

            # Send MQTT Data

            print("Sending bme280 values to MQTT...")

            client_id = ubinascii.hexlify(machine.unique_id())

            temperature, pressure, humidity = bme.read_compensated_data()

            pressure = pressure // 256
            pi = pressure // 100
            pd = pressure - pi * 100

            hi = humidity // 1024
            hd = humidity * 100 // 1024 - hi * 10

            payload = dict(
                    temperature=temperature/100,
                    humidity="{}.{:02d}".format(hi, hd),
                    pressure="{}.{:02d}".format(pi, pd)
                )

            topic = "/pieter-room/sensor"

            message = bytes(json.dumps(payload), "utf-8")

            client = MQTTClient(client_id=client_id, server="10.0.1.200", user="mqtt", password="hassio")

            client.connect()

            client.publish(topic=topic, msg=message)

            client.disconnect()

        except Exception as ex:

            print(ex)


    utime.sleep(300)