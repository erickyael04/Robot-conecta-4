import cv2
import numpy as np
import os
import urllib.request

# ---------------- CONFIGURACIÓN ----------------
COORDS_FILE = "cell_coords.npy"
R_ADAPT = 20
MIN_RATIO = 0.12
MORPH_KERNEL = np.ones((3, 3), np.uint8)

# Rangos HSV
LOWER_YELLOW = np.array([15, 80, 80])
UPPER_YELLOW = np.array([40, 255, 255])
LOWER_RED1 = np.array([0, 90, 70])
UPPER_RED1 = np.array([10, 255, 255])
LOWER_RED2 = np.array([160, 90, 70])
UPPER_RED2 = np.array([180, 255, 255])

REF_RED_BGR = np.array([0, 0, 255], dtype=np.float32)
REF_YELLOW_BGR = np.array([0, 255, 255], dtype=np.float32)

# ------------------------------------------------

def obtener_frame_desde_ip(ip):
    """Captura un frame único desde la cámara IP."""
    url = f"http://{ip}/shot.jpg"
    resp = urllib.request.urlopen(url)
    img_array = np.asarray(bytearray(resp.read()), dtype=np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return frame

def circle_mask(h, w, cx, cy, r):
    Y, X = np.ogrid[:h, :w]
    dist = (X - cx)**2 + (Y - cy)**2
    return ((dist <= r*r).astype(np.uint8)) * 255

def mean_bgr_in_mask(img_bgr, mask):
    mask_bool = mask.astype(bool)
    if mask_bool.sum() == 0:
        return np.array([0, 0, 0], dtype=np.float32)
    vals = img_bgr[mask_bool]
    return vals.mean(axis=0).astype(np.float32)

def calibrar_celdas(ip_cam):
    """Permite seleccionar manualmente los 42 centros del tablero."""
    print("\n--- MODO CALIBRACIÓN ---")
    print("Presiona con clic en el centro de cada celda (de arriba a abajo, izquierda a derecha).")
    print("Presiona 'S' cuando termines para guardar.\n")

    frame = obtener_frame_desde_ip(ip_cam)
    puntos = []

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            puntos.append((x, y))
            cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow("Calibración", frame)
            print(f"Punto {len(puntos)} guardado: ({x},{y})")

    cv2.imshow("Calibración", frame)
    cv2.setMouseCallback("Calibración", click_event)

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            break
        elif key == ord('q'):
            cv2.destroyAllWindows()
            return

    np.save(COORDS_FILE, np.array(puntos))
    cv2.destroyAllWindows()
    print(f"Guardadas {len(puntos)} coordenadas en {COORDS_FILE}")

def detectar_tablero(ip_cam):
    """Toma una foto desde la cámara y analiza el tablero."""
    if not os.path.exists(COORDS_FILE):
        raise FileNotFoundError(f"No existe {COORDS_FILE}. Primero calibra con la tecla C.")

    coords = np.load(COORDS_FILE)
    frame = obtener_frame_desde_ip(ip_cam)
    img_h, img_w = frame.shape[:2]
    img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    img_vis = frame.copy()

    filas, columnas = 6, 7
    tablero = np.zeros((filas, columnas), dtype=int)

    for idx, (cx, cy) in enumerate(coords):
        cx, cy = int(cx), int(cy)
        mask = circle_mask(img_h, img_w, cx, cy, R_ADAPT)
        roi_hsv = img_hsv[max(0, cy - R_ADAPT):cy + R_ADAPT, max(0, cx - R_ADAPT):cx + R_ADAPT]
        roi_bgr = frame[max(0, cy - R_ADAPT):cy + R_ADAPT, max(0, cx - R_ADAPT):cx + R_ADAPT]
        mask_local = mask[max(0, cy - R_ADAPT):cy + R_ADAPT, max(0, cx - R_ADAPT):cx + R_ADAPT]

        mask_y = cv2.inRange(roi_hsv, LOWER_YELLOW, UPPER_YELLOW)
        mask_r1 = cv2.inRange(roi_hsv, LOWER_RED1, UPPER_RED1)
        mask_r2 = cv2.inRange(roi_hsv, LOWER_RED2, UPPER_RED2)
        mask_r = cv2.bitwise_or(mask_r1, mask_r2)

        mask_y = cv2.bitwise_and(mask_y, mask_local)
        mask_r = cv2.bitwise_and(mask_r, mask_local)

        mask_y = cv2.morphologyEx(mask_y, cv2.MORPH_OPEN, MORPH_KERNEL)
        mask_r = cv2.morphologyEx(mask_r, cv2.MORPH_OPEN, MORPH_KERNEL)

        cnt_y = cv2.countNonZero(mask_y)
        cnt_r = cv2.countNonZero(mask_r)
        area = cv2.countNonZero(mask_local)
        ratio_y = cnt_y / float(max(1, area))
        ratio_r = cnt_r / float(max(1, area))

        detected = 0
        color_draw = (180, 180, 180)
        if ratio_y >= MIN_RATIO and ratio_y > ratio_r:
            detected = 1
            color_draw = (0, 255, 255)
        elif ratio_r >= MIN_RATIO and ratio_r > ratio_y:
            detected = 2
            color_draw = (0, 0, 255)

        row = idx // columnas
        col = idx % columnas
        tablero[row, col] = detected
        cv2.circle(img_vis, (cx, cy), R_ADAPT, color_draw, 2)

    print("\nMatriz del tablero:")
    print(tablero)

    cv2.imshow("Resultado", img_vis)
    cv2.waitKey(1000)
    cv2.destroyWindow("Resultado")

    return tablero
