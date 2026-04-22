# Tick Node — Walkthrough de Implementación

---

## Fase 1: El Núcleo Puro (Capa de Dominio) ✅

### Objetivo
Crear las estructuras de datos estrictas y matemáticamente correctas, cumpliendo SRP.

### Archivos implementados

#### [entities.py](file:///c:/Users/Gabriel/Desktop/Tareas/EstructurasDatos/TickNode/tick_node_app/src/domain/entities.py)

**Clase `Node`** — Atributos `data`, `prev`, `next` con `__slots__`. Auto-enlace al nacer.

**Clase `CircularDoublyLinkedList`** — Anillo cerrado desde el constructor.

| Método | O() | Descripción |
|---|---|---|
| `__init__(values)` | O(n) | Anillo ya cerrado — último → primero |
| `advance_forward()` | O(1) | Cursor `.current` un paso adelante |
| `advance_backward()` | O(1) | Cursor un paso atrás |
| `find(target)` | O(n) | Busca valor; `KeyError` si no existe |
| `set_current(target)` | O(n) | Mueve cursor al valor dado |
| `to_list()` / `__iter__()` | O(n) | Extracción de datos sin print |

**Reglas cumplidas:** ✅ Cero `None` · ✅ Cero `print()` · ✅ Cero `if node is None`

#### [test_domain.py](file:///c:/Users/Gabriel/Desktop/Tareas/EstructurasDatos/TickNode/tick_node_app/tests/test_domain.py) — **30 tests passed**

---

## Fase 2: Infraestructura y Datos ✅

### Archivos implementados

#### [static_data.py](file:///c:/Users/Gabriel/Desktop/Tareas/EstructurasDatos/TickNode/tick_node_app/src/infrastructure/static_data.py)

**`WATCH_BRANDS`** — 5 marcas de lujo:

| Marca | Estilo | Fondo | Marcadores |
|---|---|---|---|
| Rolex Submariner | Baton | `#0B1A2E` | Dorado `#C4A34D` |
| Patek Philippe Calatrava | Roman | `#FAF6F0` | Negro `#2C2C2C` |
| Audemars Piguet Royal Oak | Baton | `#1B2838` | Blanco `#FFFFFF` |
| Omega Speedmaster | Arabic | `#1C1C1C` | Beige `#F5F5DC` |
| Cartier Tank | Roman | `#FFFFF0` | Azul `#00008B` |

**`TIME_ZONES`** — 26 zonas IANA agrupadas por continente.

#### [time_service.py](file:///c:/Users/Gabriel/Desktop/Tareas/EstructurasDatos/TickNode/tick_node_app/src/infrastructure/time_service.py)

**`TimeCalculator`** — `hour_difference(dest, origin)` → `int`. Cero APIs externas.

#### [test_infrastructure.py](file:///c:/Users/Gabriel/Desktop/Tareas/EstructurasDatos/TickNode/tick_node_app/tests/test_infrastructure.py) — **14 tests passed**

---

## Fase 3: Engranajes y Lógica de Negocio ✅

### Archivos implementados

#### [strategies.py](file:///c:/Users/Gabriel/Desktop/Tareas/EstructurasDatos/TickNode/tick_node_app/src/use_cases/strategies.py) — Patrón Strategy

```mermaid
classDiagram
    class TimeFlowStrategy {
        <<abstract>>
        +step(ring) Node
        +direction_name() str
    }
    class ForwardStrategy {
        +step(ring) Node
        +direction_name() str
    }
    class BackwardStrategy {
        +step(ring) Node
        +direction_name() str
    }
    TimeFlowStrategy <|-- ForwardStrategy
    TimeFlowStrategy <|-- BackwardStrategy
```

#### [clock_manager.py](file:///c:/Users/Gabriel/Desktop/Tareas/EstructurasDatos/TickNode/tick_node_app/src/use_cases/clock_manager.py) — El Orquestador

