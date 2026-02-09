# Análisis de Correlaciones entre Mercados

Una herramienta profesional desarrollada en Python para analizar las correlaciones entre diversos mercados financieros (Divisas, Renta Fija, Materias Primas, Criptomonedas e Índices) utilizando datos en tiempo real de Yahoo Finance.

## 🚀 Características

- **Multimercado:** Monitorea más de 30 activos financieros clave.
- **Doble Horizonte Temporal:** Compara correlaciones de corto plazo (15 días) frente a medio plazo (3 meses).
- **Análisis de Diferencias:** Visualiza cómo están evolucionando las relaciones entre activos (si se están estrechando o separando).
- **Filtro de Correlaciones Fuertes:** Identifica automáticamente activos "Gemelos" o "Espejos" para estrategias de cobertura o diversificación.
- **Interfaz Nativa:** Diseñada para integrarse visualmente con Windows.
- **Exportación:** Guarda los mapas de calor como imágenes en alta resolución (.png).

## 🛠️ Instalación

### Versión Ejecutable (Recomendado)
1. Ve a la carpeta `dist/`.
2. Ejecuta `Analisis_Correlaciones.exe`.
*No requiere tener Python instalado.*

### Versión de Desarrollo
Si prefieres ejecutar el código fuente:
1. Clona el repositorio.
2. Instala las dependencias:
   ```bash
   pip install yfinance pandas seaborn matplotlib numpy
   ```
3. Ejecuta el script:
   ```bash
   python "corelación entre mercados.py"
   ```

## 📊 Estrategia de Uso
- **Correlación > 0.80:** Los activos se mueven casi idénticos. Riesgo de duplicar exposición.
- **Correlación < -0.80:** Los activos se mueven en sentidos opuestos. Ideal para coberturas (hedging).
- **Correlación cercana a 0:** Activos independientes. Ideal para diversificación real de cartera.

---
Desarrollado para análisis técnico y cuantitativo de mercados globales.
