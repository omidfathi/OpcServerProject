from asyncua import ua, uamethod, Server
import asyncio



async def create_database(server, tree_list):
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)
    print(tree_list)
    # print("/*/*/*/")
    for i in tree_list:
        rails = await server.nodes.objects.add_folder(idx, i['name'])
        for y in i['devices']:
            device = await rails.add_folder(idx, y['name'])
            for j in y['tags']:
                signal = await device.add_variable(idx, j['name'], ua.Float(0))
    print("Done")

