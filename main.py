import asyncio
import copy
import logging
import struct
from datetime import datetime
import time
from math import sin
from asyncio_mqtt import Client as ClientM
from asyncio_mqtt import MqttError
from struct import *
import json
from asyncua import ua, uamethod, Server
from idxSet import *

logger = logging.getLogger(__name__)
mqttTopic = [("TimeSync",1), ("Request_AP7_OPC_Tree",1), ("Response_AP7_OPC_Tree", 1), ("Redis_Archive_topic", 1)]

firstTime = True
device_id = {}
async def server_initial():
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4848/maadco/OPCserver/")
    server.set_server_name("Maadco Example Server")
    print("server RUN")
    logger.info("Connecting to MQTT")
    return server

async def data_rec_mqtt(clientMqtt, device_id):
    async with clientMqtt.filtered_messages("Redis_Archive_topic") as messages:
        async for message in messages:

            print("Archive")
            data_buffer = message.payload
            # print(len(data_buffer))
            # print(data_buffer[3])
            data_buffer_dict = {
                "serial": struct.unpack_from("h", data_buffer, 0),
                "status": struct.unpack_from("b", data_buffer, 2),
                "time": struct.unpack_from(">6bh", data_buffer, 3),
                "device_count": struct.unpack_from("b", data_buffer, 11),
            }
            for i in range(data_buffer_dict["device_count"][0]):
                a = struct.unpack_from("b", data_buffer, 12 + i * 2)
                b = struct.unpack_from("b", data_buffer, 13+i*2)
                devices = {
                    a[0]: b[0]
                }
                device_id.update(devices)
                # 12 + (2*57)

                # print(struct.unpack_from("b", data_buffer, 12+i*2))
                # print(struct.unpack_from("b", data_buffer, 13+i*2))
                # device_id["id"] + struct.unpack_from("b", data_buffer, 12+i)
                # device_id["status"] + struct.unpack_from("b", data_buffer, 13+i)
                # devices_id.update = {
                #     "id":struct.unpack_from("b", data_buffer, 12+i),
                #     "status": struct.unpack_from("b", data_buffer, 13+i),
                # }
            # print(data_buffer_dict)
            print(device_id)
            return data_buffer

async def test() -> None:
    # structPad = set_structure('>8sh')
    # structData = set_structure('<hffbb')
    # firstTime = True
    # timeSync = None
    # dataDict = {}
    firstTime = True
    tree_list = 0
    server = 0
    try:

        async with ClientM(hostname="192.168.1.51", port=1883, client_id="OPC_server") as clientMqtt:
            await clientMqtt.subscribe(mqttTopic)
            logger.info("Connection to MQTT open")
            async with clientMqtt.unfiltered_messages() as messages:
                async for message in messages:
                    if message.topic == "TimeSync":
                        timeSync = message.payload
                        print(timeSync)
                    if firstTime:
                        await clientMqtt.publish("Request_AP7_OPC_Tree", payload="")
                        print("publish_ready")
                        wait_tree = True
                        if message.topic == "Response_AP7_OPC_Tree":
                            firstTime = False
                            print("get_tree")
                            tree = message.payload.decode('UTF-8')
                            tree_list = json.loads(tree)


                    if tree_list != 0:

                        server = await server_initial()
                        await create_database(server, tree_list)
                        if server !=0:
                            async with server:
                                while True:
                                    data = await data_rec_mqtt(clientMqtt, device_id)
                                    # print(struct.unpack("h7bhb2bh", data))
                                    await asyncio.sleep(0.8)



            await asyncio.sleep(2)
    except MqttError as e:
        logger.error("Connection to MQTT closed: " + str(e))
    except Exception:
        logger.exception("Connection to MQTT closed")
    await asyncio.sleep(3)


clientMqtt = None
# set_connection = True
server_state = True


def main(server_state):
    clientMqtt = asyncio.SelectorEventLoop().run_until_complete(asyncio.wait([test()]))

    # await data_catchSend(clientMqtt, server_state)



if __name__ == "__main__":
    try:
        set_connection = True

        main(server_state)
        # asyncio.run(main(server_state))
        # asyncio.run(checkMessageFrom(q))


        # loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Closing Loop")
        for i in range(3):
            time.sleep(1)
            print(f"Reconnect to Server in {3 - i} ...")
        # mqtt_disconnect(clientMqtt)
        main(server_state)