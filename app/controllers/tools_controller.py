# app/controllers/tools_controller.py

import json
import traceback
from flask import render_template, jsonify, request
from flask_login import login_required
from app import app, db
from sqlalchemy import and_, desc, distinct, func, case, literal, literal_column, text
from app.models.database import Resultado, Sumario, Diccionario
from config import DOMINIOS_ESPECIFICOS, URL_BASE
from app import IDS_ESCANEO, FECHA_ESCANEO, HORA_FIN, HORA_INICIO, ESTADO_SPIDER
from sqlalchemy.orm import class_mapper
from flask import request
from bs4 import BeautifulSoup
import requests
from flask import render_template, request, redirect, url_for
import urllib.parse
from urllib.parse import parse_qs, unquote
from flask import Flask, render_template, request, redirect, url_for, session
from urllib.parse import urlparse, urljoin


ids_escaneo_especificos = IDS_ESCANEO
dominios_especificos = DOMINIOS_ESPECIFICOS


# Decorador de contexto para pasar variables globales a todas las plantillas
@app.context_processor
def inject_global_variables():
    return dict(fecha_escaneo=FECHA_ESCANEO,
                hora_inicio=HORA_INICIO,
                hora_fin=HORA_FIN,
                estado_spider=ESTADO_SPIDER,
                url_base=URL_BASE)


# Implementación del filtro fromjson
def fromjson(value):
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


# Agregar el filtro a la aplicación Flask
app.jinja_env.filters['fromjson'] = fromjson

# Tools rutas


@app.route('/informes/resumen')
@login_required
def informe_resumen():

    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas
    sumarios = (
        db.session.query(Sumario)
        #.filter(Sumario.dominio.in_(DOMINIOS_ESPECIFICOS))
        .filter(Sumario.id_escaneo.in_(IDS_ESCANEO)).all())

    # Convertir objetos Sumario a diccionarios
    sumarios_dict = []
    for sumario in sumarios:
        sumario_dict = {}
        for column in class_mapper(Sumario).columns:
            sumario_dict[column.name] = getattr(sumario, column.name)
        sumarios_dict.append(sumario_dict)

    # Consulta para obtener la segunda coincidencia ordenando por sumario.id de mayor a menor
    sumario_ayer = (
        db.session.query(Sumario).filter(
            Sumario.dominio.in_(DOMINIOS_ESPECIFICOS)).order_by(
                desc(Sumario.id)).offset(
                    1)  # Omite la primera coincidencia (la de mayor id)
        .limit(1)  # Limita el resultado a una fila (la segunda coincidencia)
        .first())

    # Consulta para obtener la segunda coincidencia ordenando por sumario.id de mayor a menor
    sumario_quince = (
        db.session.query(Sumario).filter(
            Sumario.dominio.in_(DOMINIOS_ESPECIFICOS)).order_by(
                desc(Sumario.id)).offset(
                    14)  # Omite la primera coincidencia (la de mayor id)
        .limit(1)  # Limita el resultado a una fila (la segunda coincidencia)
        .first())

    # Verifica si se encontró la segunda coincidencia antes de intentar iterar sobre ella
    if sumario_ayer:
        # Puedes acceder a las propiedades del objeto Sumario directamente
        print(f"ID: {sumario_ayer.id}, Dominio: {sumario_ayer.dominio}")
    else:
        print("No se encontraron coincidencias.")

    return render_template('tools/resumen.html',
                           dominio=DOMINIOS_ESPECIFICOS[0],
                           resumen_ayer=sumario_ayer,
                           resumen=sumarios,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           ids_especificos=IDS_ESCANEO)

@app.route('/usabilidad/resumen/<string:dominio>')
@login_required
def usabilidad_resumen_dominio(dominio):
    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas para un dominio específico
    sumarios = (db.session.query(Sumario).filter(
        Sumario.dominio == dominio).filter(
            Sumario.id_escaneo.in_(IDS_ESCANEO)).all())

    # Convertir objetos Sumario a diccionarios
    sumarios_dict = []
    for sumario in sumarios:
        sumario_dict = {}
        for column in class_mapper(Sumario).columns:
            sumario_dict[column.name] = getattr(sumario, column.name)
        sumarios_dict.append(sumario_dict)

    # Consulta para obtener la segunda coincidencia ordenando por sumario.id de mayor a menor
    sumario_ayer = (db.session.query(Sumario).filter(
        Sumario.dominio == dominio).order_by(desc(
            Sumario.id)).offset(1).limit(1).first())

    # Consulta para obtener la segunda coincidencia ordenando por sumario.id de mayor a menor
    sumario_quince = (db.session.query(Sumario).filter(
        Sumario.dominio == dominio).order_by(desc(
            Sumario.id)).offset(14).limit(1).first())

    # Verifica si se encontró la segunda coincidencia antes de intentar iterar sobre ella
    if sumario_ayer:
        # Puedes acceder a las propiedades del objeto Sumario directamente
        print(f"ID: {sumario_ayer.id}, Dominio: {sumario_ayer.dominio}")
    else:
        print("No se encontraron coincidencias.")

    return render_template('tools/usa/resumen_usa.html',
                           dominio=dominio,
                           solo_uno=dominio,
                           resumen_ayer=sumario_ayer,
                           resumen=sumarios,
                           dominio_actual=dominio,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           ids_especificos=IDS_ESCANEO)

@app.route('/accesibilidad/resumen/<string:dominio>')
@login_required
def accesibilidad_resumen_dominio(dominio):
    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas para un dominio específico
    sumarios = (db.session.query(Sumario).filter(
        Sumario.dominio == dominio).filter(
            Sumario.id_escaneo.in_(IDS_ESCANEO)).all())

    # Convertir objetos Sumario a diccionarios
    sumarios_dict = []
    for sumario in sumarios:
        sumario_dict = {}
        for column in class_mapper(Sumario).columns:
            sumario_dict[column.name] = getattr(sumario, column.name)
        sumarios_dict.append(sumario_dict)

    # Consulta para obtener la segunda coincidencia ordenando por sumario.id de mayor a menor
    sumario_ayer = (db.session.query(Sumario).filter(
        Sumario.dominio == dominio).order_by(desc(
            Sumario.id)).offset(1).limit(1).first())

    # Consulta para obtener la segunda coincidencia ordenando por sumario.id de mayor a menor
    sumario_quince = (db.session.query(Sumario).filter(
        Sumario.dominio == dominio).order_by(desc(
            Sumario.id)).offset(14).limit(1).first())

    # Verifica si se encontró la segunda coincidencia antes de intentar iterar sobre ella
    if sumario_ayer:
        # Puedes acceder a las propiedades del objeto Sumario directamente
        print(f"ID: {sumario_ayer.id}, Dominio: {sumario_ayer.dominio}")
    else:
        print("No se encontraron coincidencias.")

    return render_template('tools/acc/resumen_acc.html',
                           dominio=dominio,
                           solo_uno=dominio,
                           resumen_ayer=sumario_ayer,
                           resumen=sumarios,
                           dominio_actual=dominio,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           ids_especificos=IDS_ESCANEO)

@app.route('/seo/resumen/<string:dominio>')
@login_required
def seo_resumen_dominio(dominio):
    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas para un dominio específico
    sumarios = (db.session.query(Sumario).filter(
        Sumario.dominio == dominio).filter(
            Sumario.id_escaneo.in_(IDS_ESCANEO)).all())

    # Convertir objetos Sumario a diccionarios
    sumarios_dict = []
    for sumario in sumarios:
        sumario_dict = {}
        for column in class_mapper(Sumario).columns:
            sumario_dict[column.name] = getattr(sumario, column.name)
        sumarios_dict.append(sumario_dict)

    # Consulta para obtener la segunda coincidencia ordenando por sumario.id de mayor a menor
    sumario_ayer = (db.session.query(Sumario).filter(
        Sumario.dominio == dominio).order_by(desc(
            Sumario.id)).offset(1).limit(1).first())

    # Consulta para obtener la segunda coincidencia ordenando por sumario.id de mayor a menor
    sumario_quince = (db.session.query(Sumario).filter(
        Sumario.dominio == dominio).order_by(desc(
            Sumario.id)).offset(14).limit(1).first())

    # Verifica si se encontró la segunda coincidencia antes de intentar iterar sobre ella
    if sumario_ayer:
        # Puedes acceder a las propiedades del objeto Sumario directamente
        print(f"ID: {sumario_ayer.id}, Dominio: {sumario_ayer.dominio}")
    else:
        print("No se encontraron coincidencias.")

    return render_template('tools/seo/resumen_seo.html',
                           dominio=dominio,
                           solo_uno=dominio,
                           resumen_ayer=sumario_ayer,
                           resumen=sumarios,
                           dominio_actual=dominio,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           ids_especificos=IDS_ESCANEO)


@app.route('/informes/resumen/<string:dominio>')
@login_required
def informe_resumen_dominio(dominio):
    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas para un dominio específico
    sumarios = (db.session.query(Sumario).filter(
        Sumario.dominio == dominio).filter(
            Sumario.id_escaneo.in_(IDS_ESCANEO)).all())

    # Convertir objetos Sumario a diccionarios
    sumarios_dict = []
    for sumario in sumarios:
        sumario_dict = {}
        for column in class_mapper(Sumario).columns:
            sumario_dict[column.name] = getattr(sumario, column.name)
        sumarios_dict.append(sumario_dict)

    # Consulta para obtener la segunda coincidencia ordenando por sumario.id de mayor a menor
    sumario_ayer = (db.session.query(Sumario).filter(
        Sumario.dominio == dominio).order_by(desc(
            Sumario.id)).offset(1).limit(1).first())

    # Consulta para obtener la segunda coincidencia ordenando por sumario.id de mayor a menor
    sumario_quince = (db.session.query(Sumario).filter(
        Sumario.dominio == dominio).order_by(desc(
            Sumario.id)).offset(14).limit(1).first())

    # Verifica si se encontró la segunda coincidencia antes de intentar iterar sobre ella
    if sumario_ayer:
        # Puedes acceder a las propiedades del objeto Sumario directamente
        print(f"ID: {sumario_ayer.id}, Dominio: {sumario_ayer.dominio}")
    else:
        print("No se encontraron coincidencias.")

    return render_template('tools/resumen.html',
                           dominio=dominio,
                           solo_uno=dominio,
                           resumen_ayer=sumario_ayer,
                           resumen=sumarios,
                           dominio_actual=dominio,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           ids_especificos=IDS_ESCANEO)


@app.route('/informes/consultas')
@login_required
def consultas():
    return render_template('tools/informes.html')


@app.route('/informes/mejoras')
@login_required
def mejoras():
    return render_template('tools/performance.html')


