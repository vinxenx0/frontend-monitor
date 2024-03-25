# app/controllers/tools_controller.py

import json
from flask import redirect, render_template, jsonify, request, url_for
from flask_login import login_required
from app import app, db
from sqlalchemy import and_, desc, distinct, func, case
from app.models.database import Resultado, Sumario, Diccionario, Diccionario_usuario, Configuracion, Keywords
from config import URL_BASE #URL_OFFLINE, DOMINIOS_ESPECIFICOS,
from app import IDS_ESCANEO, FECHA_ESCANEO, HORA_FIN, HORA_INICIO, ESTADO_SPIDER, DOMINIOS_ESPECIFICOS
from sqlalchemy.orm import class_mapper
from flask import request
import requests
from flask import render_template, request
from flask import render_template, request, session
from googlesearch import search

ids_escaneo_especificos = IDS_ESCANEO
dominios_especificos = DOMINIOS_ESPECIFICOS


# Decorador de contexto para pasar variables globales a todas las plantillas
@app.context_processor
def inject_global_variables():
    return dict(fecha_escaneo=FECHA_ESCANEO,
                hora_inicio=HORA_INICIO,
                hora_fin=HORA_FIN,
                estado_spider=ESTADO_SPIDER
    )

@app.context_processor
def inject_global_variables():
    return dict(url_base=URL_BASE)
               

# Implementación del filtro fromjson
def fromjson(value):
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


# Agregar el filtro a la aplicación Flask
app.jinja_env.filters['fromjson'] = fromjson

# Tools rutas


@app.route('/old/informes/resumen')
@login_required
def old_informe_resumen():

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

@app.route('/informes/resumen/')
@login_required
def informe_resumen_raiz():
    return redirect(url_for('informe_resumen_dominio', domain=DOMINIOS_ESPECIFICOS[0]))

@app.route('/informes/resumen/<string:domain>')
@login_required
def informe_resumen_dominio(domain):
    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas para un dominio específico
    sumarios = (db.session.query(Sumario).filter(
        Sumario.dominio == domain).filter(
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
        Sumario.dominio == domain).order_by(desc(
            Sumario.id)).offset(1).limit(1).first())

    # Consulta para obtener la segunda coincidencia ordenando por sumario.id de mayor a menor
    sumario_quince = (db.session.query(Sumario).filter(
        Sumario.dominio == domain).order_by(desc(
            Sumario.id)).offset(14).limit(1).first())

    # Verifica si se encontró la segunda coincidencia antes de intentar iterar sobre ella
    if sumario_ayer:
        # Puedes acceder a las propiedades del objeto Sumario directamente
        print(f"ID: {sumario_ayer.id}, Dominio: {sumario_ayer.dominio}")
    else:
        print("No se encontraron coincidencias.")

    return render_template('tools/resumen.html',
                           dominio_url=domain,
                           solo_uno=domain,
                           resumen_ayer=sumario_ayer,
                           resumen=sumarios,
                           dominio_actual=domain,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           ids_especificos=IDS_ESCANEO)


@app.route('/usabilidad/resumen/')
@login_required
def usabilidad_resumen():
    return redirect(url_for('usabilidad_resumen_dominio', domain=DOMINIOS_ESPECIFICOS[0]))


@app.route('/usabilidad/resumen/<string:domain>')
@login_required
def usabilidad_resumen_dominio(domain):

    print("es esto?")
    print(IDS_ESCANEO)
    
    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas para un dominio específico
    sumarios = (db.session.query(Sumario).filter(
        Sumario.dominio == domain).filter(
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
        Sumario.dominio == domain).order_by(desc(
            Sumario.id)).offset(1).limit(1).first())

    # Consulta para obtener la segunda coincidencia ordenando por sumario.id de mayor a menor
    sumario_quince = (db.session.query(Sumario).filter(
        Sumario.dominio == domain).order_by(desc(
            Sumario.id)).offset(14).limit(1).first())

    # Verifica si se encontró la segunda coincidencia antes de intentar iterar sobre ella
    if sumario_ayer:
        # Puedes acceder a las propiedades del objeto Sumario directamente
        print(f"ID: {sumario_ayer.id}, Dominio: {sumario_ayer.dominio}")
    else:
        print("No se encontraron coincidencias.")

    return render_template('tools/usa/resumen_usa.html',
                           dominio=domain,
                           solo_uno=domain,
                           resumen_ayer=sumario_ayer,
                           resumen=sumarios,
                           dominio_actual=domain,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           ids_especificos=IDS_ESCANEO)

@app.route('/accesibilidad/resumen/')
@login_required
def accesibilidad_resumen():
    return redirect(url_for('accesibilidad_resumen_dominio', domain=DOMINIOS_ESPECIFICOS[0]))

