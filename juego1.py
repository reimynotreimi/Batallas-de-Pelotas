import pygame
import random
import sys
import os
import math
from pygame import gfxdraw
import tkinter as tk
from tkinter import filedialog

# Configuración inicial
os.chdir(os.path.dirname(__file__))
pygame.init()
ANCHO, ALTO = 800, 600
FPS = 60
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego Personalizable")
reloj = pygame.time.Clock()

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS = (100, 100, 100)
AZUL = (0, 100, 255)
VERDE = (0, 200, 100)
ROJO = (200, 50, 50)
AMARILLO = (255, 255, 0)
ROSADO = (255, 0, 255)

# Fuentes
fuente_pequena = pygame.font.SysFont('Arial', 20)
fuente_mediana = pygame.font.SysFont('Arial', 24, bold=True)
fuente_grande = pygame.font.SysFont('Arial', 36, bold=True)

# Configuración del juego
config = {
    'jugador1': {'nombre': 'Jugador 1', 'skin_path': None, 'color': ROJO, 'imagen': None},
    'jugador2': {'nombre': 'Jugador 2', 'skin_path': None, 'color': VERDE, 'imagen': None},
    'iniciado': False
}

# Cargar sonidos con manejo de errores
sonido_daño = None
sonido_chocar = None
sonido_ganar = None

try:
    # Intenta cargar los sonidos desde archivos
    sonido_daño = pygame.mixer.Sound("music/damage.mp3")
    sonido_chocar = pygame.mixer.Sound("music/hit.mp3")
    sonido_ganar = pygame.mixer.Sound("music/win.mp3")
except:
    print("Advertencia: No se encontraron archivos de sonido. El juego continuará sin sonidos.")
    # Crear sonidos básicos alternativos
    try:
        import numpy
        def crear_sonido(frecuencia, duracion):
            sample_rate = 44100
            samples = int(duracion * sample_rate)
            buf = numpy.zeros((samples, 2), dtype=numpy.int16)
            for s in range(samples):
                t = float(s)/sample_rate
                buf[s][0] = int(32767.0 * math.sin(2.0 * math.pi * frecuencia * t))
                buf[s][1] = int(32767.0 * math.sin(2.0 * math.pi * frecuencia * t))
            return pygame.sndarray.make_sound(buf)
        
        sonido_daño = crear_sonido(300, 0.1)  # Sonido grave para daño
        sonido_chocar = crear_sonido(600, 0.05)  # Sonido agudo para choque
        sonido_ganar = crear_sonido(784, 0.3)  # Sonido de victoria
    except:
        print("Advertencia: No se pudieron generar sonidos alternativos")

# Clases para el menú
class Boton:
    def __init__(self, x, y, ancho, alto, texto, color_normal, color_hover):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color_normal = color_normal
        self.color_hover = color_hover
        self.color_actual = color_normal
        self.texto_surf = fuente_mediana.render(texto, True, BLANCO)
        self.texto_rect = self.texto_surf.get_rect(center=self.rect.center)
    
    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color_actual, self.rect, border_radius=5)
        pygame.draw.rect(pantalla, BLANCO, self.rect, 2, border_radius=5)
        pantalla.blit(self.texto_surf, self.texto_rect)
    
    def verificar_hover(self, pos):
        if self.rect.collidepoint(pos):
            self.color_actual = self.color_hover
            return True
        self.color_actual = self.color_normal
        return False
    
    def verificar_clic(self, pos, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            return self.rect.collidepoint(pos)
        return False

class CampoTexto:
    def __init__(self, x, y, ancho, alto, texto_inicial=''):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.color = BLANCO
        self.texto = texto_inicial
        self.activo = False
        self.texto_surf = fuente_mediana.render(self.texto, True, self.color)
    
    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            self.activo = self.rect.collidepoint(evento.pos)
            self.color = AZUL if self.activo else BLANCO
        if evento.type == pygame.KEYDOWN and self.activo:
            if evento.key == pygame.K_RETURN:
                self.activo = False
                self.color = BLANCO
            elif evento.key == pygame.K_BACKSPACE:
                self.texto = self.texto[:-1]
            else:
                self.texto += evento.unicode
            self.texto_surf = fuente_mediana.render(self.texto, True, self.color)
    
    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rect, 2, border_radius=5)
        pantalla.blit(self.texto_surf, (self.rect.x + 5, self.rect.y + 5))
        if self.activo:
            pygame.draw.line(pantalla, self.color, 
                           (self.rect.x + 5 + self.texto_surf.get_width(), self.rect.y + 5),
                           (self.rect.x + 5 + self.texto_surf.get_width(), self.rect.y + self.rect.height - 5), 2)

