import os
import psycopg2
from twitchio.ext import commands

# Datos de autenticación de Twitch
ACCESS_TOKEN = 'fvu2x9nhoh1d60wfv8ll4luf616imf'  # Reemplaza con tu token de acceso
CHANNEL = 'tangov91'  # Reemplaza con tu canal de Twitch

# Datos de conexión a la base de datos
DB_URL = "postgresql://postgres:dTzYsyMWvGLPIGZcfsVOFjPFGHmNaHtO@postgres.railway.internal:5432/railway"

# Inicialización del bot
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=ACCESS_TOKEN, prefix='!', initial_channels=[CHANNEL])
        self.commands_dict = {}
        self.load_commands()

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
                self.add_command(commands.Command(name=nombre, func=self.create_command_response(nombre)))
                
            conn.close()
        except Exception as e:
            print(f"Error al conectar a la base de datos: {str(e)}")

    def create_command_response(self, command):
        async def command_response(ctx):
            # Enviar la respuesta directamente desde el diccionario
            if command in self.commands_dict:
                print(f"Ejecutando comando: {command} con respuesta: {self.commands_dict[command]}")
                await ctx.send(self.commands_dict[command])
            else:
                print(f"No se encontró el comando: {command}")
                await ctx.send(f"No tengo una respuesta para el comando '{command}'.")
        return command_response

    def is_moderator(self, ctx):
        return ctx.author.is_mod

    @commands.command(name='agregar')
    async def agregar_comando(self, ctx, comando: str, *, respuesta: str):
        if self.is_moderator(ctx):
            try:
                conn = psycopg2.connect(DB_URL)
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO comandos (nombre, respuesta) VALUES (%s, %s)", (comando, respuesta))
                    self.commands_dict[comando] = respuesta
                    
                    # Mensaje de depuración
                    print(f"Agregando comando '{comando}' con respuesta '{respuesta}'")

                    # Registrar el nuevo comando en el bot
                    self.add_command(commands.Command(name=comando, func=self.create_command_response(comando)))

                    # Imprimir el contenido del diccionario de comandos
                    print(f"Comandos registrados: {self.commands_dict}")

                    await ctx.send(f"Comando '{comando}' agregado con éxito.")
                conn.commit()
            except psycopg2.IntegrityError:
                await ctx.send(f"El comando '{comando}' ya existe.")
            except Exception as e:
                await ctx.send(f"Ocurrió un error al agregar el comando: {str(e)}")
            finally:
                conn.close()

    @commands.command(name='editar')
    async def editar_comando(self, ctx, comando: str, *, nueva_respuesta: str):
        if self.is_moderator(ctx):
            try:
                conn = psycopg2.connect(DB_URL)
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE comandos SET respuesta = %s WHERE nombre = %s", (nueva_respuesta, comando))
                    if cursor.rowcount > 0:
                        self.commands_dict[comando] = nueva_respuesta
                        await ctx.send(f"Comando '{comando}' editado con éxito.")
                    else:
                        await ctx.send(f"El comando '{comando}' no existe.")
            finally:
                conn.close()

    @commands.command(name='eliminar')
    async def eliminar_comando(self, ctx, comando: str):
        if self.is_moderator(ctx):
            try:
                conn = psycopg2.connect(DB_URL)
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM comandos WHERE nombre = %s", (comando,))
                    if cursor.rowcount > 0:
                        del self.commands_dict[comando]
                        self.remove_command(comando)
                        await ctx.send(f"Comando '{comando}' eliminado con éxito.")
                    else:
                        await ctx.send(f"El comando '{comando}' no existe.")
            finally:
                conn.close()

# Inicializar el bot
if __name__ == "__main__":
    bot = Bot()
    bot.run()
