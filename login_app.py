import streamlit as st
from streamlit_lottie import st_lottie
import pandas as pd
import bcrypt
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials
import json
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt


# Configuración de Google Sheets
def connect_to_google_sheets():
   """
   Conecta con Google Sheets usando Google-auth y gspread.
   """
   # Define el alcance de las APIs de Google
   scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
  
   # Carga las credenciales desde el archivo JSON
   creds = Credentials.from_service_account_file(
       "credible-datum-442414-s7-9884e655f763.json", scopes=scope
   )
   client = gspread.authorize(creds)
  
   # Abre la hoja de cálculo usando su URL
   workbook = client.open_by_url("https://docs.google.com/spreadsheets/d/1qWLv0qu59X4dyjz8kdctHy-V2AhkO7ZUB7rVOC8mYfo/edit?gid=0")
   return workbook


# Cargar animación Lottie desde un archivo o URL
def load_lottie_animation(file_path=None, url=None):
   if file_path:
       with open(file_path, "r") as f:
           return json.load(f)
   elif url:
       import requests
       r = requests.get(url)
       if r.status_code == 200:
           return r.json()
   return None


# Cargar las credenciales desde Google Sheets
def load_credentials_from_google_sheets():
   try:
       workbook = connect_to_google_sheets()
       sheet = workbook.worksheet("credenciales")  # Cambiado a "credenciales"
       data = sheet.get_all_records()
       if not data:
           st.warning("La hoja de Google Sheets 'credenciales' está vacía o no tiene datos válidos.")
       return pd.DataFrame(data)
   except Exception as e:
       st.error(f"Error al cargar credenciales desde Google Sheets: {e}")
       return pd.DataFrame()


# Función para verificar las credenciales
def verify_credentials(username, password, credenciales_df):
   credenciales_df['hashed_password'] = credenciales_df['hashed_password'].astype(str)
   user_data = credenciales_df[credenciales_df['username'] == username]
  
   if not user_data.empty:
       stored_hash = user_data['hashed_password'].values[0]
       try:
           if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
               return True, user_data
           else:
               st.error("Contraseña incorrecta")
       except ValueError:
           st.error(f"Error en el hash para el usuario: {username}.")
   return False, None


# Función para guardar interacciones en dos hojas diferentes
def save_interaction_to_sheets(interaction_data):
   try:
       workbook = connect_to_google_sheets()


       sheet2 = workbook.worksheet("Nuevas Interacciones")  # Cambiado a "Nuevas Interacciones"
      
       # Añadir la interacción a ambas hojas
       sheet2.append_row(interaction_data)
      
       st.success("¡Interacción registrada exitosamente en Google Sheets!")
   except Exception as e:
       st.error(f"Error al guardar en Google Sheets: {e}")


# Configurar el estado de la sesión
if "session_active" not in st.session_state:
   st.session_state.session_active = False
if "current_page" not in st.session_state:
   st.session_state.current_page = "login"
if "user_role" not in st.session_state:
   st.session_state.user_role = None
if "user_name" not in st.session_state:
   st.session_state.user_name = None
if "user_image" not in st.session_state:
   st.session_state.user_image = None
if "user_points" not in st.session_state:
   st.session_state.user_points = 80  # Ejemplo de puntos acumulados
if "user_anniversary" not in st.session_state:
   st.session_state.user_anniversary = date(2022, 11, 25)  # Fecha de aniversario ficticia
if "solicitud_id" not in st.session_state:
   st.session_state.solicitud_id = None


st.markdown("""
    <style>
        .stApp {
            background-color: #2E6B1F; /* Verde más oscuro */
            color: white;
        }
        .stSidebar {
            background-color: #2C2C2C !important; /* Fondo oscuro del menú */
        }
        .stButton>button {
            background-color: #FDC820 !important; /* Amarillo brillante */
            color: black !important;
            border-radius: 5px;
            font-size: 16px; /* Ajustar tamaño del texto */
            padding: 10px; /* Mejor espacio dentro de los botones */
            margin: 5px 0; /* Espaciado entre los botones */
            width: auto; /* Ajusta ancho automáticamente */
        }
        .stButton>button:hover {
            background-color: #FFCC00 !important; /* Resaltar al pasar */
        }
        a {
            color: #00BFFF !important; /* Azul brillante para enlaces */
            font-weight: bold;
            text-decoration: none;
        }
        a:hover {
            color: #1E90FF !important; /* Color más brillante al pasar el mouse */
        }
    </style>
""", unsafe_allow_html=True)



