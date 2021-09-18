#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Author: Echedey Luis Álvarez
Date: 13/09/2021
Project: Action-monitoring, for ETSIDI.py

File: Action-monitoring.py

Abstract: main file

Sources:
"""

import sys, os

from datetime import timedelta, datetime, date

import pandas as pd
import numpy as np
import streamlit as st

# Set to True to see output in the console. Set to False in releases.
dev_consoleOut = False

def retrieve_data_from_drive():
    '''TODO: implement cloud service'''
    pass
    
def retrieve_data_from_xlsx():
    '''Gets data from a excel sheet (>2007)'''
    return pd.read_excel('data/Registro_acciones.xlsx', sheet_name='Actuaciones', usecols='B:D', header=1, parse_dates=True)

def web_gui(sobrepasadasDf, proximasDf, todasDf):
    '''Uses Streamlit to produce the web page'''
    st.set_page_config(
        page_title= 'Revisiones SinRaboGato',
        page_icon= 'res/page-SRG-icon.png'
    )

    st.title("Progreso en acciones")
    st.header("Zonas a revisar")
    st.dataframe(sobrepasadasDf)

    st.header("Próximas zonas a revisar")
    st.dataframe(proximasDf)

    st.markdown("""---""") # A separator

    with st.expander("Información en de una zona de actuación específica"):
        st.text("Selecciona una zona para obtener un resumen de sus acciones")
        actionSelector = st.selectbox(label= 'Ver datos de acción',
            options= todasDf['LUGAR'] )
        zoneDates = todasDf[ todasDf['LUGAR'] == actionSelector ].iat[0, 1]
        nAcciones = len(zoneDates)
        # Strings are cut depending on the equality of nAcciones with 1
        st.write(f"""
            En {actionSelector} se ha{'n'[:nAcciones!=1]} realizado {nAcciones} acci{'óo'[nAcciones!=1:((nAcciones!=1)+1)]}n{'es'[:2*(nAcciones!=1)]} en la{'s'[:nAcciones!=1]} siguiente{'s'[:nAcciones!=1]} fecha{'s'[:nAcciones!=1]}:
            """)
        for a in zoneDates: # Esto es una cutrada como una casa (¿chabola?) pero de lo que he probado es lo que más me gusta
            st.write( a )

def main():
    # Read data from excel, drop rows with less than 2 values: LUGAR & FECHA
    accionesData = (retrieve_data_from_xlsx()
            .dropna(axis= 0, thresh= 2)
            .sort_values('FECHA')
        )
    
    if dev_consoleOut:
        print( "Histórico de acciones" )
        print( accionesData )

    # Change dates type from datetime to date - user-friendlyness
    accionesData['FECHA'] = pd.to_datetime(accionesData['FECHA']).dt.date

    # Ignore 'cancelled' actions
    lista_canceladas= accionesData['Notas'].str.contains("cancelada", case= False, na= False)
    accionesData = accionesData[ [ not a for a in lista_canceladas ] ]
    if dev_consoleOut:
        print(lista_canceladas)

    # Create a new dataframe with unique places, and add the list of dates when there was an action
    accionesParsedDf = pd.DataFrame( columns=['LUGAR', 'HISTORICO'] )
    for lugar in accionesData['LUGAR'].unique():
        dates = accionesData[ accionesData['LUGAR'] == lugar]['FECHA'].to_list()
        accionesParsedDf = pd.concat(
            [accionesParsedDf,
            pd.DataFrame( {'LUGAR': [lugar], 'HISTORICO': [dates] }, columns=['LUGAR', 'HISTORICO'] ) ], 
            ignore_index=True)

    if dev_consoleOut:
        print( "\nAcciones y su lista de actuaciones" )
        print( accionesParsedDf )

    # Make a logical index of exceeded revision time in months
    months = 4
    logicalMap_sobrepasadas = [ fecha[-1]<datetime.now().date()-timedelta(days=30*months) for fecha in accionesParsedDf['HISTORICO'].to_list() ]

    accionesSobrepasadas = accionesParsedDf[ logicalMap_sobrepasadas ]
    # Copiamos los lugares como DataFrame (doble corchete), luego añadimos columna con última fecha para cada acción
    accionesSobrepasadasOut = accionesSobrepasadas[['LUGAR']]
    accionesSobrepasadasOut = (accionesSobrepasadasOut
        .assign( FECHA_ULTIMA= [ fecha[-1] for fecha in accionesSobrepasadas['HISTORICO'].to_list() ] )
        .sort_values('FECHA_ULTIMA')
    )

    accionesProximas = accionesParsedDf[ [not a for a in logicalMap_sobrepasadas] ]
    # Idem anterior
    accionesProximasOut = accionesProximas[['LUGAR']]
    accionesProximasOut = (accionesProximasOut
        .assign( FECHA_ULTIMA= [ fecha[-1] for fecha in accionesProximas['HISTORICO'].to_list() ] )
        .sort_values('FECHA_ULTIMA')
    )

    # Reset index to numbers starting by 1
    accionesSobrepasadasOut = (accionesSobrepasadasOut
        .rename(columns= {'LUGAR': 'Lugar', 'FECHA_ULTIMA': 'Última actuación'})
        .reset_index(drop= True) )
    accionesSobrepasadasOut.index += 1

    accionesProximasOut = (accionesProximasOut
        .rename(columns= {'LUGAR': 'Lugar', 'FECHA_ULTIMA': 'Última actuación'})
        .reset_index(drop= True) )
    accionesProximasOut.index += 1

    # Output user-friendly DataFrames, else use Streamlit for the web
    if dev_consoleOut:
        print( "\nSUMARIO DE MANTENIMIENTO DE ACCIONES" )
        print( "\n\t--> TIEMPO SOBREPASADO" )
        print( accionesSobrepasadasOut )
        print( "\n\t--> PRÓXIMAS REVISIONES" )
        print( accionesProximasOut )
    else:
        web_gui( accionesSobrepasadasOut , accionesProximasOut , accionesParsedDf )


if __name__ == "__main__":
    main()
    pass
