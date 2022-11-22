# from socketio import Client
#
#
def init_socketio():
    from ... import socketManager

    #     socketio = Client()

    @socketManager.on("connect")
    async def connected():
        print("Connected")

    @socketManager.on("disconnect")
    async def disconnected():
        print("Disconnected")

    @socketManager.on("change")
    async def onChange():
        print("Changed")
