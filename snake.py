"""
Juego de Snake (La Viborita) en Interfaz Gráfica con Tkinter
Proyecto para Programación - 4to Año

Controles:
  - Flechas del teclado o W, A, S, D : Mover la serpiente
  - Barra espaciadora o P           : Pausar / Reanudar
  - R                               : Reiniciar la partida
"""

import tkinter as tk
import random

# ==========================================
# CONSTANTES Y CONFIGURACIÓN DEL JUEGO
# ==========================================
ANCHO_TABLERO = 600
ALTO_TABLERO = 600
TAMANO_CELDA = 20  # Cada casilla mide 20x20 píxeles

COLUMNAS = ANCHO_TABLERO // TAMANO_CELDA
FILAS = ALTO_TABLERO // TAMANO_CELDA

VELOCIDAD_INICIAL = 110  # Milisegundos entre cada movimiento (menor = más rápido)
VELOCIDAD_MINIMA = 45    # Límite de velocidad máxima permitida

# Paleta de colores estilo Arcade moderno
COLOR_FONDO = "#1e1e2f"          # Azul oscuro / pizarra
COLOR_TABLERO = "#161623"        # Fondo del área de juego
COLOR_LINEA_GRID = "#222236"     # Líneas sutiles de la cuadrícula
COLOR_CABEZA = "#00e676"         # Verde brillante
COLOR_CUERPO = "#00b34d"         # Verde medio
COLOR_CUERPO_BORDE = "#008f3d"   # Borde de los segmentos
COLOR_COMIDA = "#ff5252"         # Rojo manzana
COLOR_COMIDA_HOJA = "#76ff03"    # Hoja de la manzana
COLOR_TEXTO = "#ffffff"          # Blanco
COLOR_TEXTO_SECUNDARIO = "#a0a0b0"
COLOR_PUNTAJE = "#ffd700"        # Dorado

# Colores de animación de muerte
COLOR_MUERTE_1 = "#ff1744"       # Rojo vibrante de choque
COLOR_MUERTE_2 = "#ffffff"       # Blanco de destello
COLOR_MUERTE_BORDE = "#b71c1c"   # Borde rojo oscuro