@app.route('/meta-tags/<string:dominio>')
@login_required
def meta_tags(dominio):
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == dominio).limit(1).all())

    # Obtener los resultados para las fechas seleccionadas
    fechas_seleccionadas = [result[0] for result in results]

    # Consulta para obtener el campo Sumario.total_paginas
    total_paginas_result = db.session.query(Sumario.total_paginas).filter(
        Sumario.fecha == fechas_seleccionadas[0],
        Sumario.dominio == dominio).first()

    # Almacenar el valor de Sumario.total_paginas en una variable
    total_paginas = total_paginas_result[0] if total_paginas_result else None

    #.filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))

    # Consulta para obtener las páginas de la tabla Resultados con código de respuesta 200 y tiempo de respuesta mayor que 0
    paginas_metatags = (
        db.session.query(
            Resultado.fecha_escaneo,
            Resultado.dominio,
            Resultado.pagina,
            Resultado.lang,
            Resultado.meta_tags,
            Resultado.desc_short,
            Resultado.desc_long,
            Resultado.id,
            Resultado.meta_description_duplicado,
            Resultado.meta_description_mas_155_caracteres,
            Resultado.meta_description_menos_70_caracteres,
            Resultado.meta_description_falta,
            Resultado.meta_og_card,
            Resultado.meta_og_title,
            Resultado.meta_og_image
        ).filter(
            #Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.dominio == dominio,
            Resultado.codigo_respuesta == 200,
            Resultado.meta_description_falta != 0 or Resultado.meta_description_menos_70_caracteres != 0
            or Resultado.desc_short != 0 or Resultado.desc_long != 0 or Resultado.meta_description_duplicado != 0 or Resultado.meta_description_mas_155_caracteres != 0
            #Resultado.tiempo_respuesta > 0,
            #Resultado.tiempo_respuesta.isnot(None),  # Filtrar resultados con tiempo_respuesta no nulo
            #Resultado.tiempo_respuesta != '',
            #Resultado.tiempo_respuesta.isnot(False) #,  # Filtrar resultados con tiempo_respuesta False
            #Resultado.tiempo_respuesta.isnot(None)
            #~func.isnan(Resultado.tiempo_respuesta),  # Filtrar resultados que no sean números (nan)
        )
        #.filter(
        #    ~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        #.filter(
        #    ~Resultado.pagina.like('%pdf%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%/documents/%')
        #        )  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%/document_library/%')
        #        )  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%redirect%')
        #        )  # Excluir URLs que contengan 'redirect'
        .filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))
        .filter(
            Resultado.tipo_documento.like('%text%'))
        #.filter(Resultado.lang.in_(['es','ca','en','fr']))
        .all())
    # Consulta para obtener la información de carga agrupada por segundos
    resultados_agrupados = {}

    # Utilizamos una sola consulta para mejorar la eficiencia
    resultados_por_escaneo = (
        db.session.query(
            Resultado.id_escaneo,
            Resultado.dominio,
            case(
                (and_(Resultado.e_viewport != 1,
                      Resultado.e_viewport.isnot(None)),
                 'Sin etiqueta viewport'),
                (and_(Resultado.html_valid != 1,
                      Resultado.html_valid.isnot(None)),
                 'Sin estructura HTML valida'),
                (and_(Resultado.responsive_valid != 1,
                      Resultado.responsive_valid.isnot(None)),
                 'No cumple con estándares '),
                (and_(Resultado.valid_aaa != 1,
                      Resultado.valid_aaa.isnot(None)),
                 'No validan con WACG - AAA '),
                else_=
                'Otros motivos'  # Puedes cambiar 'Otra etiqueta' por lo que desees
            ).label('intervalo_carga'),
            func.count().label('count')).filter(
                Resultado.id_escaneo.in_(ids_escaneo_especificos),
                Resultado.codigo_respuesta == 200).
        filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%redirect%')
                )  # Excluir URLs que contengan 'redirect'
        .group_by(Resultado.id_escaneo, 'intervalo_carga',
                  Resultado.dominio).all())

    # Procesamos los resultados para estructurarlos en un diccionario
    for resultado in resultados_por_escaneo:
        id_escaneo = resultado.id_escaneo
        dominio = resultado.dominio
        intervalo_carga = resultado.intervalo_carga
        count = resultado.count

        if id_escaneo not in resultados_agrupados:
            resultados_agrupados[id_escaneo] = []

        resultados_agrupados[id_escaneo].append(
            (dominio, intervalo_carga, count))

    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas
    sumarios = (db.session.query(Sumario).filter(
        Sumario.id_escaneo.in_(ids_escaneo_especificos)).all())

    # Enviamos los resultados al template
    return render_template('tools/seo/metatags.html',
                           dominio_url=dominio,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           resultados=paginas_metatags,
                           detalles=resultados_agrupados,
                           resumen=sumarios,
                           indicador_1=len(paginas_metatags),
                           indicador_2=((len(paginas_metatags) * 100) /
                                        total_paginas),
                           indicador_3=total_paginas)


@app.route('/seo/health')
@login_required
def seo_health_check():
    return render_template('tools/seo/seo_health.html')


@app.route('/seo/posicionamiento')
@login_required
def seo_posicionamiento():
    return render_template('tools/seo/seo_posicionamiento.html')


@app.route('/seo/keywords')
@login_required
def seo_keywords():
    return render_template('tools/seo/seo_keywords.html')


@app.route('/seo/traffic')
@login_required
def seo_traffic():
    return render_template('tools/seo/seo_traffic.html')


@app.route('/seo/competencia')
@login_required
def seo_competencia():
    return render_template('tools/seo/seo_competencia.html')


@app.route('/seo/backlinks')
@login_required
def seo_backlinks():
    return render_template('tools/seo/seo_backlinks.html')


@app.route('/seo/indexing')
@login_required
def seo_indexing():
    return render_template('tools/seo/seo_indexing.html')


@app.route('/seo/resumen')
@login_required
def seo_resumen():

    # dominios_especificos = ["zonnox.net", "mc-mutuadeb.zonnox.net"]

    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas
    sumarios = (db.session.query(Sumario).filter(
        Sumario.dominio.in_(DOMINIOS_ESPECIFICOS)).all())

    # Convertir objetos Sumario a diccionarios
    sumarios_dict = []
    for sumario in sumarios:
        sumario_dict = {}
        for column in class_mapper(Sumario).columns:
            sumario_dict[column.name] = getattr(sumario, column.name)
        sumarios_dict.append(sumario_dict)

    return render_template('resumen.html',
                           sumario=json.dumps(sumarios_dict),
                           dominios=DOMINIOS_ESPECIFICOS)



@app.route('/velocidad/<string:domain>')
@login_required
def velocidad_url(domain):

    # Consulta para obtener las fechas seleccionadas
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(Sumario.dominio == domain).limit(1).all())

    # Obtener los resultados para las fechas seleccionadas
    fechas_seleccionadas = [result[0] for result in results]

    # Consulta para obtener el campo Sumario.total_paginas
    total_paginas_result = db.session.query(Sumario.total_paginas).filter(
        Sumario.fecha == fechas_seleccionadas[0],
        Sumario.dominio == domain).first()

    # Almacenar el valor de Sumario.total_paginas en una variable
    total_paginas = total_paginas_result[0] if total_paginas_result else None

    #.filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))

    # Consulta para obtener las páginas de la tabla Resultados con código de respuesta 200 y tiempo de respuesta mayor que 0
    paginas_velocidad = (
        db.session.query(
            Resultado.fecha_escaneo,
            Resultado.dominio,
            Resultado.tipo_documento,
            Resultado.tiempo_respuesta,
            Resultado.pagina,
            Resultado.lang,
            Resultado.imagenes,
            Resultado.images_1MB,
            Resultado.image_types,
            Resultado.id  #is_pdf
        ).filter(
            #Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.dominio==domain,
            Resultado.codigo_respuesta == 200,
            Resultado.tiempo_respuesta > .7,
            Resultado.tiempo_respuesta.isnot(
                None),  # Filtrar resultados con tiempo_respuesta no nulo
            Resultado.tiempo_respuesta != '',
            Resultado.tiempo_respuesta.isnot(
                False)  #,  # Filtrar resultados con tiempo_respuesta False
            #Resultado.tiempo_respuesta.isnot(None)
            #~func.isnan(Resultado.tiempo_respuesta),  # Filtrar resultados que no sean números (nan)
        )
        #.filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        #.filter(Resultado.lang.in_(['es','ca','en','fr']))
        .filter(func.date(
            Resultado.fecha_escaneo).in_(fechas_seleccionadas)).all())
    # Consulta para obtener la información de carga agrupada por segundos
    cargas_por_segundos = {}
    cargas_por_segundos_dos = {}
    resultados_agrupados = {}

    resultados_por_escaneo = (
        db.session.query(
            Resultado.id_escaneo,
            Resultado.dominio,
            #Resultado.codigo_respuesta == 404,
            case(
                # (Resultado.codigo_respuesta == 200, 'Correctos'),
                # (Resultado.codigo_respuesta == 404, 'Rotos'),
                # (Resultado.codigo_respuesta == 500, 'Error del servidor'),
                # (Resultado.codigo_respuesta == 503, '503'),
                (Resultado.pagina.like('%#%'), 'No existe internos'),
                (Resultado.pagina.like('%redirect=%'), 'Redirección errónea'),
                (Resultado.pagina.like('%?%'), 'Dinamicos'),
                (Resultado.pagina.like('%pdf%'), 'Enlace a un documento'),
                (Resultado.pagina.like('%estaticos%'),
                 'Archivo estatico falta'),
                (Resultado.pagina.like('%assets%'), 'Asset de la wb falta'),
                (Resultado.pagina.like('%extranet%'), 'Roto en extranet'),
                (Resultado.pagina.like('%intranet%'), 'Roto en intranet'),
                (Resultado.pagina.like('%visor%'), 'intranet'),
                else_=
                'otro tipo'  # Puedes cambiar 'Otra etiqueta' por lo que desees
            ).label('intervalo_carga'),
            func.count().label('count')).filter(
                #Resultado.dominio.in_(DOMINIOS_ESPECIFICOS),
                Resultado.id_escaneo.in_(IDS_ESCANEO),
                Resultado.codigo_respuesta == 200,
                Resultado.tiempo_respuesta >= 1)
        #.filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))
        #.filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        .group_by(Resultado.id_escaneo, 'intervalo_carga',
                  Resultado.dominio).all())

    # Procesamos los resultados para estructurarlos en un diccionario
    for resultado in resultados_por_escaneo:
        id_escaneo = resultado.id_escaneo
        dominio = resultado.dominio
        intervalo_carga = resultado.intervalo_carga
        count = resultado.count

        if id_escaneo not in resultados_agrupados:
            resultados_agrupados[id_escaneo] = []

        resultados_agrupados[id_escaneo].append(
            (dominio, intervalo_carga, count))

    # Utilizamos una sola consulta para mejorar la eficiencia
    resultados_por_escaneo = (
        db.session.query(
            Resultado.id_escaneo, Resultado.dominio,
            case((Resultado.tiempo_respuesta < 1, 'Menos de 1 segundo'),
                 ((Resultado.tiempo_respuesta >= 1) &
                  (Resultado.tiempo_respuesta <= 3), '1 a 3 segundos'),
                 ((Resultado.tiempo_respuesta > 3) &
                  (Resultado.tiempo_respuesta <= 7), '3 a 7 segundos'),
                 ((Resultado.tiempo_respuesta > 7) &
                  (Resultado.tiempo_respuesta <= 15), '7 a 15 segundos'),
                 ((Resultado.tiempo_respuesta > 15) &
                  (Resultado.tiempo_respuesta <= 30), '15 a 30 segundos'),
                 ((Resultado.tiempo_respuesta > 30) &
                  (Resultado.tiempo_respuesta <= 60), '30 a 60 segundos'),
                 ((Resultado.tiempo_respuesta > 60) &
                  (Resultado.tiempo_respuesta <= 90), '60 a 90 segundos'),
                 ((Resultado.tiempo_respuesta > 90) &
                  (Resultado.tiempo_respuesta <= 180), '90 a 180 segundos'),
                 else_='Tiempo desconocido').label('intervalo_carga'),
            func.count().label('count')).filter(
                #Resultado.dominio.in_(DOMINIOS_ESPECIFICOS),
                Resultado.id_escaneo.in_(IDS_ESCANEO),
                Resultado.codigo_respuesta == 200)

        #.filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        #.filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))
        .group_by(Resultado.id_escaneo, 'intervalo_carga',
                  Resultado.dominio).all())

    # Procesamos los resultados para estructurarlos en un diccionario
    for resultado in resultados_por_escaneo:
        id_escaneo = resultado.id_escaneo
        dominio = resultado.dominio
        intervalo_carga = resultado.intervalo_carga
        count = resultado.count

        if id_escaneo not in cargas_por_segundos:
            cargas_por_segundos[id_escaneo] = []

        cargas_por_segundos[id_escaneo].append(
            (dominio, intervalo_carga, count))

    # Utilizamos una sola consulta para mejorar la eficiencia
    resultados_por_escaneo = (
        db.session.query(
            Resultado.id_escaneo, Resultado.dominio,
            case((Resultado.is_pdf == 1, 'Documentos, pdf, assets, estaticos'),
                 (Resultado.is_pdf == 2, 'Paginas web, html'),
                 (Resultado.is_pdf == 0, 'Desconocido'),
                 (Resultado.is_pdf == -1, 'Excluido'),
                 else_='Otros').label('intervalo_carga'),
            func.count().label('count')).filter(
                #Resultado.dominio.in_(DOMINIOS_ESPECIFICOS),
                Resultado.id_escaneo.in_(IDS_ESCANEO),
                Resultado.codigo_respuesta == 200,
                Resultado.tiempo_respuesta >= 1)

        #.filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        #.filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))
        .group_by(Resultado.id_escaneo, 'intervalo_carga',
                  Resultado.dominio).all())

    # Procesamos los resultados para estructurarlos en un diccionario
    for resultado in resultados_por_escaneo:
        id_escaneo = resultado.id_escaneo
        dominio = resultado.dominio
        intervalo_carga = resultado.intervalo_carga
        count = resultado.count

        if id_escaneo not in cargas_por_segundos_dos:
            cargas_por_segundos_dos[id_escaneo] = []

        cargas_por_segundos_dos[id_escaneo].append(
            (dominio, intervalo_carga, count))

    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas
    sumarios = (db.session.query(Sumario).filter(
        Sumario.id_escaneo.in_(IDS_ESCANEO)).all())

    # Convertir objetos Sumario a diccionarios
    sumarios_dict = []
    for sumario in sumarios:
        sumario_dict = {}
        for column in class_mapper(Sumario).columns:
            sumario_dict[column.name] = getattr(sumario, column.name)
        sumarios_dict.append(sumario_dict)

    # Consulta para obtener las filas correspondientes de la tabla Sumario
    evoluciones = (
        db.session.query(Sumario)  #.dominio, Sumario.total_404, Sumario.fecha)
        .all())

    # Convertir objetos Sumario a diccionarios
    evoluciones_dict = []
    for evolucion in evoluciones:
        evolucion_dict = {}
        for column in class_mapper(Sumario).columns:
            evolucion_dict[column.name] = getattr(evolucion, column.name)
        evoluciones_dict.append(evolucion_dict)

    # Enviamos los resultados al template
    return render_template('tools/seo/velocidad.html',
                           dominio_url = domain,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           graficos=json.dumps(sumarios_dict),
                           evolucion=json.dumps(evoluciones_dict),
                           resultados=paginas_velocidad,
                           detalles_tres=resultados_agrupados,
                           detalles_dos=cargas_por_segundos_dos,
                           detalles=cargas_por_segundos,
                           resumen=sumarios,
                           sumario=json.dumps(sumarios_dict),
                           indicador_1=len(paginas_velocidad),
                           indicador_2=((len(paginas_velocidad) * 100) / total_paginas),
                           indicador_3=total_paginas)