class SelectorArchivo:
    def __init__(self, x, y, ancho, alto, texto_boton, jugador):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.boton = Boton(x, y, ancho, alto, texto_boton, GRIS, AZUL)
        self.jugador = jugador
        self.texto_archivo = fuente_pequena.render("Skin por defecto", True, BLANCO)
    
    def seleccionar_archivo(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title=f"Seleccionar skin para {self.jugador}",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            try:
                img = pygame.image.load(file_path).convert_alpha()
                config[self.jugador]['skin_path'] = file_path
                config[self.jugador]['imagen'] = img
                nombre = os.path.basename(file_path)
                self.texto_archivo = fuente_pequena.render(nombre, True, BLANCO)
                return True
            except:
                self.texto_archivo = fuente_pequena.render("Error cargando imagen", True, ROJO)
        return False
    
    def dibujar(self, pantalla):
        self.boton.dibujar(pantalla)
        pantalla.blit(self.texto_archivo, (self.rect.x, self.rect.y + self.rect.height + 5))

# Función para mostrar el menú de configuración
def mostrar_menu_configuracion():
    # Elementos de la interfaz
    titulo = fuente_grande.render("Personalización del Juego", True, BLANCO)
    
    # Campos para nombres
    campo_nombre1 = CampoTexto(150, 150, 200, 30, config['jugador1']['nombre'])
    campo_nombre2 = CampoTexto(450, 150, 200, 30, config['jugador2']['nombre'])
    
    # Selectores de skin
    selector_skin1 = SelectorArchivo(150, 220, 200, 40, "Skin Jugador 1", 'jugador1')
    selector_skin2 = SelectorArchivo(450, 220, 200, 40, "Skin Jugador 2", 'jugador2')
    
    # Botón de inicio
    boton_iniciar = Boton(300, 400, 200, 50, "INICIAR JUEGO", AZUL, (0, 150, 255))
    
    corriendo = True
    while corriendo:
        pantalla.fill(NEGRO)
        mouse_pos = pygame.mouse.get_pos()
        
        # Dibujar título
        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 50))
        
        # Dibujar etiquetas
        texto_jugador1 = fuente_mediana.render("Jugador 1", True, BLANCO)
        texto_jugador2 = fuente_mediana.render("Jugador 2", True, BLANCO)
        pantalla.blit(texto_jugador1, (150, 120))
        pantalla.blit(texto_jugador2, (450, 120))
        
        # Manejar eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            campo_nombre1.manejar_evento(evento)
            campo_nombre2.manejar_evento(evento)
            
            if selector_skin1.boton.verificar_clic(mouse_pos, evento):
                selector_skin1.seleccionar_archivo()
            if selector_skin2.boton.verificar_clic(mouse_pos, evento):
                selector_skin2.seleccionar_archivo()
            
            if boton_iniciar.verificar_clic(mouse_pos, evento):
                config['jugador1']['nombre'] = campo_nombre1.texto if campo_nombre1.texto else 'Jugador 1'
                config['jugador2']['nombre'] = campo_nombre2.texto if campo_nombre2.texto else 'Jugador 2'
                config['iniciado'] = True
                corriendo = False
        
        # Actualizar hover
        boton_iniciar.verificar_hover(mouse_pos)
        
        # Dibujar elementos
        campo_nombre1.dibujar(pantalla)
        campo_nombre2.dibujar(pantalla)
        selector_skin1.dibujar(pantalla)
        selector_skin2.dibujar(pantalla)
        boton_iniciar.dibujar(pantalla)
        
        pygame.display.flip()
        reloj.tick(FPS)

