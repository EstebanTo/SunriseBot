import os
import psycopg2
from twitchio.ext import commands

# Datos de autenticación de Twitch
ACCESS_TOKEN = 'fvu2x9nhoh1d60wfv8ll4luf616imf'  # Reemplaza con tu token de acceso
CHANNEL = 'tangov91'  # Reemplazado por 'tangov91'

# Datos de conexión a la base de datos
DB_URL = "postgresql://postgres:dTzYsyMWvGLPIGZcfsVOFjPFGHmNaHtO@postgres.railway.internal:5432/railway"

# Inicialización del bot
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=ACCESS_TOKEN, prefix='!', initial_channels=[CHANNEL])
        self.commands_dict = {}
        self.load_commands()  # Cargar comandos de la base de datos
        self.register_test_command()  # Registrar un comando de prueba

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
                self.commands_dict[nombre] = respuesta
                
                # Registrar el comando directamente en el bot
                self.add_command(commands.Command(name=nombre, func=self.create_command_function(respuesta)))
                print(f"Comando registrado: {nombre}")

            conn.close()
            print(f"Comandos registrados: {self.commands_dict}")  # Verificar los comandos registrados
        except Exception as e:
            print(f"Error al conectar a la base de datos: {str(e)}")

    def create_command_function(self, respuesta):
        async def command_response(ctx):
            print(f"Ejecutando comando, se envía respuesta: {respuesta}")  # Mensaje de depuración
            await ctx.send(respuesta)
        return command_response

    def register_test_command(self):
        # Registro de un comando de prueba directamente
        async def test_command(ctx):
            await ctx.send("¡Comando de prueba ejecutado correctamente!")
        self.add_command(commands.Command(name='test', func=test_command))

# Inicializar el bot
if __name__ == "__main__":
    bot = Bot()
    bot.run()