@app.route('/enlaces-rotos')
@login_required
def enlaces_rotos():
    # IDs de escaneo específicos
    #ids_escaneo_especificos = ['4b99956ba942f7986ccc2e5c992c3a2a111385bfdbbfa2223818c6a8d9e28510',\
    #    '41038960d6084d0e2ba5416c0c2a52777cc40e119b7c69fb0aeaa4b8231cd2e0',\
    #    '5b485f2d386e81e56d67e6f1663d7d965f69985e11d771e56b0caf6f5ecb0849'
    #  ]  # Reemplaza con los IDs específicos que se proporcionarán

    #ids_escaneo_especificos = IDS_ESCANEO

    # Modificar la consulta para seleccionar las 7 últimas fechas sin repetir
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).limit(1).all())

    # Obtener los resultados para las fechas seleccionadas
    fechas_seleccionadas = [result[0] for result in results]

    #.filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))

    #print(fechas_seleccionadas)
    #
    # Consulta principal para obtener todas las URLs que coincidan con los IDs de escaneo proporcionados
    results = (
        db.session.query(Resultado).filter(
            Resultado.codigo_respuesta == 404).filter(
                Resultado.dominio.in_(DOMINIOS_ESPECIFICOS)).filter(
                    func.date(
                        Resultado.fecha_escaneo).in_(fechas_seleccionadas))
        #.filter(Resultado.id_escaneo.in_(ids_escaneo_especificos))
        .filter(
            ~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%redirect%')
                )  # Excluir URLs que contengan 'redirect'
        .all())

    # Consulta para obtener la información de carga agrupada por segundos
    resultados_agrupados = {}
    resultados_agrupados_dos = {}

    resultados_por_escaneo = (
        db.session.query(
            Resultado.id_escaneo,
            Resultado.dominio,
            #Resultado.codigo_respuesta == 404,
            case(
                # (Resultado.codigo_respuesta == 200, 'Correctos'),
                # (Resultado.codigo_respuesta == 404, 'Rotos'),
                # (Resultado.codigo_respuesta == 500, 'Error del servidor'),
                # (Resultado.codigo_respuesta == 503, '503'),
                (Resultado.pagina.like('%#%'), 'Interno'),
                (Resultado.pagina.like('%redirect=%'), 'Redirección'),
                (Resultado.pagina.like('%?%'), 'Dinamicos'),
                (Resultado.pagina.like('%pdf%'), 'PDF - DOC'),
                (Resultado.pagina.like('%estaticos%'), 'Estático'),
                (Resultado.pagina.like('%assets%'), 'Asset'),
                (Resultado.pagina.like('%extranet%'), 'Extranet'),
                (Resultado.pagina.like('%intranet%'), 'Intranet'),
                (Resultado.pagina.like('%visor%'), 'Visor'),
                else_='HTML'  # Puedes cambiar 'Otra etiqueta' por lo que desees
            ).label('intervalo_carga'),
            func.count().label('count')).filter(
                Resultado.id_escaneo.in_(IDS_ESCANEO),
                Resultado.codigo_respuesta == 404)
        #.filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        .group_by(Resultado.id_escaneo, 'intervalo_carga',
                  Resultado.dominio).all())

    # Procesamos los resultados para estructurarlos en un diccionario
    for resultado in resultados_por_escaneo:
        id_escaneo = resultado.id_escaneo
        dominio = resultado.dominio
        intervalo_carga = resultado.intervalo_carga
        count = resultado.count

        if id_escaneo not in resultados_agrupados:
            resultados_agrupados[id_escaneo] = []

        resultados_agrupados[id_escaneo].append(
            (dominio, intervalo_carga, count))

    # Utilizamos una sola consulta para mejorar la eficiencia
    resultados_por_escaneo = (
        db.session.query(
            Resultado.id_escaneo, Resultado.dominio,
            case((Resultado.enlaces_inseguros >= 1, 'Enlaces inseguros'),
                 else_='Otros').label('intervalo_carga'),
            func.count().label('count')).filter(
                Resultado.id_escaneo.in_(ids_escaneo_especificos),
                Resultado.codigo_respuesta == 404)

        #.filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        .group_by(Resultado.id_escaneo, 'intervalo_carga',
                  Resultado.dominio).all())

    # Procesamos los resultados para estructurarlos en un diccionario
    for resultado in resultados_por_escaneo:
        id_escaneo = resultado.id_escaneo
        dominio = resultado.dominio
        intervalo_carga = resultado.intervalo_carga
        count = resultado.count

        if id_escaneo not in resultados_agrupados_dos:
            resultados_agrupados_dos[id_escaneo] = []

        resultados_agrupados_dos[id_escaneo].append(
            (dominio, intervalo_carga, count))

    # Consulta para obtener las filas correspondientes de la tabla Sumario
    sumarios = (db.session.query(Sumario).filter(
        Sumario.id_escaneo.in_(ids_escaneo_especificos)).all())

    # Convertir objetos Sumario a diccionarios
    sumarios_dict = []
    for sumario in sumarios:
        sumario_dict = {}
        for column in class_mapper(Sumario).columns:
            sumario_dict[column.name] = getattr(sumario, column.name)
        sumarios_dict.append(sumario_dict)

    # Consulta para obtener las filas correspondientes de la tabla Sumario
    evoluciones = (
        db.session.query(Sumario)  #.dominio, Sumario.total_404, Sumario.fecha)
        .all())

    # Convertir objetos Sumario a diccionarios
    evoluciones_dict = []
    for evolucion in evoluciones:
        evolucion_dict = {}
        for column in class_mapper(Sumario).columns:
            evolucion_dict[column.name] = getattr(evolucion, column.name)
        evoluciones_dict.append(evolucion_dict)

    # Envía los resultados al template
    return render_template('tools/usa/enlaces_rotos.html',
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           evolucion=json.dumps(evoluciones_dict),
                           resultados=results,
                           resumen=sumarios,
                           detalles=resultados_agrupados,
                           detalles_dos=resultados_agrupados_dos,
                           graficos=json.dumps(sumarios_dict))


