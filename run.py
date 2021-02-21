from arena import *
from etl import load_uuid_data

# setup library
arena = Arena(host="arena.andrew.cmu.edu", realm="realm", scene="example")

@arena.run_async
async def func():
    # make a box
    box = Box(object_id="my_box", position=Position(0,4,-2), scale=Scale(2,2,2))
    arena.add_object(box)

    # create avatar/3d head
    model_url = "models/Court.glb"
    avatar = GLTF(object_id="court", url=model_url, position=Position(4,1.75,-1.5), scale=Scale(5,5,5))
    arena.add_object(avatar)

    def mouse_handler(evt):
        if evt.type == "mousedown":
            load_uuid_data()
            print('-'*20)
            print('BOX PRESSED')
            # box.data.position.x += 0.5
            # arena.update_object(box)

    # add click_listener
    arena.update_object(box, click_listener=True, evt_handler=mouse_handler)

    # sleep for 10 seconds
    await arena.sleep(10000)

# start tasks
arena.run_tasks()
