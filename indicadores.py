import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Indicadores", page_icon=":bar_chart:")

class Mindicador:
    def consultar_indicadores(self):
        url = "https://mindicador.cl/api"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"No se pudo obtener datos. Código HTTP: {response.status_code}"}

    def consultar_indicadores_fecha(self, indicador, fecha=None):
        if fecha:
            url = f"https://mindicador.cl/api/{indicador}/{fecha}"
        else:
            url = f"https://mindicador.cl/api/{indicador}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"No se pudo obtener datos. Código HTTP: {response.status_code}"}

def main():
    # Fuente de datos
    st.sidebar.text("Fuente:")
    st.sidebar.link_button("Banco Central de Chile","https://www.bcentral.cl/inicio")
    st.sidebar.title("Opciones")

    # Menú lateral
    opcion = st.sidebar.radio(
        "Selecciona una funcionalidad:",
        ["Calculadora de Conversión", "Consulta de Indicadores"]
    )
    
    st.title("🗓️ Consulta de Indicadores Económicos")
    
    # Mostrar ambas funcionalidades juntas
    if opcion == "Consulta de Indicadores":
        st.header("Consulta de Indicadores")
        consulta_indicadores()
    elif opcion == "Calculadora de Conversión":
        st.header("Calculadora de Conversión")
        calculadora_conversion()