@app.route('/enlaces-rotos/<string:domain>')
@login_required
def enlaces_rotos_dominio(domain):

    # Consulta para obtener las fechas seleccionadas
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(Sumario.dominio == domain).limit(1).all())

    # Obtener los resultados para las fechas seleccionadas
    fechas_seleccionadas = [result[0] for result in results]

    # Consulta para obtener el campo Sumario.total_paginas
    total_paginas_result = db.session.query(Sumario.total_paginas).filter(
        Sumario.fecha == fechas_seleccionadas[0],
        Sumario.dominio == domain).first()

    # Almacenar el valor de Sumario.total_paginas en una variable
    total_paginas = total_paginas_result[0] if total_paginas_result else None

    #.filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))

    #print(fechas_seleccionadas)
    #
    # Consulta principal para obtener todas las URLs que coincidan con los IDs de escaneo proporcionados
    results = (
        db.session.query(Resultado).filter(
            Resultado.codigo_respuesta == 404).filter(
                Resultado.dominio == domain).filter(
                    func.date(
                        Resultado.fecha_escaneo).in_(fechas_seleccionadas))
        #.filter(Resultado.id_escaneo.in_(ids_escaneo_especificos))
        #.filter(
        #    ~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        .all())

    # Consulta para obtener la información de carga agrupada por segundos
    resultados_agrupados = {}
    resultados_agrupados_dos = {}

    resultados_por_escaneo = (
        db.session.query(
            Resultado.id_escaneo,
            Resultado.dominio,
            #Resultado.codigo_respuesta == 404,
            case(
                # (Resultado.codigo_respuesta == 200, 'Correctos'),
                # (Resultado.codigo_respuesta == 404, 'Rotos'),
                # (Resultado.codigo_respuesta == 500, 'Error del servidor'),
                # (Resultado.codigo_respuesta == 503, '503'),
                (Resultado.pagina.like('%#%'), 'Interno'),
                (Resultado.pagina.like('%redirect=%'), 'Redirección'),
                (Resultado.pagina.like('%?%'), 'Dinamicos'),
                (Resultado.pagina.like('%pdf%'), 'PDF - DOC'),
                (Resultado.pagina.like('%estaticos%'), 'Estático'),
                (Resultado.pagina.like('%assets%'), 'Asset'),
                (Resultado.pagina.like('%extranet%'), 'Extranet'),
                (Resultado.pagina.like('%intranet%'), 'Intranet'),
                (Resultado.pagina.like('%visor%'), 'Visor'),
                else_='HTML'  # Puedes cambiar 'Otra etiqueta' por lo que desees
            ).label('intervalo_carga'),
            func.count().label('count')).filter(
                Resultado.id_escaneo.in_(IDS_ESCANEO),
                Resultado.codigo_respuesta == 404, Resultado.dominio == domain)
        #.filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        .group_by(Resultado.id_escaneo, 'intervalo_carga',
                  Resultado.dominio).all())

    # Procesamos los resultados para estructurarlos en un diccionario
    for resultado in resultados_por_escaneo:
        id_escaneo = resultado.id_escaneo
        dominio = resultado.dominio
        intervalo_carga = resultado.intervalo_carga
        count = resultado.count

        if id_escaneo not in resultados_agrupados:
            resultados_agrupados[id_escaneo] = []

        resultados_agrupados[id_escaneo].append(
            (dominio, intervalo_carga, count))

    # Utilizamos una sola consulta para mejorar la eficiencia
    resultados_por_escaneo = (
        db.session.query(
            Resultado.id_escaneo, Resultado.dominio,
            case((Resultado.enlaces_inseguros >= 1, 'Enlaces inseguros'),
                 else_='Otros').label('intervalo_carga'),
            func.count().label('count')).filter(
                Resultado.id_escaneo.in_(ids_escaneo_especificos),
                Resultado.codigo_respuesta == 404, Resultado.dominio == domain)

        #.filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        .group_by(Resultado.id_escaneo, 'intervalo_carga',
                  Resultado.dominio).all())

    # Procesamos los resultados para estructurarlos en un diccionario
    for resultado in resultados_por_escaneo:
        id_escaneo = resultado.id_escaneo
        dominio = resultado.dominio
        intervalo_carga = resultado.intervalo_carga
        count = resultado.count

        if id_escaneo not in resultados_agrupados_dos:
            resultados_agrupados_dos[id_escaneo] = []

        resultados_agrupados_dos[id_escaneo].append(
            (dominio, intervalo_carga, count))

    # Consulta para obtener las filas correspondientes de la tabla Sumario
    sumarios = (db.session.query(Sumario).filter(
        Sumario.dominio == domain).filter(
            Sumario.id_escaneo.in_(ids_escaneo_especificos)).all())

    # Convertir objetos Sumario a diccionarios
    sumarios_dict = []
    for sumario in sumarios:
        sumario_dict = {}
        for column in class_mapper(Sumario).columns:
            sumario_dict[column.name] = getattr(sumario, column.name)
        sumarios_dict.append(sumario_dict)

    # Consulta para obtener las filas correspondientes de la tabla Sumario
    evoluciones = (
        db.session.query(Sumario)  #.dominio, Sumario.total_404, Sumario.fecha
        .filter(Sumario.dominio == domain).all())

    # Convertir objetos Sumario a diccionarios
    evoluciones_dict = []
    for evolucion in evoluciones:
        evolucion_dict = {}
        for column in class_mapper(Sumario).columns:
            evolucion_dict[column.name] = getattr(evolucion, column.name)
        evoluciones_dict.append(evolucion_dict)

    # Envía los resultados al template
    return render_template('tools/usa/enlaces_rotos.html',
                           dominio_url=domain,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           evolucion=json.dumps(evoluciones_dict),
                           resultados=results,
                           resumen=sumarios,
                           detalles=resultados_agrupados,
                           detalles_dos=resultados_agrupados_dos,
                           graficos=json.dumps(sumarios_dict),
                           indicador_1=len(results),
                           indicador_2=((len(results) * 100) / total_paginas),
                           indicador_3=total_paginas)


@app.route('/usabilidad/broken-links')
@login_required
def usa_broken_links():
    return render_template('tools/usa/usa_broken_links.html')


@app.route('/usabilidad/font-colors')
@login_required
def usa_font_colors():
    return render_template('tools/usa/usa_font_colors.html')


@app.route('/usabilidad/form')
@login_required
def usa_form():
    return render_template('tools/usa/usa_form.html')


@app.route('/usabilidad/nav')
@login_required
def usa_nav():
    return render_template('tools/usa/usa_nav.html')

@app.route('/titulos/<string:dominio>')
@login_required
def titulos(dominio):
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == dominio).limit(1).all())

    # Obtener los resultados para las fechas seleccionadas
    fechas_seleccionadas = [result[0] for result in results]

    # Consulta para obtener el campo Sumario.total_paginas
    total_paginas_result = db.session.query(Sumario.total_paginas).filter(
        Sumario.fecha == fechas_seleccionadas[0],
        Sumario.dominio == dominio).first()

    # Almacenar el valor de Sumario.total_paginas en una variable
    total_paginas = total_paginas_result[0] if total_paginas_result else None

    #.filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))

    # Consulta para obtener las páginas de la tabla Resultados con código de respuesta 200 y tiempo de respuesta mayor que 0
    paginas_titulos = (
        db.session.query(
            Resultado.fecha_escaneo,
            Resultado.dominio,
            Resultado.pagina,
            Resultado.lang,
            Resultado.e_title,
            Resultado.title_long,
            Resultado.title_short,
            Resultado.id,
            Resultado.title_duplicate,
            Resultado.titulos_pagina_menos_30_caracteres,
            Resultado.titulos_pagina_mas_60_caracteres,
            Resultado.titulos_pagina_igual_h1,
            Resultado.titulos_pagina_duplicado,
            Resultado.c_title,
            Resultado.meta_tags
        ).filter(
            #Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.dominio == dominio,
            Resultado.codigo_respuesta == 200,
            Resultado.e_title != 1 or Resultado.title_long != 0
            or Resultado.title_short != 0 or Resultado.title_duplicate != 0 or Resultado.titulos_pagina_duplicado != 0 or Resultado.titulos_pagina_igual_h1 != 0
            #Resultado.tiempo_respuesta > 0,
            #Resultado.tiempo_respuesta.isnot(None),  # Filtrar resultados con tiempo_respuesta no nulo
            #Resultado.tiempo_respuesta != '',
            #Resultado.tiempo_respuesta.isnot(False) #,  # Filtrar resultados con tiempo_respuesta False
            #Resultado.tiempo_respuesta.isnot(None)
            #~func.isnan(Resultado.tiempo_respuesta),  # Filtrar resultados que no sean números (nan)
        )
        #.filter(
        #    ~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        #.filter(
        #    ~Resultado.pagina.like('%pdf%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%/documents/%')
        #        )  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%/document_library/%')
        #        )  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%redirect%')
        #        )  # Excluir URLs que contengan 'redirect'
        .filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))
        .filter(
            Resultado.tipo_documento.like('%text%'))
        #.filter(Resultado.lang.in_(['es','ca','en','fr']))
        .all())
    # Consulta para obtener la información de carga agrupada por segundos
    resultados_agrupados = {}

    # Utilizamos una sola consulta para mejorar la eficiencia
    resultados_por_escaneo = (
        db.session.query(
            Resultado.id_escaneo,
            Resultado.dominio,
            case(
                (and_(Resultado.e_viewport != 1,
                      Resultado.e_viewport.isnot(None)),
                 'Sin etiqueta viewport'),
                (and_(Resultado.html_valid != 1,
                      Resultado.html_valid.isnot(None)),
                 'Sin estructura HTML valida'),
                (and_(Resultado.responsive_valid != 1,
                      Resultado.responsive_valid.isnot(None)),
                 'No cumple con estándares '),
                (and_(Resultado.valid_aaa != 1,
                      Resultado.valid_aaa.isnot(None)),
                 'No validan con WACG - AAA '),
                else_=
                'Otros motivos'  # Puedes cambiar 'Otra etiqueta' por lo que desees
            ).label('intervalo_carga'),
            func.count().label('count')).filter(
                Resultado.id_escaneo.in_(ids_escaneo_especificos),
                Resultado.codigo_respuesta == 200).
        filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%redirect%')
                )  # Excluir URLs que contengan 'redirect'
        .group_by(Resultado.id_escaneo, 'intervalo_carga',
                  Resultado.dominio).all())

    # Procesamos los resultados para estructurarlos en un diccionario
    for resultado in resultados_por_escaneo:
        id_escaneo = resultado.id_escaneo
        dominio = resultado.dominio
        intervalo_carga = resultado.intervalo_carga
        count = resultado.count

        if id_escaneo not in resultados_agrupados:
            resultados_agrupados[id_escaneo] = []

        resultados_agrupados[id_escaneo].append(
            (dominio, intervalo_carga, count))

    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas
    sumarios = (db.session.query(Sumario).filter(
        Sumario.id_escaneo.in_(ids_escaneo_especificos)).all())

    # Enviamos los resultados al template
    return render_template('tools/usa/titulos.html',
                           dominio_url=dominio,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           resultados=paginas_titulos,
                           detalles=resultados_agrupados,
                           resumen=sumarios,
                           indicador_1=len(paginas_titulos),
                           indicador_2=((len(paginas_titulos) * 100) /
                                        total_paginas),
                           indicador_3=total_paginas)


@app.route('/responsive/<string:dominio>')
@login_required
def responsive(dominio):

