# app/controllers/spider_controller.py

import imghdr
from io import BytesIO
import json
from sqlalchemy.orm import class_mapper
import re
import string
import aspell
import textstat
import langid
from PIL import Image
import subprocess
from app import app, db
from app.models.database import Diccionario, Diccionario_usuario
from config import DOMINIOS_ESPECIFICOS, URL_BASE #URL_OFFLINE
from app import IDS_ESCANEO
from bs4 import BeautifulSoup
import requests
from flask import request, redirect, url_for, session
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from flask import request
from io import BytesIO
#from google import Translator
from googletrans import Translator

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
    elif tool == 'meta-tags':
         resultados = extraer_meta_tags(url)
    elif tool == 'keywords':
         resultados = extraer_meta_tags(url)
    elif tool == 'salud-seo':
         resultados = extraer_meta_tags(url)
    elif tool == 'ortografia':
         resultados = resaltar_errores_ortograficos(url) #analizar_ortografia(url)
         print(resultados)
    elif tool == 'seguridad':
         resultados = extraer_meta_tags(url)
    else:
        # Si la herramienta no está definida, puedes devolver un error 404 o redirigir a una página de error
        resultados = [{'Herramienta no encontrada':tool}]

    session['resultados'] = resultados
    session['url'] = url

    return redirect(url_for('resultados_popup'))



def resaltar_errores_ortograficos(url):


    # Obtener todas las palabras de la base de datos
    palabras = [palabra.palabra for palabra in db.session.query(Diccionario_usuario).all()]
    palabras.extend([palabra.palabra for palabra in db.session.query(Diccionario).all()])


    # Convertir la lista de palabras a formato JSON
    PALABRAS_DICCIONARIO = json.dumps(palabras)

    errores_ortograficos = None  # Inicializa como None en lugar de una lista vacía
    palabras = set()  # Usamos un conjunto para almacenar las palabras únicas

    idioma_detectado = obtener_idioma_desde_url(url)  #detectar_idioma(texto)
    response = requests.get(url)
    # Obtener el contenido de la página web
    # Codificar el contenido a UTF-8
    texto = extraer_texto_visible(response.text)

    speller = aspell.Speller('lang', idioma_detectado)

    # Eliminar números y símbolos de moneda, así como exclamaciones, interrogaciones y caracteres similares
    translator = str.maketrans(
        '', '', string.digits + string.punctuation + '¡!¿?$€£')
    texto_limpio = texto.translate(translator)

    caracteres_especiales = string.punctuation + '“»«¡!¿?’@#%^&`*()_-+=[]{}|;:,.<>/"'
    palabras = {
        palabra
        for palabra in texto_limpio.split()
        if not all(c in caracteres_especiales for c in palabra)
        if palabra not in PALABRAS_DICCIONARIO
        and len(palabra) >= 4
    }

    errores_ortograficos = [
        palabra for palabra in palabras if not speller.check(palabra) and palabra not in PALABRAS_DICCIONARIO
        and palabra.lower() not in PALABRAS_DICCIONARIO and palabra.upper() not in PALABRAS_DICCIONARIO and palabra.capitalize() not in PALABRAS_DICCIONARIO
    ]

    
    # Descargar la página web
    response = requests.get(url)
    if response.status_code == 200:
        # Parsear el contenido HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Obtener todo el texto de la página
        texto_pagina = soup.get_text()

        # Buscar palabras con errores ortográficos y resaltarlas con CSS
        for error in errores_ortograficos:
            # Usamos expresiones regulares para encontrar todas las ocurrencias de la palabra con errores ortográficos
            texto_pagina = re.sub(r'\b' + re.escape(error) + r'\b', f'<span class="error">{error}</span>', texto_pagina, flags=re.IGNORECASE)

        # Generar el contenido HTML con las palabras resaltadas
        contenido_sin_html = f'''
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Página con errores ortográficos resaltados</title>
            <style>
                .error {{
                    background-color: yellow;
                }}
            </style>
        </head>
        <body>
            {texto_pagina}
        </body>
        </html>
        '''

        # Buscar todas las etiquetas de texto (p, div, span, etc.)
        etiquetas_texto = soup.find_all(text=True)

        # Buscar palabras con errores ortográficos y resaltarlas con CSS
        for tag in etiquetas_texto:
            contenido_tag = str(tag)
            for error in errores_ortograficos:
                # Usamos expresiones regulares para encontrar todas las ocurrencias de la palabra con errores ortográficos
                contenido_tag = re.sub(r'\b' + re.escape(error) + r'\b', f'<span style="color:white!important;background-color:red!important">{error}</span>', contenido_tag, flags=re.IGNORECASE)
            tag.replace_with(BeautifulSoup(contenido_tag, 'html.parser'))  # Creamos un nuevo objeto BeautifulSoup con el contenido modificado


        # Generar el contenido HTML con las palabras resaltadas
        contenido_html = str(soup)


        # Guardar el contenido HTML en un archivo
        with open('pagina_con_errores.html', 'w', encoding='utf-8') as file:
            file.write(contenido_html)
        
        print("Página con errores ortográficos resaltados guardada como 'pagina_con_errores.html'.")
    else:
        print("Error al descargar la página web.")

    # local
    #file_path = '///home/vinxenxo/frontend-monitor/ortografia-temp.html'
    file_path = '/var/www/html/offline/ortografia-temp.html'
    file_url = URL_BASE + '/offline/ortografia-temp.html'
    with open(file_path, 'w') as f:
        f.write(contenido_html)

    
  
    return [{"Errores ortograficos:":len(list(errores_ortograficos)),
             "Palabras:":list(errores_ortograficos), "html:":file_url
             }]