```mermaid
flowchart LR
    A["tick()"] --> B["strategy.step(seconds)"]
    B --> C{59→0 o 0→59?}
    C -->|Sí| D["strategy.step(minutes)"]
    C -->|No| G["return state"]
    D --> E{59→0 o 0→59?}
    E -->|Sí| F["strategy.step(hours)"]
    E -->|No| G
    F --> G
```

| Método | Descripción |
|---|---|
| `tick()` | Avanza segundos + cascada Observer a min/hrs |
| `shift_time_zone(int)` | Mueve solo puntero de horas N posiciones |
| `get_state()` | Dict `{hours, minutes, seconds, direction}` |
| `toggle_time_machine()` | Intercambia Forward ↔ Backward |

#### [test_use_cases.py](file:///c:/Users/Gabriel/Desktop/Tareas/EstructurasDatos/TickNode/tick_node_app/tests/test_use_cases.py) — **26 tests passed**

---

## Fase 4: Fábricas Visuales e Historial ✅

### Archivos implementados

#### [history.py](file:///c:/Users/Gabriel/Desktop/Tareas/EstructurasDatos/TickNode/tick_node_app/src/use_cases/history.py) — Pila LIFO

**Clase `HistoryStack`** — Stack clásico con lista nativa de Python.

| Método | Descripción |
|---|---|
| `push(item)` | Apila un registro de viaje |
| `pop()` | Desapila y retorna el último viaje (para "Deshacer") |
| `peek()` | Lee el tope sin desapilar |
| `is_empty()` | `True` si la pila está vacía |
| `__len__()` | Cantidad de viajes en el historial |

Cada item apilado: `{"from": "America/Bogota", "to": "Asia/Tokyo", "diff": 14}`

#### [watch_faces.py](file:///c:/Users/Gabriel/Desktop/Tareas/EstructurasDatos/TickNode/tick_node_app/src/ui/watch_faces.py) — Patrón Factory

**Clase `WatchFaceFactory`** — Construye figuras Plotly de relojes analógicos.

| Componente | Detalle |
|---|---|
| Dial | Círculo con fondo + bisel usando `go.Scatter(fill="toself")` |
| Marcadores | 3 estilos: `baton` (líneas), `roman` (I–XII), `arabic` (1–12) |
| Ticks minuto | 60 líneas pequeñas (excluye posiciones de hora) |
| Manecillas | 3 líneas con contrapeso: hora (0.50r), minuto (0.70r), segundo (0.80r) |
| Ángulos | `s*6°`, `m*6° + s*0.1°` (smooth), `h*30° + m*0.5°` (smooth) |
| Centro | Punto pivote con `go.Scatter(mode="markers")` |

> [!TIP]
> Las manecillas tienen **smooth sweep** — la manecilla de hora se mueve gradualmente con los minutos, y la de minutos con los segundos.

---

## Fase 5: Ensamblaje Frontend (Streamlit) ✅

### Archivo implementado

#### [app.py](file:///c:/Users/Gabriel/Desktop/Tareas/EstructurasDatos/TickNode/tick_node_app/app.py) — Punto de entrada

**Session State** — Inicializa una sola vez por sesión:
- `ClockManager` (sincronizado con hora real)
- `HistoryStack` (vacío)
- `brand_key` (default: "rolex")
- `current_zone` (detectado del sistema)
- `time_machine_on` / `auto_tick` (flags)

**Sidebar — Panel de Control:**

| Control | Acción |
|---|---|
| 🏷️ Marca de Lujo | Dropdown → cambia el estilo visual (Factory) |
| 🌍 Zona Horaria | Dropdown → calcula `hour_difference()`, ejecuta `shift_time_zone()`, push al `HistoryStack` |
| ⏪ Deshacer Viaje | Pop de la pila, aplica `shift_time_zone(-diff)` |
| ⏳ Máquina del Tiempo | Toggle → `toggle_time_machine()` (Forward ↔ Backward) |
| ⚡ Tick ×1 / ×60 | Botones manuales |
| Tick automático | Toggle → `st_autorefresh` cada 1 segundo |

**Área Principal:**
- Header "🕐 Tick Node"
- Reloj Plotly renderizado con `st.plotly_chart()`
- Readout digital monospace debajo
- Zona horaria actual

