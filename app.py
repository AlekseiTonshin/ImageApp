from sanic import Sanic
from sanic.response import json
import gino
import asyncio
import aio_pika
from sanic_openapi import swagger_blueprint
from gino.ext.sanic import Gino
from sanic import response
import base64


app = Sanic("Image")


app.config.DB_HOST = 'localhost'
app.config.DB_PORT = '8000'
app.config.DB_DATABASE = 'Gino'
app.config.DB_USER = 'alekseit'
app.config.DB_PASSWORD = '76969879'
db = Gino()
db.init_app(app)


""" Работа с бд """
class User(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer(), primary_key=True)
    picture = db.Column(db.Text())


async def main():
    await db.set_bind('postgresql://localhost/gino')
    await db.gino.create_all()
    img_code = code_base64()
    user = await User.create(picture = img_code)


""" Кодирование изображения """
def code_base64():
    jpgtxt = base64.encodestring(open("py.jpeg","rb").read())
    f = open("jpg1_b64.txt", "wb")
    f.write(jpgtxt)
    f.close()
    return str(jpgtxt)[:-3].replace("'","").replace("b","",1).replace(" ","")

""" Запускаем кролика,с картинкой """
async def no_main(loop):
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/", loop=loop
    )
    with open("jpg1_b64.txt") as file:
        str_image = file.read()
    
    async with connection:
        routing_key = "images"

        channel = await connection.channel()

        await channel.default_exchange.publish(
            aio_pika.Message(str_image.encode()),
            routing_key=routing_key,
        )


@app.route("/api/image_ch", methods=['GET', 'POST'])
async def image_get(request):
    code_image = code_base64()
    return response.text(code_image)


""" Декодинг полученной измененной картинки """
def decode_base64():
    newpngtxt = open("png_b64.txt","rb").read()
    g = open("py.png", "wb")
    g.write(base64.decodestring(newpngtxt))
    g.close()
    return g


""" Картинка до изменений """
@app.route("/api/image_old", methods=['GET', 'POST'])
async def image_post(request):
    return await response.file('/home/alekseit/MyApp/py.jpeg')
    
""" Картинка после изменений """
@app.route("/api/image_new", methods=['GET', 'POST'])
async def image_post1(request):
    images = decode_base64()
    return await response.file('/home/alekseit/MyApp/py.png')
    # return images


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(no_main(loop))
    loop.close()
    app.run(host="0.0.0.0", port=8000)