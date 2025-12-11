from spatialmath import SE3  # Manejo de transformaciones espaciales
import numpy as np
from roboticstoolbox import *  # Librería de Peter Corke

# -------------------------------
# Función para obtener la posición según el valor c
# -------------------------------
ultimoservo=180  # Variable para almacenar la última posición del servo
def valor(c):
    H=SE3.Rz(1.5708) * SE3(.218, 0, .365)
    abierto = 180
    cerrado = 40
    global ultimoservo
    match c:
        case 0:
            ultimoservo= abierto
            return H* SE3(0, -.12857, 0), abierto
        case 1:
            ultimoservo= abierto
            return H *SE3(0, -.08571, 0), abierto
        case 2:
            ultimoservo= abierto
            return H* SE3(0, -.04285, 0), abierto
        case 3:
            ultimoservo= abierto
            return H * SE3(0, 0, 0), abierto
        case 4:
            ultimoservo= abierto
            return H *SE3(0, .04285, 0), abierto
        case 5:
            ultimoservo= abierto
            return H* SE3(0, .08571, 0), abierto
        case 6:
            ultimoservo= abierto
            return H* SE3(0, .12857, 0), abierto
        case 7:
            ultimoservo= cerrado
            return SE3(.196, 0, .317), cerrado
        case 8:
            ultimoservo= cerrado
            return SE3(.196, 0, .317), abierto
        case 9:
            return SE3(.118, .068, .425), ultimoservo
        case 10: # agarrar ficha en un punto alto
            ultimoservo= cerrado
            return SE3(.164, 0, .412), cerrado
        case 11: #mover el robot a lq altura del punto medio
            ultimoservo= abierto
            return SE3(.164, 0, .412), abierto
        case _:
            raise ValueError("El valor debe ser un número entero entre 1 y 7.")


# -------------------------------
# Función para obtener la transformación total
# -------------------------------
def mt(c):
    T, servo = valor(c)
    x = round(T.t[0], 4)
    y = round(T.t[1], 4)
    return T, x, y, servo


# -------------------------------
# Definición del robot
# -------------------------------
l1 = float(.1067)
l2 = float(0.210)
l3 = float(.0901)
l4 = float(.10)

robot = DHRobot([
    RevoluteDH(d=l1, a=0, alpha=-(np.pi / 2), offset=0, qlim=[-np.pi, np.pi]),
    RevoluteDH(d=0, a=l2, alpha=0, offset=-(np.pi / 2), qlim=[(-np.pi) / 4, (np.pi) / 4]),
    RevoluteDH(d=0, a=l3, alpha=np.pi, offset=(np.pi / 2), qlim=[(-np.pi) / 2, (np.pi) / 2]),
    RevoluteDH(d=0, a=l4, alpha=0, offset=0, qlim=[(-np.pi) / 2, (np.pi) / 2]),
], name='MyRobot')


# -------------------------------
# FUNCIÓN PRINCIPAL
# -------------------------------
def mover_robot(c):
    try:
        # Transformación del punto seleccionado
        T, x, y, servo = mt(c)
        q1 = round(np.arctan2(y, x), 4)
        q_init = [q1, 0, 0, 0]

        # Cálculo de la cinemática inversa
        solution = robot.ikine_LM(T, q_init, mask=[1, 1, 1, 0, 0, 0], joint_limits=True)
        #print(solution2)
        q_rad = solution.q
        q_deg = np.degrees(q_rad)
        q_deg = [round(angulo, 4) for angulo in q_deg]

        q_deg = np.append(q_deg, servo)

        print(f"Casilla seleccionada: {c}")
        print("Solución IK:", solution)
        print("Ángulos (°):", q_deg)

        return q_deg

    except Exception as e:
        print("Error:", e)
        return None, None, None
