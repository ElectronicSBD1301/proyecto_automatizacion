# app.py

from flask import Flask, render_template, request, redirect, url_for
from netmiko import ConnectHandler
import json
import os

app = Flask(__name__)
app.config.from_pyfile('config.py')

# Cargar la lista de switches
with open(app.config['SWITCHES_FILE']) as f:
    switches = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vlans')
def vlans():
    vlan_info = []
    for switch in switches:
        try:
            net_connect = ConnectHandler(**switch)
            net_connect.enable()  # Entra en modo privilegiado si es necesario
            output = net_connect.send_command('show vlan brief')
            vlan_info.append({'host': switch['host'], 'output': output})
            net_connect.disconnect()
        except Exception as e:
            vlan_info.append({'host': switch['host'], 'output': f'Error: {e}'})
    return render_template('vlans.html', vlan_info=vlan_info)

@app.route('/add_vlan', methods=['GET', 'POST'])
def add_vlan():
    if request.method == 'POST':
        vlan_id = request.form['vlan_id']
        vlan_name = request.form['vlan_name']
        commands = [f'vlan {vlan_id}', f'name {vlan_name}']
        for switch in switches:
            try:
                net_connect = ConnectHandler(**switch)
                net_connect.enable()
                net_connect.send_config_set(commands)
                net_connect.disconnect()
            except Exception as e:
                return f'Error al conectar con {switch["host"]}: {e}', 500
        return redirect(url_for('vlans'))
    return render_template('add_vlan.html')

@app.route('/assign_vlan', methods=['GET', 'POST'])
def assign_vlan():
    if request.method == 'POST':
        vlan_id = request.form['vlan_id']
        port = request.form['port']
        commands = [
            f'interface {port}',
            f'switchport access vlan {vlan_id}',
            'exit'
        ]
        for switch in switches:
            try:
                net_connect = ConnectHandler(**switch)
                net_connect.enable()
                net_connect.send_config_set(commands)
                net_connect.disconnect()
            except Exception as e:
                return f'Error al conectar con {switch["host"]}: {e}', 500
        return redirect(url_for('vlans'))
    return render_template('assign_vlan.html')

@app.route('/backups')
def backups():
    backup_dir = app.config['BACKUP_DIR']
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    backup_files = os.listdir(backup_dir)
    return render_template('backups.html', backup_files=backup_files)

if __name__ == '__main__':
    app.run(debug=True)
