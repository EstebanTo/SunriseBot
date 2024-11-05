import os
import psycopg2
from twitchio.ext import commands

# Datos de autenticación de Twitch
ACCESS_TOKEN = 'fvu2x9nhoh1d60wfv8ll4luf616imf'  # Reemplaza con tu token de acceso
CHANNEL = 'tangov91'  # Reemplazado por 'tangov91'

# Datos de conexión a la base de datos
DB_URL = "postgresql://postgres:dTzYsyMWvGLPIGZcfsVOFjPFGHmNaHtO@postgres.railway.internal:5432/railway"

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=ACCESS_TOKEN, prefix='!', initial_channels=[CHANNEL])
        self.commands_dict = {}  # Almacenamiento para los comandos
        self.load_commands()  # Cargar comandos de la base de datos
        self.register_admin_commands()  # Registrar comandos de administración

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
            print("Comandos obtenidos de la base de datos:")
            for nombre, respuesta in rows:
                print(f"Comando: {nombre}, Respuesta: {respuesta}")
                self.commands_dict[nombre] = respuesta  # Almacenar en el diccionario

                # Crear y registrar el comando
                async def command_response(ctx, respuesta=respuesta):
                    print(f"Ejecutando comando {nombre} con respuesta: {respuesta}")
                    await ctx.send(respuesta)

                self.add_command(commands.Command(name=nombre.lstrip('!'), func=command_response))
                print(f"Comando registrado: {nombre}")

            conn.close()
            print(f"Comandos registrados: {self.commands_dict}")  # Verificar los comandos registrados
        except Exception as e:
            print(f"Error al conectar a la base de datos: {str(e)}")

    def register_admin_commands(self):
        async def agregar_command(ctx, nombre: str, *, respuesta: str):
            try:
                conn = psycopg2.connect(DB_URL)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO comandos (nombre, respuesta) VALUES (%s, %s)", (nombre, respuesta))
                conn.commit()
                cursor.close()
                conn.close()
                
                # Agregar al diccionario local y registrar el nuevo comando
                self.commands_dict[nombre] = respuesta
                async def new_command_response(ctx, respuesta=respuesta):
                    await ctx.send(respuesta)

                self.add_command(commands.Command(name=nombre.lstrip('!'), func=new_command_response))
                await ctx.send(f"Comando '{nombre}' agregado con éxito. Respuesta: {respuesta}")
            except Exception as e:
                await ctx.send(f"Error al agregar el comando: {str(e)}")

        async def eliminar_command(ctx, nombre: str):
            try:
                conn = psycopg2.connect(DB_URL)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM comandos WHERE nombre = %s", (nombre,))
                conn.commit()
                cursor.close()
                conn.close()
                
                # Eliminar del diccionario local y desregistrar el comando
                if nombre in self.commands_dict:
                    del self.commands_dict[nombre]  # Eliminar del diccionario local
                    self.remove_command(nombre.lstrip('!'))  # Desregistrar el comando
                await ctx.send(f"Comando '{nombre}' eliminado con éxito.")
            except Exception as e:
                await ctx.send(f"Error al eliminar el comando: {str(e)}")

        # Registrar los comandos de administración
        self.add_command(commands.Command(name='agregar', func=agregar_command))
        self.add_command(commands.Command(name='eliminar', func=eliminar_command))
        print("Comandos de administración registrados.")

# Inicializar el bot
if __name__ == "__main__":
    bot = Bot()
    bot.run()
