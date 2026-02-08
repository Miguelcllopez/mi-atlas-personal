import os
import subprocess
import sys
from PIL import Image

# --- CONFIGURACIÓN DE LA MISIÓN ---
CARPETA_ORIGEN = "/mnt/d/FOTOS_GOOGLE/armenia-georgia" 
CARPETA_DESTINO = "assets/img/viajes/armenia"   
ANCHO_MAXIMO_FOTO = 1600
ANCHO_MAXIMO_VIDEO = 1280  # 720p (Ideal para móvil/web)
DURACION_MAXIMA = 10       # Recortar videos a X segundos
CALIDAD_JPG = 80                                

def verificar_ffmpeg():
    """Verifica si el motor de video está instalado"""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def procesar_video_ffmpeg(ruta_entrada, ruta_salida):
    """
    Comprime video usando ingeniería FFmpeg:
    - Recorta tiempo (-t)
    - Elimina audio (-an)
    - Redimensiona (-vf scale)
    - Comprime (-crf)
    """
    comando = [
        'ffmpeg',
        '-i', ruta_entrada,          
        '-t', str(DURACION_MAXIMA),  # Límite de tiempo
        '-vf', f"scale={ANCHO_MAXIMO_VIDEO}:-2", # Redimensionar 720p
        '-c:v', 'libx264',           # Codec estándar web
        '-an',                       # ELIMINAR AUDIO (Clave para reducir peso)
        '-crf', '28',                # Compresión alta calidad/bajo peso
        '-preset', 'faster',         
        '-y',                        # Sobrescribir
        ruta_salida,
        '-loglevel', 'error'
    ]
    subprocess.run(comando, check=True)

def ejecutar_mision():
    # 1. Check de Seguridad
    if not verificar_ffmpeg():
        print("❌ ERROR: FFmpeg no instalado. Ejecuta: sudo apt install ffmpeg")
        sys.exit(1)

    if not os.path.exists(CARPETA_DESTINO):
        os.makedirs(CARPETA_DESTINO)
        print(f"[INFO] Creando directorio: {CARPETA_DESTINO}")

    codigo_html = '<div class="galeria-dinamica">'
    contador_img = 0
    contador_vid = 0
    
    # Listas para la lógica de portada
    imagenes_validas = []
    candidato_portada = None

    # 2. Obtener archivos
    archivos = [f for f in os.listdir(CARPETA_ORIGEN) if not f.startswith('.')]
    archivos.sort() 

    print(f"--- 🚀 Iniciando Procesamiento (Fotos + Videos {DURACION_MAXIMA}s) ---")

    for nombre_archivo in archivos:
        ruta_origen = os.path.join(CARPETA_ORIGEN, nombre_archivo)
        ruta_final = os.path.join(CARPETA_DESTINO, nombre_archivo)
        
        # Normalizamos extensión
        nombre_base, ext_original = os.path.splitext(nombre_archivo)
        ext = ext_original.lower().replace('.', '')
        
        # Ruta web para Jekyll
        ruta_web = f"/{CARPETA_DESTINO}/{nombre_archivo}"

        try:
            # --- CASO A: FOTOS (Tu código original mejorado) ---
            if ext in ['jpg', 'jpeg', 'png', 'webp']:
                with Image.open(ruta_origen) as img:
                    ratio = ANCHO_MAXIMO_FOTO / float(img.size[0])
                    altura_nueva = int((float(img.size[1]) * float(ratio)))
                    img = img.resize((ANCHO_MAXIMO_FOTO, altura_nueva), Image.Resampling.LANCZOS)
                    if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                    
                    # Guardamos
                    img.save(ruta_final, "JPEG", quality=CALIDAD_JPG, optimize=True)
                    print(f"[FOTO] {nombre_archivo} -> Optimizada")
                    
                    # Generamos HTML
                    codigo_html += f'<img src="{ruta_web}" alt="{nombre_archivo}" loading="lazy">'
                    contador_img += 1
                    
                    # Lógica de Portada
                    imagenes_validas.append(ruta_web)
                    if "portada" in nombre_archivo.lower():
                        candidato_portada = ruta_web

            # --- CASO B: VIDEOS (La nueva funcionalidad) ---
            elif ext in ['mp4', 'mov', 'webm', 'm4v']:
                # Forzamos salida .mp4 siempre
                nombre_mp4 = f"{nombre_base}.mp4"
                ruta_final_video = os.path.join(CARPETA_DESTINO, nombre_mp4)
                ruta_web_video = f"/{CARPETA_DESTINO}/{nombre_mp4}"

                print(f"[VIDEO] {nombre_archivo} -> Comprimiendo...", end="", flush=True)
                
                # LLAMADA AL MOTOR FFMPEG (Sustituye a shutil.copy)
                procesar_video_ffmpeg(ruta_origen, ruta_final_video)
                
                print(" ✅")
                
                # HTML Inteligente
                codigo_html += f'<video src="{ruta_web_video}" autoplay loop muted playsinline preload="metadata"></video>'
                contador_vid += 1
            
        except Exception as e:
            print(f"\n[ERROR] {nombre_archivo}: {e}")

    codigo_html += '</div>'

    # --- SELECCIÓN DE PORTADA ---
    # Si hay una llamada "portada", úsala. Si no, la primera foto.
    portada_final = candidato_portada if candidato_portada else (imagenes_validas[0] if imagenes_validas else "")

    # 5. Salida de datos
    print("\n" + "="*50)
    print("✅  MISIÓN COMPLETADA")
    print(f"   📸 Fotos: {contador_img}")
    print(f"   🎥 Videos: {contador_vid}")
    print("="*50)
    print("1. COPIA ESTO EN EL YAML (Cabecera):")
    print(f"miniatura: {portada_final}")
    print("-" * 20)
    print("2. COPIA ESTO EN EL CUERPO DEL POST:")
    print(codigo_html)
    print("-" * 20)

if __name__ == "__main__":
    ejecutar_mision()