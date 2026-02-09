import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
import numpy as np

# --- CONFIGURACIÓN DE ACTIVOS ---
activos = {
    # Divisas y Renta Fija
    "6B (Libra)": "6B=F", "ZN (10Y Bond)": "ZN=F", "6J (Yen)": "6J=F", 
    "6E (Euro)": "6E=F", "6S (Franco S.)": "6S=F", "6N (NZD)": "6N=F", 
    "6A (AUD)": "6A=F", "6C (CAD)": "6C=F", "ZT (2Y Bond)": "ZT=F",
    # Granos y Carnes
    "ZW (Trigo)": "ZW=F", "ZS (Soja)": "ZS=F", "ZC (Maíz)": "ZC=F",
    "ZM (Harina Soja)": "ZM=F", "ZL (Aceite Soja)": "ZL=F",
    "LE (Ganado Vivo)": "LE=F", "HE (Cerdo)": "HE=F",
    # Cripto y Metales
    "BTC": "BTC-USD", "ETH": "ETH-USD", "GC (Oro)": "GC=F", 
    "SI (Plata)": "SI=F", "HG (Cobre)": "HG=F", "PL (Platino)": "PL=F",
    # Energías
    "CL (Crudo WTI)": "CL=F", "RB (Gasolina)": "RB=F", 
    "NG (Gas Nat)": "NG=F", "HO (Heating Oil)": "HO=F",
    # Índices Bursátiles
    "ES (S&P 500)": "ES=F", "NQ (Nasdaq)": "NQ=F", 
    "YM (Dow Jones)": "YM=F", "RTY (Russell)": "RTY=F"
}

def obtener_datos():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Descargando datos de {len(activos)} mercados...")
    try:
        # Descargamos 6 meses para que la correlación de 60 días (3 meses) tenga sentido
        downloaded = yf.download(list(activos.values()), period="6mo", interval="1d", progress=False)
        if 'Close' in downloaded.columns:
            data = downloaded['Close']
        elif 'Adj Close' in downloaded.columns:
            data = downloaded['Adj Close']
        else:
            data = downloaded.iloc[:, 0] 
    except Exception as e:
        print(f"Error descargando datos: {e}")
        return None, None

    # Renombrar columnas
    inv_map = {v: k for k, v in activos.items()}
    data = data.rename(columns=inv_map)
    
    # Cálculo de matrices
    corr_15d = data.pct_change(15).dropna().corr()
    corr_60d = data.pct_change(60).dropna().corr() # 60 días ~ 3 meses de mercado
    
    return corr_15d, corr_60d