# Modificar la consulta para seleccionar las 7 últimas fechas sin repetir
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == dominio).limit(1).all())

    # Obtener los resultados para las fechas seleccionadas
    fechas_seleccionadas = [result[0] for result in results]

    # Consulta para obtener el campo Sumario.total_paginas
    total_paginas_result = db.session.query(Sumario.total_paginas).filter(
        Sumario.fecha == fechas_seleccionadas[0],
        Sumario.dominio == dominio).first()

    # Almacenar el valor de Sumario.total_paginas en una variable
    total_paginas = total_paginas_result[0] if total_paginas_result else None

    #.filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))

    # Consulta para obtener las páginas de la tabla Resultados con código de respuesta 200 y tiempo de respuesta mayor que 0
    paginas_responsive = (
        db.session.query(
            Resultado.fecha_escaneo,
            Resultado.dominio,
            Resultado.pagina,
            Resultado.lang,
            Resultado.e_viewport,
            Resultado.html_valid,
            Resultado.responsive_valid,
            Resultado.id,
            Resultado.valid_aaa,
            Resultado.meta_tags  #is_pdf
        ).filter(
            #Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.dominio == dominio,
            Resultado.codigo_respuesta == 200,
            Resultado.e_viewport != 1 or Resultado.html_valid != 1
            or Resultado.responsive_valid != 1
            #Resultado.tiempo_respuesta > 0,
            #Resultado.tiempo_respuesta.isnot(None),  # Filtrar resultados con tiempo_respuesta no nulo
            #Resultado.tiempo_respuesta != '',
            #Resultado.tiempo_respuesta.isnot(False) #,  # Filtrar resultados con tiempo_respuesta False
            #Resultado.tiempo_respuesta.isnot(None)
            #~func.isnan(Resultado.tiempo_respuesta),  # Filtrar resultados que no sean números (nan)
        )
        #.filter(
        #    ~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        #.filter(
        #    ~Resultado.pagina.like('%pdf%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%/documents/%')
        #        )  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%/document_library/%')
        #        )  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%redirect%')
        #        )  # Excluir URLs que contengan 'redirect'
        .filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))
        .filter(
            Resultado.tipo_documento.like('%text%'))
        #.filter(Resultado.lang.in_(['es','ca','en','fr']))
        .all())
    # Consulta para obtener la información de carga agrupada por segundos
    resultados_agrupados = {}

    # Utilizamos una sola consulta para mejorar la eficiencia
    resultados_por_escaneo = (
        db.session.query(
            Resultado.id_escaneo,
            Resultado.dominio,
            case(
                (and_(Resultado.e_viewport != 1,
                      Resultado.e_viewport.isnot(None)),
                 'Sin etiqueta viewport'),
                (and_(Resultado.html_valid != 1,
                      Resultado.html_valid.isnot(None)),
                 'Sin estructura HTML valida'),
                (and_(Resultado.responsive_valid != 1,
                      Resultado.responsive_valid.isnot(None)),
                 'No cumple con estándares '),
                (and_(Resultado.valid_aaa != 1,
                      Resultado.valid_aaa.isnot(None)),
                 'No validan con WACG - AAA '),
                else_=
                'Otros motivos'  # Puedes cambiar 'Otra etiqueta' por lo que desees
            ).label('intervalo_carga'),
            func.count().label('count')).filter(
                Resultado.id_escaneo.in_(ids_escaneo_especificos),
                Resultado.codigo_respuesta == 200).
        filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%redirect%')
                )  # Excluir URLs que contengan 'redirect'
        .group_by(Resultado.id_escaneo, 'intervalo_carga',
                  Resultado.dominio).all())

    # Procesamos los resultados para estructurarlos en un diccionario
    for resultado in resultados_por_escaneo:
        id_escaneo = resultado.id_escaneo
        dominio = resultado.dominio
        intervalo_carga = resultado.intervalo_carga
        count = resultado.count

        if id_escaneo not in resultados_agrupados:
            resultados_agrupados[id_escaneo] = []

        resultados_agrupados[id_escaneo].append(
            (dominio, intervalo_carga, count))

    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas
    sumarios = (db.session.query(Sumario).filter(
        Sumario.id_escaneo.in_(ids_escaneo_especificos)).all())

    # Enviamos los resultados al template
    return render_template('tools/acc/responsive.html',
                            dominio_url=dominio,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           resultados=paginas_responsive,
                           detalles=resultados_agrupados,
                           resumen=sumarios,
                           indicador_1=len(paginas_responsive),
                           indicador_2=((len(paginas_responsive) * 100) /
                                        total_paginas),
                           indicador_3=total_paginas)


@app.route('/seguridad/<string:dominio>')
@login_required
def seguridad(dominio):
    # Modificar la consulta para seleccionar las 7 últimas fechas sin repetir
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == dominio).limit(1).all())

    # Obtener los resultados para las fechas seleccionadas
    fechas_seleccionadas = [result[0] for result in results]

    # Consulta para obtener el campo Sumario.total_paginas
    total_paginas_result = db.session.query(Sumario.total_paginas).filter(
        Sumario.fecha == fechas_seleccionadas[0],
        Sumario.dominio == dominio).first()

    # Almacenar el valor de Sumario.total_paginas en una variable
    total_paginas = total_paginas_result[0] if total_paginas_result else None

    #.filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))

    # Consulta para obtener las páginas de la tabla Resultados con código de respuesta 200 y tiempo de respuesta mayor que 0
    seguridad_results = (
        db.session.query(
            Resultado.fecha_escaneo,
            Resultado.dominio,
            Resultado.pagina,
            Resultado.lang,
            Resultado.falta_encabezado_x_content_type_options,
            Resultado.falta_encabezado_secure_referrer_policy,
            Resultado.falta_encabezado_x_frame_options,
            Resultado.version_http,
            Resultado.enlaces_inseguros,
            Resultado.id,
            Resultado.tipo_documento,
            Resultado.meta_tags  #is_pdf
        ).filter(
            #Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.dominio == dominio,
            Resultado.codigo_respuesta == 200,
            Resultado.falta_encabezado_x_content_type_options != 0 or Resultado.falta_encabezado_secure_referrer_policy != 0 or Resultado.falta_encabezado_x_frame_options != 0
            #Resultado.tiempo_respuesta > 0,
            #Resultado.tiempo_respuesta.isnot(None),  # Filtrar resultados con tiempo_respuesta no nulo
            #Resultado.wcagaaa != [] or Resultado.wcagaaa != {} or Resultado.wcagaaa != {"pa11y_results": []}
            #Resultado.errores_ortograficos == False #,  # Filtrar resultados con tiempo_respuesta False
            #Resultado.tiempo_respuesta.isnot(None)
            #~func.isnan(Resultado.tiempo_respuesta),  # Filtrar resultados que no sean números (nan)
        ).filter(
            ~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(
            ~Resultado.pagina.like('%pdf%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%/asset_publisher/%')
                )  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%/document_library/%')
                )  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%estaticos%')
                )  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%/document_library/%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%redirect%')
                )  # Excluir URLs que contengan 'redirect'
        .filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))
        #.filter(Resultado.lang.in_(['es','ca','en','fr']))
        .all())

    return render_template('tools/diag/seguridad.html',
                           dominio_url=dominio,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           resultados=seguridad_results,
                           indicador_1=len(seguridad_results),
                           indicador_2=((len(seguridad_results) * 100) /
                                        total_paginas),
                           indicador_3=total_paginas)


@app.route('/imagenes/<string:dominio>')
@login_required
def imagenes(dominio):
    # Modificar la consulta para seleccionar las 7 últimas fechas sin repetir
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == dominio).limit(1).all())

    # Obtener los resultados para las fechas seleccionadas
    fechas_seleccionadas = [result[0] for result in results]

    # Consulta para obtener el campo Sumario.total_paginas
    total_paginas_result = db.session.query(Sumario.total_paginas).filter(
        Sumario.fecha == fechas_seleccionadas[0],
        Sumario.dominio == dominio).first()

    # Almacenar el valor de Sumario.total_paginas en una variable
    total_paginas = total_paginas_result[0] if total_paginas_result else None

    #.filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))

    # Consulta para obtener las páginas de la tabla Resultados con código de respuesta 200 y tiempo de respuesta mayor que 0
    imagenes_results = (
        db.session.query(
            Resultado.fecha_escaneo,
            Resultado.dominio,
            Resultado.pagina,
            Resultado.alt_vacias,
            Resultado.image_types,
            Resultado.tiempo_respuesta,
            Resultado.images_1MB,
            Resultado.imagenes_rotas,
            Resultado.id,
            Resultado.tipo_documento,
            Resultado.imagenes  #is_pdf
        ).filter(
            #Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.dominio == dominio,
            Resultado.codigo_respuesta == 200,
            Resultado.imagenes_rotas != 0 or Resultado.alt_vacias != 0
            
            #Resultado.tiempo_respuesta.isnot(None),  # Filtrar resultados con tiempo_respuesta no nulo
            #Resultado.wcagaaa != [] or Resultado.wcagaaa != {} or Resultado.wcagaaa != {"pa11y_results": []}
            #Resultado.errores_ortograficos == False #,  # Filtrar resultados con tiempo_respuesta False
            #Resultado.tiempo_respuesta.isnot(None)
            #~func.isnan(Resultado.tiempo_respuesta),  # Filtrar resultados que no sean números (nan)
        ).filter(
            ~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(
            Resultado.tipo_documento.like('%text%'))
        .filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))
        #.filter(Resultado.lang.in_(['es','ca','en','fr']))
        .all())

    return render_template('tools/acc/imagenes.html',
                           dominio_url=dominio,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           resultados=imagenes_results,
                           indicador_1=len(imagenes_results),
                           indicador_2=((len(imagenes_results) * 100) /
                                        total_paginas),
                           indicador_3=total_paginas)



@app.route('/legibilidad/<string:dominio>')
@login_required
def legibilidad(dominio):
    # Modificar la consulta para seleccionar las 7 últimas fechas sin repetir
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == dominio).limit(1).all())

    # Obtener los resultados para las fechas seleccionadas
    fechas_seleccionadas = [result[0] for result in results]

    # Consulta para obtener el campo Sumario.total_paginas
    total_paginas_result = db.session.query(Sumario.total_paginas).filter(
        Sumario.fecha == fechas_seleccionadas[0],
        Sumario.dominio == dominio).first()

    # Almacenar el valor de Sumario.total_paginas en una variable
    total_paginas = total_paginas_result[0] if total_paginas_result else None

    #.filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))

    # Consulta para obtener las páginas de la tabla Resultados con código de respuesta 200 y tiempo de respuesta mayor que 0
    legibilidad_results = (
        db.session.query(
            Resultado.fecha_escaneo,
            Resultado.dominio,
            Resultado.pagina,
            Resultado.lang,
            Resultado.num_palabras,
            Resultado.frases,
            Resultado.media_palabras_frase,
            Resultado.flesh_score,
            Resultado.num_errores_ortograficos,
            Resultado.id,
            Resultado.tipo_documento,
            Resultado.content_valid  #is_pdf
        ).filter(
            #Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.dominio == dominio,
            Resultado.codigo_respuesta == 200,
            #Resultado.tiempo_respuesta > 0,
            #Resultado.tiempo_respuesta.isnot(None),  # Filtrar resultados con tiempo_respuesta no nulo
            #Resultado.wcagaaa != [] or Resultado.wcagaaa != {} or Resultado.wcagaaa != {"pa11y_results": []}
            #Resultado.errores_ortograficos == False #,  # Filtrar resultados con tiempo_respuesta False
            #Resultado.tiempo_respuesta.isnot(None)
            #~func.isnan(Resultado.tiempo_respuesta),  # Filtrar resultados que no sean números (nan)
        ).filter(
            ~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(
            Resultado.tipo_documento.like('%text%'))
        .filter(
            ~Resultado.pagina.like('%pdf%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%/asset_publisher/%')
                )  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%/document_library/%')
                )  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%estaticos%')
                )  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%/document_library/%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%redirect%')
                )  # Excluir URLs que contengan 'redirect'
        .filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))
        #.filter(Resultado.lang.in_(['es','ca','en','fr']))
        .all())

    return render_template('tools/acc/legibilidad.html',
                           dominio_url=dominio,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           resultados=legibilidad_results,
                           indicador_1=len(legibilidad_results),
                           indicador_2=((len(legibilidad_results) * 100) /
                                        total_paginas),
                           indicador_3=total_paginas)


