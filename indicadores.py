import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title= "Indicadores", page_icon=':bar_chart:')

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
        cantidad = st.number_input("Cantidad a convertir:", min_value=0, value=1)
        fecha = st.date_input("Selecciona una fecha").strftime("%d-%m-%Y")
        if st.button("Consultar", key="consultar_fecha"):
            origen = api.consultar_indicadores_fecha(indicador, fecha)
            if "serie" in origen and len(origen["serie"]) > 0:
                valor_origen = origen["serie"][0]["valor"]
                calculo = cantidad * valor_origen
                st.success(f"{cantidad} {indicador.upper()} equivale a {calculo:.2f} pesos, en la fecha {fecha}.")
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
                    st.write(f"Fecha: {fecha}, Valor: {item['valor']} pesos")
            else:
                st.warning("No se encontraron datos recientes para este indicador.")

def calculadora_conversion():
    api = Mindicador()
    indicador_origen = st.selectbox("Selecciona el indicador de origen:", ["uf", "dolar", "euro", "utm"])
    indicador_destino = st.selectbox("Selecciona el indicador de destino:", ["uf", "dolar", "euro", "utm"])
    cantidad = st.number_input("Cantidad a convertir:", min_value=0.0, value=1.0)
    fecha = st.date_input("Selecciona una fecha").strftime("%d-%m-%Y")
    
    if st.button("Convertir"):
        origen = api.consultar_indicadores_fecha(indicador_origen, fecha)
        destino = api.consultar_indicadores_fecha(indicador_destino, fecha)

        if "serie" in origen and "serie" in destino:
            try:
                valor_origen = origen["serie"][0]["valor"]
                valor_destino = destino["serie"][0]["valor"]
                conversion = (cantidad * valor_origen) / valor_destino
                st.success(f"{cantidad} {indicador_origen.upper()} equivale a {conversion:.2f} {indicador_destino.upper()} en la fecha {fecha}.")
            except (IndexError, KeyError):
                st.error("No se encontraron valores para los indicadores en la fecha seleccionada.")
        else:
            st.error("No se pudieron obtener los datos para la conversión.")

if __name__ == "__main__":
    main()