def analizar_ortografia(url):

    # Obtener todas las palabras de la base de datos
    palabras = [palabra.palabra for palabra in db.session.query(Diccionario_usuario).all()]
    palabras.extend([palabra.palabra for palabra in db.session.query(Diccionario).all()])


    # Convertir la lista de palabras a formato JSON
    PALABRAS_DICCIONARIO = json.dumps(palabras)

    #print("diccionario db: ")
    #print(PALABRAS_DICCIONARIO)

    #PALABRAS_DICCIONARIO = [
    #            row.palabra for row in session.query(Diccionario).all()
    #        ]
     
    errores_ortograficos = None  # Inicializa como None en lugar de una lista vacía
    palabras = set()  # Usamos un conjunto para almacenar las palabras únicas

    idioma_detectado = obtener_idioma_desde_url(url)  #detectar_idioma(texto)
    response = requests.get(url)
    # Obtener el contenido de la página web
    # Codificar el contenido a UTF-8
    modified_html = response.content.decode('utf-8')
    texto = extraer_texto_visible(response.text)

    speller = aspell.Speller('lang', idioma_detectado)

    # Eliminar números y símbolos de moneda, así como exclamaciones, interrogaciones y caracteres similares
    translator = str.maketrans(
        '', '', string.digits + string.punctuation + '¡!¿?$€£')
    texto_limpio = texto.translate(translator)


    #print(PALABRAS_DICCIONARIO)
    # Agrega palabras personalizadas excluidas
    #palabras = {
    #    palabra
    #    for palabra in texto_limpio.split()
    #    if palabra not in PALABRAS_DICCIONARIO
    #    and len(palabra) >= 4
    #}

    # Filtra palabras que tengan TODOS los signos de puntuación, interrogación, exclamación, caracteres especiales o símbolos de moneda
    caracteres_especiales = string.punctuation + '“»«¡!¿?’@#%^&`*()_-+=[]{}|;:,.<>/"'
    palabras = {
        palabra
        for palabra in texto_limpio.split()
        if not all(c in caracteres_especiales for c in palabra)
        if palabra not in PALABRAS_DICCIONARIO
        and len(palabra) >= 4
    }

    # Errores ortográficos solo para palabras que no están en la lista excluida y no cumplen con el chequeo del speller
    errores_ortograficos = [
        palabra for palabra in palabras if not speller.check(palabra) and palabra not in PALABRAS_DICCIONARIO
        and palabra.lower() not in PALABRAS_DICCIONARIO and palabra.upper() not in PALABRAS_DICCIONARIO and palabra.capitalize() not in PALABRAS_DICCIONARIO
    ]

    #print(list(errores_ortograficos))

    #send_file(html_archivo, attachment_filename='resultado.html', as_attachment=True)
    #for palabra in errores_ortograficos:
        # Encontrar la posición de la palabra en el HTML original
    #    start_index = modified_html.find(palabra)

    #    if start_index != -1:
    #        modified_html = (
    #            modified_html[:start_index] +
    #            f'<span style="background-color:red!important;color:white!important;border:2px solid #fff!important">{palabra}</span>'
    #            + modified_html[start_index +
    #                            len(palabra):])



    #for palabra in errores_ortograficos:
    #    # Buscar la etiqueta <body> en el HTML
    #    start_body_index = modified_html.find('<body>')
        
        # Si no encuentra la etiqueta <body>, buscar en todo el documento
    #    if start_body_index == -1:
    #        start_index = modified_html.find(palabra)
    #    else:
            # Encontrar la posición de la palabra en el HTML original después de la etiqueta <body>
    #        start_index = modified_html.find(palabra, start_body_index)
        
    #    if start_index != -1:
    #        modified_html = (
    #            modified_html[:start_index] +
    #            f'<span style="background-color:red!important;color:white!important;border:2px solid #fff!important">{palabra}</span>'
    #            + modified_html[start_index +
    #                            len(palabra):])

    for palabra in errores_ortograficos:
        # Buscar la etiqueta <body> en el HTML
        start_body_index = modified_html.find('<body>')
        
        # Si no encuentra la etiqueta <body>, buscar en todo el documento
        if start_body_index == -1:
            start_index = modified_html.find(palabra)
        else:
            # Encontrar la posición de la palabra en el HTML original después de la etiqueta <body>
            start_index = modified_html.find(palabra, start_body_index)
        
        if start_index != -1:
            # Utilizamos BeautifulSoup para analizar el HTML
            soup = BeautifulSoup(modified_html, 'html.parser')
            # Buscamos todas las etiquetas que tengan el atributo 'alt'
            for tag in soup.find_all(alt=True):
                # Extraemos el texto de la etiqueta
                tag_text = tag.get_text()
                # Verificamos si la palabra está dentro del texto de la etiqueta
                if palabra in tag_text:
                    # Si la palabra está dentro del texto de la etiqueta, no la modificamos
                    continue
            
            # Si la palabra no está dentro de ninguna etiqueta 'alt', la reemplazamos
            modified_html = (
                modified_html[:start_index] +
                f'<span style="background-color:red!important;color:white!important;border:2px solid #fff!important">{palabra}</span>'
                + modified_html[start_index + len(palabra):])




    # local
    file_path = '///home/vinxenxo/frontend-monitor/ortografia-temp.html'
    #file_path = '/var/www/html/offline/ortografia-temp.html'
    file_url = URL_BASE + '/offline/ortografia-temp.html'
    with open(file_path, 'w') as f:
        f.write(modified_html)

    
  
    return [{"Errores ortograficos:":len(list(errores_ortograficos)),
             "Palabras:":list(errores_ortograficos), "html:":file_url
             }]
    