@app.route('/usabilidad/w3c')
@login_required
def usa_w3c():
    return render_template('tools/usa/usa_w3c.html')


@app.route('/analisis-aaa/<string:dominio>')
@login_required
def analisis_aaa(dominio):

    # Modificar la consulta para seleccionar las 7 últimas fechas sin repetir
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == dominio).limit(1).all())

    # Obtener los resultados para las fechas seleccionadas
    fechas_seleccionadas = [result[0] for result in results]

    # Consulta para obtener el campo Sumario.total_paginas
    total_paginas_result = db.session.query(Sumario.total_paginas).filter(
        Sumario.fecha == fechas_seleccionadas[0],
        Sumario.dominio == dominio).first()

    # Almacenar el valor de Sumario.total_paginas en una variable
    total_paginas = total_paginas_result[0] if total_paginas_result else None

    #.filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))

    # Consulta para obtener las páginas de la tabla Resultados con código de respuesta 200 y tiempo de respuesta mayor que 0
    paginas_wcagaaa = (
        db.session.query(
            Resultado.fecha_escaneo,
            Resultado.dominio,
            Resultado.pagina,
            Resultado.lang,
            Resultado.tiempo_respuesta,
            Resultado.lang,
            # Aplicar json.loads a la columna Resultado.wcagaaa
            #literal_column("JSON_UNQUOTE(JSON_EXTRACT(resultados.wcagaaa, '$.pa11y_results'))").label('wcagaaa'),
            Resultado.wcagaaa,
            Resultado.html_valid,
            Resultado.responsive_valid,
            Resultado.id,
            Resultado.valid_aaa,
            Resultado.meta_tags  #is_pdf
        ).filter(
            #Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.dominio == dominio,
            Resultado.codigo_respuesta == 200,
            Resultado.valid_aaa == 0,
            #Resultado.wcagaaa.isnot(None),  # Seleccionar solo cuando wcagaaa no es None
            #Resultado.e_viewport != 1 or Resultado.html_valid != 1 or Resultado.responsive_valid != 1
            #Resultado.tiempo_respuesta > 0,
            #Resultado.tiempo_respuesta.isnot(None),  # Filtrar resultados con tiempo_respuesta no nulo
            #Resultado.wcagaaa != [] or Resultado.wcagaaa != {} or Resultado.wcagaaa != {"pa11y_results": []}
            #Resultado.errores_ortograficos == False #,  # Filtrar resultados con tiempo_respuesta False
            #Resultado.tiempo_respuesta.isnot(None)
            #~func.isnan(Resultado.tiempo_respuesta),  # Filtrar resultados que no sean números (nan)
        ).filter(
            ~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(
            ~Resultado.pagina.like('%pdf%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%/asset_publisher/%')
                )  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%/document_library/%')
                )  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%estaticos%')
                )  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%/document_library/%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%redirect%')
                )  # Excluir URLs que contengan 'redirect'
        .filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))
        #.filter(Resultado.lang.in_(['es','ca','en','fr']))
        .all())
    # Consulta para obtener la información de carga agrupada por segundos
    resultados_agrupados = {}

    # Utilizamos una sola consulta para mejorar la eficiencia
    resultados_por_escaneo = (
        db.session.query(
            Resultado.id_escaneo,
            Resultado.dominio,
            case(
                (Resultado.is_pdf == 1, 'assets · docs · pdf · estaticos'),
                (Resultado.is_pdf == 2, 'paginas web html'),
                (Resultado.is_pdf == -1, 'error'),
                else_=
                'otros formatos'  # Puedes cambiar 'Otra etiqueta' por lo que desees
            ).label('intervalo_carga'),
            func.count().label('count')).filter(
                Resultado.dominio == dominio,
                Resultado.codigo_respuesta == 200, Resultado.valid_aaa == 0).
        filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%redirect%')
                )  # Excluir URLs que contengan 'redirect'
        .group_by(Resultado.id_escaneo, 'intervalo_carga',
                  Resultado.dominio).all())

    # Procesamos los resultados para estructurarlos en un diccionario
    for resultado in resultados_por_escaneo:
        id_escaneo = resultado.id_escaneo
        dominio = resultado.dominio
        intervalo_carga = resultado.intervalo_carga
        count = resultado.count

        if id_escaneo not in resultados_agrupados:
            resultados_agrupados[id_escaneo] = []

        resultados_agrupados[id_escaneo].append(
            (dominio, intervalo_carga, count))

    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas
    sumarios = (db.session.query(Sumario).filter(
        Sumario.id_escaneo.in_(ids_escaneo_especificos)).filter(
            Sumario.dominio == dominio).all())

    # Convertir objetos Sumario a diccionarios
    sumarios_dict = []
    for sumario in sumarios:
        sumario_dict = {}
        for column in class_mapper(Sumario).columns:
            sumario_dict[column.name] = getattr(sumario, column.name)
        sumarios_dict.append(sumario_dict)


# Consulta para obtener las filas correspondientes de la tabla Sumario
    evoluciones = (
        db.session.query(Sumario)  #.dominio, Sumario.total_404, Sumario.fecha)
        .filter(Sumario.dominio == dominio).all())

    # Convertir objetos Sumario a diccionarios
    evoluciones_dict = []
    for evolucion in evoluciones:
        evolucion_dict = {}
        for column in class_mapper(Sumario).columns:
            evolucion_dict[column.name] = getattr(evolucion, column.name)
        evoluciones_dict.append(evolucion_dict)

    # Enviamos los resultados al template
    return render_template('tools/usa/analisis_aaa.html',
                           dominio_url=dominio,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           graficos=json.dumps(sumarios_dict),
                           evolucion=json.dumps(evoluciones_dict),
                           resultados=paginas_wcagaaa,
                           detalles=resultados_agrupados,
                           resumen=sumarios,
                           indicador_1=len(paginas_wcagaaa),
                           indicador_2=((len(paginas_wcagaaa) * 100) /
                                        total_paginas),
                           indicador_3=total_paginas)


@app.route('/accesibilidad/compatible')
@login_required
def acc_comp():
    return render_template('tools/acc/acc_comp.html')


@app.route('/accesibilidad/contraste')
@login_required
def acc_contraste():
    return render_template('tools/acc/acc_contraste.html')


@app.route('/accesibilidad/imagenes')
@login_required
def acc_images():
    return render_template('tools/acc/acc_images.html')


@app.route('/accesibilidad/lectores')
@login_required
def acc_lectores():
    return render_template('tools/acc/acc_lectores.html')


@app.route('/accesibilidad/media')
@login_required
def acc_media():
    return render_template('tools/acc/acc_media.html')


@app.route('/accesibilidad/sintax')
@login_required
def acc_sintax():
    return render_template('tools/acc/acc_sintax.html')


@app.route('/accesibilidad/structure')
@login_required
def acc_structure():
    return render_template('tools/acc/acc_structure.html')


@app.route('/accesibilidad/validators')
@login_required
def acc_validators():
    return render_template('tools/acc/acc_validators.html')


