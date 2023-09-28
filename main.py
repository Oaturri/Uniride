from flask import Flask, request, jsonify, render_template, session
from flask_session import Session  # Importa la extensión Flask-Session

# Modelos
class Usuario:
    def __init__(self, nombre_usuario, contraseña):
        self.nombre_usuario = nombre_usuario
        self.contraseña = contraseña
        self.saldo = 0

usuarios = {
    "usuarioEjemplo": Usuario("usuarioEjemplo", "contraseñaEjemplo")
}

class Viaje:
    def __init__(self, hora, lugar_salida, placa, color_carro, cupos, inicio_recorrido, fin_recorrido):
        global id_viaje
        self.id = id_viaje
        self.hora = hora
        self.lugar_salida = lugar_salida
        self.placa = placa
        self.color_carro = color_carro
        self.cupos = cupos
        self.inicio_recorrido = inicio_recorrido
        self.fin_recorrido = fin_recorrido
        id_viaje += 1

viajes = []
id_viaje = 0  # Identificador único para cada viaje

# Aplicación principal
class MainApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'una_clave_secreta'

        # Configura Flask-Session para almacenar sesiones en cookies
        self.app.config['SESSION_TYPE'] = 'filesystem'  # Puedes cambiarlo para usar cookies
        Session(self.app)

        self.registrar_rutas()

    def registrar_rutas(self):
        @self.app.route('/')
        def inicio():
            return render_template('publicar_viaje.html')

        @self.app.route('/publicar_viaje', methods=['POST'])
        def publicar_viaje():
            hora = request.form.get('hora')
            lugar_salida = request.form.get('lugar_salida')
            placa = request.form.get('placa')
            color_carro = request.form.get('color_carro')
            cupos = int(request.form.get('cupos'))
            inicio_recorrido = request.form.get('inicio_recorrido')
            fin_recorrido = request.form.get('fin_recorrido')
            viaje = Viaje(hora, lugar_salida, placa, color_carro, cupos, inicio_recorrido, fin_recorrido)
            viajes.append(viaje)
            return jsonify({"exito": "Viaje publicado con éxito!"})

        @self.app.route('/reservar/<int:id>', methods=['POST'])
        def reservar(id):
            viaje = next((v for v in viajes if v.id == id), None)
            if not viaje:
                return jsonify({"error": "Viaje no encontrado."}), 404
            if viaje.cupos <= 0:
                return jsonify({"error": "No hay cupos disponibles."}), 400
            viaje.cupos -= 1
            if viaje.cupos == 0:
                viajes.remove(viaje)
            return jsonify({"exito": "Cupo reservado con éxito!"})

        @self.app.route('/listar_viajes', methods=['GET'])
        def listar_viajes():
            viajes_json = [{"id": v.id, "hora": v.hora, "lugar_salida": v.lugar_salida, "placa": v.placa,
                            "color_carro": v.color_carro, "cupos": v.cupos, "inicio_recorrido": v.inicio_recorrido,
                            "fin_recorrido": v.fin_recorrido} for v in viajes]
            return jsonify(viajes_json)

        # Ruta para el inicio de sesión
        @self.app.route('/login', methods=['POST'])
        def login():
             nombre_usuario = request.form.get('nombre_usuario')
             contraseña = request.form.get('contraseña')
             usuario = usuarios.get(nombre_usuario)
    
             if usuario and usuario.contraseña == contraseña:
                   # Almacena el nombre de usuario en la sesión (y la cookie)
                   session['nombre_usuario'] = nombre_usuario
                   return jsonify({"exito": "Inicio de sesión exitoso."})
             else:
                   return jsonify({"error": "Nombre de usuario o contraseña incorrectos."}), 401

        @self.app.route('/saldo', methods=['GET'])
        def saldo():
            nombre_usuario = session.get('nombre_usuario')
            if not nombre_usuario:
                return jsonify({"error": "No has iniciado sesión."}), 401
            return jsonify({"saldo": usuarios[nombre_usuario].saldo})

        @self.app.route('/agregar_saldo', methods=['POST'])
        def agregar_saldo():
            nombre_usuario = session.get('nombre_usuario')
            if not nombre_usuario:
                return jsonify({"error": "No has iniciado sesión."}), 401
            monto = float(request.form.get('monto'))
            usuarios[nombre_usuario].saldo += monto
            return jsonify({"exito": f"Se agregaron ${monto} a tu billetera."})

        @self.app.route('/retirar_saldo', methods=['POST'])
        def retirar_saldo():
            nombre_usuario = session.get('nombre_usuario')
            if not nombre_usuario:
                return jsonify({"error": "No has iniciado sesión."}), 401
            monto = float(request.form.get('monto'))
            if monto > usuarios[nombre_usuario].saldo:
                return jsonify({"error": "No tienes suficiente saldo para retirar esa cantidad."}), 400
            usuarios[nombre_usuario].saldo -= monto
            return jsonify({"exito": f"Se retiraron ${monto} de tu billetera."})

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    app = MainApp()
    app.run()