# Función que renderiza la página de inicio (Gestor y Call Center)
def render_home_page():
   st.title(f"Bienvenido {st.session_state.user_name}! 👋")
   if st.session_state.user_image:
       st.image(st.session_state.user_image, caption="Foto de perfil", width=200)


   # Reconocimiento personal
   st.subheader("🎉 Reconocimiento Personal")
   days_in_company = (datetime.now().date() - st.session_state.user_anniversary).days
   years = days_in_company // 365
   months = (days_in_company % 365) // 30
   st.write(f"Gracias por formar parte de nuestra familia. Llevas **{years} años y {months} meses** con nosotros. ¡Eres invaluable!")


   # Progreso hacia el bono
   st.subheader("🌟 Progreso hacia tu Bono")
   target_points = 100  # Meta de puntos para el bono
   progress = st.session_state.user_points / target_points
   st.progress(progress)
   st.write(f"¡Llevas **{st.session_state.user_points} de {target_points} puntos** acumulados! 🎯")
   if st.session_state.user_points >= target_points:
       st.success("¡Felicidades! Has alcanzado el bono de este mes. 🎉")


   # Métrica de logros recientes
   st.subheader("📈 Desempeño Reciente")
   st.metric("Clientes Gestionados Este Mes", value=50, delta="+10 respecto al mes anterior")
   st.metric("Tasa de Éxito", value="85%", delta="+5% respecto al mes anterior")


   # Frase motivacional del día
   st.subheader("📢 Motivación del Día")
   st.write("“El éxito no es la clave de la felicidad. La felicidad es la clave del éxito. Si amas lo que haces, tendrás éxito.” – Albert Schweitzer")


   # Gráfico de desempeño reciente
   st.subheader("📊 Desempeño en los Últimos Meses")
   data = {
       "Mes": ["Enero", "Febrero", "Marzo", "Abril", "Mayo"],
       "Interacciones Exitosas": [30, 45, 50, 40, 55],
   }
   df = pd.DataFrame(data)
  
   plt.figure(figsize=(8, 4))
   plt.plot(df["Mes"], df["Interacciones Exitosas"], marker="o")
   plt.title("Interacciones Exitosas en los Últimos Meses")
   plt.xlabel("Mes")
   plt.ylabel("Interacciones Exitosas")
   plt.grid(True)
   st.pyplot(plt)


def gestor_page():
   with st.sidebar:
       st.header("Menú de Navegación")
       if st.button("Inicio"):
           st.session_state.current_page = "inicio"
       if st.button("Clientes de hoy"):
           st.session_state.current_page = "Clientes de hoy"
       if st.button("Nueva Interacción"):
           st.session_state.current_page = "nueva_interaccion"
       if st.button("Consultar Cliente"):
           st.session_state.current_page = "consultar_cliente"
       if st.button("Cerrar sesión"):
           st.session_state.session_active = False
           st.session_state.current_page = "login"


   if st.session_state.current_page == "inicio":
       render_home_page()


   elif st.session_state.current_page == "Clientes de hoy":
       st.title("Clientes de Hoy - Puerta a Puerta")
       try:
           sheet = connect_to_google_sheets().worksheet("M+I")
           registros = sheet.get_all_records()
           df = pd.DataFrame(registros)
           puerta_puerta = df.head(5)  # Tomar los primeros 5 clientes


           if puerta_puerta.empty:
               st.info("No hay clientes disponibles para 'Puerta a Puerta'.")
           else:
               for _, row in puerta_puerta.iterrows():
                   with st.container():
                       col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                       with col1:
                           st.write(f"**Solicitud ID:** {row['Solicitud_id']}")
                       with col2:
                           # Botón Nueva Interacción
                           if st.button("Nueva Interacción", key=f"interaccion_{row['Solicitud_id']}"):
                               st.session_state["solicitud_id"] = row["Solicitud_id"]
                               st.session_state.current_page = "nueva_interaccion"
                               return  # Finaliza la función para permitir que Streamlit renderice la nueva página
                       with col3:
                           # Botón Consultar Cliente
                           if st.button("Consultar Cliente", key=f"consultar_{row['Solicitud_id']}"):
                               st.session_state["solicitud_id"] = row["Solicitud_id"]
                               st.session_state.current_page = "consultar_cliente"
                               return  # Redirige a la página de consulta de cliente
                       with col4:
                           # Link a Google Maps
                           latitud, longitud = row.get("Latitud", None), row.get("Longitud", None)
                           if latitud and longitud:
                               url = f"https://www.google.com/maps/search/?api=1&query={latitud},{longitud}"
                           else:
                               url = "https://www.google.com.mx/maps/search/Tecnológico+de+Monterrey/@25.6485935,-100.3049229,14z"
                           st.markdown(f"[Ir a Ubicación](<{url}>)", unsafe_allow_html=True)
       except Exception as e:
           st.error(f"Error al cargar los clientes: {e}")


   elif st.session_state.current_page == "nueva_interaccion":
       st.title("📋 Registra una nueva interacción")
       interaction_form(page="Gestor")


   elif st.session_state.current_page == "consultar_cliente":
       consultar_cliente()