@app.route('/ortografia/<string:dominio>')
@login_required
def ortografia(dominio):

    # Modificar la consulta para seleccionar las 7 últimas fechas sin repetir
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == dominio).limit(1).all())

    # Obtener los resultados para las fechas seleccionadas
    fechas_seleccionadas = [result[0] for result in results]

    # Consulta para obtener el campo Sumario.total_paginas
    total_paginas_result = db.session.query(Sumario.total_paginas).filter(
        Sumario.fecha == fechas_seleccionadas[0],
        Sumario.dominio == dominio).first()

    # Almacenar el valor de Sumario.total_paginas en una variable
    total_paginas = total_paginas_result[0] if total_paginas_result else None

    #.filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))

    # Consulta para obtener las páginas de la tabla Resultados con código de respuesta 200 y tiempo de respuesta mayor que 0
    paginas_ortografia = (
        db.session.query(Resultado.fecha_escaneo, Resultado.dominio,
                         Resultado.pagina, Resultado.lang,
                         Resultado.errores_ortograficos,
                         Resultado.num_errores_ortograficos,
                         Resultado.html_copy, Resultado.id,
                         Resultado.meta_tags).
        filter(
            #Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.dominio == dominio,
            Resultado.codigo_respuesta == 200,
            Resultado.num_errores_ortograficos >= 1,
            #Resultado.wcagaaa.isnot(None),  # Seleccionar solo cuando wcagaaa no es None
            #Resultado.e_viewport != 1 or Resultado.html_valid != 1 or Resultado.responsive_valid != 1
            #Resultado.tiempo_respuesta > 0,
            #Resultado.tiempo_respuesta.isnot(None),  # Filtrar resultados con tiempo_respuesta no nulo
            #Resultado.wcagaaa != [] or Resultado.wcagaaa != {} or Resultado.wcagaaa != {"pa11y_results": []}
            #Resultado.html_copy.isnot(None), #,  # Filtrar resultados con tiempo_respuesta False
            Resultado.errores_ortograficos != 'false'
            #~func.isnan(Resultado.tiempo_respuesta),  # Filtrar resultados que no sean números (nan)
        ).filter(
            ~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%pdf%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%?%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%/asset_publisher/%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%/document_library/%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        #.filter(Resultado.lang.in_(['es','ca','en','fr']))
        .filter(func.date(
            Resultado.fecha_escaneo).in_(fechas_seleccionadas)).all())
    # Consulta para obtener la información de carga agrupada por segundos
    resultados_agrupados = {}

    resultados_agrupados_dos = {}

    resultados_por_escaneo = (
        db.session.query(
            Resultado.id_escaneo,
            Resultado.dominio,
            #Resultado.codigo_respuesta == 404,
            case(
                # (Resultado.codigo_respuesta == 200, 'Correctos'),
                # (Resultado.codigo_respuesta == 404, 'Rotos'),
                # (Resultado.codigo_respuesta == 500, 'Error del servidor'),
                # (Resultado.codigo_respuesta == 503, '503'),
                (Resultado.pagina.like('%#%'), 'No existe internos'),
                (Resultado.pagina.like('%redirect=%'),
                 'pagina redireccionada'),
                (Resultado.pagina.like('%?%'), 'pagina dinamica'),
                (Resultado.pagina.like('%pdf%'), 'documento'),
                (Resultado.pagina.like('%estaticos%'), 'estatico'),
                (Resultado.pagina.like('%assets%'), 'asset'),
                (Resultado.pagina.like('%extranet%'), 'extranet'),
                (Resultado.pagina.like('%intranet%'), 'intranet'),
                (Resultado.pagina.like('%visor%'), 'visor'),
                else_='otros'  # Puedes cambiar 'Otra etiqueta' por lo que desees
            ).label('intervalo_carga'),
            func.count().label('count')).filter(
                Resultado.dominio == dominio,
                Resultado.codigo_respuesta == 200).
        filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        .group_by(Resultado.id_escaneo, 'intervalo_carga',
                  Resultado.dominio).all())

    # Procesamos los resultados para estructurarlos en un diccionario
    for resultado in resultados_por_escaneo:
        id_escaneo = resultado.id_escaneo
        dominio = resultado.dominio
        intervalo_carga = resultado.intervalo_carga
        count = resultado.count

        if id_escaneo not in resultados_agrupados_dos:
            resultados_agrupados_dos[id_escaneo] = []

        resultados_agrupados_dos[id_escaneo].append(
            (dominio, intervalo_carga, count))

    # Utilizamos una sola consulta para mejorar la eficiencia
    resultados_por_escaneo = (
        db.session.query(
            Resultado.id_escaneo,
            Resultado.dominio,
            case(
                (Resultado.lang == 'en', 'Inglés'),
                (Resultado.lang == 'ca', 'Catalan'),
                (Resultado.lang == 'es', 'Español'),
                (Resultado.lang == 'fr', 'Frances'),
                else_=
                'Otros idiomas'  # Puedes cambiar 'Otra etiqueta' por lo que desees
            ).label('intervalo_carga'),
            func.count().label('count')).filter(
                Resultado.dominio == dominio,
                Resultado.codigo_respuesta == 200,
                Resultado.num_errores_ortograficos >= 1).
        filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%redirect%')
                )  # Excluir URLs que contengan 'redirect'
        .group_by(Resultado.id_escaneo, 'intervalo_carga',
                  Resultado.dominio).all())

    # Procesamos los resultados para estructurarlos en un diccionario
    for resultado in resultados_por_escaneo:
        id_escaneo = resultado.id_escaneo
        dominio = resultado.dominio
        intervalo_carga = resultado.intervalo_carga
        count = resultado.count

        if id_escaneo not in resultados_agrupados:
            resultados_agrupados[id_escaneo] = []

        resultados_agrupados[id_escaneo].append(
            (dominio, intervalo_carga, count))

    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas
    sumarios = (db.session.query(Sumario).filter(
        Sumario.id_escaneo.in_(ids_escaneo_especificos)).all())

    # Convertir objetos Sumario a diccionarios
    sumarios_dict = []
    for sumario in sumarios:
        sumario_dict = {}
        for column in class_mapper(Sumario).columns:
            sumario_dict[column.name] = getattr(sumario, column.name)
        sumarios_dict.append(sumario_dict)


# Consulta para obtener las filas correspondientes de la tabla Sumario
    evoluciones = (
        db.session.query(Sumario)  #.dominio, Sumario.total_404, Sumario.fecha)
        .all())

    # Convertir objetos Sumario a diccionarios
    evoluciones_dict = []
    for evolucion in evoluciones:
        evolucion_dict = {}
        for column in class_mapper(Sumario).columns:
            evolucion_dict[column.name] = getattr(evolucion, column.name)
        evoluciones_dict.append(evolucion_dict)

    # Enviamos los resultados al template
    return render_template('tools/dicc/ortografia.html',
                           dominio_url=dominio,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           graficos=json.dumps(sumarios_dict),
                           evolucion=json.dumps(evoluciones_dict),
                           resultados=paginas_ortografia,
                           detalles_dos=resultados_agrupados_dos,
                           detalles=resultados_agrupados,
                           resumen=sumarios,
                           indicador_1=len(paginas_ortografia),
                           indicador_2=((len(paginas_ortografia) * 100) /
                                        total_paginas),
                           indicador_3=total_paginas)


@app.route('/diccionarios/spanish')
@login_required
def dicc_spanish():

    results = (
        db.session.query(Resultado).filter(
            Resultado.codigo_respuesta == 404).filter(
                Resultado.dominio.in_(DOMINIOS_ESPECIFICOS))
        #.filter(Resultado.id_escaneo.in_(ids_escaneo_especificos))
        .filter(
            ~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%redirect%')
                )  # Excluir URLs que contengan 'redirect'
        .all())

    # Consulta para obtener la información de carga agrupada por segundos
    resultados_agrupados = {}
    resultados_agrupados_dos = {}

    resultados_por_escaneo = (
        db.session.query(
            Resultado.id_escaneo,
            Resultado.dominio,
            #Resultado.codigo_respuesta == 404,
            case(
                # (Resultado.codigo_respuesta == 200, 'Correctos'),
                # (Resultado.codigo_respuesta == 404, 'Rotos'),
                # (Resultado.codigo_respuesta == 500, 'Error del servidor'),
                # (Resultado.codigo_respuesta == 503, '503'),
                (Resultado.pagina.like('%#%'), 'Interno'),
                (Resultado.pagina.like('%redirect=%'), 'Redirección'),
                (Resultado.pagina.like('%?%'), 'Dinamicos'),
                (Resultado.pagina.like('%pdf%'), 'PDF - DOC'),
                (Resultado.pagina.like('%estaticos%'), 'Estático'),
                (Resultado.pagina.like('%assets%'), 'Asset'),
                (Resultado.pagina.like('%extranet%'), 'Extranet'),
                (Resultado.pagina.like('%intranet%'), 'Intranet'),
                (Resultado.pagina.like('%visor%'), 'Visor'),
                else_='HTML'  # Puedes cambiar 'Otra etiqueta' por lo que desees
            ).label('intervalo_carga'),
            func.count().label('count')).filter(
                Resultado.id_escaneo.in_(ids_escaneo_especificos),
                Resultado.codigo_respuesta == 404)
        #.filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        .group_by(Resultado.id_escaneo, 'intervalo_carga',
                  Resultado.dominio).all())

    # Procesamos los resultados para estructurarlos en un diccionario
    for resultado in resultados_por_escaneo:
        id_escaneo = resultado.id_escaneo
        dominio = resultado.dominio
        intervalo_carga = resultado.intervalo_carga
        count = resultado.count

        if id_escaneo not in resultados_agrupados:
            resultados_agrupados[id_escaneo] = []

        resultados_agrupados[id_escaneo].append(
            (dominio, intervalo_carga, count))

    # Utilizamos una sola consulta para mejorar la eficiencia
    resultados_por_escaneo = (
        db.session.query(
            Resultado.id_escaneo, Resultado.dominio,
            case((Resultado.enlaces_inseguros >= 1, 'Enlaces inseguros'),
                 else_='Otros').label('intervalo_carga'),
            func.count().label('count')).filter(
                Resultado.id_escaneo.in_(ids_escaneo_especificos),
                Resultado.codigo_respuesta == 404)

        #.filter(~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%redirect%'))  # Excluir URLs que contengan 'redirect'
        .group_by(Resultado.id_escaneo, 'intervalo_carga',
                  Resultado.dominio).all())

    # Procesamos los resultados para estructurarlos en un diccionario
    for resultado in resultados_por_escaneo:
        id_escaneo = resultado.id_escaneo
        dominio = resultado.dominio
        intervalo_carga = resultado.intervalo_carga
        count = resultado.count

        if id_escaneo not in resultados_agrupados_dos:
            resultados_agrupados_dos[id_escaneo] = []

        resultados_agrupados_dos[id_escaneo].append(
            (dominio, intervalo_carga, count))

    # Consulta para obtener las filas correspondientes de la tabla Sumario
    sumarios = (db.session.query(Sumario).filter(
        Sumario.id_escaneo.in_(ids_escaneo_especificos)).all())

    # Convertir objetos Sumario a diccionarios
    sumarios_dict = []
    for sumario in sumarios:
        sumario_dict = {}
        for column in class_mapper(Sumario).columns:
            sumario_dict[column.name] = getattr(sumario, column.name)
        sumarios_dict.append(sumario_dict)

    # Consulta para obtener las filas correspondientes de la tabla Sumario
    evoluciones = (
        db.session.query(Sumario)  #.dominio, Sumario.total_404, Sumario.fecha)
        .all())

    # Convertir objetos Sumario a diccionarios
    evoluciones_dict = []
    for evolucion in evoluciones:
        evolucion_dict = {}
        for column in class_mapper(Sumario).columns:
            evolucion_dict[column.name] = getattr(evolucion, column.name)
        evoluciones_dict.append(evolucion_dict)

    return render_template('tools/dicc/dicc_spanish.html',
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           evolucion=json.dumps(evoluciones_dict),
                           resultados=results,
                           resumen=sumarios,
                           detalles=resultados_agrupados,
                           detalles_dos=resultados_agrupados_dos,
                           graficos=json.dumps(sumarios_dict))


@app.route('/ortografia/<int:resultado_id>')
@login_required
def mostrar_html_copy(resultado_id):
    # Obtener el resultado de la base de datos según el resultado_id
    resultado = Resultado.query.get(resultado_id)

    # Verificar si el resultado existe
    if not resultado:
        # Puedes manejar esto según tus necesidades (por ejemplo, mostrar un error)
        return "Resultado no encontrado", 404

    web_offline = ""

    # Verificar y agregar resultado.html_copy
    if hasattr(resultado, 'html_copy'):
        web_offline += resultado.html_copy

    # Verificar y agregar resultado.html_copy_dos
    if hasattr(resultado, 'html_copy_dos'):
        web_offline += resultado.html_copy_dos

    # Verificar y agregar resultado.html_copy_tres
    if hasattr(resultado, 'html_copy_tres'):
        web_offline += resultado.html_copy_tres

    # Verificar y agregar resultado.html_copy_cuatro
    if hasattr(resultado, 'html_copy_cuatro'):
        web_offline += resultado.html_copy_cuatro

    # Verificar y agregar resultado.html_copy_cinco
    if hasattr(resultado, 'html_copy_cinco'):
        web_offline += resultado.html_copy_cinco

        # Verificar y agregar resultado.html_copy
    if hasattr(resultado, 'html_copy_seis'):
        web_offline += resultado.html_copy_seis

    # Verificar y agregar resultado.html_copy_dos
    if hasattr(resultado, 'html_copy_siete'):
        web_offline += resultado.html_copy_siete

    # Verificar y agregar resultado.html_copy_tres
    if hasattr(resultado, 'html_copy_ocho'):
        web_offline += resultado.html_copy_ocho

    # Verificar y agregar resultado.html_copy_cuatro
    if hasattr(resultado, 'html_copy_nueve'):
        web_offline += resultado.html_copy_nueve

    # Verificar y agregar resultado.html_copy_cinco
    if hasattr(resultado, 'html_copy_diez'):
        web_offline += resultado.html_copy_diez

    # Renderizar la plantilla con el contenido de html_copy
    return render_template('tools/dicc/html_copy.html',
                           contenido_html=web_offline)