class CorrelationApp:
    def __init__(self, root, corr_15d, corr_60d):
        self.root = root
        self.root.title(f"Análisis de Correlaciones - {datetime.now().strftime('%d/%m/%Y')}")
        
        self.corr_15d = corr_15d
        self.corr_60d = corr_60d
        self.assets = list(corr_15d.columns)
        
        # --- NOTEBOOK (PESTAÑAS) ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 1: Matriz 15 Días
        self.tab_15d = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_15d, text="Matriz 15 Días")
        self.setup_heatmap_tab(self.tab_15d, self.corr_15d, "15 días")
        
        # Pestaña 2: Matriz 3 Meses
        self.tab_60d = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_60d, text="Matriz 3 Meses")
        self.setup_heatmap_tab(self.tab_60d, self.corr_60d, "3 meses (60 días)")

        # Pestaña 3: Comparativa Temporal (Diferencia)
        self.tab_diff = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_diff, text="Comparativa (15d vs 3m)")
        self.setup_diff_tab()
        
        # Pestaña 4: Correlaciones Fuertes (basada en 15 días)
        self.tab_strong = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_strong, text="Correlaciones Fuertes")
        self.setup_strong_corr_tab()

    def setup_diff_tab(self):
        # Calcular la matriz de diferencia
        self.diff_matrix = self.corr_15d - self.corr_60d
        
        container = ttk.Frame(self.tab_diff, padding="10")
        container.pack(fill=tk.BOTH, expand=True)

        # --- FRAME DE CONTROLES ---
        control_frame = ttk.Frame(container, padding="5")
        control_frame.pack(side=tk.TOP, fill=tk.X)

        style = ttk.Style()
        style.configure("Bold.TLabel", font=("Segoe UI", 10, "bold"))
        
        ttk.Label(control_frame, text="Activo A:", style="Bold.TLabel").pack(side=tk.LEFT, padx=5)
        self.diff_combo1 = ttk.Combobox(control_frame, values=self.assets, state="readonly", width=20)
        self.diff_combo1.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="Activo B:", style="Bold.TLabel").pack(side=tk.LEFT, padx=5)
        self.diff_combo2 = ttk.Combobox(control_frame, values=self.assets, state="readonly", width=20)
        self.diff_combo2.pack(side=tk.LEFT, padx=5)

        self.diff_result_label = ttk.Label(control_frame, text=" Seleccione activos para comparar ", font=("Segoe UI", 11, "bold"))
        self.diff_result_label.pack(side=tk.LEFT, padx=20)

        # Eventos para los selectores
        self.diff_combo1.bind("<<ComboboxSelected>>", self.update_diff_view)
        self.diff_combo2.bind("<<ComboboxSelected>>", self.update_diff_view)

        # Información de contexto
        lbl_info = ttk.Label(container, 
                             text="Diferencia: [15 Días] - [3 Meses]  |  Verde: Sube Correlación  |  Rojo: Baja Correlación",
                             font=("Segoe UI", 9, "italic"))
        lbl_info.pack(anchor=tk.W, pady=5)

        # --- FRAME DEL GRÁFICO ---
        plot_frame = ttk.Frame(container)
        plot_frame.pack(fill=tk.BOTH, expand=True)

        self.diff_figure = plt.Figure(figsize=(14, 10), dpi=100)
        self.diff_ax = self.diff_figure.add_subplot(111)
        self.diff_canvas = FigureCanvasTkAgg(self.diff_figure, master=plot_frame)
        self.diff_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.diff_highlight_rect = None

        sns.heatmap(
            self.diff_matrix, 
            annot=True, 
            fmt=".2f", 
            cmap='PiYG', 
            center=0, 
            linewidths=.5, 
            ax=self.diff_ax,
            cbar_kws={"label": "Cambio en Correlación"}
        )
        self.diff_ax.set_title("Evolución de Correlaciones (Corto vs Medio Plazo)", fontsize=16)
        self.diff_ax.tick_params(axis='x', rotation=45, labelsize=8)
        self.diff_ax.tick_params(axis='y', labelsize=8)
        self.diff_figure.tight_layout()
        
        # Clic en el mapa
        self.diff_canvas.mpl_connect('button_press_event', self.on_diff_click)

    def on_diff_click(self, event):
        if event.inaxes == self.diff_ax:
            col_idx = int(event.xdata)
            row_idx = int(event.ydata)
            if 0 <= col_idx < len(self.assets) and 0 <= row_idx < len(self.assets):
                self.diff_combo1.set(self.assets[row_idx])
                self.diff_combo2.set(self.assets[col_idx])
                self.update_diff_view()

    def update_diff_view(self, event=None):
        a1 = self.diff_combo1.get()
        a2 = self.diff_combo2.get()
        if a1 and a2:
            v15 = self.corr_15d.loc[a1, a2]
            v60 = self.corr_60d.loc[a1, a2]
            diff = self.diff_matrix.loc[a1, a2]
            
            # Calcular porcentaje de cambio
            if abs(v60) > 0.01:
                pct_change = (diff / abs(v60)) * 100
                pct_text = f"({pct_change:+.1f}%)"
            else:
                pct_text = "(Nuevo)" if abs(diff) > 0.1 else "(Sin cambio)"
            
            color = "#006400" if diff > 0.1 else "#8B0000" if diff < -0.1 else "black"
            texto = f"15d: {v15:.2f}  |  3m: {v60:.2f}  |  Dif: {diff:+.2f}  {pct_text}"
            self.diff_result_label.config(text=texto, foreground=color)
            
            # Resaltar en el mapa
            if self.diff_highlight_rect:
                self.diff_highlight_rect.remove()
            
            row_idx = self.assets.index(a1)
            col_idx = self.assets.index(a2)
            self.diff_highlight_rect = patches.Rectangle(
                (col_idx, row_idx), 1, 1, fill=False, edgecolor='blue', linewidth=3, zorder=100
            )
            self.diff_ax.add_patch(self.diff_highlight_rect)
            self.diff_canvas.draw()

    def setup_heatmap_tab(self, frame, matrix, label_text):
        # Almacenar datos específicos en el frame para recuperarlos en eventos
        frame.matrix = matrix
        frame.highlight_rect = None

        control_frame = ttk.Frame(frame, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        style = ttk.Style()
        style.configure("Bold.TLabel", font=("Segoe UI", 10, "bold"))
        style.configure("Big.TLabel", font=("Segoe UI", 14, "bold"), foreground="#333")

        ttk.Label(control_frame, text="Activo A:", style="Bold.TLabel").pack(side=tk.LEFT, padx=5)
        combo1 = ttk.Combobox(control_frame, values=self.assets, state="readonly", width=20)
        combo1.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="Activo B:", style="Bold.TLabel").pack(side=tk.LEFT, padx=5)
        combo2 = ttk.Combobox(control_frame, values=self.assets, state="readonly", width=20)
        combo2.pack(side=tk.LEFT, padx=5)
        
        result_label = ttk.Label(control_frame, text=" Seleccione dos activos ", style="Big.TLabel")
        result_label.pack(side=tk.LEFT, padx=30)

        # Guardar referencias en el frame para poder actualizarlas
        frame.combo1 = combo1
        frame.combo2 = combo2
        frame.result_label = result_label

        # Eventos
        combo1.bind("<<ComboboxSelected>>", lambda e: self.update_view_generic(frame))
        combo2.bind("<<ComboboxSelected>>", lambda e: self.update_view_generic(frame))

        ttk.Button(control_frame, text="Guardar Imagen", command=lambda: self.save_image_generic(frame, label_text)).pack(side=tk.RIGHT, padx=5)

        plot_frame = ttk.Frame(frame)
        plot_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        figure = plt.Figure(figsize=(14, 10), dpi=100)
        ax = figure.add_subplot(111)
        canvas = FigureCanvasTkAgg(figure, master=plot_frame)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        frame.figure = figure
        frame.ax = ax
        frame.canvas = canvas

        self.draw_heatmap_generic(frame, label_text)

    def draw_heatmap_generic(self, frame, label_text):
        sns.set_theme(style="white")
        
        def format_text(val):
            if val == 1.0: return "1.0"
            r2 = (val ** 2) * 100
            return f"{val:.2f}\n{r2:.0f}%"
        
        annot_labels = frame.matrix.applymap(format_text)
        
        sns.heatmap(
            frame.matrix, 
            annot=annot_labels, 
            fmt="", 
            cmap='RdYlGn', 
            center=0, 
            linewidths=.5, 
            ax=frame.ax,
            cbar_kws={"shrink": .8, "label": "Correlación"},
            annot_kws={"size": 7}
        )
        
        frame.ax.set_title(f"Matriz de Correlación ({label_text})", fontsize=16, pad=20)
        frame.ax.tick_params(axis='x', rotation=45, labelsize=8)
        frame.ax.tick_params(axis='y', labelsize=8)
        frame.figure.tight_layout()
        
        frame.canvas.mpl_connect('button_press_event', lambda e: self.on_heatmap_click_generic(e, frame))

    def on_heatmap_click_generic(self, event, frame):
        if event.inaxes == frame.ax:
            col_idx = int(event.xdata)
            row_idx = int(event.ydata)
            
            if 0 <= col_idx < len(self.assets) and 0 <= row_idx < len(self.assets):
                asset_a = self.assets[row_idx]
                asset_b = self.assets[col_idx]
                
                frame.combo1.set(asset_a)
                frame.combo2.set(asset_b)
                self.update_view_generic(frame)

    def update_view_generic(self, frame):
        asset1 = frame.combo1.get()
        asset2 = frame.combo2.get()
        
        if asset1 and asset2:
            val = frame.matrix.loc[asset1, asset2]
            r2 = (val ** 2) * 100
            
            color = "green" if val > 0 else "red"
            if abs(val) < 0.3: color = "gray"
            frame.result_label.config(text=f"Correlación: {val:.4f} | Similitud: {r2:.1f}%", foreground=color)
            
            if frame.highlight_rect:
                frame.highlight_rect.remove()
            
            row_idx = self.assets.index(asset1)
            col_idx = self.assets.index(asset2)
            
            frame.highlight_rect = patches.Rectangle(
                (col_idx, row_idx), 1, 1, 
                fill=False, edgecolor='#0000FF', linewidth=4, zorder=100
            )
            frame.ax.add_patch(frame.highlight_rect)
            frame.canvas.draw()

    def save_image_generic(self, frame, label_text):
        tag = label_text.replace(" ", "_").lower()
        filename = f"correlacion_{tag}_{datetime.now().strftime('%Y_%m_%d_%H%M')}.png"
        frame.figure.savefig(filename, dpi=300, bbox_inches='tight')
        tk.messagebox.showinfo("Guardado", f"Imagen guardada como:\n{filename}")

    def setup_strong_corr_tab(self):
        # Usamos la matriz de 15 días para las alertas fuertes
        corr_matrix = self.corr_15d
        
        # Frame contenedor
        container = ttk.Frame(self.tab_strong, padding="20")
        container.pack(fill=tk.BOTH, expand=True)
        
        # Explicación visual
        info_frame = ttk.LabelFrame(container, text="Leyenda", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        lbl_info = ttk.Label(info_frame, 
                             text="• Se muestran TODAS las correlaciones dentro de un mismo sector (Intra-Mercado).\n"
                                  "• Para cruces entre sectores (Inter-Mercado), se filtran las irrelevantes (0.2 a 0.5).\n"
                                  "• R² (Similitud): Porcentaje de movimiento compartido.",
                             font=("Segoe UI", 9), justify=tk.LEFT)
        lbl_info.pack(anchor=tk.W)

        # Treeview para listar
        columns = ("Par", "Corr", "R2", "Interpretación")
        tree = ttk.Treeview(container, columns=columns, show="tree headings", height=20)
        
        # Configurar columnas
        tree.heading("#0", text="Sector / Mercado")
        tree.heading("Par", text="Activos Comparados")
        tree.heading("Corr", text="Correlación (r)")
        tree.heading("R2", text="Similitud (R²)")
        tree.heading("Interpretación", text="Estrategia")
        
        tree.column("#0", width=200, anchor="w")
        tree.column("Par", width=200, anchor="center")
        tree.column("Corr", width=100, anchor="center")
        tree.column("R2", width=100, anchor="center")
        tree.column("Interpretación", width=250, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # --- DEFINICIÓN DE SECTORES ---
        cat_map = {}
        categorias_raw = {
            "Índices Bursátiles": ["ES", "NQ", "YM", "RTY"],
            "Energías": ["CL", "RB", "NG", "HO"],
            "Metales": ["GC", "SI", "HG", "PL"],
            "Cripto": ["BTC", "ETH"],
            "Divisas": ["6B", "6J", "6E", "6S", "6N", "6A", "6C"],
            "Bonos/Renta Fija": ["ZN", "ZT"],
            "Agricultura (Granos)": ["ZW", "ZS", "ZC", "ZM", "ZL"],
            "Ganadería (Carnes)": ["LE", "HE"]
        }
        
        # Mapeo inverso: Nombre Activo -> Categoría
        for cat, tickers in categorias_raw.items():
            for ticker_key in tickers:
                for asset_full in self.assets:
                    if asset_full.startswith(ticker_key + " ") or asset_full == ticker_key:
                        cat_map[asset_full] = cat

        # Estructura para agrupar resultados
        grouped_data = {cat: [] for cat in categorias_raw.keys()}
        grouped_data["Inter-Mercado (Mixtos)"] = []

        # Procesar datos
        for i in range(len(self.assets)):
            for j in range(i + 1, len(self.assets)):
                asset_a = self.assets[i]
                asset_b = self.assets[j]
                val = corr_matrix.iloc[i, j]
                r2 = (val ** 2) * 100
                
                cat_a = cat_map.get(asset_a, "Otros")
                cat_b = cat_map.get(asset_b, "Otros")
                
                # Determinar etiqueta y relevancia
                tipo = "Moderada"
                tag = "normal"
                
                if val >= 0.80:
                    tipo = "Gemelos (Riesgo Alto)"
                    tag = "pos_strong"
                elif 0.50 <= val < 0.80:
                    tipo = "Positiva Moderada"
                    tag = "pos_mod"
                elif -0.20 <= val <= 0.20:
                    tipo = "Independientes (Diversificar)"
                    tag = "null"
                elif -0.50 < val < -0.20:
                    tipo = "Inversa Débil"
                    tag = "neg_weak"
                elif -0.80 < val <= -0.50:
                    tipo = "Inversa Moderada"
                    tag = "neg_mod"
                elif val <= -0.80:
                    tipo = "Espejo (Cobertura)"
                    tag = "neg_strong"
                else:
                    tipo = "Positiva Débil / Ruido"
                    tag = "weak"

                # LÓGICA DE INCLUSIÓN
                incluir = False
                target_cat = "Inter-Mercado (Mixtos)"
                
                if cat_a == cat_b and cat_a != "Otros":
                    target_cat = cat_a
                    incluir = True
                else:
                    if tag != "weak" and tag != "null":
                        incluir = True

                if incluir:
                    item_data = (f"{asset_a} vs {asset_b}", val, r2, tipo, tag)
                    grouped_data[target_cat].append(item_data)

        # Insertar en Treeview
        for sector, items in grouped_data.items():
            if items:
                items.sort(key=lambda x: (x[0].split(' vs ')[0], -abs(x[1])))
                parent_id = tree.insert("", tk.END, text=f"{sector} ({len(items)})", open=True)
                for pair, val, r2, tipo, tag in items:
                    tree.insert(parent_id, tk.END, values=(pair, f"{val:.2f}", f"{r2:.1f}%", tipo), tags=(tag,))

        # Configurar colores
        tree.tag_configure("pos_strong", foreground="#006400", font=("Segoe UI", 9, "bold")) 
        tree.tag_configure("pos_mod", foreground="#228B22") 
        tree.tag_configure("neg_strong", foreground="#8B0000", font=("Segoe UI", 9, "bold")) 
        tree.tag_configure("neg_mod", foreground="#CD5C5C") 
        tree.tag_configure("neg_weak", foreground="#E9967A") 
        tree.tag_configure("null", foreground="#555555") 
        tree.tag_configure("weak", foreground="#999999")

if __name__ == "__main__":
    c15, c60 = obtener_datos()
    
    if c15 is not None:
        root = tk.Tk()
        
        # Aplicar tema nativo de Windows si está disponible
        style = ttk.Style(root)
        try:
            if "vista" in style.theme_names():
                style.theme_use("vista")
            elif "xpnative" in style.theme_names():
                style.theme_use("xpnative")
        except:
            pass

        try:
            root.state('zoomed')
        except:
            root.geometry("1400x900")
            
        app = CorrelationApp(root, c15, c60)
        root.mainloop()
    else:
        print("No se pudieron obtener datos para generar la matriz.")