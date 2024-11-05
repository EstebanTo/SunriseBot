import os
import psycopg2
from twitchio.ext import commands

# Datos de autenticación de Twitch
ACCESS_TOKEN = 'fvu2x9nhoh1d60wfv8ll4luf616imf'  # Reemplaza con tu token de acceso
CHANNEL = 'tangov91'  # Reemplaza con tu canal

# Datos de conexión a la base de datos
DB_URL = "postgresql://usuario:contraseña@host:puerto/nombre_bd"  # Reemplaza con tus credenciales de PostgreSQL

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=ACCESS_TOKEN, prefix='!', initial_channels=[CHANNEL])
        self.load_commands()  # Cargar comandos de la base de datos

    async def event_ready(self):
        print(f'Logged in as {self.nick}')
        print(f'Connected to {CHANNEL}')

    async def event_message(self, message):
        if message.author:  # Verificar que el autor no sea None
            await self.handle_commands(message)

    def load_commands(self):
        try:
            conn = psycopg2.connect(DB_URL)
            cursor = conn.cursor()
            cursor.execute("SELECT nombre, respuesta FROM comandos")
            rows = cursor.fetchall()
            for nombre, respuesta in rows:
                self.add_command(commands.Command(name=nombre.lstrip('!'), func=lambda ctx, resp=respuesta: self.send_response(ctx, resp)))
            conn.close()
        except Exception as e:
            print(f"Error al conectar a la base de datos: {str(e)}")

    async def send_response(self, ctx, respuesta):
        await ctx.send(respuesta)

    @commands.command(name='agregar')
    async def agregar_comando(self, ctx, nombre: str, *, respuesta: str):
        try:
            conn = psycopg2.connect(DB_URL)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO comandos (nombre, respuesta) VALUES (%s, %s)", (nombre, respuesta))
            conn.commit()
            conn.close()
            self.add_command(commands.Command(name=nombre.lstrip('!'), func=lambda c: self.send_response(c, respuesta)))
            await ctx.send(f"Comando '{nombre}' agregado con éxito.")
        except Exception as e:
            await ctx.send(f"Error al agregar el comando: {str(e)}")

    @commands.command(name='editar')
    async def editar_comando(self, ctx, nombre: str, *, nueva_respuesta: str):
        try:
            conn = psycopg2.connect(DB_URL)
            cursor = conn.cursor()
            cursor.execute("UPDATE comandos SET respuesta = %s WHERE nombre = %s", (nueva_respuesta, nombre))
            conn.commit()
            conn.close()
            await ctx.send(f"Comando '{nombre}' editado con éxito.")
        except Exception as e:
            await ctx.send(f"Error al editar el comando: {str(e)}")

    @commands.command(name='eliminar')
    async def eliminar_comando(self, ctx, nombre: str):
        try:
            conn = psycopg2.connect(DB_URL)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM comandos WHERE nombre = %s", (nombre,))
            conn.commit()
            conn.close()
            await ctx.send(f"Comando '{nombre}' eliminado con éxito.")
        except Exception as e:
            await ctx.send(f"Error al eliminar el comando: {str(e)}")

# Inicializar el bot
if __name__ == "__main__":
    bot = Bot()
    bot.run()