@app.route('/diccionario')
@login_required
def diccionario():
    palabras = (db.session.query(Diccionario.id, Diccionario.palabra,
                                 Diccionario.idioma).all())

    palabras_diccionario = [{
        'id': palabra[0],
        'palabra': palabra[1],
        'idioma': palabra[2]
    } for palabra in palabras]
    return render_template('tools/dicc/visor_diccionario.html',
                           palabras_diccionario=palabras_diccionario,
                           indicador_1=len(palabras_diccionario))


#
#
# DICCIONARIOS
#


@app.route('/agregar_palabras_bulk', methods=['POST'])
def agregar_palabras_bulk():
    data = json.loads(request.data)
    palabras = data['palabras']  # Obtener la lista de palabras del JSON
    idioma = data['idioma']  # Obtener el idioma del JSON
    nuevas_entradas = []

    for palabra in palabras:
        if palabra.strip():  # Verificar si la palabra no está en blanco
            nueva_entrada = Diccionario(palabra=palabra.strip(), idioma=idioma)
            nuevas_entradas.append(nueva_entrada)

    db.session.add_all(nuevas_entradas)
    db.session.commit()

    palabras = (db.session.query(Diccionario.id, Diccionario.palabra,
                                 Diccionario.idioma).all())

    palabras_diccionario = [{
        'id': palabra[0],
        'palabra': palabra[1],
        'idioma': palabra[2]
    } for palabra in palabras]
    return jsonify({'palabras_diccionario': palabras_diccionario})


@app.route('/agregar_palabra', methods=['POST'])
def agregar_palabra():
    nueva_palabra = request.form['palabra']
    nuevo_idioma = request.form[
        'idioma']  # Agrega la lógica para obtener el idioma desde el formulario

    nueva_entrada = Diccionario(palabra=nueva_palabra, idioma=nuevo_idioma)
    db.session.add(nueva_entrada)
    db.session.commit()

    palabras = (
        db.session.query(Diccionario.id, Diccionario.palabra,
                         Diccionario.idioma)  # Incluye la columna 'idioma'
        .all())

    palabras_diccionario = [{
        'id': palabra[0],
        'palabra': palabra[1],
        'idioma': palabra[2],
    } for palabra in palabras]
    return jsonify({'palabras_diccionario': palabras_diccionario})


@app.route('/editar_palabra', methods=['POST'])
def editar_palabra():
    id = request.form['id']
    palabra = request.form['palabra']
    nuevo_idioma = request.form[
        'idioma']  # Agrega la lógica para obtener el idioma desde el formulario

    palabra_editar = Diccionario.query.get(id)
    palabra_editar.palabra = palabra
    palabra_editar.idioma = nuevo_idioma  # Actualiza la columna 'idioma'
    db.session.commit()

    palabras = (
        db.session.query(Diccionario.id, Diccionario.palabra,
                         Diccionario.idioma)  # Incluye la columna 'idioma'
        .all())

    palabras_diccionario = [{
        'id': palabra[0],
        'palabra': palabra[1],
        'idioma': palabra[2]
    } for palabra in palabras]
    return jsonify({'palabras_diccionario': palabras_diccionario})


@app.route('/borrar_palabra/<int:id>', methods=['DELETE'])
def borrar_palabra(id):
    palabra_borrar = Diccionario.query.get_or_404(id)
    db.session.delete(palabra_borrar)
    db.session.commit()
    palabras = (db.session.query(Diccionario.id, Diccionario.palabra).all())

    palabras_diccionario = [{
        'id': palabra[0],
        'palabra': palabra[1]
    } for palabra in palabras]
    return jsonify({'palabras_diccionario': palabras_diccionario})


@app.route('/diccionarios/english')
@login_required
def dicc_english():
    return render_template('tools/dicc/dicc_english.html')


@app.route('/diccionarios/catalan')
@login_required
def dicc_catalan():
    return render_template('tools/dicc/dicc_catalan.html')


@app.route('/diagnosis/dominios')
@login_required
def diag_domains():
    return render_template('tools/diag/diag_domains.html')


@app.route('/diagnosis/spam')
@login_required
def diag_spam():
    return render_template('tools/diag/diag_spam.html')


@app.route('/diagnosis/copyright')
@login_required
def diag_copyright():
    return render_template('tools/diag/diag_copyright.html')


@app.route('/diagnosis/gdpr')
@login_required
def diag_gdpr():
    return render_template('tools/diag/diag_gdpr.html')


@app.route('/diagnosis/politicas-legales')
@login_required
def diag_textos_legales():
    return render_template('tools/diag/diag_textos_legales.html')


@app.route('/tools/config')
@login_required
def tools_config():
    return render_template('tools/config.html')


@app.route('/resultados-popup', methods=['GET'])
def resultados_popup():

    print("popup-url\t\n")

    # print(resultados)# resultados = request.args.to_dict(flat=False)  # Obtiene los valores de la cadena de consulta como un diccionario

    #  resultados_str = request.args.get('resultados', '')

    # Decodifica la cadena de consulta y convierte a un diccionario con listas de valores
    #  resultados_dict = parse_qs(unquote(resultados_str))

    # Convierte los valores a enteros
    #  resultados_dict = {key: int(value[0]) for key, value in resultados_dict.items()}

    #  print(resultados_dict)
    #   print(resultados)

    # resultados = request.args.get('resultados')
    #  print(resultados)
    #   if resultados:
    #       resultados_dict = parse_qs(unquote(resultados))
    # Convierte los valores a enteros
    #        resultados_dict = {key: int(value[0]) for key, value in resultados_dict.items()}
    #   else:
    #       resultados_dict = None

    #   print("popup-url dict \t\n")
    #    print(resultados_dict)

    # resultados = session.pop('resultados')
    resultados = session.get('resultados', None)

    print("popup-url session \t\n")
    print(resultados)

    return render_template('resultado_popup.html', resultados=resultados)


# return render_template('resultado_popup.html', resultados=resultados_dict)


@app.route('/analizar-url', methods=['POST', 'GET'])
def analizar_url():
    url = request.form.get('url')
    response = requests.get(url, timeout=180)
    resultados = contar_enlaces(response.text, url)

    # Construye manualmente la cadena de consulta
    resultados_str_encoded = '&'.join(
        [f"{key}={value}" for key, value in resultados.items()])

    print("analizar-url\t\n")

    print(resultados)

    resultados_str = request.args.get('resultados', '')
    resultados_dict = parse_qs(unquote(resultados_str))

    # Convierte los valores a enteros
    resultados_dict = {
        key: int(value[0])
        for key, value in resultados_dict.items()
    }

    print('resultados dict')
    # Imprime los resultados en la consola para verificar
    print(resultados_dict)

    # return render_template('resultado_popup.html', resultados=resultados)
    # return resultados_popup(resultados=resultados)
    # return redirect(url_for('resultados_popup'), resultados)
    #  return redirect(url_for('resultados_popup', resultados=resultados_str_encoded))
    #    return redirect(url_for('resultados_popup', resultados=resultados_str_encoded))

    #
    # Almacena los resultados en la sesión
    session['resultados'] = resultados

    print('resultados')
    print(session['resultados'])

    return redirect(url_for('resultados_popup'))



def contar_enlaces(response_text, url):
    soup = BeautifulSoup(response_text, 'html.parser')
    base_url = urlparse(url).scheme + "://" + urlparse(url).hostname

    enlaces_rotos_url = []
    enlaces_rotos = 0

    # Enlaces totales y enlaces inseguros
    enlaces = soup.find_all('a', href=True)
    enlaces_en_documento = [
        enlace['href'] for enlace in enlaces
    ]  #  if not enlace['href'].startswith(('http://', 'https://'))]

    #enlaces_inseguros = [enlace['href'] for enlace in enlaces if enlace['href'].startswith('http://')]

    # Enlaces internos y enlaces internos únicos
    #enlaces_internos = [urljoin(base_url, enlace['href']) for enlace in enlaces if not enlace['href'].startswith(('http://', 'https://'))]
    #enlaces_internos_unicos = list(set(enlaces_internos))

    # Enlaces JS únicos
    #enlaces_js_unicos = [enlace['href'] for enlace in enlaces if enlace.get('href') and enlace['href'].startswith('javascript:')]

    # Enlaces salientes y enlaces salientes únicos
    #enlaces_salientes = [urljoin(base_url, enlace['href']) for enlace in enlaces if enlace.get('href') and enlace['href'].startswith(('http://', 'https://'))]
    #enlaces_salientes_unicos = list(set(enlaces_salientes))

    # Enlaces salientes JS únicos
    #enlaces_salientes_js_unicos = [enlace['href'] for enlace in enlaces_salientes if enlace.startswith('javascript:')]

    # Enlaces salientes externos y enlaces salientes externos únicos
    #enlaces_salientes_externos = [enlace for enlace in enlaces_salientes if not urlparse(enlace).hostname == urlparse(url).hostname]
    #enlaces_salientes_externos_unicos = list(set(enlaces_salientes_externos))

    # Enlaces salientes JS externos únicos
    #enlaces_salientes_js_externos_unicos = [enlace for enlace in enlaces_salientes_js_unicos if not urlparse(enlace).hostname == urlparse(url).hostname]

    for enlace in enlaces_en_documento:  # enlaces_salientes:
        enlace_absoluto = urljoin(base_url, enlace)
        if urlparse(enlace_absoluto).hostname == urlparse(
                url).hostname and not verificar_enlace(enlace_absoluto):
            enlaces_rotos_url.append(enlace_absoluto)
            enlaces_rotos += 1

    # Verificar enlaces rotos


# enlaces_rotos = [enlace for enlace in enlaces_salientes if not verificar_enlace(enlace)]

    return {
        "url": url,
        #"total_enlaces": len(enlaces),
        #"enlaces_rotos": enlaces_rotos,
        #"enlaces_inseguros": len(enlaces_inseguros),
        #"enlaces_internos": len(enlaces_internos),
        #"enlaces_internos_unicos": len(enlaces_internos_unicos),
        #"enlaces_js_unicos": len(enlaces_js_unicos),
        #"enlaces_salientes": len(enlaces_salientes),
        #"enlaces_salientes_unicos": len(enlaces_salientes_unicos),
        #"enlaces_salientes_js_unicos": len(enlaces_salientes_js_unicos),
        #"enlaces_salientes_externos": len(enlaces_salientes_externos),
        #"enlaces_salientes_externos_unicos": len(enlaces_salientes_externos_unicos),
        #"enlaces_salientes_js_externos_unicos": len(enlaces_salientes_js_externos_unicos),
        "urls": enlaces_rotos_url
    }


def verificar_enlace(enlace):
    try:
        response = requests.head(enlace, timeout=5)
        return response.status_code == 200 and not (
            response.status_code == 301 or response.status_code == 302)
    except requests.RequestException:
        return False
