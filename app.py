from flask import Flask, request, redirect, render_template_string, session, url_for
import requests
from bs4 import BeautifulSoup
import json
import random

app = Flask(__name__)
app.secret_key = "clave_secreta_de_salome"

# Cargar usuarios y mensajes desde archivos JSON
try:
    with open("usuarios.json", "r", encoding="utf-8") as f:
        usuarios = json.load(f)
except:
    usuarios = []

try:
    with open("mensajes.json", "r", encoding="utf-8") as f:
        mensajes = json.load(f)
except:
    mensajes = []

# Lista de avatares predefinidos (animales, plantas, etc.)
avatares = [
    "🦁", "🐯", "🐼", "🦊", "🐨", "🐸", "🐵", "🐢", "🦋", "🌻", "🌼", "🌸", "🌿", "🍄"
]

def obtener_avatar():
    usados = [u.get("avatar") for u in usuarios]
    disponibles = [a for a in avatares if a not in usados]
    return random.choice(disponibles) if disponibles else random.choice(avatares)

def guardar_datos():
    with open("usuarios.json", "w", encoding="utf-8") as f:
        json.dump(usuarios, f)
    with open("mensajes.json", "w", encoding="utf-8") as f:
        json.dump(mensajes, f)

def buscar_noticias_html(palabra):
    fuentes = [
        f"https://www.bing.com/news/search?q={palabra}&cc=es",
        f"https://www.eltiempo.com/buscar/{palabra}",
        f"https://www.bbc.com/mundo/search?q={palabra}"
    ]
    resultados = []
    for url in fuentes:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            noticias = soup.find_all('a', class_='title')
            for n in noticias[:2]:
                titulo = n.get_text()
                enlace = n['href']
                resultados.append({'titulo': titulo, 'enlace': enlace})
        except:
            continue
    return resultados

