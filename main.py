import asyncio
import copy
import logging
from datetime import datetime
import time
from math import sin
from asyncio_mqtt import Client as ClientM
from asyncio_mqtt import MqttError
import json
from asyncua import ua, uamethod, Server
from idxSet import *
logger = logging.getLogger(__name__)
mqttTopic = [("TimeSync",1), ("Request_AP7_OPC_Tree",1), ("Response_AP7_OPC_Tree", 1)]

firstTime = True

async def test() -> None:
    # structPad = set_structure('>8sh')
    # structData = set_structure('<hffbb')
    # firstTime = True
    # timeSync = None
    # dataDict = {}
    firstTime = True
    tree_list = 0

    try:

        logger.info("Connecting to MQTT")

        async with ClientM(hostname="192.168.1.51", port=1883, client_id="OPC_server") as clientMqtt:
            logger.info("Connection to MQTT open")
            async with clientMqtt.unfiltered_messages() as messages:
                await clientMqtt.subscribe(mqttTopic)
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
                        server = Server()
                        await server.init()
                        server.set_endpoint("opc.tcp://0.0.0.0:4848/maadco/OPCserver/")
                        server.set_server_name("Maadco Example Server")
                        await create_database(server, tree_list)
                        async with server:
                            print("Available loggers are: ")
                            while True:
                                await asyncio.sleep(0.8)
                                print("Value Updated")
                    #     dataBase, opcServers = await create_database(message)
                    #     dataDict, client = await create_dataDict(dataBase)
                    #     logger.info(
                    #         "Message %s %s", message.topic, message.payload
                    #     )
                    # if message.topic == "Receive_OPC_Server":
                    #     bMessage = message.payload.decode('UTF-8')
                    #     # dataBase = json.loads(bMessage["send_opc_tag"])
                    #     client = await opcConnection(bMessage)
                    #     if client != 0:
                    #         nodesTree = await catchNodes(client)
                    #         await clientMqtt.publish('OPC_Server_Tree', nodesTree)
                    #         print("Tree Cached")
                    #     else:
                    #         clientMqtt.publish('OPC_Server_Tree', "")
                    #         print("Not Tree")
                    # if dataDict != {}:
                    #     dataDict = await get_values(dataDict, client)
                    #
                    #     value = []
                    #     percentt = []
                    #     id = []
                    #     for i in dataDict:
                    #         id.append(i)
                    #         if dataDict[i]["nodeList"] != []:
                    #             if dataDict[i]["values"][0] is None:
                    #                 value.append(00.00)
                    #                 dataDict[i]["percent"] = 00.00
                    #                 percentt.append(0.0)
                    #             else:
                    #                 value.append(dataDict[i]["values"][0])
                    #                 dataDict[i]["percent"] = percentage(dataDict[i]["VMX"], dataDict[i]["VMN"],
                    #                                                     dataDict[i]["values"])
                    #                 percentt.append(dataDict[i]["percent"][0])
                    #             dataDict[i]["timeStamp"] = timeSync
                    #             dataDict[i]['bufferSize'] = buffer_data_get_padding(structPad, dataDict[i]["bufferSize"], 0,
                    #                                                                 timeSync, 1)
                    #             # dataDict[i]['bufferSize'] = await buffer_data_get(structData, dataDict[i]["bufferSize"], i, dataDict[i])
                    #     values = {
                    #         "id": id,
                    #         "values": value,
                    #         "percent": percentt,
                    #         "buffer": estimate_buffer_size(len(value))
                    #     }
                    #     buffer = values["buffer"]
                    #     buffer_data_get_padding(structPad, buffer, 0, timeSync, len(value))
                    #     buffer_data_get(structData, buffer, values)
                    #     print(values["id"])
                    #     await clientMqtt.publish("omid_test_topic", payload=buffer)

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