@app.route('/accesibilidad/resumen/<string:domain>')
@login_required
def accesibilidad_resumen_dominio(domain):
    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas para un dominio específico
    sumarios = (db.session.query(Sumario).filter(
        Sumario.dominio == domain).filter(
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
        Sumario.dominio == domain).order_by(desc(
            Sumario.id)).offset(1).limit(1).first())

    # Consulta para obtener la segunda coincidencia ordenando por sumario.id de mayor a menor
    sumario_quince = (db.session.query(Sumario).filter(
        Sumario.dominio == domain).order_by(desc(
            Sumario.id)).offset(14).limit(1).first())

    # Verifica si se encontró la segunda coincidencia antes de intentar iterar sobre ella
    if sumario_ayer:
        # Puedes acceder a las propiedades del objeto Sumario directamente
        print(f"ID: {sumario_ayer.id}, Dominio: {sumario_ayer.dominio}")
    else:
        print("No se encontraron coincidencias.")

    return render_template('tools/acc/resumen_acc.html',
                           dominio=domain,
                           solo_uno=domain,
                           resumen_ayer=sumario_ayer,
                           resumen=sumarios,
                           dominio_actual=domain,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           ids_especificos=IDS_ESCANEO)
    


@app.route('/seo/resumen/')
@login_required
def seo_resumen():
    return redirect(url_for('seo_resumen_dominio', domain=DOMINIOS_ESPECIFICOS[0]))