html_template = """
<!DOCTYPE html>
<html lang=\"es\">
<head>
    <meta charset=\"UTF-8\">
    <title>Mi Mundo Salomé</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f3e8d7;
            padding: 20px;
        }
        header {
            background-color: white;
            color: black;
            padding: 20px;
            text-align: center;
            border-radius: 16px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            border-bottom: 2px solid #e0e0e0;
            font-family: 'Georgia', 'Palatino Linotype', serif;
            font-style: italic;
            position: relative;
        }
        header img {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            position: absolute;
            left: 20px;
            top: 20px;
        }
        .logout {
            position: absolute;
            top: 20px;
            right: 20px;
        }
        .logout a {
            background-color: #4CAF50;
            color: white;
            padding: 8px 16px;
            border-radius: 8px;
            text-decoration: none;
            font-size: 14px;
        }
        main {
            background: #ffffffcc;
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
            max-width: 500px;
            margin: 20px auto;
        }
        input, button, select {
            margin: 8px 0;
            padding: 12px;
            font-size: 16px;
            border-radius: 10px;
            border: 1px solid #ccc;
            width: 100%;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #45a049;
        }
        section {
            margin-top: 20px;
        }
        h2, h3, p, li, label {
            color: #333;
        }
        ul {
            padding-left: 20px;
        }
        a {
            color: #4a4a4a;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        #chat-boton {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        #chat-ventana {
            display: none;
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 320px;
            background-color: #ffffffee;
            border: 1px solid #ddd;
            border-radius: 16px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
            padding: 15px;
            z-index: 100;
        }
        #chat-box {
            background: #f0f0f0;
            padding: 10px;
            border-radius: 10px;
            max-height: 200px;
            overflow-y: auto;
            margin-bottom: 10px;
        }
    </style>
    <script>
        function toggleChat() {
            var chat = document.getElementById("chat-ventana");
            chat.style.display = chat.style.display === "none" ? "block" : "none";
        }
    </script>
</head>
<body>
    <header>
        <img src="https://cdn-icons-png.flaticon.com/512/616/616408.png" alt="logo natural">
        <h1>Bienvenidos a Mi Mundo Salomé 🌍</h1>
        {% if session.get('usuario') %}
        <div class="logout">
            <a href="{{ url_for('logout') }}">Cerrar sesión</a>
        </div>
        {% endif %}
    </header>

    {% if not session.get('usuario') %}
    <main>
        <h2>Registro</h2>
        <form action="/registro" method="POST">
            <input type="text" name="nombre" placeholder="Tu nombre" required>
            <input type="email" name="correo" placeholder="Correo electrónico" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <label>Elige un color favorito:</label>
            <input type="color" name="color" required>
            <button type="submit">Registrarse</button>
        </form>
        <h2>Iniciar Sesión</h2>
        <form action="/login" method="POST">
            <input type="email" name="correo" placeholder="Correo electrónico" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <button type="submit">Entrar</button>
        </form>
    </main>
    {% else %}
    <main>
        <p><strong>Hola {{ session['usuario'] }} 👋</strong></p>
        <form action="/buscar" method="POST" style="text-align: center;">
            <input type="text" name="tema" placeholder="Buscar noticias del mundo..." style="width: 60%;">
            <button type="submit">Buscar</button>
        </form>
        {% if noticias %}
        <section>
            <h2>Resultados de noticias:</h2>
            <ul>
                {% for n in noticias %}
                    <li><a href="{{ n.enlace }}" target="_blank">{{ n.titulo }}</a></li>
                {% endfor %}
            </ul>
        </section>
        {% endif %}
        <section>
            <h3>Personas registradas:</h3>
            <ul>
                {% for u in usuarios %}
                    <li>{{ u.avatar }} {{ u.nombre }}</li>
                {% endfor %}
            </ul>
        </section>
        <button id="chat-boton" onclick="toggleChat()">💬</button>
        <div id="chat-ventana">
            <h3>Chat grupal</h3>
            <div id="chat-box">
                {% for m in mensajes %}
                    <p><strong style="color: {{ m.color }}">{{ m.nombre }}:</strong> {{ m.texto }}</p>
                {% endfor %}
            </div>
            <form action="/mensaje" method="POST">
                <input type="text" name="mensaje" placeholder="Escribe tu mensaje...">
                <button type="submit">Enviar</button>
            </form>
        </div>
    </main>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def inicio():
    return render_template_string(html_template, usuarios=usuarios, mensajes=mensajes, noticias=[])

@app.route("/registro", methods=["POST"])
def registro():
    nombre = request.form["nombre"]
    correo = request.form["correo"]
    password = request.form["password"]
    color = request.form["color"]
    avatar = obtener_avatar()
    session['usuario'] = nombre
    if not any(u['correo'] == correo for u in usuarios):
        usuarios.append({"nombre": nombre, "correo": correo, "password": password, "color": color, "avatar": avatar})
        guardar_datos()
    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    correo = request.form["correo"]
    password = request.form["password"]
    for u in usuarios:
        if u['correo'] == correo and u['password'] == password:
            session['usuario'] = u['nombre']
            return redirect("/")
    return "Correo o contraseña incorrectos. <a href='/'>Volver</a>"

@app.route("/logout")
def logout():
    session.pop('usuario', None)
    return redirect("/")

@app.route("/mensaje", methods=["POST"])
def mensaje():
    texto = request.form["mensaje"]
    nombre = session.get("usuario")
    if nombre and texto.strip() != "":
        color = next((u["color"] for u in usuarios if u["nombre"] == nombre), "#000000")
        mensajes.append({"nombre": nombre, "texto": texto, "color": color})
        guardar_datos()
    return redirect("/")

@app.route("/buscar", methods=["POST"])
def buscar():
    if not session.get('usuario'):
        return redirect("/")
    palabra = request.form["tema"]
    resultados = buscar_noticias_html(palabra)
    return render_template_string(html_template, usuarios=usuarios, mensajes=mensajes, noticias=resultados)

if __name__ == "__main__":
    app.run(debug=True)
