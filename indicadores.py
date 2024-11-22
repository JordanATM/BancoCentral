import streamlit as st
import requests
import json
from datetime import datetime

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

#Función principal
def main():
    st.title("🗓️ Consulta de Indicadores Económicos")
    st.sidebar.title("Opciones")

    # Sidebar para elegir funcionalidad
    opcion = st.sidebar.selectbox(
        "Selecciona una opción",
        ["Calculadora de Conversión", "Consulta de Indicadores"]
    )

    if opcion == "Consulta de Indicadores":
        consulta_indicadores()
    elif opcion == "Calculadora de Conversión":
        calculadora_conversion()

def consulta_indicadores():
    consulta_tipo = st.sidebar.radio(
        "Selecciona el tipo de consulta",
        ("Indicador por fecha","Indicador específico último mes")
    )

    api = Mindicador()

    if consulta_tipo == "Indicador por fecha":
        indicador = st.selectbox("Selecciona el indicador", [
            "uf", "dolar","utm", "euro"
        ])
        cantidad = st.number_input("Cantidad a convertir", min_value=0, value=1)
        fecha = st.date_input("Selecciona una fecha").strftime("%d-%m-%Y")
        origen = api.consultar_indicadores_fecha(indicador, fecha)
        if st.button("Consultar"):
            origen = api.consultar_indicadores_fecha(indicador, fecha)
            valor_origen = origen["serie"][0]["valor"]
            calculo = cantidad * valor_origen
            st.write(f"{cantidad} {indicador.upper()} equivale a {calculo:.2f} pesos, en la fecha {fecha}.")

            if "error" in origen:
                st.error(f"Error: {origen['error']}")
                st.warning("No se encontraron datos para esta fecha.")


    elif consulta_tipo == "Indicador específico último mes":
        indicador = st.selectbox("Selecciona el indicador", [
            "uf", "ivp", "dolar", "dolar_intercambio", "euro", "ipc", 
            "utm", "imacec", "tpm", "libra_cobre", "tasa_desempleo", "bitcoin"
        ])
        # Agregar clave única al botón
        if st.button("Consultar", key="consultar_indicador_especifico"):
            resultado = api.consultar_indicadores_fecha(indicador, fecha=None)
            if "error" in resultado:
                st.error(f"Error: {resultado['error']}")
            else:
                st.write(f"Resultados para el indicador **{indicador.upper()}**:")
                if "serie" in resultado and resultado["serie"]:
                    for item in resultado["serie"]:
                        # Convertir fecha al formato dd/mm/yy
                        fecha = datetime.strptime(item['fecha'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%y")
                        st.write(f"Fecha: {fecha}, Valor: {item['valor']} pesos")
                else:
                    st.warning("No se encontraron datos recientes para este indicador.")



    elif consulta_tipo == "Indicador específico":
        indicador = st.selectbox("Selecciona el indicador", [
            "uf", "ivp", "dolar", "dolar_intercambio", "euro", "ipc", 
            "utm", "imacec", "tpm", "libra_cobre", "tasa_desempleo", "bitcoin"
        ])
        if st.sidebar.button("Consultar"):
            resultado = api.consultar_indicadores_fecha(indicador, fecha=None)
            if "error" in resultado:
                st.error(f"Error: {resultado['error']}")
            else:
                st.write(f"Resultados para el indicador **{indicador.upper()}**:")
                if "serie" in resultado:
                    for item in resultado["serie"]:
                        st.write(f"Fecha: {item['fecha']}, Valor: {item['valor']} pesos")
                else:
                    st.warning("No se encontraron datos recientes para este indicador.")

    

def calculadora_conversion():
    st.write("Calculadora de conversión entre indicadores.")
    api = Mindicador()

    # Selección de indicadores
    indicador_origen = st.selectbox("Selecciona el indicador de origen", [
        "uf", "dolar", "euro", 
        "utm"
    ])
    indicador_destino = st.selectbox("Selecciona el indicador de destino", [
        "uf", "dolar","euro", 
        "utm"
    ])
    cantidad = st.number_input("Cantidad a convertir", min_value=0.0, value=1.0)
    fecha = st.date_input("Selecciona una fecha").strftime("%d-%m-%Y")

    if st.button("Convertir"):
        # Obtener valores para ambos indicadores
        origen = api.consultar_indicadores_fecha(indicador_origen, fecha)
        destino = api.consultar_indicadores_fecha(indicador_destino, fecha)

        if "error" in origen or "error" in destino:
            st.error(f"No se pudieron obtener los datos para la conversión.")
        else:
            try:
                valor_origen = origen["serie"][0]["valor"]
                valor_destino = destino["serie"][0]["valor"]
                conversion = (cantidad * valor_origen) / valor_destino
                st.write(f"{cantidad} {indicador_origen.upper()} equivale a {conversion:.2f} {indicador_destino.upper()} en la fecha {fecha}.")
            except (IndexError, KeyError):
                st.error("No se encontraron valores para los indicadores en la fecha seleccionada.")

if __name__ == "__main__":
    main()
