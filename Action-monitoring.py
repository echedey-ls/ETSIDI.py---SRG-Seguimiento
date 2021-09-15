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

from datetime import timedelta, datetime

import pandas as pd
import numpy as np

def retrieve_data_from_drive():
    '''TODO: implement cloud service'''
    pass
    
def retrieve_data_from_xlsx():
    '''Gets data from a excel sheet (>2007)'''
    return pd.read_excel('registro_acciones.xlsx', sheet_name='Actuaciones', usecols='B:C', header=1, parse_dates=True)


def main():
    accionesData = (retrieve_data_from_xlsx()
            .dropna()
            .sort_values('FECHA')
        )
    print( "Histórico de acciones" )
    print( accionesData )
    
    accionesParsedDf = pd.DataFrame( columns=['LUGAR', 'HISTORICO'] )
    for lugar in accionesData['LUGAR'].unique():
        dates = accionesData[accionesData['LUGAR'] == lugar]['FECHA'].to_list()
        accionesParsedDf = pd.concat(
            [accionesParsedDf,
            pd.DataFrame( {'LUGAR': [lugar], 'HISTORICO': [dates] }, columns=['LUGAR', 'HISTORICO'] ) ], 
            ignore_index=True)

    print( "\nAcciones y su lista de actuaciones" )
    print( accionesParsedDf )

    print( "\nSUMARIO DE MANTENIMIENTO DE ACCIONES" )
    logicalMap_sobrepasadas = [fecha[-1]<datetime.now()-timedelta(days=30*4) for fecha in accionesParsedDf['HISTORICO'].to_list()]
    
    print( "\n\t--> TIEMPO SOBREPASADO" )
    accionesSobrepasadas = accionesParsedDf[ logicalMap_sobrepasadas ]
    # Copiamos los lugares como DataFrame (doble corchete), luego añadimos columna con última fecha para cada acción
    accionesSobrepasadasOut = accionesSobrepasadas[['LUGAR']]
    accionesSobrepasadasOut = (accionesSobrepasadasOut
        .assign( FECHA_ULTIMA= [ fecha[-1] for fecha in accionesSobrepasadas['HISTORICO'].to_list() ] )
        .sort_values('FECHA_ULTIMA')
    )
    print( accionesSobrepasadasOut )

    print( "\n\t--> PRÓXIMAS REVISIONES" )
    accionesProximas = accionesParsedDf[ [not a for a in logicalMap_sobrepasadas] ]
    # Idem anterior
    accionesProximasOut = accionesProximas[['LUGAR']]
    accionesProximasOut = (accionesProximasOut
        .assign( FECHA_ULTIMA= [ fecha[-1] for fecha in accionesProximas['HISTORICO'].to_list() ] )
        .sort_values('FECHA_ULTIMA')
    )
    print( accionesProximasOut )


if __name__ == "__main__":
    main()
    pass