def interaction_form(page):
   solicitud_id = st.text_input(
       "Solicitud_id",
       placeholder="Ingresa el ID de la solicitud",
       value=st.session_state.get("solicitud_id", "")
   )
   resultado = st.selectbox("Resultado:", ["Atendió un tercero", "Atendió Cliente", "No Localizado"])
   tipo_gestion = "Puerta Puerta" if page == "Gestor" else "Call Center"
   st.text_input("Tipo de Gestión:", tipo_gestion, disabled=True)
   oferta = st.selectbox("Oferta:", ["Tus Pesos Valen Mas", "Quita / Castigo", "Pago sin Beneficio", "Reestructura del Credito"])
   promesa_pago = st.selectbox("Promesa Pago:", ["SI", "NO"])
   fecha = st.date_input("Fecha de Gestión", value=datetime.now().date())
   if st.button("Guardar Interacción"):
       registro = [solicitud_id, tipo_gestion, resultado, oferta, promesa_pago, str(fecha)]
       save_interaction_to_sheets(registro)




# Página del call center
def callcenter_page():
   with st.sidebar:
       st.header("Menú de Navegación")
       if st.button("Inicio"):
           st.session_state.current_page = "inicio"
       if st.button("Nueva Interacción"):
           st.session_state.current_page = "nueva_interaccion"
       if st.button("Consultar Cliente"):
           st.session_state.current_page = "consultar_cliente"
       if st.button("Cerrar sesión"):
           st.session_state.session_active = False
           st.session_state.current_page = "login"


   if st.session_state.current_page == "inicio":
       render_home_page()


   elif st.session_state.current_page == "nueva_interaccion":
       st.title("📋 Registra una nueva interacción")
       interaction_form(page="Call Center")


   elif st.session_state.current_page == "consultar_cliente":
       consultar_cliente()


# Página de inicio de sesión
def login_page():
   st.title("DIMEX")
   st.write("Por favor, ingresa tus credenciales para acceder.")


   username = st.text_input("Usuario", placeholder="Ingresa tu usuario")
   password = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña")


   if st.button("Iniciar sesión"):
       credenciales_df = load_credentials_from_google_sheets()
       if not credenciales_df.empty:
           valid, user_data = verify_credentials(username, password, credenciales_df)
           if valid:
               st.session_state.session_active = True
               st.session_state.user_role = user_data['role'].values[0]
               st.session_state.user_name = user_data['name'].values[0]
               st.session_state.user_image = user_data['image_path'].values[0]
               st.session_state.current_page = "inicio"
           else:
               st.error("Usuario o contraseña incorrectos.")
       else:
           st.error("Error al cargar las credenciales.")


