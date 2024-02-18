# app/controllers/spider_controller.py

import imghdr
from io import BytesIO
import re
import textstat
from PIL import Image
import subprocess
from flask import request
from app import app
from config import DOMINIOS_ESPECIFICOS, URL_BASE #URL_OFFLINE
from app import IDS_ESCANEO
from flask import request
from bs4 import BeautifulSoup
import requests
from flask import request, redirect, url_for
from urllib.parse import parse_qs, unquote
from flask import request, redirect, url_for, session
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

ids_escaneo_especificos = IDS_ESCANEO
dominios_especificos = DOMINIOS_ESPECIFICOS

@app.context_processor
def inject_global_variables():
    return dict(url_base=URL_BASE)



@app.route('/<string:tool>/analizar-url', methods=['POST', 'GET'])
def tool_popup(tool):
    url = request.form.get('url')

    if tool == 'encabezados':
        resultados = analizar_heading_url(url)
    elif tool == 'responsive':
        resultados = es_responsive_valid(url)
    elif tool == 'velocidad':
        resultados = analisis_velocidad_url(url)
    elif tool == 'titulos':
        resultados = extraer_meta_tags(url)
    elif tool == 'velocidad':
        resultados = analisis_velocidad_url(url)
    elif tool == 'legibilidad':
        resultados = analizar_legibilidad_url(url)
    elif tool == 'imagenes':
        resultados = analizar_imagenes_url(url)
    elif tool == 'analisis-aaa':
         resultados = ejecutar_pa11y(url)
    elif tool == 'enlaces-rotos':
        response = requests.get(url, timeout=180)
        resultados = contar_enlaces(response.text, url)
    else:
        # Si la herramienta no está definida, puedes devolver un error 404 o redirigir a una página de error
        resultados = [{'Herramienta no encontrada':tool}]

    session['resultados'] = resultados
    session['url'] = url

    return redirect(url_for('resultados_popup'))
    


@app.route('/encabezados/analizar-url', methods=['POST', 'GET'])
def analisis_encabezados_url():
    url = request.form.get('url')
    resultados = analizar_heading_url(url)

    session['resultados'] = resultados
    session['url'] = url

    return redirect(url_for('resultados_popup'))


def analizar_heading_url(url):
    response = requests.get(url, timeout=180)
    soup = BeautifulSoup(response.text, 'html.parser')
    heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    heading_tags_count = {tag: len(soup.find_all(tag)) for tag in heading_tags}

    # Contar las veces que aparece la etiqueta h1 específicamente
    h1_duplicate = heading_tags_count.get('h1', 0)

    # Nuevas métricas para h2
    h1_falta = heading_tags_count.get('h1', 0) == 0
    h2_mas_70_caracteres = sum(
        len(tag.text) > 70 for tag in soup.find_all('h2'))
    h2_duplicado = any(count > 1 for count in heading_tags_count.values())
    h2_multiple = any(count > 1 for count in heading_tags_count.values())
    h2_falta = heading_tags_count.get('h2', 0) == 0
    h2_no_secuencial = heading_tags_count.get(
        'h1', 0) > 0 and heading_tags_count.get(
            'h2', 0) > 0 and soup.find_all('h1')[0].find_next('h2') is None

    # Nuevas métricas para h1 y h2
    #h1_longitud = max(len(tag.text) for tag in soup.find_all('h1'))
    #h2_longitud = max(len(tag.text) for tag in soup.find_all('h2'))

    #return heading_tags_count, h1_falta, h1_duplicate, h2_mas_70_caracteres, h2_duplicado, h2_multiple, h2_falta, h2_no_secuencial
    return [{
        'orden:':heading_tags_count,'h1 falta:':h1_falta,'h1 duplicado': h1_duplicate, 'h2 largo':h2_mas_70_caracteres, \
            'h2 duplicado:':h2_duplicado, 'h2 repetidos:':h2_multiple, 'h2 no esta:':h2_falta, 'no ordenados:':h2_no_secuencial
        }]

@app.route('/responsive/analizar-url', methods=['POST', 'GET'])
def analisis_responsive_url():
    url = request.form.get('url')
    resultados = es_responsive_valid(url)

    session['resultados'] = resultados
    session['url'] = url

    return redirect(url_for('resultados_popup'))

def es_responsive_valid(url):
    try:
        response = requests.get(url, timeout=180)
        soup = BeautifulSoup(response.text, 'html.parser')
        viewport_tag = soup.find('meta', attrs={'name': 'viewport'})
        if viewport_tag:
            return [{"Pass":True}]
        else:
            return [{"Pass":False}]
        #return viewport_tag is not None
    except Exception as e:
        return [{"Pass":False}]# return False


@app.route('/velocidad/analizar-url', methods=['POST', 'GET'])
def analisis_velocidad_url():
    url = request.form.get('url')
    resultados = analisis_velocidad_url(url)

    session['resultados'] = resultados
    session['url'] = url

    return redirect(url_for('resultados_popup'))

