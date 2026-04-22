# Mi Desarrollo: Taller de Reloj en Python (Tick Node)

¡Hola! Este es mi desarrollo para el **Taller de Desarrollo de un Reloj con Python**. He construido esta aplicación enfocándome en demostrar cómo las estructuras de datos y los patrones de diseño pueden transformar un problema simple (un reloj) en una solución de software robusta, inmersiva y elegante.

## 🚀 Cómo Inicializar mi App

He desarrollado todo el proyecto utilizando **puramente Python**, cumpliendo con los requisitos del taller.

1. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecuta mi código**:
   ```bash
   python app.py
   ```

---

## 🧠 Estructuras de Datos que Utilicé

Para este taller, decidí no usar variables simples para el tiempo, sino estructuras que modelan el comportamiento circular de las horas, minutos y segundos:

1. **Listas Circulares Doblemente Enlazadas (Mi "Anillo de Tiempo")**: 
   - Implementé una `CircularDoublyLinkedList` personalizada para manejar los segundos, los minutos y las horas. 
   - **Ventaja**: El tiempo es intrínsecamente circular. Con esta lista, el paso del segundo 59 al 0 es simplemente saltar al siguiente nodo del anillo. Al ser **Doble**, pude implementar la "Máquina del Tiempo" que permite que el reloj corra hacia atrás con la misma fluidez.
   
2. **Pilas (Stacks - LIFO)**: 
   - Utilicé una estructura de **Pila** para gestionar mi **Historial de Viajes**.
   - **Ventaja**: Cada vez que viajas a una zona horaria, guardo el registro en el tope de la pila. Esto me permite ofrecer el botón "Deshacer Viaje", que saca el último destino y te devuelve exactamente por donde viniste.

---

## 🏗️ Patrones de Diseño de Software

Apliqué varios patrones para que mi código sea profesional y fácil de mantener:

- **Patrón Strategy**: Lo usé para definir cómo avanza el tiempo. Tengo una estrategia de "Flujo hacia Adelante" y otra de "Flujo hacia Atrás". El motor del reloj solo pide "avanzar", sin importarle la dirección.
- **Patrón Factory / Renderer Strategy**: He diseñado cada marca de lujo (Rolex, Cartier, Patek, etc.) como una estrategia de dibujo independiente. Esto me permitió crear geometrías complejas (como el Cartier rectangular) sin afectar el funcionamiento del reloj.
- **Clean Architecture**: Separé mi lógica en capas de **Dominio**, **Casos de Uso** e **Infraestructura**, asegurando que mi "Frontend" (hecho en CustomTkinter) solo sea una cáscara visual para mi motor de datos.

---

## ✨ Funcionalidad Aumentada (Mi Propuesta)

Para cumplir con el requerimiento de "aumentar una funcionalidad pertinente", desarrollé un **Motor de Ambientación Dinámica (Sky Engine)**:
- Mi reloj no está en un fondo estático; tiene un cielo que cambia según la hora virtual.
- Diseñé paisajes vectoriales con gradientes, montañas, nubes y estrellas que se adaptan al momento del día (Amanecer, Día, Atardecer y Noche).
- Además, los textos tienen sombras inteligentes que cambian para ser siempre legibles sobre cualquier color de fondo.

---

## 📖 Bitácora Detallada
He preparado una documentación paso a paso de cómo fui construyendo cada parte de mi taller:

👉 **[Ver Mi Walkthrough de Implementación](./docs/walkthrough.md)**

---
*Entregable para el Taller de Desarrollo de Relojes - Fecha de entrega: 28 de Abril.*
