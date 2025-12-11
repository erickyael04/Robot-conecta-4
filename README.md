# Robot-conecta-4
Códigos para un robot de 4gdl para jugar conecta 4

Este proyecto consta de 5 códigos que trabajan en conjunto para que un robot pueda jugar conecta 4 contra alguien.

El código CI describe la cinemática inversa de un robot de 4gdl, en este código se eneucnta un match el cuál tiene valores de puntos en el espacio de trabajo a los cuales el robot se deberá de mover, el valor de H que aparece dentro de los casos de 1-6 es un valor utilizado para crear un marco de referencia en el medio del tablero.

El código de conecta4_IA es el que rige toda la lógica sobre los moviemientos a emplear en el conecta 4, el código recibe una matriz de 1, 2 y 0, los cuales el 0 son celdas vacías y el 1 y el 2 serán los valores destinados a tus fichas y las del robot, el código lee la matriz y mediante ciclos for revisa si es que puede ganar en el siguiente moviemiento, si es así regresa el valor de la columna a mover, si no puede ganar revisa la posbilidad de que si puede perder en el siguiente movimiento, si puede perder el robot regresa el valor de la columna a bloquear, si ninguno de estos 2 casos se cumple mediante un minimax y sistemas de recompensas hacia el código el robot elige donde es más viable poner la ficha y regresa el valor de la columna jugada.

El código detector_tablero este código se ayuda de la librería openCV para poder abrir una cámara, en este caso desde una dirección IP, aquí podremos ver que hay una opción que es la letra C que nos servirá para calibrar nuestra cámara para que detecte el conecta 4, aquí tendras que seleccionar un total de 42 puntos empenzando de izquierda a derecha, arriba a abajo. El código en estos puntos detectará si hay un color rojo o amarillo y con eso creará una matriz para enviarla al programa principal.

El código de la ESP32 consiste en un control de los motores mediante lazo abierto, se crea una función que enviará el paso hacia el motor a pasos, cada motor tiene una configuración diferente dentro de su resolución, reducción, pines de step y dir, y si cuenta con micropasos.

El código final lo que hace es unir los primeros 3 códigos entre sí, el resultado de esto será una arreglo de números los cuáles son los valores de q1,q2,q3,q4 y el servomotor, primero se ejecutará una secuencia que el robot deberá seguir siempre, esta secuencia se enviará mediante el puerto serial a la ESP32.
