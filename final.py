import time
import numpy as np
import cv2
import serial

from detector_tablero import detectar_tablero, calibrar_celdas
from ai_conecta4 import get_best_move, check_winner  

# Importamos tu función CINEMÁTICA INVERSA
from CI import mover_robot


# ------------------ CONFIG ------------------
IP_CAMARA = "192.168.1.181:8080"
# --------------------------------------------

# ========= PUERTO SERIAL =========
# Se abre solo UNA VEZ
ser = serial.Serial('COM13', 115200, timeout=1)
time.sleep(2)


# ========= FUNCIÓN PARA ENVIAR =========
def enviar_movimiento(arr):
    """
    Envía al ESP32 el arreglo EXACTO que entrega mover_robot()
    sin modificar nada.
    """
    msg = ",".join(str(v) for v in arr) + "\n"
    ser.write(msg.encode())
    print("Sent to ESP32:", msg.strip())


# ========= SECUENCIA COMPLETA DEL ROBOT =========
def ejecutar_secuencia_robot(columna_robot):
    print("\n[MOVIMIENTO] Ir a punto de toma (7)")
    arr = mover_robot(10)
    print("Arreglo:", arr)
    enviar_movimiento(arr)
    time.sleep(10)

    print("\n[MOVIMIENTO] Ir a punto medio (9)")
    arr = mover_robot(9)
    print("Arreglo:", arr)
    enviar_movimiento(arr)
    time.sleep(5)

    print(f"\n[MOVIMIENTO] Ir a columna {columna_robot}")
    arr = mover_robot(columna_robot)
    print("Arreglo:", arr)
    enviar_movimiento(arr)
    time.sleep(5)

    print("\n[MOVIMIENTO] Regresar a punto medio (9)")
    arr = mover_robot(9)
    print("Arreglo:", arr)
    enviar_movimiento(arr)
    time.sleep(5)

    print("\n[MOVIMIENTO] Regresar a punto de toma (8)")
    arr = mover_robot(11)
    print("Arreglo:", arr)
    enviar_movimiento(arr)



# =============== LOGICA JUEGO ===============
def jugar_partida():
    print("\n=== CONECTA 4 con Visión Artificial + Robot ===")
    humano_color = input("Elige tu color (R=rojo, Y=amarillo): ").strip().upper()
    color_humano = 2 if humano_color == "R" else 1
    color_robot = 1 if color_humano == 2 else 2

    print(f"Tu color: {'ROJO' if color_humano == 2 else 'AMARILLO'}")
    print("Presiona S para analizar el tablero, C para recalibrar, Q para salir.\n")

    while True:
        tecla = input(">> ").lower()

        if tecla == "s":
            try:
                tablero = detectar_tablero(IP_CAMARA)
                tablero_para_ia = np.flipud(tablero)
                print("Tablero detectado por cámara:\n", tablero)

                # Revisar ganador antes de jugar
                previo = check_winner(tablero_para_ia)

                if previo == color_robot:
                    print("\n>>> El robot YA HABÍA GANADO antes de mover.")
                    continue
                elif previo == color_humano:
                    print("\n>>> TÚ YA HABÍAS GANADO antes de mover.")
                    continue

                columna = get_best_move(tablero_para_ia, color_robot, color_humano)

                if columna is None:
                    print("\nNo hay jugadas disponibles. TABLERO LLENO.")
                    continue

                print(f"\n>>> El robot jugará en la columna {columna}")

                ejecutar_secuencia_robot(columna)

                time.sleep(2)
                tablero_despues = detectar_tablero(IP_CAMARA)
                tablero_final = np.flipud(tablero_despues)

                ganador = check_winner(tablero_final)

                if ganador == color_robot:
                    print("\n>>> El robot gana la partida.")
                elif ganador == color_humano:
                    print("\n>>> Tú ganas la partida.")
                else:
                    print("\n>>> Jugada completada. No hay ganador todavía.\n")

            except Exception as e:
                print("Error:", e)

        elif tecla == "c":
            calibrar_celdas(IP_CAMARA)

        elif tecla == "q":
            print("Saliendo...")
            return

        else:
            print("Tecla inválida. Usa S, C o Q.")



# ============== MAIN CON LOOP ==============
if __name__ == "__main__":
    while True:
        jugar_partida()
        again = input("\n¿Quieres jugar otra vez? (s/n): ").strip().lower()

        if again != "s":
            print("Fin del programa.")
            break