def analisis_velocidad_url(url):
    response = requests.get(url, timeout=180)
    tiempo_respuesta = response.elapsed.total_seconds()
    codigo_respuesta = response.status_code
    return [{'Tiempo ms':tiempo_respuesta,'Codigo':codigo_respuesta}]

@app.route('/titulos/analizar-url', methods=['POST', 'GET'])
def analisis_titulos_url():
    url = request.form.get('url')
    resultados = extraer_meta_tags(url)

    session['resultados'] = resultados
    session['url'] = url

    return redirect(url_for('resultados_popup'))

def extraer_meta_tags(url): #(response_text, response):
    response = requests.get(url, timeout=180)
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_tags = soup.find_all('meta')
    meta_tags_info = [{
        'name': tag.get('name'),
        'content': tag.get('content')
    } for tag in meta_tags]

    # Nuevos datos de meta tags
    meta_description_mas_155_caracteres = any(
        len(tag.get('content', '')) > 155 for tag in meta_tags
        if tag.get('name') == 'description')
    meta_description_duplicado = any(
        meta_tags_info.count(tag) > 1 for tag in meta_tags_info
        if tag.get('name') == 'description')

    canonicals_falta = not soup.find('link', {'rel': 'canonical'})
    directivas_noindex = 'noindex' in [
        tag.get('content') for tag in meta_tags if tag.get('name') == 'robots'
    ]

    falta_encabezado_x_content_type_options = 'X-Content-Type-Options' not in [
        header[0] for header in response.headers
    ]
    falta_encabezado_secure_referrer_policy = 'Referrer-Policy' not in [
        header[0] for header in response.headers
    ]
    falta_encabezado_content_security_policy = 'Content-Security-Policy' not in [
        header[0] for header in response.headers
    ]
    falta_encabezado_x_frame_options = 'X-Frame-Options' not in [
        header[0] for header in response.headers
    ]

    titulos_pagina_menos_30_caracteres = any(
        len(tag.text) < 30
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
    meta_description_menos_70_caracteres = any(
        len(tag.get('content', '')) < 70 for tag in meta_tags
        if tag.get('name') == 'description')
    titulos_pagina_mas_60_caracteres = any(
        len(tag.text) > 60
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
    titulos_pagina_igual_h1 = any(
        tag.text == soup.find('h1').text
        for tag in soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6']))
    titulos_pagina_duplicado = any(
        meta_tags_info.count(tag) > 1 for tag in meta_tags_info
        if tag.get('name') == 'title')

    meta_description_falta = not any(
        tag.get('name') == 'description' for tag in meta_tags)

    version_http = response.headers.get('Version')
    ultima_modificacion = response.headers.get('last-modified')

    meta_og_card = any(tag.get('property') == 'og:card' for tag in meta_tags)
    meta_og_title = any(tag.get('property') == 'og:title' for tag in meta_tags)
    meta_og_image = any(tag.get('property') == 'og:image' for tag in meta_tags)

    #return meta_tags_info, meta_description_mas_155_caracteres, meta_description_duplicado, canonicals_falta, directivas_noindex, \
    #       falta_encabezado_x_content_type_options, falta_encabezado_secure_referrer_policy, \
    #       falta_encabezado_content_security_policy, falta_encabezado_x_frame_options, \
    #       titulos_pagina_menos_30_caracteres, meta_description_menos_70_caracteres, titulos_pagina_mas_60_caracteres, \
    #       titulos_pagina_igual_h1, titulos_pagina_duplicado, meta_description_falta, version_http, ultima_modificacion, \
    #       meta_og_card, meta_og_title, meta_og_image
    return meta_tags_info

@app.route('/legibilidad/analizar-url', methods=['POST', 'GET'])
def analisis_legibilidad_url():
    url = request.form.get('url')
    resultados = analizar_legibilidad_url(url)

    session['resultados'] = resultados
    session['url'] = url

    return redirect(url_for('resultados_popup'))


def extraer_texto_visible(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    visible_text = ' '.join(soup.stripped_strings)
    return visible_text

def analizar_legibilidad_url(url) :
    response = requests.get(url, timeout=180)
    texto_visible = extraer_texto_visible(response.text)
    palabras = texto_visible.split()

    # Almacenar el número de frases en resultado.frases
    frases = re.split(r'[;.|,]', texto_visible)
    
    # Calcular la media de palabras por frase y almacenarla en resultado.media_palabras_frases
    palabras_por_frase = [
        len(frase.split()) for frase in frases
        if frase.strip()
    ]
    media_palabras_frase = sum(
        palabras_por_frase) / len(
            palabras_por_frase
        ) if palabras_por_frase else 0
  
    # Calcular la prueba de legibilidad de Flesch-Kincaid y almacenarla en resultado.flesh
    try:
        total_palabras = len(
            re.findall(r'\b\w+\b', texto_visible))
        total_oraciones = len(frases)
        #total_silabas = sum([textstat.syllable(word) for word in re.findall(r'\b\w+\b', texto_visible)])
        total_silabas = sum([
            textstat.lexicon_count(word, True)
            for word in re.findall(
                r'\b\w+\b', texto_visible)
        ])
        flesh_score = 206.835 - 1.015 * (
            total_palabras / total_oraciones
        ) - 84.6 * (total_silabas / total_palabras)
        flesh_score = round(
            flesh_score, 2)
    except ZeroDivisionError:
        flesh_score = 0.0
    
    return [{
        'palabras':len(palabras), 'frases':len(frases), 'palabras x frase':media_palabras_frase,'flesh score':flesh_score
    }]

@app.route('/imagenes/analizar-url', methods=['POST', 'GET'])
def analisis_imagenes_url():
    url = request.form.get('url')
    resultados = analizar_imagenes_url(url)

    session['resultados'] = resultados
    session['url'] = url

    return redirect(url_for('resultados_popup'))

def analizar_imagenes_url(url):
    response = requests.get(url, timeout=180)
    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')
    info_imagenes = []
    image_types = []
    images_1MB = 0
    imagenes_rotas = 0

    for img_tag in img_tags:
        src = img_tag.get('src')
        alt = img_tag.get('alt', '')
        src_url = urljoin(url, src)

        try:
            response = requests.get(src_url, stream=True)
            response.raise_for_status()

            # Get the filename, size in MB, and check if the image is broken
            filename = urlparse(src_url).path.split("/")[-1]
            size_mb = len(response.content) / (1024 * 1024)
            is_broken = False

            # Nuevo campo
            if size_mb > 1:
                images_1MB += 1

            # Check if the image is broken by opening it with PIL
            try:
                Image.open(BytesIO(response.content))
            except Exception as e:
                is_broken = True
                imagenes_rotas += 1

            # Get the image type
            image_type = imghdr.what(None, h=response.content)

            info_imagen = {
                'filename': filename,
                'size_mb': size_mb,
                'url': src_url,
                'alt_text': alt,
                'broken': is_broken,
                'image_type': image_type
            }

            info_imagenes.append(info_imagen)
            image_types.append(image_type)
        except Exception as e:
            print(
                f"Error al obtener informaciÃ³n de la imagen {src_url}: {str(e)}"
            )

    return info_imagenes


@app.route('/analisis-aaa/analizar-url', methods=['POST', 'GET'])
def analisis_aaa_url():
    url = request.form.get('url')
    resultados = ejecutar_pa11y(url)

    # Construye manualmente la cadena de consulta
    #resultados_str_encoded = '&'.join(
    #    [f"{key}={value}" for key, value in resultados.items()])

    print("analizar-url\t\n")

    print(resultados)

    #resultados_str = request.args.get('resultados', '')
    #resultados_dict = parse_qs(unquote(resultados_str))

    # Convierte los valores a enteros
    #resultados_dict = {
    #    key: int(value[0])
    #    for key, value in resultados_dict.items()
    #}

    #print('resultados dict')
    # Imprime los resultados en la consola para verificar
    #print(resultados_dict)

    # return render_template('resultado_popup.html', resultados=resultados)
    # return resultados_popup(resultados=resultados)
    # return redirect(url_for('resultados_popup'), resultados)
    #  return redirect(url_for('resultados_popup', resultados=resultados_str_encoded))
    #    return redirect(url_for('resultados_popup', resultados=resultados_str_encoded))

    #
    # Almacena los resultados en la sesión
    session['resultados'] = resultados
    session['url'] = url
    
    print('resultados')
    print(session['resultados'])

    return redirect(url_for('resultados_popup'))


def ejecutar_pa11y(url_actual):
    try:
        # Ejecuta pa11y y captura la salida directamente
        #command = f"pa11y --standard WCAG2AAA  --ignore issue-code-1 --ignore issue-code-2 --reporter csv {url_actual}"
        #command = f"pa11y --standard WCAG2AA  --reporter csv {url_actual}"
        #print("url p4lly:")
        #print(url_actual)
        #command = f"pa11y -e axe -d -T 3 --ignore issue-code-2 --ignore issue-code-1 -r json {url_actual}"
        command = f"pa11y -T 1 --ignore issue-code-2 --ignore issue-code-1 -r json {url_actual}"
        process = subprocess.run(command,
                                 shell=True,
                                 check=False,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)
        return process.stdout
    
    except Exception as e:  # subprocess.CalledProcessError as e:
        error_message = f"Error al ejecutar pa11y para {url_actual}: {e}"
        print(error_message)
        return []


@app.route('/enlaces-rotos/analizar-url', methods=['POST', 'GET'])
def analizar_enlancesrotos_url():
    url = request.form.get('url')
    response = requests.get(url, timeout=180)
    resultados = contar_enlaces(response.text, url)

    # Construye manualmente la cadena de consulta
    #resultados_str_encoded = '&'.join(
    #    [f"{key}={value}" for key, value in resultados.items()])

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
    session['url'] = url

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
    print(enlaces_rotos_url)

    return enlaces_rotos_url

    #return {
    #    "url": url,
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
    #    "urls": enlaces_rotos_url
    #}


def verificar_enlace(enlace):
    try:
        response = requests.head(enlace, timeout=5)
        return response.status_code == 200 and not (
            response.status_code == 301 or response.status_code == 302)
    except requests.RequestException:
        return False

               