def obtener_idioma_desde_url(url):
    response = requests.get(url, timeout=180)
    response.raise_for_status()  # Lanza una excepción si la solicitud no tiene éxito

    # Parsea el HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encuentra la etiqueta meta con el atributo property="og:locale"
    etiqueta_meta = soup.find('meta', property='og:locale')

    # Si se encuentra la etiqueta meta, extrae el valor del atributo content
    if etiqueta_meta:
        idioma_meta = etiqueta_meta.get('content', None)
        if idioma_meta:
            # Elimina las comillas escapadas usando expresiones regulares
            codigo_idioma = re.sub(r'^\\"|\\"$', '', idioma_meta).split('_')[0]
            #print("idioma:")
            #print(codigo_idioma)
            return codigo_idioma
        else:
            print("No se encontró el atributo content en la etiqueta meta con property='og:locale'.")
    else:
        print("No se encontró la etiqueta meta con property='og:locale'.")

        # Encuentra la etiqueta <html> y extrae el valor del atributo lang
        idioma_html = soup.html.get('lang', None)

        # Si se encuentra el atributo lang, extrae los dos primeros caracteres (código del idioma)
        if idioma_html:
            # Elimina las comillas escapadas usando expresiones regulares
            codigo_idioma = re.sub(r'^\\"|\\"$', '', idioma_html).split('-')[0]
            #print("idioma:")
            #print(codigo_idioma)
            return codigo_idioma
        else:
            print("No se encontró el atributo lang en la etiqueta <html>.")

            # Si no se encuentra el idioma en ninguna de las etiquetas, utiliza la función detectar_idioma
            texto_pagina = soup.get_text()
            codigo_idioma_detectado = detectar_idioma(texto_pagina)
            if codigo_idioma_detectado:
                print("Idioma detectado mediante texto de la página:", codigo_idioma_detectado)
                return codigo_idioma_detectado

    return "es"  # Idioma predeterminado

