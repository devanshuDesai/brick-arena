from arena import *
from etl import load_uuid_data
from fault_detect import check_if_consistent

# setup library
arena = Arena(host="arena.andrew.cmu.edu", realm="realm", scene="example2")

@arena.run_async
async def func():

    # make a box
    box_1 = Box(object_id="rm-2126", position=Position(0,4,-2), scale=Scale(2,2,2), color='#FF0000')
    box_2 = Box(object_id="rm-1231", position=Position(6,4,-2), scale=Scale(2,2,2), color='#FFFF00')
    box_3 = Box(object_id="rm-2136", position=Position(12,4,-2), scale=Scale(2,2,2), color='#00FF00')

    arena.add_object(box_1)
    arena.add_object(box_2)
    arena.add_object(box_3)

    def mouse_handler(evt):
        # TODO: Get input value from ARENA directly
        rooms_dict = {
            "rm-2126": 540,
            "rm-1231": 650,
            "rm-2136": 215,
            "rm-3130": 540
        }
        if evt.type == "mousedown":
            check_if_consistent({evt.object_id: rooms_dict[evt.object_id]})

    # add click_listener
    arena.update_object(box_1, click_listener=True, evt_handler=mouse_handler)
    arena.update_object(box_2, click_listener=True, evt_handler=mouse_handler)
    arena.update_object(box_3, click_listener=True, evt_handler=mouse_handler)

    # sleep for 10 seconds
    await arena.sleep(10000)

# start tasks
arena.run_tasks()
