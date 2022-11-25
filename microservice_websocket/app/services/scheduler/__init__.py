from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ...config import config as Config
from ...services.database import Node
from ...utils.node import update_state
from ...utils.sync_cache import sync_cached


def init_scheduler():
    scheduler = AsyncIOScheduler()

    async def periodically_check_nodes():
        from ... import socketManager

        nodes: list[Node] = await Node.find_all().to_list()

        update_frontend = False

        for node in nodes:
            new_state = update_state(node.state, node.lastSeenAt)

            if node.state != new_state:
                update_frontend = True
                node.state = new_state
                await node.save()

        if update_frontend:
            print("Detected node-state change(s), emitting 'change'")
            await socketManager.emit("change-reading")
            await socketManager.emit("change")

    scheduler.add_job(
        periodically_check_nodes,
        "interval",
        id="update_state",
        seconds=Config.app.NODE_TIMEOUT_CHECK_INTERVAL,
    )

    async def periodically_sync_cache():
        await sync_cached()

    scheduler.add_job(
        periodically_sync_cache,
        "interval",
        id="sync_cache",
        seconds=Config.app.CHECK_SYNC_READY,
    )

    scheduler.start()
