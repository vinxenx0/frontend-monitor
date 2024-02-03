from app import db
from datetime import datetime
from sqlalchemy import func, create_engine, Column, Integer, String, Text, DateTime, JSON, desc, update, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy import LargeBinary



# Definir el modelo de la tabla "resultados"
class Resultado(db.Model):
    __tablename__ = 'resultados'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha_escaneo = Column(DateTime, default=datetime.now)
    dominio = Column(String(255))
    codigo_respuesta = Column(Integer)
    tiempo_respuesta = Column(Float) #Column(Integer)
    pagina = Column(String(1383))
    parent_url = Column(String(1383))
    meta_tags = Column(JSON)
    heading_tags = Column(JSON)
    imagenes = Column(JSON)
    enlaces_totales = Column(Integer)
    enlaces_inseguros = Column(Integer)
    enlaces_internos = Column(Integer)
    enlaces_internos_unicos = Column(Integer)
    enlaces_js_unicos = Column(Integer)
    enlaces_salientes = Column(Integer)
    enlaces_salientes_unicos = Column(Integer)
    enlaces_salientes_js_unicos = Column(Integer)
    enlaces_salientes_externos = Column(Integer)
    enlaces_salientes_externos_unicos = Column(Integer)
    enlaces_salientes_js_externos_unicos = Column(Integer)
    tipos_archivos = Column(JSON)
    errores_ortograficos = Column(JSON)
    num_errores_ortograficos = Column(Integer)
    num_redirecciones = Column(Integer)
    alt_vacias = Column(Integer)
    num_palabras = Column(Integer)
    frases = Column(Integer)
    media_palabras_frase = Column(Integer)
    flesh_score = Column(Float)
    e_title = Column(Integer)
    e_head = Column(Integer)
    e_body = Column(Integer)
    e_html = Column(Integer)
    e_robots = Column(Integer)
    e_description = Column(Integer)
    e_keywords = Column(Integer)
    e_viewport = Column(Integer)
    e_charset = Column(Integer)
    c_title = Column(Text)
    c_robots = Column(Text)
    c_description = Column(Text)
    c_keywords = Column(Text)
    c_charset = Column(Text)
    html_valid = Column(Integer)
    content_valid = Column(Integer)
    responsive_valid = Column(Integer)
    image_types = Column(JSON)
    wcagaaa = Column(JSON)
    valid_aaa = Column(Integer)
    lang = Column(String(10))
    title_long = Column(String(1383))
    title_short = Column(String(1383))
    title_duplicate = Column(String(1383))
    desc_long = Column(String(1383))
    desc_short = Column(String(1383))
    h1_duplicate = Column(Integer)
    images_1MB = Column(Integer)
    imagenes_rotas = Column(Integer)
    html_copy = Column(Text)
    html_copy_dos = Column(Text)
    html_copy_tres = Column(Text)
    html_copy_cuatro = Column(Text)
    html_copy_cinco = Column(Text)
    html_copy_seis = Column(Text)
    html_copy_siete = Column(Text)
    html_copy_ocho = Column(Text)
    html_copy_nueve = Column(Text)
    html_copy_diez = Column(Text)
    id_escaneo = Column(String(255), nullable=False)
    peso_total_pagina = Column(Integer)
    is_pdf = Column(Integer)  
    meta_description_mas_155_caracteres = Column(Integer)
    meta_description_duplicado = Column(Integer)
    canonicals_falta = Column(Integer)
    directivas_noindex = Column(Integer)
    falta_encabezado_x_content_type_options = Column(Integer)
    falta_encabezado_secure_referrer_policy = Column(Integer)
    falta_encabezado_content_security_policy = Column(Integer)
    falta_encabezado_x_frame_options = Column(Integer)
    titulos_pagina_menos_30_caracteres = Column(Integer)
    meta_description_menos_70_caracteres = Column(Integer)
    titulos_pagina_mas_60_caracteres = Column(Integer)
    titulos_pagina_igual_h1 = Column(Integer)
    titulos_pagina_duplicado = Column(Integer)
    meta_description_falta = Column(Integer)
    version_http = Column(String(50))
    ultima_modificacion = Column(String(50))
    meta_og_card = Column(String(255))
    meta_og_title = Column(String(1383))
    meta_og_image = Column(String(1383))
    h2_duplicado = Column(Integer)
    h2_mas_70_caracteres = Column(Integer)
    h2_multiple = Column(Integer)
    h2_falta = Column(Integer)
    h2_no_secuencial = Column(Integer)


class Sumario(db.Model):
    __tablename__ = 'sumario'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dominio = Column(String(255))
    total_paginas = Column(Float)
    duracion_total = Column(Integer)
    codigos_respuesta = Column(JSON)
    hora_inicio = Column(String(20))
    hora_fin = Column(String(20))
    fecha = Column(String(10))
    html_valid_count = Column(Integer)
    content_valid_count = Column(Integer)
    responsive_valid_count = Column(Integer)
    valid_aaaa_pages = Column(Integer)
    idiomas = Column(JSON)
    paginas_inseguras = Column(Integer)  # Nuevo campo
    total_404 = Column(Integer)  # Nuevo campo
    enlaces_inseguros = Column(Integer)
    pages_title_long = Column(Integer)  # Nuevos campos
    pages_title_short = Column(Integer)
    pages_title_dup = Column(Integer)
    pages_desc_long = Column(Integer)
    pages_desc_short = Column(Integer)
    pages_h1_dup = Column(Integer)
    pages_img_1mb = Column(Integer)
    id_escaneo = Column(String(255), nullable=False)
    #id_escaneo = Column(Integer, ForeignKey('escaneo.id'))
    tiempo_medio = Column(Float)
    pages_err_orto = Column(Integer)
    pages_alt_vacias = Column(Integer)
    peso_total_paginas = Column(Integer)
    pdf_count = Column(Integer)
    html_count = Column(Integer)
    others_count = Column(Integer)
    media_frases= Column(Integer)
    total_media_palabras_frase= Column(Integer)
    media_flesh_score= Column(Integer)
    total_meta_description_mas_155_caracteres= Column(Integer)
    total_meta_description_duplicado= Column(Integer)
    total_canonicals_falta= Column(Integer)
    total_directivas_noindex= Column(Integer)
    total_falta_encabezado_x_content_type_options= Column(Integer)
    total_falta_encabezado_secure_referrer_policy= Column(Integer)
    total_falta_encabezado_content_security_policy= Column(Integer)
    total_falta_encabezado_x_frame_options= Column(Integer)
    total_titulos_pagina_menos_30_caracteres= Column(Integer)
    total_meta_description_menos_70_caracteres= Column(Integer)
    total_titulos_pagina_mas_60_caracteres= Column(Integer)
    total_titulos_pagina_igual_h1= Column(Integer)
    total_titulos_pagina_duplicado= Column(Integer)
    total_meta_description_falta= Column(Integer)
    total_h2_duplicado= Column(Integer)
    total_h2_mas_70_caracteres= Column(Integer)
    total_h2_multiple= Column(Integer)
    total_h2_falta= Column(Integer)
    total_h2_no_secuencial= Column(Integer)
    