@app.route('/seo/resumen/<string:domain>')
@login_required
def seo_resumen_dominio(domain):
    # Consulta para obtener los sumarios correspondientes a las IDs de escaneo propuestas para un dominio específico
    sumarios = (db.session.query(Sumario).filter(
        Sumario.dominio == domain).filter(
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
        Sumario.dominio == domain).order_by(desc(
            Sumario.id)).offset(1).limit(1).first())

    # Consulta para obtener la segunda coincidencia ordenando por sumario.id de mayor a menor
    sumario_quince = (db.session.query(Sumario).filter(
        Sumario.dominio == domain).order_by(desc(
            Sumario.id)).offset(14).limit(1).first())

    # Verifica si se encontró la segunda coincidencia antes de intentar iterar sobre ella
    if sumario_ayer:
        # Puedes acceder a las propiedades del objeto Sumario directamente
        print(f"ID: {sumario_ayer.id}, Dominio: {sumario_ayer.dominio}")
    else:
        print("No se encontraron coincidencias.")

    return render_template('tools/seo/resumen_seo.html',
                           dominio=domain,
                           solo_uno=domain,
                           resumen_ayer=sumario_ayer,
                           resumen=sumarios,
                           dominio_actual=domain,
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


@app.route('/meta-tags/')
@login_required
def meta_tags_raiz():
    return redirect(url_for('meta_tags', domain=DOMINIOS_ESPECIFICOS[0]))

@app.route('/meta-tags/<string:domain>')
@login_required
def meta_tags(domain):
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == domain).limit(1).all())

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
    paginas_metatags = (
        db.session.query(Resultado.fecha_escaneo, Resultado.dominio,
                         Resultado.pagina, Resultado.lang, Resultado.meta_tags,
                         Resultado.desc_short, Resultado.desc_long,
                         Resultado.id, Resultado.meta_description_duplicado,
                         Resultado.meta_description_mas_155_caracteres,
                         Resultado.meta_description_menos_70_caracteres,
                         Resultado.meta_description_falta,
                         Resultado.meta_og_card, Resultado.meta_og_title,
                         Resultado.meta_og_image).
        filter(
            #Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.dominio == domain,
            Resultado.codigo_respuesta == 200,
            Resultado.meta_description_falta != 0
            or Resultado.meta_description_menos_70_caracteres != 0
            or Resultado.desc_short != 0 or Resultado.desc_long != 0
            or Resultado.meta_description_duplicado != 0
            or Resultado.meta_description_mas_155_caracteres != 0
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
        .filter(func.date(
            Resultado.fecha_escaneo).in_(fechas_seleccionadas)).filter(
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
                           dominio_url=domain,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           resultados=paginas_metatags,
                           detalles=resultados_agrupados,
                           resumen=sumarios,
                           indicador_1=len(paginas_metatags),
                           indicador_2=((len(paginas_metatags) * 100) /
                                        total_paginas),
                           indicador_3=total_paginas)


@app.route('/encabezados/')
@login_required
def encabezados_raiz():
    return redirect(url_for('encabezados', domain=DOMINIOS_ESPECIFICOS[0]))

@app.route('/encabezados/<string:domain>')
@login_required
def encabezados(domain):
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == domain).limit(1).all())

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
    paginas_encabezados = (
        db.session.query(Resultado.fecha_escaneo, Resultado.dominio,
                         Resultado.pagina, Resultado.lang,
                         Resultado.heading_tags, Resultado.h2_duplicado,
                         Resultado.h2_multiple, Resultado.id,
                         Resultado.h2_falta, Resultado.h2_no_secuencial,
                         Resultado.titulos_pagina_igual_h1,
                         Resultado.h1_duplicate).
        filter(
            #Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.dominio == domain,
            Resultado.codigo_respuesta == 200,
            Resultado.h2_duplicado != 1
            or Resultado.titulos_pagina_igual_h1 != 0
            or Resultado.h1_duplicate != 1 or Resultado.h2_no_secuencial != 0
            or Resultado.h2_falta != 0
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
        .filter(func.date(
            Resultado.fecha_escaneo).in_(fechas_seleccionadas)).filter(
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
    return render_template('tools/seo/encabezados.html',
                           dominio_url=domain,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           resultados=paginas_encabezados,
                           detalles=resultados_agrupados,
                           resumen=sumarios,
                           indicador_1=len(paginas_encabezados),
                           indicador_2=((len(paginas_encabezados) * 100) /
                                        total_paginas),
                           indicador_3=total_paginas)


@app.route('/indexabilidad/')
@login_required
def indexabilidad_raiz():
    return redirect(url_for('indexabilidad', domain=DOMINIOS_ESPECIFICOS[0]))

@app.route('/indexabilidad/<string:domain>')
@login_required
def indexabilidad(domain):
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == domain).limit(1).all())

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
    paginas_indexables = (
        db.session.query(Resultado.fecha_escaneo, Resultado.dominio,
                         Resultado.pagina, Resultado.lang, Resultado.e_robots,
                         Resultado.canonicals_falta, Resultado.e_title,
                         Resultado.id, Resultado.e_charset, Resultado.e_keywords,
                         Resultado.tiempo_respuesta, Resultado.html_valid,
                         Resultado.directivas_noindex, Resultado.meta_tags).
        filter(
            #Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.dominio == domain,
            Resultado.codigo_respuesta == 200,
            Resultado.meta_description_falta != 0
            or Resultado.e_title != 1
            or Resultado.e_robots != 1 or Resultado.e_robots  != 1
            or Resultado.e_keywords != 1

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
        .filter(func.date(
            Resultado.fecha_escaneo).in_(fechas_seleccionadas)).filter(
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
    return render_template('tools/seo/indexabilidad.html',
                           dominio_url=domain,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           resultados=paginas_indexables,
                           detalles=resultados_agrupados,
                           resumen=sumarios,
                           indicador_1=len(paginas_indexables),
                           indicador_2=((len(paginas_indexables) * 100) /
                                        total_paginas),
                           indicador_3=total_paginas)


@app.route('/salud-seo/')
@login_required
def salud_seo_raiz():
    return redirect(url_for('salud_seo', domain=DOMINIOS_ESPECIFICOS[0]))

@app.route('/salud-seo/<string:domain>')
@login_required
def salud_seo(domain):
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == domain).limit(1).all())

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
    paginas_salud = (
        db.session.query(Resultado.fecha_escaneo, Resultado.dominio,
                         Resultado.pagina, Resultado.lang, Resultado.e_robots,
                         Resultado.canonicals_falta, Resultado.e_title,
                         Resultado.id, Resultado.e_charset, Resultado.tipo_documento,Resultado.e_description, Resultado.e_keywords,
                         Resultado.tiempo_respuesta, Resultado.html_valid,
                         Resultado.directivas_noindex, Resultado.meta_tags).
        filter(
            #Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.dominio == domain,
            Resultado.codigo_respuesta == 200,
            Resultado.e_robots != 1
            or Resultado.e_title != 1
            or Resultado.e_description != 1 or Resultado.e_keywords != 1
            or Resultado.tiempo_respuesta > 15
            #Resultado.tiempo_respuesta > 0,
            #Resultado.tiempo_respuesta.isnot(None),  # Filtrar resultados con tiempo_respuesta no nulo
            #Resultado.tiempo_respuesta != '',
            #Resultado.tiempo_respuesta.isnot(False) #,  # Filtrar resultados con tiempo_respuesta False
            #Resultado.tiempo_respuesta.isnot(None)
            #~func.isnan(Resultado.tiempo_respuesta),  # Filtrar resultados que no sean números (nan)
        )
        #.filter(
        #    ~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(
            ~Resultado.pagina.like('%pdf%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%/documents/%')
        #        )  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%/document_library/%')
        #        )  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%redirect%')
        #        )  # Excluir URLs que contengan 'redirect'
        .filter(func.date(
            Resultado.fecha_escaneo).in_(fechas_seleccionadas)).filter(
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
    return render_template('tools/seo/salud_seo.html',
                           dominio_url=domain,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           resultados=paginas_salud,
                           detalles=resultados_agrupados,
                           resumen=sumarios,
                           indicador_1=len(paginas_salud),
                           indicador_2=((len(paginas_salud) * 100) /
                                        total_paginas),
                           indicador_3=total_paginas)

@app.route('/keywords/')
@login_required
def keywords_raiz():
    return redirect(url_for('keywords', domain=DOMINIOS_ESPECIFICOS[0]))

@app.route('/keywords/<string:domain>')
@login_required
def keywords(domain):
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == domain).limit(1).all())

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
    paginas_keywords = (
        db.session.query(Resultado.fecha_escaneo, Resultado.dominio,
                         Resultado.pagina, Resultado.lang,
                         Resultado.e_keywords, Resultado.e_robots,
                         Resultado.c_robots, Resultado.id,
                         Resultado.c_keywords, Resultado.directivas_noindex,
                         Resultado.tipo_documento, Resultado.meta_tags).
        filter(
            #Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.dominio == domain,
            Resultado.codigo_respuesta == 200,
            Resultado.e_keywords != 1
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
        .filter(func.date(
            Resultado.fecha_escaneo).in_(fechas_seleccionadas)).filter(
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
    return render_template('tools/seo/keywords.html',
                           dominio_url=domain,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           resultados=paginas_keywords,
                           detalles=resultados_agrupados,
                           resumen=sumarios,
                           indicador_1=len(paginas_keywords),
                           indicador_2=((len(paginas_keywords) * 100) /
                                        total_paginas),
                           indicador_3=total_paginas)


@app.route('/seo/backlinks')
@login_required
def seo_backlinks():
    return render_template('tools/seo/seo_backlinks.html')


@app.route('/old/seo/resumen')
@login_required
def seo_resumen_back():

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
    

@app.route('/velocidad/')
@login_required
def velocidad():
    return redirect(url_for('velocidad_url', domain=DOMINIOS_ESPECIFICOS[0]))

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
            Resultado.dominio == domain,
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
                           dominio_url=domain,
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
                           indicador_2=((len(paginas_velocidad) * 100) /
                                        total_paginas),
                           indicador_3=total_paginas)


@app.route('/enlaces-rotos/')
@login_required
def enlaces_rotos():
    return redirect(url_for('enlaces_rotos_dominio', domain=DOMINIOS_ESPECIFICOS[0]))



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

@app.route('/enlaces/')
@login_required
def enlaces():
    return redirect(url_for('enlaces_dominio', domain=DOMINIOS_ESPECIFICOS[0]))


@app.route('/enlaces/<string:domain>')
@login_required
def enlaces_dominio(domain):

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
            Resultado.codigo_respuesta == 200).filter(
                Resultado.dominio == domain).filter(
                    func.date(
                        Resultado.fecha_escaneo).in_(fechas_seleccionadas))
        #.filter(Resultado.id_escaneo.in_(ids_escaneo_especificos))
        .filter(
            ~Resultado.pagina.like('%documents%'),
            ~Resultado.pagina.like('%estaticos%'),
            ~Resultado.pagina.like('%png%')
            )  # Excluir URLs que contengan '#'
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
                # Resultado.id_escaneo.in_(IDS_ESCANEO),
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
    return render_template('tools/usa/enlaces.html',
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


@app.route('/usabilidad/font-colors')
@login_required
def usa_font_colors():
    return render_template('tools/usa/usa_font_colors.html')


@app.route('/usabilidad/nav')
@login_required
def usa_nav():
    return render_template('tools/usa/usa_nav.html')


@app.route('/titulos/')
@login_required
def titulos_raiz():
    return redirect(url_for('titulos', domain=DOMINIOS_ESPECIFICOS[0]))

@app.route('/titulos/<string:domain>')
@login_required
def titulos(domain):
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == domain).limit(1).all())

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
    paginas_titulos = (
        db.session.query(Resultado.fecha_escaneo, Resultado.dominio,
                         Resultado.pagina, Resultado.lang, Resultado.e_title,
                         Resultado.title_long, Resultado.title_short,
                         Resultado.id, Resultado.title_duplicate,
                         Resultado.titulos_pagina_menos_30_caracteres,
                         Resultado.titulos_pagina_mas_60_caracteres,
                         Resultado.titulos_pagina_igual_h1,
                         Resultado.titulos_pagina_duplicado, Resultado.c_title,
                         Resultado.meta_tags).
        filter(
            #Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.dominio == domain,
            Resultado.codigo_respuesta == 200,
            Resultado.e_title != 1 or Resultado.title_long != 0
            or Resultado.title_short != 0 or Resultado.title_duplicate != 0
            or Resultado.titulos_pagina_duplicado != 0
            or Resultado.titulos_pagina_igual_h1 != 0
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
        .filter(func.date(
            Resultado.fecha_escaneo).in_(fechas_seleccionadas)).filter(
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
                           dominio_url=domain,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           resultados=paginas_titulos,
                           detalles=resultados_agrupados,
                           resumen=sumarios,
                           indicador_1=len(paginas_titulos),
                           indicador_2=((len(paginas_titulos) * 100) /
                                        total_paginas),
                           indicador_3=total_paginas)


@app.route('/responsive/')
@login_required
def responsive_raiz():
    return redirect(url_for('responsive', domain=DOMINIOS_ESPECIFICOS[0]))


@app.route('/responsive/<string:domain>')
@login_required
def responsive(domain):

    # Modificar la consulta para seleccionar las 7 últimas fechas sin repetir
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == domain).limit(1).all())

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
    paginas_responsive = (
        db.session.query(
            Resultado.fecha_escaneo,
            Resultado.dominio,
            Resultado.pagina,
            Resultado.lang,
            Resultado.e_viewport,
            Resultado.html_valid,
            Resultado.responsive_valid,
            Resultado.id, Resultado.e_title,
            Resultado.valid_aaa,
            Resultado.meta_tags  #is_pdf
        ).filter(
            #Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.dominio == domain,
            Resultado.codigo_respuesta == 200,
            Resultado.responsive_valid != 1 or Resultado.e_title != 1 or
            Resultado.e_viewport != 1 or Resultado.html_valid != 1
            #or Resultado.responsive_valid != 1
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
        .filter(func.date(
            Resultado.fecha_escaneo).in_(fechas_seleccionadas)).filter(
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
                           dominio_url=domain,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           resultados=paginas_responsive,
                           detalles=resultados_agrupados,
                           resumen=sumarios,
                           indicador_1=len(paginas_responsive),
                           indicador_2=((len(paginas_responsive) * 100) /
                                        total_paginas),
                           indicador_3=total_paginas)


@app.route('/seguridad/')
@login_required
def seguridad_raiz():
    return redirect(url_for('seguridad', domain=DOMINIOS_ESPECIFICOS[0]))

@app.route('/seguridad/<string:domain>')
@login_required
def seguridad(domain):
    # Modificar la consulta para seleccionar las 7 últimas fechas sin repetir
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == domain).limit(1).all())

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
            Resultado.dominio == domain,
            Resultado.codigo_respuesta == 200,
            Resultado.falta_encabezado_x_content_type_options != 0
            or Resultado.falta_encabezado_secure_referrer_policy != 0
            or Resultado.falta_encabezado_x_frame_options != 0
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
                           dominio_url=domain,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           resultados=seguridad_results,
                           indicador_1=len(seguridad_results),
                           indicador_2=((len(seguridad_results) * 100) /
                                        total_paginas),
                           indicador_3=total_paginas)



@app.route('/imagenes/')
@login_required
def imagenes_raiz():
    return redirect(url_for('imagenes', domain=DOMINIOS_ESPECIFICOS[0]))

@app.route('/imagenes/<string:domain>')
@login_required
def imagenes(domain):
    # Modificar la consulta para seleccionar las 7 últimas fechas sin repetir
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == domain).limit(1).all())

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
            Resultado.dominio == domain,
            Resultado.codigo_respuesta == 200,
            Resultado.imagenes_rotas != 0 or Resultado.alt_vacias != 0 or Resultado.images_1MB != 0

            #Resultado.tiempo_respuesta.isnot(None),  # Filtrar resultados con tiempo_respuesta no nulo
            #Resultado.wcagaaa != [] or Resultado.wcagaaa != {} or Resultado.wcagaaa != {"pa11y_results": []}
            #Resultado.errores_ortograficos == False #,  # Filtrar resultados con tiempo_respuesta False
            #Resultado.tiempo_respuesta.isnot(None)
            #~func.isnan(Resultado.tiempo_respuesta),  # Filtrar resultados que no sean números (nan)
        ).filter(
            ~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(Resultado.tipo_documento.like('%text%')).filter(
            func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))
        #.filter(Resultado.lang.in_(['es','ca','en','fr']))
        .all())

    return render_template('tools/acc/imagenes.html',
                           dominio_url=domain,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           resultados=imagenes_results,
                           indicador_1=len(imagenes_results),
                           indicador_2=((len(imagenes_results) * 100) /
                                        total_paginas),
                           indicador_3=total_paginas)


