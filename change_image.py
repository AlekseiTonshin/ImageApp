import PIL
from PIL import Image
import sys
import base64
import asyncio
import aio_pika


async def no_main(loop):
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/", loop=loop
    )

    queue_name = "images"

    async with connection:
        # Creating channel
        channel = await connection.channel()

        # Declaring queue
        queue = await channel.declare_queue(queue_name, auto_delete=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    image_code = str(message.body).replace("'","").replace("b","",1).replace(" ","")
                    #  print(image_code)
                    return image_code


def uncode_image():
    #    newjpgtxt = open("jpg1_b64.txt","rb").read()
    newjpgtxt = no_main(loop)
    g = open("py.jpeg", "wb")
    g.write(base64.decodebytes(newjpgtxt))
    g.close()

# with open("jpg1_b64.txt") as file:
#     int_number = file.read()
#     print(int_number)


def resize_image(input_image_path,
                 output_image_path,
                 size):
    original_image = Image.open(input_image_path)
    width, height = original_image.size
    print('The original image size is {wide} wide x {height} '
          'high'.format(wide=width, height=height))
 
    resized_image = original_image.resize(size)
    width, height = resized_image.size
    print('The resized image size is {wide} wide x {height} '
          'high'.format(wide=width, height=height))
    # resized_image.show()
    resized_image.save(output_image_path)

def save():
    try:
        pyt = Image.open("py1.jpeg")
    except IOError:
        print("Unable to load image")
        sys.exit(1)
    pyt.save('py.png', 'png')


def coding():
    pngtxt = base64.encodestring(open("py.png","rb").read())
    f = open("png_b64.txt", "wb")
    f.write(pngtxt)
    f.close()

# pyt.show()
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(no_main(loop))
    loop.close()
    uncode_image()
    resize_image(input_image_path='py.jpeg',
                 output_image_path='py1.jpeg',
                 size=(100, 50))
    save()
    coding()