def detectar_idioma(texto):
    try:
        idioma, _ = langid.classify(texto)
        return idioma
    except Exception as e:
        print(f"Error al detectar el idioma: {e}")
        return None



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

def analisis_velocidad_url(url):
    response = requests.get(url, timeout=180)
    tiempo_respuesta = response.elapsed.total_seconds()
    codigo_respuesta = response.status_code
    return [{'Tiempo ms':tiempo_respuesta,'Codigo':codigo_respuesta}]

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

def extraer_texto_visible(response_text):
    # soup = BeautifulSoup(response_text, 'html.parser')
    #soup = BeautifulSoup(response_text, 'html.parser', markup_type='html')
    #soup = BeautifulSoup(response_text, 'html.parser', parse_only=NoConversionHTMLParser())

    #visible_text = ' '.join(soup.stripped_strings)
   
    soup = BeautifulSoup(response_text, 'html.parser')
    for element in soup.find_all(['script', 'style', 'noscript']):  # Eliminar scripts, estilos y contenido sin script
        element.extract()
    visible_text = soup.get_text(separator=' ', strip=True)

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

def traducir_mensajes(process_stdout):
    try:
        # Verificar si la salida del proceso no está vacía y tiene formato JSON válido
        if process_stdout.strip() and process_stdout.strip().startswith('{'):
            # Decodificar la salida del proceso como JSON
            stdout_json = json.loads(process_stdout)
            # Resto del código para traducir los mensajes...
        else:
            print("La salida del proceso no contiene datos JSON válidos.")
            return []
    except json.JSONDecodeError as e:
        print(f"Error al decodificar la salida del proceso: {e}")
        return []



def traducir_mensajes(process_stdout):
    # Decodificar la salida del proceso como JSON
    stdout_json = json.loads(process_stdout)

    # Inicializar el traductor
    translator = Translator()

    # Traducir los mensajes en cada objeto JSON
    for item in stdout_json:
        mensaje_traducido = translator.translate(item["message"], src='en', dest='es').text
        item["message"] = mensaje_traducido

    # Convertir nuevamente a formato JSON y devolver
    return json.dumps(stdout_json)


def ejecutar_pa11y(url_actual):
#    try:
    # Ejecuta pa11y y captura la salida directamente
    #command = f"pa11y --standard WCAG2AAA  --ignore issue-code-1 --ignore issue-code-2 --reporter csv {url_actual}"
    #command = f"pa11y --standard WCAG2AA  --reporter csv {url_actual}"
    #print("url p4lly:")
    #print(url_actual)
    #command = f"pa11y -e axe -d -T 3 --ignore issue-code-2 --ignore issue-code-1 -r json {url_actual}"
    command = f"pa11y -T 1 --ignore issue-code-2 --ignore issue-code-1 -r json {url_actual} 2>/dev/null"
    process = subprocess.run(command,
                                shell=True,
                                check=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)
    #return process.stdout
    #translator = Translator()
    #traduccion = translator.translate("hello sir how are you", src='en', dest='es')
    # Traducir los mensajes y devolver el resultado
    process_stdout_traducido = traducir_mensajes(process.stdout)

    #print("traduss:")
    #print(process_stdout_traducido)

    return process_stdout_traducido
    
 #   except Exception as e:  # subprocess.CalledProcessError as e:
 #       error_message = f"Error al ejecutar pa11y para {url_actual}: {e}"
 #       print(error_message)
 #       return []

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

               
