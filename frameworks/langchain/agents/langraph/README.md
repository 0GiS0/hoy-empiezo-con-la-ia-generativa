# 🕸️ LangGraph Agents

Esta carpeta contiene ejemplos de agentes utilizando **LangGraph**, mostrando las ventajas de un control explícito del flujo sobre el `AgentExecutor` tradicional.

## 📁 Archivos

- **`app.py`** - Ejemplo original más complejo (puede tener issues)
- **`app_simple.py`** - ✅ **Versión recomendada** - Ejemplo simplificado y funcional
- **`requirements.txt`** - Dependencias necesarias

## 🚀 Cómo ejecutar

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno (copia desde el directorio raíz)
cp ../../../.env.example .env

# Ejecutar el ejemplo
python app_simple.py
```

## 🌟 Ventajas de LangGraph vs AgentExecutor

### AgentExecutor (Tradicional)
❌ **Caja negra** - No puedes ver qué pasa internamente  
❌ **Control limitado** - Flujo fijo y poco personalizable  
❌ **Difícil depuración** - Solo modo `verbose=True`  
❌ **Estado oculto** - No sabes qué información maneja  

### LangGraph
✅ **Transparencia total** - Ves cada paso del proceso  
✅ **Control explícito** - Defines exactamente el flujo  
✅ **Observabilidad completa** - Stream en tiempo real  
✅ **Estado predecible** - Sabes exactamente qué datos tienes  
✅ **Modular** - Reutilizas nodos en diferentes grafos  
✅ **Flexible** - Ciclos, ramificaciones, intervención humana  

## 🎯 Cuándo usar cada uno

### Usa AgentExecutor cuando:
- 🚀 Necesites un prototipo rápido
- 📝 El caso de uso sea simple y directo
- 🎯 No requieras personalización del flujo

### Usa LangGraph cuando:
- 🏭 Desarrolles aplicaciones de producción
- 🤹 Necesites múltiples agentes colaborando
- 🔍 Requieras máxima observabilidad
- 🌊 El flujo tenga lógica compleja de decisión
- 👨‍💻 Necesites intervención humana en el proceso

## 🎬 Ejemplo de Salida

```
🤖 Ejecutando el grafo del agente...
--- 🔄 SALIDA DEL NODO: 'agent' ---
--- 🔄 SALIDA DEL NODO: 'action' ---  
--- 🔄 SALIDA DEL NODO: 'agent' ---

🤖 Respuesta Final del Agente:
Estos son 5 títulos optimizados para YouTube...
```

## 🧩 Arquitectura del Grafo

```
[Entrada] → [Agente] → [¿Usar herramientas?]
                ↓            ↓
              [FIN] ← [Herramientas] ← [SÍ]
```

Cada paso es **visible** y **controlable**, a diferencia del AgentExecutor que oculta esta lógica.

## 🎨 Visualización del Grafo

Una de las **ventajas clave** de LangGraph es poder visualizar el grafo:

### 📊 Representación Mermaid (Texto)
```python
mermaid_code = app.get_graph().draw_mermaid()
print(mermaid_code)
```

### 🖼️ Imagen PNG
```python
png_data = app.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(png_data)
```

### 🔍 Ejecutar Demo de Visualización
```bash
python demo_visualization.py
```

Este comando genera:
- ✅ Código Mermaid para copiar a [mermaid.live](https://mermaid.live/)
- ✅ Imagen PNG del grafo
- ✅ Información detallada de nodos y aristas
- ✅ Consejos para usar las visualizaciones

### 🎯 Archivos Generados
- `graph_visualization.png` - Grafo del ejemplo principal
- `demo_graph_complex.png` - Grafo más complejo del demo