@app.route('/legibilidad/')
@login_required
def legibilidad_raiz():
    return redirect(url_for('legibilidad', domain=DOMINIOS_ESPECIFICOS[0]))

@app.route('/legibilidad/<string:domain>')
@login_required
def legibilidad(domain):
    # Modificar la consulta para seleccionar las 7 últimas fechas sin repetir
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == domain).limit(1).all())

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
            Resultado.dominio == domain,
            Resultado.codigo_respuesta == 200,
            #Resultado.tiempo_respuesta > 0,
            #Resultado.tiempo_respuesta.isnot(None),  # Filtrar resultados con tiempo_respuesta no nulo
            #Resultado.wcagaaa != [] or Resultado.wcagaaa != {} or Resultado.wcagaaa != {"pa11y_results": []}
            #Resultado.errores_ortograficos == False #,  # Filtrar resultados con tiempo_respuesta False
            #Resultado.tiempo_respuesta.isnot(None)
            #~func.isnan(Resultado.tiempo_respuesta),  # Filtrar resultados que no sean números (nan)
        )
        #.filter(
        #    ~Resultado.pagina.like('%#%'))  # Excluir URLs que contengan '#'
        .filter(Resultado.tipo_documento.like('%text%'))
        #.filter(
        #    ~Resultado.pagina.like('%pdf%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%/asset_publisher/%')
        #        )  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%/document_library/%')
        #        )  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%estaticos%')
        #        )  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%/document_library/%'))  # Excluir URLs que contengan '#'
        #.filter(~Resultado.pagina.like('%redirect%')
        #        )  # Excluir URLs que contengan 'redirect'
        .filter(func.date(Resultado.fecha_escaneo).in_(fechas_seleccionadas))
        #.filter(Resultado.lang.in_(['es','ca','en','fr']))
        .all())

    return render_template('tools/acc/legibilidad.html',
                           dominio_url=domain,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           resultados=legibilidad_results,
                           indicador_1=len(legibilidad_results),
                           indicador_2=((len(legibilidad_results) * 100) /
                                        total_paginas),
                           indicador_3=total_paginas)