def consulta_indicadores():
    api = Mindicador()

    consulta_tipo = st.radio(
        "Selecciona el tipo de consulta:",
        ("Indicador por fecha", "Indicador específico último mes"),
        key="consulta_tipo"
    )
    
    if consulta_tipo == "Indicador por fecha":
        indicador = st.selectbox("Selecciona el indicador:", ["uf", "dolar", "utm", "euro"])
        cantidad = st.number_input("Cantidad a convertir:", min_value=0.0, value=1.0)
        fecha = st.date_input("Selecciona una fecha").strftime("%d-%m-%Y")
        if st.button("Consultar", key="consultar_fecha"):
            origen = api.consultar_indicadores_fecha(indicador, fecha)
            if "serie" in origen and len(origen["serie"]) > 0:
                valor_origen = origen["serie"][0]["valor"]
                calculo = cantidad * valor_origen
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.success(f"{cantidad} {indicador.upper()} equivale a {calculo:.2f} pesos, en la fecha {fecha}.")
                with col2:
                    copiar_valor_html(calculo)
            else:
                st.error("No se encontraron datos para esta fecha.")
    
    elif consulta_tipo == "Indicador específico último mes":
        indicador = st.selectbox("Selecciona el indicador:", ["uf", "dolar", "euro", "utm"])
        if st.button("Consultar", key="consultar_mes"):
            resultado = api.consultar_indicadores_fecha(indicador)
            if "serie" in resultado and resultado["serie"]:
                st.success(f"Resultados para el indicador **{indicador.upper()}**:")
                for item in resultado["serie"]:
                    fecha = datetime.strptime(item['fecha'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%y")
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"Fecha: {fecha}, Valor: {item['valor']} pesos")
                    with col2:
                        copiar_valor_html(item['valor'])
            else:
                st.warning("No se encontraron datos recientes para este indicador.")


def calculadora_conversion():
    api = Mindicador()
    
    # Incluye "peso chileno" como opción
    indicador_origen = st.selectbox("Selecciona el indicador de origen:", ["uf", "Peso", "dolar", "euro", "utm"])
    indicador_destino = st.selectbox("Selecciona el indicador de destino:", ["Peso", "uf", "dolar", "euro", "utm"])
    if indicador_origen == 'Peso':
        cantidad = st.number_input("Cantidad a convertir:", min_value=0, value=1)
    else:
        cantidad = st.number_input("Cantidad a convertir:", min_value=0.0, value=1.0)

    fecha = st.date_input("Selecciona una fecha").strftime("%d-%m-%Y")
    
    if st.button("Convertir"):
        if indicador_origen == "Peso":
            # Convertir desde pesos chilenos a otra divisa
            
            destino = api.consultar_indicadores_fecha(indicador_destino, fecha)
            if "serie" in destino and destino["serie"]:
                try:
                    valor_destino = destino["serie"][0]["valor"]
                    conversion = cantidad / valor_destino
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.success(f"{cantidad} pesos chilenos equivalen a {conversion:.5f} {indicador_destino.upper()} en la fecha {fecha}.")
                    with col2:
                        copiar_valor_html(conversion)
                except (IndexError, KeyError):
                    st.error("No se encontraron valores para el indicador de destino en la fecha seleccionada.")
            else:
                st.error("No se pudo obtener el dato para la divisa de destino.")
        elif indicador_destino == "Peso":
            # Convertir desde otra divisa a pesos chilenos
            origen = api.consultar_indicadores_fecha(indicador_origen, fecha)
            if "serie" in origen and origen["serie"]:
                try:
                    valor_origen = origen["serie"][0]["valor"]
                    conversion = cantidad * valor_origen
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.success(f"{cantidad:.2f} {indicador_origen.upper()} equivalen a {conversion:.2f} pesos chilenos en la fecha {fecha}.")
                    with col2:
                        copiar_valor_html(conversion)
                except (IndexError, KeyError):
                    st.error("No se encontraron valores para el indicador de origen en la fecha seleccionada.")
            else:
                st.error("No se pudo obtener el dato para la divisa de origen.")
        else:
            # Convertir entre otras divisas
            origen = api.consultar_indicadores_fecha(indicador_origen, fecha)
            destino = api.consultar_indicadores_fecha(indicador_destino, fecha)

            if "serie" in origen and "serie" in destino:
                try:
                    valor_origen = origen["serie"][0]["valor"]
                    valor_destino = destino["serie"][0]["valor"]
                    conversion = (cantidad * valor_origen) / valor_destino
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.success(f"{cantidad:.2f} {indicador_origen.upper()} equivalen a {conversion:.2f} {indicador_destino.upper()} en la fecha {fecha}.")
                    with col2:
                        copiar_valor_html(conversion)
                except (IndexError, KeyError):
                    st.error("No se encontraron valores para los indicadores en la fecha seleccionada.")
            else:
                st.error("No se pudieron obtener los datos para la conversión.")


# def calculadora_conversion():
#     api = Mindicador()
#     indicador_origen = st.selectbox("Selecciona el indicador de origen:", ["uf", "dolar", "euro", "utm"])
#     indicador_destino = st.selectbox("Selecciona el indicador de destino:", ["uf", "dolar", "euro", "utm"])
#     cantidad = st.number_input("Cantidad a convertir:", min_value=0.0, value=1.0)
#     fecha = st.date_input("Selecciona una fecha").strftime("%d-%m-%Y")
    
#     if st.button("Convertir"):
#         origen = api.consultar_indicadores_fecha(indicador_origen, fecha)
#         destino = api.consultar_indicadores_fecha(indicador_destino, fecha)

#         if "serie" in origen and "serie" in destino:
#             try:
#                 valor_origen = origen["serie"][0]["valor"]
#                 valor_destino = destino["serie"][0]["valor"]
#                 conversion = (cantidad * valor_origen) / valor_destino
#                 col1, col2 = st.columns([2, 1])
#                 with col1:
#                     st.success(f"{cantidad} {indicador_origen.upper()} equivale a {conversion:.2f} {indicador_destino.upper()} en la fecha {fecha}.")
#                 with col2:
#                     copiar_valor_html(conversion)

#             except (IndexError, KeyError):
#                 st.error("No se encontraron valores para los indicadores en la fecha seleccionada.")
#         else:
#             st.error("No se pudieron obtener los datos para la conversión.")

def copiar_valor_html(valor):
    """Función para mostrar el bloque de código con funcionalidad de copia al portapapeles y mensaje temporal."""
    html_code = f"""
    <style>
        html{{
           
            
        }}

        .copy-button {{
            background-color: #007BFF;
            color: white;
            border: none;
            padding: 5px 15px;
            font-size: 14px;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            margin-top: -1.1px;
            margin-bottom: 15px;
            
        }}
        .copy-button:hover {{
            background-color: #0056b3;
        }}
        .copy-button:active {{
            background-color: #003f7f;
        }}
        .copy-container {{
            display: flex;
            justify-content: space-between;
            gap: 5px;
        }}
        .copy-code {{
            font-family: arial;
            background-color: #f8f9fa;
            padding: 5px 30px;
            border-radius: 5px;
            align-items: center;
            border: solid black;
            margin-bottom: 12px;
            margin-top: -1px;
        }}
        .copy-message {{
            font-family: arial;
            font-size: 15px;
            font-weight: bold;
            background-color: green;
            color: white;
            margin-top: -5px;
            display: none;
            text-align: center;
            border-radius: 5px;
        }}
    </style>
    <div class="copy-container">
        <pre id="code-block" class="copy-code">{valor:.2f}</pre>
        <button class="copy-button" onclick="copyToClipboard()">Copiar</button>
    </div>
    <div id="copy-message" class="copy-message">Valor copiado</div>
    <script>
    function copyToClipboard() {{
        const codeBlock = document.getElementById('code-block');
        navigator.clipboard.writeText(codeBlock.innerText).then(() => {{
            const message = document.getElementById('copy-message');
            message.style.display = 'block';  
            setTimeout(() => {{
                message.style.display = 'none'; 
            }}, 1000);
        }});
    }}
    </script>
    """
    st.components.v1.html(html_code, height=150)


if __name__ == "__main__":
    main()