def consultar_cliente():
   st.title("🔍 Consultar Cliente")


   if "cliente_data" not in st.session_state:
       st.session_state.cliente_data = None


   solicitud_id = st.text_input("Ingresa el ID de la solicitud:", placeholder="Ejemplo: 12345", value=st.session_state.solicitud_id)


   if st.button("Buscar"):
       st.session_state.solicitud_id = solicitud_id
       try:
           # Conectar con Google Sheets
           sheet = connect_to_google_sheets().worksheet("M+I")
           registros = sheet.get_all_records()
           df = pd.DataFrame(registros)


           # Mostrar las columnas disponibles para depuración
           st.write("Columnas disponibles en los datos:", df.columns)


           if "Solicitud_id" not in df.columns:
               st.error("No se encontró la columna `Solicitud_id` en los datos.")
               return


           # Filtrar por el ID de la solicitud
           cliente = df[df["Solicitud_id"] == int(solicitud_id)]


           if not cliente.empty:
               # Seleccionar las columnas importantes
               columnas_importantes = {
                   "Oferta_de_Cobranza": "Oferta de Cobranza",
                   "Linea_Credito": "Línea de Crédito",
                   "Tasa_Interes": "Tasa de Interés",
                   "Plazo_Meses": "Plazo en Meses",
                   "Pago": "Monto de Pago",
                   "Nivel_Atraso": "Nivel de Atraso",
                   "Edad_cliente": "Edad del Cliente",
                   "Ingreso_Bruto": "Ingreso Bruto",
                   "Probabilidad_Estimada": "Probabilidad Estimada",
                   "Ultima_Gestion": "Última Gestión",
                   "Mejor_oferta": "Mejor Oferta",
                   "pth": "Ruta de Imagen",
                   "Latitud": "Latitud",
                   "Longitud": "Longitud",
               }


               cliente_filtrado = cliente[list(columnas_importantes.keys())].rename(columns=columnas_importantes)
               st.session_state.cliente_data = cliente_filtrado
           else:
               st.warning("No se encontró información para el ID proporcionado.")
               st.session_state.cliente_data = None
       except Exception as e:
           st.error(f"Error al consultar al cliente: {e}")
           st.session_state.cliente_data = None


   if st.session_state.cliente_data is not None:
       cliente_data = st.session_state.cliente_data


       # Mostrar la mejor oferta destacada
       mejor_oferta = cliente_data["Mejor Oferta"].values[0] if "Mejor Oferta" in cliente_data else None
       if mejor_oferta:
           st.markdown(f"<h1 style='color:white; text-align:center; background-color:green; padding:10px;'>{mejor_oferta}</h1>", unsafe_allow_html=True)
       else:
           st.warning("No hay una 'Mejor Oferta' disponible para este cliente.")


       # Excluir columnas innecesarias del DataFrame mostrado
       columnas_excluidas = ["Ruta de Imagen", "Latitud", "Longitud"]
       cliente_mostrado = cliente_data.drop(columns=columnas_excluidas, errors="ignore")
       st.write("### Información del Cliente:")
       st.dataframe(cliente_mostrado)


       # Mostrar imagen del cliente desde la ruta local
       if "Ruta de Imagen" in cliente_data.columns:
           ruta_imagen = cliente_data["Ruta de Imagen"].values[0]
           if pd.notnull(ruta_imagen):
               try:
                   st.write("### Imagen del Cliente:")
                   st.image(ruta_imagen, use_column_width=True, caption="Imagen del cliente")
               except FileNotFoundError:
                   st.error("No se encontró la imagen en la ruta especificada.")
           else:
               st.warning("No hay una imagen disponible para este cliente.")


       # Mostrar mapa con ubicación del cliente
       if "Latitud" in cliente_data.columns and "Longitud" in cliente_data.columns:
           latitud = cliente_data["Latitud"].values[0]
           longitud = cliente_data["Longitud"].values[0]


           if pd.notnull(latitud) and pd.notnull(longitud):
               try:
                   mapa = folium.Map(location=[latitud, longitud], zoom_start=15)
                   folium.Marker(
                       [latitud, longitud],
                       popup=f"ID de Solicitud: {st.session_state.solicitud_id}",
                       tooltip="Ubicación del cliente",
                   ).add_to(mapa)
                   st.write("### Ubicación del Cliente:")
                   st_folium(mapa, width=700, height=500)
               except Exception as e:
                   st.error(f"Error al generar el mapa: {e}")
           else:
               st.warning("La latitud o longitud tienen valores nulos.")
       else:
           st.warning("No se encontraron las columnas 'Latitud' o 'Longitud' en los datos.")






# Control de flujo
if st.session_state.session_active:
   if st.session_state.user_role == "Gestor":
       gestor_page()
   elif st.session_state.user_role == "Call Center":
       callcenter_page()
else:
   login_page()