@app.route('/analisis-aaa/')
@login_required
def analisis_aaa_raiz():
    return redirect(url_for('analisis_aaa', domain=DOMINIOS_ESPECIFICOS[0]))

@app.route('/analisis-aaa/<string:domain>')
@login_required
def analisis_aaa(domain):

    # Modificar la consulta para seleccionar las 7 últimas fechas sin repetir
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == domain).limit(1).all())

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
            Resultado.dominio == domain,
            Resultado.codigo_respuesta == 200,
            #Resultado.valid_aaa == 0
            #Resultado.wcagaaa.isnot(None),  # Seleccionar solo cuando wcagaaa no es None
            #Resultado.e_viewport != 1 or Resultado.html_valid != 1 or Resultado.responsive_valid != 1
            #Resultado.tiempo_respuesta > 0,
            #Resultado.tiempo_respuesta.isnot(None),  # Filtrar resultados con tiempo_respuesta no nulo
            Resultado.wcagaaa != [] or Resultado.wcagaaa != {}
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
        .filter(~Resultado.pagina.like('%/documents/%')
                ) 
        .filter(~Resultado.pagina.like('%estaticos%')
                )  # Excluir URLs que contengan '#'
        .filter(~Resultado.pagina.like('%.png%'))  # Excluir URLs que contengan '#'
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
                Resultado.dominio == domain,
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
            Sumario.dominio == domain).all())

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
        .filter(Sumario.dominio == domain).all())

    # Convertir objetos Sumario a diccionarios
    evoluciones_dict = []
    for evolucion in evoluciones:
        evolucion_dict = {}
        for column in class_mapper(Sumario).columns:
            evolucion_dict[column.name] = getattr(evolucion, column.name)
        evoluciones_dict.append(evolucion_dict)

    # Enviamos los resultados al template
    return render_template('tools/usa/analisis_aaa.html',
                           dominio_url=domain,
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



@app.route('/ortografia/')
@login_required
def ortografia_raiz():
    return redirect(url_for('ortografia', domain=DOMINIOS_ESPECIFICOS[0]))

@app.route('/ortografia/<string:domain>')
@login_required
def ortografia(domain):

    # Modificar la consulta para seleccionar las 7 últimas fechas sin repetir
    results = (db.session.query(distinct(Sumario.fecha)).order_by(
        Sumario.fecha.desc()).filter(
            Sumario.dominio == domain).limit(1).all())

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
    paginas_ortografia = (
        db.session.query(Resultado.fecha_escaneo, Resultado.dominio,
                         Resultado.pagina, Resultado.lang,
                         Resultado.errores_ortograficos,
                         Resultado.num_errores_ortograficos,
                         Resultado.html_copy, Resultado.id,
                         Resultado.meta_tags).
        filter(
            #Resultado.id_escaneo.in_(ids_escaneo_especificos),
            Resultado.dominio == domain,
            Resultado.codigo_respuesta == 200,
            Resultado.num_errores_ortograficos != 0,
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
        .filter(~Resultado.pagina.like('%estaticos%'))
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
                Resultado.dominio == domain,
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
                Resultado.dominio == domain,
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
                           dominio_url=domain,
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

@app.route('/excluidas')
@login_required   
def visor_excluidas():
    palabras = (db.session.query(Diccionario_usuario.id, Diccionario_usuario.palabra,
                                 Diccionario_usuario.idioma).all())

    palabras_diccionario = [{
        'id': palabra[0],
        'palabra': palabra[1],
        'idioma': palabra[2]  
    } for palabra in palabras]
    return render_template('tools/dicc/visor_excluidas.html',
                           palabras_diccionario=palabras_diccionario,
                           indicador_1=len(palabras_diccionario))

@app.route('/lista-blanca')
@login_required   
def visor_whitelist():
    palabras = (db.session.query(Diccionario.id, Diccionario.palabra,
                                 Diccionario.idioma).all())

    palabras_diccionario = [{
        'id': palabra[0],
        'palabra': palabra[1],
        'idioma': palabra[2]  
    } for palabra in palabras]
    return render_template('tools/dicc/visor_whitelist.html',
                           palabras_diccionario=palabras_diccionario,
                           indicador_1=len(palabras_diccionario))





# DICCIONARIOS


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

@app.route('/excluidas/agregar_palabra', methods=['POST'])
def agregar_palabra_excluidas():
    nueva_palabra = request.form['palabra']
    nuevo_idioma = request.form[
        'idioma']  # Agrega la lógica para obtener el idioma desde el formulario

    nueva_entrada = Diccionario_usuario(palabra=nueva_palabra, idioma=nuevo_idioma)
    db.session.add(nueva_entrada)
    db.session.commit()

    palabras = (
        db.session.query(Diccionario_usuario.id, Diccionario_usuario.palabra,
                         Diccionario_usuario.idioma)  # Incluye la columna 'idioma'
        .all())

    palabras_diccionario = [{
        'id': palabra[0],
        'palabra': palabra[1],
        'idioma': palabra[2],
    } for palabra in palabras]
    return jsonify({'palabras_diccionario': palabras_diccionario})

@app.route('/excluidas/agregar_palabras_bulk', methods=['POST'])
def agregar_palabras_bulk_excluidas():
    data = json.loads(request.data)
    palabras = data['palabras']  # Obtener la lista de palabras del JSON
    idioma = data['idioma']  # Obtener el idioma del JSON
    nuevas_entradas = []

    for palabra in palabras:
        if palabra.strip():  # Verificar si la palabra no está en blanco
            nueva_entrada = Diccionario_usuario(palabra=palabra.strip(), idioma=idioma)
            nuevas_entradas.append(nueva_entrada)

    db.session.add_all(nuevas_entradas)
    db.session.commit()

    palabras = (db.session.query(Diccionario_usuario.id, Diccionario_usuario.palabra,
                                 Diccionario_usuario.idioma).all())

    palabras_diccionario = [{
        'id': palabra[0],
        'palabra': palabra[1],
        'idioma': palabra[2]
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

@app.route('/excluidas/editar_palabra', methods=['POST'])
def editar_palabra_excluidas():
    id = request.form['id']
    palabra = request.form['palabra']
    nuevo_idioma = request.form[
        'idioma']  # Agrega la lógica para obtener el idioma desde el formulario

    palabra_editar = Diccionario_usuario.query.get(id)
    palabra_editar.palabra = palabra
    palabra_editar.idioma = nuevo_idioma  # Actualiza la columna 'idioma'
    db.session.commit()

    palabras = (db.session.query(Diccionario_usuario.id, Diccionario_usuario.palabra,
                                 Diccionario_usuario.idioma).all())

    palabras_diccionario = [{
        'id': palabra[0],
        'palabra': palabra[1],
        'idioma': palabra[2]
    } for palabra in palabras]
    return jsonify({'palabras_diccionario': palabras_diccionario})


@app.route('/excluidas/borrar_palabra/<int:id>', methods=['DELETE'])
def borrar_palabra_excluidas(id):
    palabra_borrar = Diccionario_usuario.query.get_or_404(id)
    db.session.delete(palabra_borrar)
    db.session.commit()
    palabras = (db.session.query(Diccionario_usuario.id, Diccionario_usuario.palabra).all())

    palabras_diccionario = [{
        'id': palabra[0],
        'palabra': palabra[1]
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
        # Obtener la última configuración de la base de datos
    ultima_configuracion = Configuracion.query.order_by(Configuracion.id.desc()).first()
    return render_template('config.html', configuracion=ultima_configuracion)
    #return render_template('config.html')

@app.route('/tools/config/update', methods=['POST'])
def actualizar_configuracion():
    try:
        # Obtener datos del formulario
        dominios = request.form.get('dominios_analizar') #"https://www.mc-mutual.com\r\nhttps://mejoratuabsentismo.mc-mutual.com\r\nhttps://prevencion.mc-mutual.com"
        frecuencia = request.form.get('frecuencia_dias')
        validator = request.form.get('w3c_validator')
        urlExcluidas = request.form.get('url_Excluidas')
        extensionesExcluidas = request.form.get('extensiones_Excluidas')
        keywords = request.form.get('keywords_analizar')

        print(urlExcluidas)
        # Resto de campos

        # Crear instancia de Configuracion
        configuracion = Configuracion(
            dominios_analizar=dominios,
            frecuencia_dias=frecuencia,
            w3c_validator = validator,
            url_Excluidas = urlExcluidas,
            extensiones_Excluidas = extensionesExcluidas,
            keywords_analizar = keywords,
            is_running = 0
            # Resto de campos
        )
        # Guardar en la base de datos
        db.session.add(configuracion)
        db.session.commit()
        
        print("dominios analizar sin config.py")
        print(DOMINIOS_ESPECIFICOS)
        # Redirigir a una página de éxito
        return redirect(url_for('tools_config'))
        #ultima_configuracion = Configuracion.query.order_by(Configuracion.id.desc()).first()
        #return render_template('config.html', configuracion=ultima_configuracion)
        #return render_template('config.html')
    except Exception as e:
        # Manejar errores
        return "Error al actualizar la configuración: " + str(e)


@app.route('/sitemap/<string:domain>')
def sitemap(domain):
    results = check_sitemap(domain)
    return render_template('sitemap.html', domain=domain, results=results)


def check_sitemap(url):
    sitemap_paths = [
        '/sitemap_index.xml',
        '/sitemap.php',
        '/sitemap.txt',
        '/sitemap.xml.gz',
        '/sitemap/',
        '/sitemap/sitemap.xml',
        '/sitemapindex.xml',
        '/sitemap/index.xml',
        '/sitemap1.xml',
        '/rss.xml',
        '/atom.xml',
        '/sitemap.xml',
        '/tag-sitemap.xml',
        '/sitemap_index/xml',
        '/category-sitemap.xml',
        '/sitemap.html',
        # Agrega otros nombres de archivos según sea necesario
    ]

    results = {}

    for path in sitemap_paths:
        full_url = url + path
        response = requests.head(full_url)
        if response.status_code == 200:
            results[path] = "Disponible"
        else:
            results[path] = "No disponible"

    return results


@app.route('/ranking/<string:domain>')
def obtener_posiciones_dominio(domain):
    palabras_clave_ejemplo = [
        "mc-mutual","mc mutua de accidentes"
    ]
    posiciones_totales = {}
    top3_count = 0
    top10_count = 0

    for palabra_clave in palabras_clave_ejemplo:
        posicion = obtener_posicion_dominio(palabra_clave, domain)
        posiciones_totales[palabra_clave] = posicion

        if posicion and posicion <= 3:
            top3_count += 1

        if posicion and posicion <= 10:
            top10_count += 1

    print("posiciones totales 1")
    print(posiciones_totales)

    # Asignar un valor predeterminado de 0 a los elementos None
    posiciones_totales_con_valor_predeterminado = {
        k: v if v is not None else 999
        for k, v in posiciones_totales.items()
    }

    # Ordenar el diccionario con el valor predeterminado
    posiciones_ordenadas = sorted(
        posiciones_totales_con_valor_predeterminado.items(),
        key=lambda x: x[1])

        # Guardar o actualizar los resultados en la base de datos
    for keyword, rank in posiciones_totales.items():
        # Consultar si la palabra clave ya existe en la base de datos
        existing_keyword = Keywords.query.filter_by(keyword=keyword).first()

        if existing_keyword:
            # Si la palabra clave existe, actualizar su rango
            existing_keyword.rank = rank
        else:
            # Si la palabra clave no existe, crear un nuevo registro
            new_keyword = Keywords(keyword=keyword, rank=rank)
            db.session.add(new_keyword)

    db.session.commit()

   
    return render_template('tools/seo/ranking.html',
                           dominio_url=domain,
                           dominios_ordenados=DOMINIOS_ESPECIFICOS,
                           resultados=jsonify(posiciones_totales),
                           posiciones=posiciones_ordenadas,
                           indicador_3=len(palabras_clave_ejemplo),
                           indicador_1=4,
                           indicador_2=9)


def obtener_posicion_dominio(palabra_clave,
                             dominio_objetivo,
                             num_resultados=10):
    posicion = None

    try:
        # Realiza la búsqueda en Google
        search_results = search(palabra_clave, num_results=num_resultados)

        # Busca la posición del dominio objetivo en los resultados
        for i, result in enumerate(search_results, start=1):
            if dominio_objetivo in result:
                posicion = i
                break
    except Exception as e:
        print(f"Error para '{palabra_clave}': {e}")

    return posicion

@app.route('/resultados-popup', methods=['GET'])
def resultados_popup():

    print("popup-url\t\n")

    # resultados = session.pop('resultados')
    resultados = session.get('resultados', None)
    url = session.get('url', None)

    print("popup-url session \t\n")
    print(resultados)

    return render_template('resultado_popup.html', resultados=resultados, url=url)

