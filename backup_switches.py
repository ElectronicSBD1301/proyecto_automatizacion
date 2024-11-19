# backup_switches.py

from netmiko import ConnectHandler
import json
import datetime
import os

# Crear directorio de backups si no existe
backup_dir = 'static/backups/'
os.makedirs(backup_dir, exist_ok=True)

# Cargar la lista de switches
with open('devices/switches.json') as f:
    switches = json.load(f)

fecha = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

for switch in switches:
    try:
        net_connect = ConnectHandler(**switch)
        net_connect.enable()  # Entra en modo privilegiado si es necesario
        output = net_connect.send_command('show running-config')
        filename = f"{backup_dir}{switch['host']}_{fecha}.cfg"
        with open(filename, 'w') as file:
            file.write(output)
        net_connect.disconnect()
        print(f"Backup exitoso para {switch['host']}: {filename}")
    except Exception as e:
        print(f"Error al conectar con {switch['host']}: {e}")