### Captura de la App Funcionando

![Tick Node — Rolex Submariner](file:///C:/Users/Gabriel/.gemini/antigravity/brain/1cc32264-1b69-4b83-bdee-4ccc3be84a57/streamlit_app_view_1776874448900.png)

---

---

## Fase 6: Ambientación Dinámica e Inmersión (Final Polish) ✅

### Archivos actualizados

#### [clock_canvas.py](file:///c:/Users/Gabriel/Desktop/Tareas/EstructurasDatos/TickNode/tick_node_app/src/ui/clock_canvas.py) — El "Motor de Renderizado"
Se implementó un sistema de renderizado procedural que va más allá de un simple reloj:
- **Cielo Dinámico (Sky Engine)**: El fondo del Canvas ya no es estático. Dibuja dinámicamente 5 estados del día basados en la hora virtual:
  - **Madrugada (0-5h)**: Cielo estrellado con luna creciente.
  - **Mañana (6-11h)**: Gradientes celestes a melocotón con montañas vectoriales y sol naciente.
  - **Día (12-16h)**: Praderas verdes, nubes esponjosas y sol en el cenit.
  - **Ocaso (17-19h)**: Paisaje dramático con montañas en silueta y gradientes de fuego (naranja/púrpura).
  - **Noche (20-23h)**: Cielo profundo con estrellas aleatorias (sembradas por la hora).
- **Legibilidad Inteligente (Drop Shadows)**: Los textos (Marca, Hora Digital, Itinerario) se dibujan con sombras paralelas que cambian de color automáticamente según el brillo del fondo para garantizar visibilidad total.
- **Estrategias de Relojes de Lujo (watch_faces.py)**: Cada marca tiene su propia geometría:
  - **Rolex Submariner**: Aguja "Mercedes" corregida matemáticamente para rotación perfecta.
  - **Cartier Tank**: Caja rectangular con "chemin de fer" (vía de tren) y aguja azulada de espada (minimalista, sin segundero originalmente, pero activable).
  - **Patek / Omega / Audemars**: Detalles en sub-esferas y biseles octogonales (Royal Oak).

#### [app.py](file:///c:/Users/Gabriel/Desktop/Tareas/EstructurasDatos\TickNode\tick_node_app\app.py) — Integración de Capas
- **Escalado Inteligente**: El reloj se ajusta al tamaño de la ventana pero mantiene un límite de zoom para no tapar los paisajes de fondo.
- **Desacoplamiento de UI**: La información digital (itinerario con banderas emoji 🇮🇹🇺🇸) se posiciona en los bordes para dejar el centro libre para la pieza de joyería analógica.

---

## Arquitectura Final — Clean Architecture (Desktop Edition)

```mermaid
graph TB
    subgraph "Capa de Dominio (Estructuras)"
        N["Node"]
        CDLL["CircularDoublyLinkedList (Anillos de Tiempo)"]
    end
    subgraph "Capa de Infraestructura (Datos)"
        SD["static_data.py (Zonas, Banderas, Marcas)"]
        TS["time_service.py (Cálculos de Delta)"]
    end
    subgraph "Capa de Casos de Uso (Lógica)"
        ST["strategies.py (Forward/Backward)"]
        CM["clock_manager.py (El Motor del Tiempo)"]
        HS["history.py (Pila de Viajes - LIFO)"]
    end
    subgraph "Capa de UI (Presentación 60FPS)"
        CC["clock_canvas.py<br/>HighResClockCanvas (Sky Engine)"]
        WF["watch_faces.py<br/>Estrategias de Dibujo (Rolex, Cartier...)"]
        CP["control_panel.py<br/>Sidebar CTk"]
        APP["app.py<br/>Game Loop & Sincronización"]
    end

    CDLL --> CM
    ST --> CM
    TS --> CM
    CM --> APP
    HS --> APP
    WF --> CC
    CC --> APP
    CP --> APP
```

### Cómo ejecutar la versión Desktop

```bash
cd tick_node_app
pip install -r requirements.txt
python app.py
```