class JuegoSnake:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Juego de Snake 🐍 | Programación 4to Año")
        self.ventana.resizable(False, False)
        self.ventana.configure(bg=COLOR_FONDO)

        # Variables de estado del juego
        self.direccion = "Right"
        self.siguiente_direccion = "Right"
        self.puntaje = 0
        self.record = 0
        self.velocidad_actual = VELOCIDAD_INICIAL
        self.en_juego = False
        self.pausado = False
        self.en_animacion_muerte = False
        self.animacion_id = None
        self.es_nuevo_record = False

        # Widget del botón de reinicio en el canvas
        self.boton_reinicio = None

        # Estructuras de datos
        self.serpiente = []  # Lista de tuplas (x, y) representando cada segmento
        self.comida = None   # Tupla (x, y) con la posición de la manzana

        # Construir interfaz gráfica
        self._crear_interfaz()

        # Configurar eventos de teclado
        self._vincular_teclas()

        # Mostrar pantalla inicial de bienvenida
        self._mostrar_pantalla_inicio()

    # ----------------------------------------------------
    # CONSTRUCCIÓN DE LA INTERFAZ
    # ----------------------------------------------------
    def _crear_interfaz(self):
        # Panel superior: Puntajes y estado
        self.panel_superior = tk.Frame(self.ventana, bg=COLOR_FONDO, padx=15, pady=10)
        self.panel_superior.pack(fill="x")

        self.label_puntaje = tk.Label(
            self.panel_superior,
            text=f"Puntaje: {self.puntaje}",
            font=("Helvetica", 14, "bold"),
            fg=COLOR_PUNTAJE,
            bg=COLOR_FONDO
        )
        self.label_puntaje.pack(side="left")

        self.label_record = tk.Label(
            self.panel_superior,
            text=f"Récord: {self.record}",
            font=("Helvetica", 14, "bold"),
            fg=COLOR_TEXTO_SECUNDARIO,
            bg=COLOR_FONDO
        )
        self.label_record.pack(side="right")

        # Lienzo (Canvas) donde ocurre la acción del juego
        self.canvas = tk.Canvas(
            self.ventana,
            width=ANCHO_TABLERO,
            height=ALTO_TABLERO,
            bg=COLOR_TABLERO,
            highlightthickness=2,
            highlightbackground="#2d2d44"
        )
        self.canvas.pack(padx=15, pady=(0, 10))

        # Panel inferior: Atajos de teclado
        self.panel_inferior = tk.Frame(self.ventana, bg=COLOR_FONDO, pady=5)
        self.panel_inferior.pack(fill="x")

        self.label_ayuda = tk.Label(
            self.panel_inferior,
            text="Movimiento: Flechas / W A S D  |  Pausa: Espacio o P  |  Reiniciar: R",
            font=("Helvetica", 9),
            fg=COLOR_TEXTO_SECUNDARIO,
            bg=COLOR_FONDO
        )
        self.label_ayuda.pack()

    def _vincular_teclas(self):
        """Asocia las teclas con sus respectivas funciones."""
        teclas_flechas = ["<Up>", "<Down>", "<Left>", "<Right>"]
        for tecla in teclas_flechas:
            self.ventana.bind(tecla, self._cambiar_direccion)

        # Controles WASD (mayúsculas y minúsculas)
        self.ventana.bind("<w>", lambda e: self._solicitar_direccion("Up"))
        self.ventana.bind("<W>", lambda e: self._solicitar_direccion("Up"))
        self.ventana.bind("<s>", lambda e: self._solicitar_direccion("Down"))
        self.ventana.bind("<S>", lambda e: self._solicitar_direccion("Down"))
        self.ventana.bind("<a>", lambda e: self._solicitar_direccion("Left"))
        self.ventana.bind("<A>", lambda e: self._solicitar_direccion("Left"))
        self.ventana.bind("<d>", lambda e: self._solicitar_direccion("Right"))
        self.ventana.bind("<D>", lambda e: self._solicitar_direccion("Right"))

        # Pausa y reinicio
        self.ventana.bind("<space>", self._tecla_espacio_presionada)
        self.ventana.bind("<Return>", self._tecla_enter_presionada)
        self.ventana.bind("<p>", self._alternar_pausa)
        self.ventana.bind("<P>", self._alternar_pausa)
        self.ventana.bind("<r>", lambda e: self.iniciar_juego())
        self.ventana.bind("<R>", lambda e: self.iniciar_juego())

    # ----------------------------------------------------
    # CONTROL DE FLUJO Y EVENTOS
    # ----------------------------------------------------
    def _cambiar_direccion(self, evento):
        self._solicitar_direccion(evento.keysym)

    def _solicitar_direccion(self, nueva_direccion):
        """Evita giros en 180 grados sobre el propio cuerpo y cambios durante muerte."""
        if not self.en_juego or self.pausado or self.en_animacion_muerte:
            return

        opuestos = {
            "Up": "Down",
            "Down": "Up",
            "Left": "Right",
            "Right": "Left"
        }
        if nueva_direccion in opuestos:
            # Solo permitir el cambio si no es en sentido exactamente opuesto al actual
            if nueva_direccion != opuestos.get(self.direccion):
                self.siguiente_direccion = nueva_direccion

    def _tecla_espacio_presionada(self, evento=None):
        if self.en_animacion_muerte:
            return
        if not self.en_juego:
            self.iniciar_juego()
        else:
            self._alternar_pausa()

    def _tecla_enter_presionada(self, evento=None):
        if not self.en_juego and not self.en_animacion_muerte:
            self.iniciar_juego()

    def _alternar_pausa(self, evento=None):
        if not self.en_juego or self.en_animacion_muerte:
            return

        self.pausado = not self.pausado

        if self.pausado:
            if self.animacion_id:
                self.ventana.after_cancel(self.animacion_id)
            self._mostrar_pantalla_pausa()
        else:
            self.canvas.delete("mensaje_pausa")
            self._bucle_principal()

    # ----------------------------------------------------
    # LÓGICA DEL JUEGO
    # ----------------------------------------------------
    def iniciar_juego(self):
        """Reinicia el tablero y comienza una nueva partida."""
        if self.animacion_id:
            self.ventana.after_cancel(self.animacion_id)
            self.animacion_id = None

        # Destruir botón de reinicio anterior si existe
        if self.boton_reinicio:
            self.boton_reinicio.destroy()
            self.boton_reinicio = None

        # Posición inicial en el centro: cabeza y 2 segmentos
        cx = COLUMNAS // 2
        cy = FILAS // 2
        self.serpiente = [
            (cx, cy),
            (cx - 1, cy),
            (cx - 2, cy)
        ]

        self.direccion = "Right"
        self.siguiente_direccion = "Right"
        self.puntaje = 0
        self.velocidad_actual = VELOCIDAD_INICIAL
        self.en_juego = True
        self.pausado = False
        self.en_animacion_muerte = False
        self.es_nuevo_record = False

        self._actualizar_etiquetas()
        self._generar_comida()
        self._dibujar_escena()
        self._bucle_principal()

    def _generar_comida(self):
        """Genera una manzana en una casilla libre."""
        posiciones_ocupadas = set(self.serpiente)
        todas_las_posiciones = [
            (x, y)
            for x in range(COLUMNAS)
            for y in range(FILAS)
            if (x, y) not in posiciones_ocupadas
        ]

        if todas_las_posiciones:
            self.comida = random.choice(todas_las_posiciones)
        else:
            # ¡Tablero lleno! Ganó el juego
            self._juego_terminado(victoria=True)

    def _bucle_principal(self):
        """Ciclo continuo que actualiza la lógica y redibuja."""
        if not self.en_juego or self.pausado or self.en_animacion_muerte:
            return

        self._mover_serpiente()
        self._dibujar_escena()

        if self.en_juego:
            self.animacion_id = self.ventana.after(self.velocidad_actual, self._bucle_principal)

    def _mover_serpiente(self):
        self.direccion = self.siguiente_direccion
        cabeza_x, cabeza_y = self.serpiente[0]

        # Calcular nueva posición de la cabeza según la dirección
        desplazamiento = {
            "Up": (0, -1),
            "Down": (0, 1),
            "Left": (-1, 0),
            "Right": (1, 0)
        }
        dx, dy = desplazamiento[self.direccion]
        nueva_cabeza = (cabeza_x + dx, cabeza_y + dy)

        # 1. Comprobar colisión con bordes del tablero
        nx, ny = nueva_cabeza
        if nx < 0 or nx >= COLUMNAS or ny < 0 or ny >= FILAS:
            self._iniciar_muerte()
            return

        # 2. Comprobar colisión consigo misma
        cuerpo_a_chocar = self.serpiente[:-1]
        if nueva_cabeza in cuerpo_a_chocar:
            self._iniciar_muerte()
            return

        # Insertar la nueva cabeza
        self.serpiente.insert(0, nueva_cabeza)

        # 3. Comprobar si comió la manzana
        if nueva_cabeza == self.comida:
            self.puntaje += 10
            if self.puntaje > self.record:
                self.record = self.puntaje
                self.es_nuevo_record = True

            # Acelerar gradualmente
            if self.velocidad_actual > VELOCIDAD_MINIMA:
                self.velocidad_actual = max(VELOCIDAD_MINIMA, self.velocidad_actual - 2)

            self._actualizar_etiquetas()
            self._generar_comida()
        else:
            # Si no comió, se elimina el último segmento para mantener la longitud
            self.serpiente.pop()

    def _actualizar_etiquetas(self):
        self.label_puntaje.config(text=f"Puntaje: {self.puntaje}")
        self.label_record.config(text=f"Récord: {self.record}")

    # ----------------------------------------------------
    # ANIMACIÓN DE MUERTE
    # ----------------------------------------------------
    def _iniciar_muerte(self):
        """Detiene el movimiento e inicia la secuencia visual de muerte."""
        self.en_juego = False
        self.en_animacion_muerte = True
        if self.animacion_id:
            self.ventana.after_cancel(self.animacion_id)
            self.animacion_id = None

        # Fase 1: Parpadeo de impacto con ojos de 'X'
        self._animar_parpadeo_impacto(paso=0)

    def _animar_parpadeo_impacto(self, paso):
        """Hace parpadear la serpiente en rojo/blanco para enfatizar el choque."""
        if not self.en_animacion_muerte:
            return

        total_parpadeos = 6  # 3 ciclos de alternancia
        if paso < total_parpadeos:
            # Alternar colores de alarma
            color_activo = COLOR_MUERTE_1 if paso % 2 == 0 else COLOR_MUERTE_2
            borde_activo = COLOR_MUERTE_BORDE if paso % 2 == 0 else "#ff8a80"

            self.canvas.delete("all")
            self._dibujar_cuadricula()
            self._dibujar_comida()
            self._dibujar_serpiente(
                color_cabeza=color_activo,
                color_cuerpo=color_activo,
                color_borde=borde_activo,
                ojos_muertos=True
            )

            self.animacion_id = self.ventana.after(
                80, lambda: self._animar_parpadeo_impacto(paso + 1)
            )
        else:
            # Fase 2: Desintegración progresiva desde la cola hacia la cabeza
            self._animar_desintegracion()

    def _animar_desintegracion(self):
        """Elimina la serpiente segmento a segmento con efecto de partículas."""
        if not self.en_animacion_muerte:
            return

        if len(self.serpiente) > 0:
            # Retirar el último segmento (la cola)
            gx, gy = self.serpiente.pop()
            px = gx * TAMANO_CELDA
            py = gy * TAMANO_CELDA

            # Redibujar la escena restante
            self.canvas.delete("all")
            self._dibujar_cuadricula()
            self._dibujar_comida()
            self._dibujar_serpiente(
                color_cabeza=COLOR_MUERTE_1,
                color_cuerpo="#e53935",
                color_borde=COLOR_MUERTE_BORDE,
                ojos_muertos=True
            )

            # Efecto de destello / partícula en el segmento desvanecido
            destello = self.canvas.create_oval(
                px - 2, py - 2,
                px + TAMANO_CELDA + 2, py + TAMANO_CELDA + 2,
                fill="#ff8a80", outline="#ffffff", width=2
            )
            self.ventana.after(60, lambda d=destello: self.canvas.delete(d))

            # Calcular velocidad de desintegración fluida según longitud
            delay = max(25, min(50, 500 // (len(self.serpiente) + 1)))
            self.animacion_id = self.ventana.after(delay, self._animar_desintegracion)
        else:
            # Serpiente completamente desintegrada -> Fase 3: Mostrar Menú
            self.en_animacion_muerte = False
            self.canvas.delete("all")
            self._dibujar_cuadricula()
            self._dibujar_comida()
            self._mostrar_menu_game_over()

    def _juego_terminado(self, victoria=False):
        """Fin del juego por victoria (tablero completo)."""
        self.en_juego = False
        if self.animacion_id:
            self.ventana.after_cancel(self.animacion_id)
            self.animacion_id = None
        self._mostrar_menu_game_over(victoria=victoria)

    # ----------------------------------------------------
    # DIBUJO Y RENDERIZADO EN EL CANVAS
    # ----------------------------------------------------
    def _dibujar_escena(self):
        """Limpia el lienzo y redibuja la cuadrícula, comida y serpiente."""
        self.canvas.delete("all")
        self._dibujar_cuadricula()
        self._dibujar_comida()
        self._dibujar_serpiente()

    def _dibujar_cuadricula(self):
        """Dibuja líneas suaves para guiar la visión del jugador."""
        for x in range(0, ANCHO_TABLERO, TAMANO_CELDA):
            self.canvas.create_line(x, 0, x, ALTO_TABLERO, fill=COLOR_LINEA_GRID, width=1)
        for y in range(0, ALTO_TABLERO, TAMANO_CELDA):
            self.canvas.create_line(0, y, ANCHO_TABLERO, y, fill=COLOR_LINEA_GRID, width=1)

    def _dibujar_serpiente(
        self,
        color_cabeza=COLOR_CABEZA,
        color_cuerpo=COLOR_CUERPO,
        color_borde=COLOR_CUERPO_BORDE,
        ojos_muertos=False
    ):
        """Dibuja cada segmento del cuerpo y agrega detalles a la cabeza."""
        for indice, (gx, gy) in enumerate(self.serpiente):
            px = gx * TAMANO_CELDA
            py = gy * TAMANO_CELDA

            if indice == 0:
                # --- CABEZA ---
                self.canvas.create_rectangle(
                    px + 1, py + 1,
                    px + TAMANO_CELDA - 1, py + TAMANO_CELDA - 1,
                    fill=color_cabeza,
                    outline=color_borde,
                    width=2
                )
                self._dibujar_ojos(px, py, muertos=ojos_muertos)
            else:
                # --- CUERPO ---
                self.canvas.create_rectangle(
                    px + 2, py + 2,
                    px + TAMANO_CELDA - 2, py + TAMANO_CELDA - 2,
                    fill=color_cuerpo,
                    outline=color_borde,
                    width=1
                )

    def _dibujar_ojos(self, px, py, muertos=False):
        """Dibuja los ojos; en estado muerto dibuja cruces 'X'."""
        offset_ojos = {
            "Right": [(14, 6), (14, 14)],
            "Left":  [(6, 6), (6, 14)],
            "Up":    [(6, 6), (14, 6)],
            "Down":  [(6, 14), (14, 14)]
        }
        puntos = offset_ojos.get(self.direccion, [(14, 6), (14, 14)])

        for ox, oy in puntos:
            centro_x = px + ox
            centro_y = py + oy

            if muertos:
                # Ojos en forma de 'X' al morir
                radio_x = 3
                self.canvas.create_line(
                    centro_x - radio_x, centro_y - radio_x,
                    centro_x + radio_x, centro_y + radio_x,
                    fill="#ffffff", width=2
                )
                self.canvas.create_line(
                    centro_x - radio_x, centro_y + radio_x,
                    centro_x + radio_x, centro_y - radio_x,
                    fill="#ffffff", width=2
                )
            else:
                # Ojos vivos normales
                radio_ojo = 2.5
                radio_pupila = 1.2
                self.canvas.create_oval(
                    centro_x - radio_ojo, centro_y - radio_ojo,
                    centro_x + radio_ojo, centro_y + radio_ojo,
                    fill="#ffffff", outline=""
                )
                self.canvas.create_oval(
                    centro_x - radio_pupila, centro_y - radio_pupila,
                    centro_x + radio_pupila, centro_y + radio_pupila,
                    fill="#111111", outline=""
                )

    def _dibujar_comida(self):
        """Dibuja una manzana con hoja en la posición de la comida."""
        if not self.comida:
            return

        gx, gy = self.comida
        px = gx * TAMANO_CELDA
        py = gy * TAMANO_CELDA

        # Manzana (círculo rojo con margen interior)
        margen = 2
        self.canvas.create_oval(
            px + margen, py + margen,
            px + TAMANO_CELDA - margen, py + TAMANO_CELDA - margen,
            fill=COLOR_COMIDA,
            outline="#d32f2f",
            width=1
        )

        # Hoja pequeña verde arriba
        self.canvas.create_oval(
            px + TAMANO_CELDA // 2 - 1, py + 1,
            px + TAMANO_CELDA // 2 + 4, py + 5,
            fill=COLOR_COMIDA_HOJA,
            outline=""
        )

    # ----------------------------------------------------
    # MENÚS Y PANTALLAS (INICIO, PAUSA, GAME OVER)
    # ----------------------------------------------------
    def _mostrar_pantalla_inicio(self):
        self._dibujar_escena()

        # Marco del menú de bienvenida
        self.canvas.create_rectangle(
            60, 170, ANCHO_TABLERO - 60, 430,
            fill="#12121c", outline="#3a3a5a", width=2
        )

        self.canvas.create_text(
            ANCHO_TABLERO // 2, 220,
            text="SNAKE 🐍",
            font=("Helvetica", 32, "bold"),
            fill=COLOR_CABEZA
        )
        self.canvas.create_text(
            ANCHO_TABLERO // 2, 280,
            text="Moverse: Flechas del teclado o W, A, S, D",
            font=("Helvetica", 12),
            fill=COLOR_TEXTO
        )
        self.canvas.create_text(
            ANCHO_TABLERO // 2, 315,
            text="Pausa: Barra Espaciadora o tecla P",
            font=("Helvetica", 11),
            fill=COLOR_TEXTO_SECUNDARIO
        )
        self.canvas.create_text(
            ANCHO_TABLERO // 2, 370,
            text="Presiona ESPACIO, ENTER o 'R' para jugar",
            font=("Helvetica", 14, "bold"),
            fill=COLOR_PUNTAJE
        )

    def _mostrar_pantalla_pausa(self):
        self.canvas.create_rectangle(
            120, 240, ANCHO_TABLERO - 120, 360,
            fill="#12121c", outline=COLOR_PUNTAJE, width=2,
            tags="mensaje_pausa"
        )
        self.canvas.create_text(
            ANCHO_TABLERO // 2, 280,
            text="⏸️ JUEGO EN PAUSA",
            font=("Helvetica", 20, "bold"),
            fill=COLOR_PUNTAJE,
            tags="mensaje_pausa"
        )
        self.canvas.create_text(
            ANCHO_TABLERO // 2, 320,
            text="Presiona ESPACIO o P para continuar",
            font=("Helvetica", 11),
            fill=COLOR_TEXTO,
            tags="mensaje_pausa"
        )

    def _mostrar_menu_game_over(self, victoria=False):
        """Despliega una tarjeta de menú con puntajes y botón de reinicio interactivo."""
        centro_x = ANCHO_TABLERO // 2

        # 1. Tarjeta central de Game Over
        borde_color = COLOR_PUNTAJE if (self.es_nuevo_record or victoria) else "#ff5252"
        self.canvas.create_rectangle(
            60, 100, ANCHO_TABLERO - 60, 500,
            fill="#12121d", outline=borde_color, width=3,
            tags="menu_game_over"
        )

        # 2. Encabezado dinámico
        if victoria:
            titulo = "🏆 ¡VICTORIA TOTAL! 🏆"
            subtitulo = "¡Completaste todo el tablero!"
            color_titulo = COLOR_PUNTAJE
        elif self.es_nuevo_record and self.puntaje > 0:
            titulo = "🌟 ¡NUEVO RÉCORD! 🌟"
            subtitulo = "¡Superaste tu mejor marca personal!"
            color_titulo = COLOR_PUNTAJE
        else:
            titulo = "💀 ¡FIN DEL JUEGO! 💀"
            subtitulo = "La serpiente no sobrevivió al impacto"
            color_titulo = "#ff5252"

        self.canvas.create_text(
            centro_x, 150,
            text=titulo,
            font=("Helvetica", 24, "bold"),
            fill=color_titulo,
            tags="menu_game_over"
        )
        self.canvas.create_text(
            centro_x, 185,
            text=subtitulo,
            font=("Helvetica", 11),
            fill=COLOR_TEXTO_SECUNDARIO,
            tags="menu_game_over"
        )

        # 3. Recuadro comparativo de puntajes
        self.canvas.create_rectangle(
            90, 220, ANCHO_TABLERO - 90, 360,
            fill="#1c1c2e", outline="#2f2f4a", width=2,
            tags="menu_game_over"
        )

        # Puntaje de la partida
        self.canvas.create_text(
            centro_x, 255,
            text=f"Puntaje de la partida:  {self.puntaje}",
            font=("Helvetica", 18, "bold"),
            fill=COLOR_TEXTO,
            tags="menu_game_over"
        )

        # Récord histórico de la sesión
        self.canvas.create_text(
            centro_x, 300,
            text=f"👑  Mejor Récord:  {self.record}",
            font=("Helvetica", 15, "bold"),
            fill=COLOR_PUNTAJE,
            tags="menu_game_over"
        )

        # Mensaje de progreso
        manzanas_comidas = self.puntaje // 10
        self.canvas.create_text(
            centro_x, 335,
            text=f"🍎 Manzanas recolectadas: {manzanas_comidas}",
            font=("Helvetica", 11),
            fill=COLOR_TEXTO_SECUNDARIO,
            tags="menu_game_over"
        )

        # 4. Botón interactivo de Reinicio
        self.boton_reinicio = tk.Button(
            self.canvas,
            text="🔄  JUGAR DE NUEVO",
            font=("Helvetica", 13, "bold"),
            bg="#00e676",
            fg="#0e1726",
            activebackground="#00b34d",
            activeforeground="#0e1726",
            relief="flat",
            borderwidth=0,
            padx=25,
            pady=10,
            cursor="hand2",
            command=self.iniciar_juego
        )

        # Efecto visual de hover en el botón
        def on_enter(e):
            if self.boton_reinicio:
                self.boton_reinicio.config(bg="#33ff99")

        def on_leave(e):
            if self.boton_reinicio:
                self.boton_reinicio.config(bg="#00e676")

        self.boton_reinicio.bind("<Enter>", on_enter)
        self.boton_reinicio.bind("<Leave>", on_leave)

        # Insertar el botón centrado dentro del Canvas
        self.canvas.create_window(
            centro_x, 415,
            window=self.boton_reinicio,
            tags="menu_game_over"
        )

        # 5. Atajo rápido desde el teclado
        self.canvas.create_text(
            centro_x, 470,
            text="o presiona ESPACIO / R para reiniciar",
            font=("Helvetica", 10),
            fill=COLOR_TEXTO_SECUNDARIO,
            tags="menu_game_over"
        )


# ==========================================
# PUNTO DE ENTRADA PRINCIPAL
# ==========================================
if __name__ == "__main__":
    raiz = tk.Tk()
    app = JuegoSnake(raiz)
    raiz.mainloop()