# Mostrar menú de configuración
mostrar_menu_configuracion()

# Si se completó la configuración, iniciar el juego
if config['iniciado']:
    # Cargar imágenes por defecto si no se seleccionaron
    if not config['jugador1']['imagen']:
        try:
            img_jugador1 = pygame.image.load("img/J1.png").convert_alpha()
            config['jugador1']['imagen'] = img_jugador1
        except:
            print("Error cargando skin por defecto para Jugador 1")
            # Crear una imagen por defecto
            img_jugador1 = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(img_jugador1, config['jugador1']['color'], (25, 25), 25)
            config['jugador1']['imagen'] = img_jugador1
    
    if not config['jugador2']['imagen']:
        try:
            img_jugador2 = pygame.image.load("img/J2.png").convert_alpha()
            config['jugador2']['imagen'] = img_jugador2
        except:
            print("Error cargando skin por defecto para Jugador 2")
            img_jugador2 = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(img_jugador2, config['jugador2']['color'], (25, 25), 25)
            config['jugador2']['imagen'] = img_jugador2

    # Cargar imagen de sierra
    try:
        img_sierra = pygame.image.load("img/saw.jpeg").convert_alpha()
        img_sierra = pygame.transform.scale(img_sierra, (30, 30))
    except:
        print("Error cargando imagen de sierra")
        img_sierra = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.rect(img_sierra, AMARILLO, (0, 0, 30, 30))

    # Configuración del juego
    pygame.display.set_caption(f"{config['jugador1']['nombre']} vs {config['jugador2']['nombre']}")
    
    # Clases del juego
    class Particula:
        def __init__(self, x, y, color):
            self.x = x
            self.y = y
            self.color = color
            self.radio = random.randint(2, 5)
            self.velx = random.uniform(-3, 3)
            self.vely = random.uniform(-3, 3)
            self.vida = 30
        
        def actualizar(self):
            self.x += self.velx
            self.y += self.vely
            self.vida -= 1
            self.radio = max(0, self.radio - 0.1)
        
        def dibujar(self):
            alpha = min(255, self.vida * 8)
            color_con_alpha = (*self.color, alpha)
            surf = pygame.Surface((self.radio*2, self.radio*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color_con_alpha, (self.radio, self.radio), self.radio)
            pantalla.blit(surf, (int(self.x - self.radio), int(self.y - self.radio)))

    class Estrella:
        def __init__(self):
            self.x = random.randint(0, ANCHO)
            self.y = random.randint(0, ALTO)
            self.tamano = random.randint(1, 3)
            self.velocidad = random.uniform(0.1, 0.5)
            self.brillo = random.randint(100, 255)
        
        def actualizar(self):
            self.y += self.velocidad
            if self.y > ALTO:
                self.y = 0
                self.x = random.randint(0, ANCHO)
            
            if random.random() < 0.02:
                self.brillo = random.randint(100, 255)
        
        def dibujar(self):
            color = (self.brillo, self.brillo, self.brillo)
            pygame.draw.circle(pantalla, color, (int(self.x), int(self.y)), self.tamano)

    def recortar_circular(imagen, radio):
        superficie_sombra = pygame.Surface((radio*2 + 6, radio*2 + 6), pygame.SRCALPHA)
        for i in range(10, 0, -1):
            alpha = 30 - i*3
            pygame.draw.circle(superficie_sombra, (0, 0, 0, alpha), (radio + 3, radio + 3), radio + i - 5)
        
        superficie_circular = pygame.Surface((radio*2, radio*2), pygame.SRCALPHA)
        pygame.draw.circle(superficie_circular, (255,255,255,255), (radio, radio), radio)
        mascara = pygame.mask.from_surface(superficie_circular)
        resultado = pygame.Surface((radio*2, radio*2), pygame.SRCALPHA)
        imagen_escalada = pygame.transform.smoothscale(imagen, (radio*2, radio*2))
        
        for x in range(radio*2):
            for y in range(radio*2):
                if mascara.get_at((x,y)):
                    resultado.set_at((x,y), imagen_escalada.get_at((x,y)))
                else:
                    resultado.set_at((x,y), (0,0,0,0))
        
        superficie_final = pygame.Surface((radio*2 + 6, radio*2 + 6), pygame.SRCALPHA)
        superficie_final.blit(superficie_sombra, (0, 0))
        superficie_final.blit(resultado, (3, 3))
        return superficie_final

    class Pelota:
        def __init__(self, x, y, tipo):
            self.x = x
            self.y = y
            self.radio = 36
            self.tipo = tipo
            self.velx = random.choice([-3, 3])
            self.vely = random.choice([-3, 3])
            self.vida = 100
            self.vida_segmentos = 10
            self.sierra_activa = False
            self.sierra_tiempo = 0
            self.imagen = recortar_circular(config[tipo]['imagen'], self.radio)
            self.tiempo_invulnerable = 0
            self.efecto_brillo = 0
        
        def mover(self):
            self.x += self.velx
            self.y += self.vely

            if self.x - self.radio <= cuadro_x or self.x + self.radio >= cuadro_x + cuadro_ancho:
                self.velx *= -1
            if self.y - self.radio <= cuadro_y or self.y + self.radio >= cuadro_y + cuadro_alto:
                self.vely *= -1

            self.limitar_velocidad()
            self.mantener_dentro()
            
            if self.sierra_activa:
                self.efecto_brillo = (self.efecto_brillo + 10) % 360
            else:
                self.efecto_brillo = 0

        def limitar_velocidad(self, max_vel=7):
            self.velx = max(-max_vel, min(self.velx, max_vel))
            self.vely = max(-max_vel, min(self.vely, max_vel))

        def mantener_dentro(self):
            if self.x - self.radio < cuadro_x:
                self.x = cuadro_x + self.radio
            if self.x + self.radio > cuadro_x + cuadro_ancho:
                self.x = cuadro_x + cuadro_ancho - self.radio
            if self.y - self.radio < cuadro_y:
                self.y = cuadro_y + self.radio
            if self.y + self.radio > cuadro_y + cuadro_alto:
                self.y = cuadro_y + cuadro_alto - self.radio

        def dibujar(self):
            if hasattr(self, 'tiempo_invulnerable') and self.tiempo_invulnerable > 0:
                self.tiempo_invulnerable -= 1
                if self.tiempo_invulnerable % 5 < 3:
                    return
            
            pantalla.blit(self.imagen, (int(self.x - self.radio - 3), int(self.y - self.radio - 3)))
            
            if self.sierra_activa:
                alpha = int(100 + 100 * math.sin(math.radians(self.efecto_brillo)))
                surf_brillo = pygame.Surface((self.radio*2, self.radio*2), pygame.SRCALPHA)
                pygame.draw.circle(surf_brillo, (255, 255, 100, alpha), (self.radio, self.radio), self.radio)
                pantalla.blit(surf_brillo, (int(self.x - self.radio), int(self.y - self.radio)))
            
            if self.sierra_activa:
                tiempo_restante = max(0, 3 - (pygame.time.get_ticks() - self.sierra_tiempo) // 1000)
                texto = fuente_mediana.render(str(tiempo_restante), True, AMARILLO)
                sombra_texto = fuente_mediana.render(str(tiempo_restante), True, (0, 0, 0))
                pantalla.blit(sombra_texto, (self.x - 6, self.y - 41))
                pantalla.blit(texto, (self.x - 5, self.y - 40))

        def recibir_daño(self, cantidad):
            self.vida = max(0, self.vida - cantidad)
            self.vida_segmentos = max(0, (self.vida + 9) // 10)
            self.tiempo_invulnerable = 30
            
            color = config[self.tipo]['color']
            for _ in range(15):
                angulo = random.uniform(0, 2 * math.pi)
                velocidad = random.uniform(1, 3)
                particulas.append(Particula(
                    self.x + math.cos(angulo) * self.radio,
                    self.y + math.sin(angulo) * self.radio,
                    color
                ))

    class Item:
        def __init__(self):
            self.x = random.randint(cuadro_x + 50, cuadro_x + cuadro_ancho - 50)
            self.y = random.randint(cuadro_y + 50, cuadro_y + cuadro_alto - 50)
            self.radio = 15
            self.angulo = 0
            self.tiempo_vida = 0
            self.alpha = 255
        
        def actualizar(self):
            self.angulo = (self.angulo + 10) % 360
            self.tiempo_vida += 1
            
            if self.tiempo_vida < 30:
                self.alpha = min(255, self.tiempo_vida * 8)
            
            if self.tiempo_vida > 150 and self.tiempo_vida % 10 < 5:
                self.alpha = 100
            else:
                self.alpha = 255
                
            return self.tiempo_vida < 180
        
        def dibujar(self):
            img_rotada = pygame.transform.rotate(img_sierra, self.angulo)
            img_rotada.set_alpha(self.alpha)
            rect = img_rotada.get_rect(center=(self.x, self.y))
            pantalla.blit(img_rotada, rect.topleft)
            
            if random.random() < 0.3:
                surf_aura = pygame.Surface((60, 60), pygame.SRCALPHA)
                pygame.draw.circle(surf_aura, (255, 255, 100, 30), (30, 30), 30)
                pantalla.blit(surf_aura, (self.x-30, self.y-30))

    def dibujar_barra_vida_segmentada(x, y, segmentos, color, etiqueta):
        pygame.draw.rect(pantalla, (50, 50, 50), (x-2, y-2, 204, 24))
        pygame.draw.rect(pantalla, (30, 30, 30), (x, y, 200, 20))
        
        for i in range(segmentos):
            segmento_x = x + i * 20
            color_brillo = (min(color[0]+40, 255), min(color[1]+40, 255), min(color[2]+40, 255))
            pygame.draw.rect(pantalla, color, (segmento_x, y, 18, 20))
            pygame.draw.rect(pantalla, color_brillo, (segmento_x, y, 18, 5))
        
        pygame.draw.rect(pantalla, (150, 150, 150), (x, y, 200, 20), 1)
        pygame.draw.rect(pantalla, (80, 80, 80), (x+1, y+1, 198, 18), 1)
        
        texto = fuente_mediana.render(etiqueta, True, (0, 0, 0))
        pantalla.blit(texto, (x + 76, y - 21))
        texto = fuente_mediana.render(etiqueta, True, (255, 255, 255))
        pantalla.blit(texto, (x + 75, y - 20))

    def dibujar_cuadro_juego():
        pygame.draw.rect(pantalla, (40, 0, 40), (cuadro_x-5, cuadro_y-5, cuadro_ancho+10, cuadro_alto+10), border_radius=10)
        
        for i in range(3):
            alpha = 100 - i*30
            color = (*ROSADO[:3], alpha)
            surf = pygame.Surface((cuadro_ancho+10-i*2, cuadro_alto+10-i*2), pygame.SRCALPHA)
            pygame.draw.rect(surf, color, (0, 0, cuadro_ancho+10-i*2, cuadro_alto+10-i*2), 2, border_radius=10-i)
            pantalla.blit(surf, (cuadro_x-5+i, cuadro_y-5+i))
        
        surf_interior = pygame.Surface((cuadro_ancho, cuadro_alto), pygame.SRCALPHA)
        surf_interior.fill((30, 0, 30, 150))
        pantalla.blit(surf_interior, (cuadro_x, cuadro_y))

    def colision(a, b):
        distancia = ((a.x - b.x)**2 + (a.y - b.y)**2)**0.5
        return distancia <= a.radio + b.radio

    def rebote(p1, p2):
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        distancia = (dx**2 + dy**2)**0.5
        if distancia == 0:
            distancia = 0.1
        nx, ny = dx / distancia, dy / distancia
        solapamiento = (p1.radio + p2.radio - distancia) / 2
        p1.x += nx * solapamiento
        p1.y += ny * solapamiento
        p2.x -= nx * solapamiento
        p2.y -= ny * solapamiento
        dvx = p1.velx - p2.velx
        dvy = p1.vely - p2.vely
        dot = dvx * nx + dvy * ny
        if dot > 0:
            return
    
        impulso = 1.2 * dot  # Menos impulso para no ralentizarlas mucho
        p1.velx -= impulso * nx
        p1.vely -= impulso * ny
        p2.velx += impulso * nx
        p2.vely += impulso * ny

    # Después del rebote, conservamos la magnitud de velocidad con dirección aleatoria
        for p in [p1, p2]:
            velocidad = math.hypot(p.velx, p.vely)
            velocidad = max(3, min(velocidad, 6))  # Controla que no sea muy lenta ni demasiado rápida
            angulo = random.uniform(0, 2 * math.pi)
            p.velx = math.cos(angulo) * velocidad
            p.vely = math.sin(angulo) * velocidad

    def reiniciar():
        global cuadro_x, cuadro_y, cuadro_ancho, cuadro_alto, items, tiempo_ultimo_item, juego_terminado, particulas
        jugador1.vida = 100
        jugador1.vida_segmentos = 10
        jugador2.vida = 100
        jugador2.vida_segmentos = 10

    # Posición aleatoria
        jugador1.x, jugador1.y = random.randint(cuadro_x + 100, cuadro_x + cuadro_ancho - 100), random.randint(cuadro_y + 100, cuadro_y + cuadro_alto - 100)
        jugador2.x, jugador2.y = random.randint(cuadro_x + 100, cuadro_x + cuadro_ancho - 100), random.randint(cuadro_y + 100, cuadro_y + cuadro_alto - 100)

    # Velocidad fija con dirección aleatoria (magnitud ≈ 4.2)
        ang1 = random.uniform(0, 2 * math.pi)
        jugador1.velx = math.cos(ang1) * 4.2
        jugador1.vely = math.sin(ang1) * 4.2

        ang2 = random.uniform(0, 2 * math.pi)
        jugador2.velx = math.cos(ang2) * 4.2
        jugador2.vely = math.sin(ang2) * 4.2

        jugador1.sierra_activa = jugador2.sierra_activa = False
        items.clear()
        particulas.clear()
        cuadro_x, cuadro_y = 100, 150
        cuadro_ancho, cuadro_alto = 600, 400
        tiempo_ultimo_item = pygame.time.get_ticks()
        juego_terminado = False


    # Configuración del juego
    cuadro_x, cuadro_y = 100, 150
    cuadro_ancho, cuadro_alto = 600, 400
    cuadro_min = 300
    tiempo_reduccion = 10000
    ultimo_encogimiento = pygame.time.get_ticks()
    tiempo_ultimo_item = pygame.time.get_ticks()
    TIEMPO_ESPERA_ITEM = 3000
    
    # Crear estrellas de fondo
    estrellas = [Estrella() for _ in range(100)]
    
    # Crear jugadores
    jugador1 = Pelota(200, 300, 'jugador1')
    jugador2 = Pelota(600, 300, 'jugador2')
    items = []
    particulas = []
    juego_terminado = False
    
    # Bucle principal del juego
    jugando = True
    while jugando:
        pantalla.fill(NEGRO)
        
        # Dibujar estrellas de fondo
        for estrella in estrellas:
            estrella.actualizar()
            estrella.dibujar()
        
        dibujar_cuadro_juego()
        
        mouse_pos = pygame.mouse.get_pos()
        ahora = pygame.time.get_ticks()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                jugando = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    reiniciar()
        
        if not juego_terminado:
            if ahora - ultimo_encogimiento > tiempo_reduccion and cuadro_ancho > cuadro_min:
                cuadro_x += 10
                cuadro_y += 10
                cuadro_ancho -= 20
                cuadro_alto -= 20
                ultimo_encogimiento = ahora
            
            jugador1.mover()
            jugador2.mover()
            
            if colision(jugador1, jugador2):
                rebote(jugador1, jugador2)
                if sonido_chocar:  # Reproducir sonido si existe
                    sonido_chocar.play()
                
                punto_medio_x = (jugador1.x + jugador2.x) / 2
                punto_medio_y = (jugador1.y + jugador2.y) / 2
                for _ in range(20):
                    color = random.choice([(255, 255, 255), (255, 200, 100), (200, 200, 255)])
                    particulas.append(Particula(punto_medio_x, punto_medio_y, color))
                
                if jugador1.sierra_activa:
                    jugador2.recibir_daño(10)
                    if sonido_daño:
                        sonido_daño.play()
                    jugador1.sierra_activa = False
                    tiempo_ultimo_item = ahora
                elif jugador2.sierra_activa:
                    jugador1.recibir_daño(10)
                    if sonido_daño:
                        sonido_daño.play()
                    jugador2.sierra_activa = False
                    tiempo_ultimo_item = ahora
            
            if not items and not jugador1.sierra_activa and not jugador2.sierra_activa:
                if ahora - tiempo_ultimo_item > TIEMPO_ESPERA_ITEM:
                    items.append(Item())
                    tiempo_ultimo_item = ahora
            
            for item in items[:]:
                if colision(jugador1, item):
                    jugador1.sierra_activa = True
                    jugador1.sierra_tiempo = ahora
                    items.remove(item)
                    tiempo_ultimo_item = ahora
                elif colision(jugador2, item):
                    jugador2.sierra_activa = True
                    jugador2.sierra_tiempo = ahora
                    items.remove(item)
                    tiempo_ultimo_item = ahora
            
            if jugador1.sierra_activa and ahora - jugador1.sierra_tiempo > 3000:
                jugador1.sierra_activa = False
                tiempo_ultimo_item = ahora
            if jugador2.sierra_activa and ahora - jugador2.sierra_tiempo > 3000:
                jugador2.sierra_activa = False
                tiempo_ultimo_item = ahora
        
        # Actualizar y dibujar partículas
        for particula in particulas[:]:
            particula.actualizar()
            if particula.vida <= 0:
                particulas.remove(particula)
        
        for particula in particulas:
            particula.dibujar()
        
        # Dibujar jugadores
        jugador1.dibujar()
        jugador2.dibujar()
        
        # Dibujar ítems
        for item in items:
            item.dibujar()
        
        # Dibujar barras de vida
        dibujar_barra_vida_segmentada(150, 50, jugador1.vida_segmentos, config['jugador1']['color'], config['jugador1']['nombre'])
        dibujar_barra_vida_segmentada(450, 50, jugador2.vida_segmentos, config['jugador2']['color'], config['jugador2']['nombre'])
        
        # Verificar si hay ganador
        if jugador1.vida <= 0 or jugador2.vida <= 0:
            if not juego_terminado:
                if sonido_ganar:  # Reproducir sonido de victoria si existe
                    sonido_ganar.play()
                juego_terminado = True
                
                ganador = jugador2 if jugador1.vida <= 0 else jugador1
                color = config['jugador2']['color'] if jugador1.vida <= 0 else config['jugador1']['color']
                for _ in range(50):
                    particulas.append(Particula(ganador.x, ganador.y, color))
            
            nombre_ganador = config['jugador2']['nombre'] if jugador1.vida <= 0 else config['jugador1']['nombre']
            texto = fuente_grande.render(f"¡{nombre_ganador} GANA!", True, BLANCO)
            sombra_texto = fuente_grande.render(f"¡{nombre_ganador} GANA!", True, (0, 0, 0))
            pantalla.blit(sombra_texto, (ANCHO // 2 - 140, ALTO // 2 - 51))
            pantalla.blit(texto, (ANCHO // 2 - 140, ALTO // 2 - 50))
            
            texto_reinicio = fuente_mediana.render("Presiona R para reiniciar", True, BLANCO)
            sombra_reinicio = fuente_mediana.render("Presiona R para reiniciar", True, (0, 0, 0))
            pantalla.blit(sombra_reinicio, (ANCHO // 2 - 100, ALTO // 2 + 10))
            pantalla.blit(texto_reinicio, (ANCHO // 2 - 100, ALTO // 2 + 11))
        
        pygame.display.flip()
        reloj.tick(FPS)

pygame.quit()
sys.exit()