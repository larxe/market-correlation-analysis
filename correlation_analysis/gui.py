"""GUI application for market correlation analysis using Tkinter."""

from __future__ import annotations

import logging
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Optional

import matplotlib.patches as mpl_patches
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from correlation_analysis.config import (
    COLOR_HIGHLIGHT,
    COLOR_NEGATIVE,
    COLOR_NEUTRAL,
    COLOR_POSITIVE,
    DIFF_NEGATIVE_THRESHOLD,
    DIFF_POSITIVE_THRESHOLD,
    EXPORT_DPI,
    FIGURE_DPI,
    FIGURE_SIZE,
    NEW_CORRELATION_THRESHOLD,
    PCT_CHANGE_MIN_DENOMINATOR,
    SECTORS,
    WEAK_CORRELATION_DISPLAY,
    WINDOW_FALLBACK_GEOMETRY,
)
from correlation_analysis.logic import (
    build_category_map,
    classify_correlation,
    group_correlations,
)

logger = logging.getLogger(__name__)


class _HeatmapTabState:
    """Holds mutable state for a single heatmap tab to avoid dynamic frame attrs."""

    def __init__(
        self,
        matrix: pd.DataFrame,
        figure: plt.Figure,
        ax: plt.Axes,
        canvas: FigureCanvasTkAgg,
        combo1: ttk.Combobox,
        combo2: ttk.Combobox,
        result_label: ttk.Label,
    ) -> None:
        self.matrix = matrix
        self.figure = figure
        self.ax = ax
        self.canvas = canvas
        self.combo1 = combo1
        self.combo2 = combo2
        self.result_label = result_label
        self.highlight_rect: Optional[mpl_patches.Rectangle] = None


class CorrelationApp:
    """Main application class for the market correlation GUI."""

    def __init__(
        self, root: tk.Tk, corr_short: pd.DataFrame, corr_medium: pd.DataFrame
    ) -> None:
        self.root = root
        self.root.title(
            f"Market Correlation Analysis - {datetime.now().strftime('%m/%d/%Y')}"
        )

        self.corr_short = corr_short
        self.corr_medium = corr_medium
        self.assets: list[str] = list(corr_short.columns)

        self._tab_states: dict[str, _HeatmapTabState] = {}

        # --- NOTEBOOK (TABS) ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Short-term matrix
        tab_short = ttk.Frame(self.notebook)
        self.notebook.add(tab_short, text="15-Day Matrix")
        self._setup_heatmap_tab(tab_short, self.corr_short, "15 Days", "short")

        # Tab 2: Medium-term matrix
        tab_medium = ttk.Frame(self.notebook)
        self.notebook.add(tab_medium, text="3-Month Matrix")
        self._setup_heatmap_tab(
            tab_medium, self.corr_medium, "3 Months (60 Days)", "medium"
        )

        # Tab 3: Temporal comparison (difference)
        self.tab_diff = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_diff, text="Comparison (15d vs 3m)")
        self._setup_diff_tab()

        # Tab 4: Strong correlations
        tab_strong = ttk.Frame(self.notebook)
        self.notebook.add(tab_strong, text="Strong Correlations")
        self._setup_strong_corr_tab(tab_strong)

    # ------------------------------------------------------------------ #
    #  Diff tab
    # ------------------------------------------------------------------ #

    def _setup_diff_tab(self) -> None:
        self.diff_matrix = self.corr_short - self.corr_medium

        container = ttk.Frame(self.tab_diff, padding="10")
        container.pack(fill=tk.BOTH, expand=True)

        control_frame = ttk.Frame(container, padding="5")
        control_frame.pack(side=tk.TOP, fill=tk.X)

        style = ttk.Style()
        style.configure("Bold.TLabel", font=("Segoe UI", 10, "bold"))

        ttk.Label(control_frame, text="Asset A:", style="Bold.TLabel").pack(
            side=tk.LEFT, padx=5
        )
        self.diff_combo1 = ttk.Combobox(
            control_frame, values=self.assets, state="readonly", width=20
        )
        self.diff_combo1.pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Asset B:", style="Bold.TLabel").pack(
            side=tk.LEFT, padx=5
        )
        self.diff_combo2 = ttk.Combobox(
            control_frame, values=self.assets, state="readonly", width=20
        )
        self.diff_combo2.pack(side=tk.LEFT, padx=5)

        self.diff_result_label = ttk.Label(
            control_frame,
            text=" Select assets to compare ",
            font=("Segoe UI", 11, "bold"),
        )
        self.diff_result_label.pack(side=tk.LEFT, padx=20)

        self.diff_combo1.bind("<<ComboboxSelected>>", self._update_diff_view)
        self.diff_combo2.bind("<<ComboboxSelected>>", self._update_diff_view)

        lbl_info = ttk.Label(
            container,
            text=(
                "Difference: [15 Days] - [3 Months]  |  "
                "Green: Correlation Increasing  |  Red: Correlation Decreasing"
            ),
            font=("Segoe UI", 9, "italic"),
        )
        lbl_info.pack(anchor=tk.W, pady=5)

        plot_frame = ttk.Frame(container)
        plot_frame.pack(fill=tk.BOTH, expand=True)

        self.diff_figure = plt.Figure(figsize=FIGURE_SIZE, dpi=FIGURE_DPI)
        self.diff_ax = self.diff_figure.add_subplot(111)
        self.diff_canvas = FigureCanvasTkAgg(self.diff_figure, master=plot_frame)
        self.diff_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.diff_highlight_rect: Optional[mpl_patches.Rectangle] = None

        sns.heatmap(
            self.diff_matrix,
            annot=True,
            fmt=".2f",
            cmap="PiYG",
            center=0,
            linewidths=0.5,
            ax=self.diff_ax,
            cbar_kws={"label": "Correlation Change"},
        )
        self.diff_ax.set_title(
            "Correlation Evolution (Short vs Medium Term)", fontsize=16
        )
        self.diff_ax.tick_params(axis="x", rotation=45, labelsize=8)
        self.diff_ax.tick_params(axis="y", labelsize=8)
        self.diff_figure.tight_layout()

        self.diff_canvas.mpl_connect("button_press_event", self._on_diff_click)

    def _on_diff_click(self, event: object) -> None:
        if event.inaxes != self.diff_ax:
            return
        if event.xdata is None or event.ydata is None:
            return
        col_idx = int(event.xdata)
        row_idx = int(event.ydata)
        if 0 <= col_idx < len(self.assets) and 0 <= row_idx < len(self.assets):
            self.diff_combo1.set(self.assets[row_idx])
            self.diff_combo2.set(self.assets[col_idx])
            self._update_diff_view()

    def _update_diff_view(self, _event: object = None) -> None:
        a1 = self.diff_combo1.get()
        a2 = self.diff_combo2.get()
        if not (a1 and a2):
            return

        v_short = self.corr_short.loc[a1, a2]
        v_medium = self.corr_medium.loc[a1, a2]
        diff = self.diff_matrix.loc[a1, a2]

        if abs(v_medium) > PCT_CHANGE_MIN_DENOMINATOR:
            pct_change = (diff / abs(v_medium)) * 100
            pct_text = f"({pct_change:+.1f}%)"
        else:
            pct_text = (
                "(New)" if abs(diff) > NEW_CORRELATION_THRESHOLD else "(No change)"
            )

        if diff > DIFF_POSITIVE_THRESHOLD:
            color = COLOR_POSITIVE
        elif diff < DIFF_NEGATIVE_THRESHOLD:
            color = COLOR_NEGATIVE
        else:
            color = COLOR_NEUTRAL

        text = (
            f"15d: {v_short:.2f}  |  3m: {v_medium:.2f}  |  "
            f"Diff: {diff:+.2f}  {pct_text}"
        )
        self.diff_result_label.config(text=text, foreground=color)

        if self.diff_highlight_rect is not None:
            self.diff_highlight_rect.remove()

        row_idx = self.assets.index(a1)
        col_idx = self.assets.index(a2)
        self.diff_highlight_rect = mpl_patches.Rectangle(
            (col_idx, row_idx), 1, 1, fill=False, edgecolor="blue", linewidth=3, zorder=100
        )
        self.diff_ax.add_patch(self.diff_highlight_rect)
        self.diff_canvas.draw()

    # ------------------------------------------------------------------ #
    #  Generic heatmap tabs
    # ------------------------------------------------------------------ #

    def _setup_heatmap_tab(
        self, frame: ttk.Frame, matrix: pd.DataFrame, label_text: str, key: str
    ) -> None:
        control_frame = ttk.Frame(frame, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)

        style = ttk.Style()
        style.configure("Bold.TLabel", font=("Segoe UI", 10, "bold"))
        style.configure("Big.TLabel", font=("Segoe UI", 14, "bold"), foreground="#333")

        ttk.Label(control_frame, text="Asset A:", style="Bold.TLabel").pack(
            side=tk.LEFT, padx=5
        )
        combo1 = ttk.Combobox(
            control_frame, values=self.assets, state="readonly", width=20
        )
        combo1.pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Asset B:", style="Bold.TLabel").pack(
            side=tk.LEFT, padx=5
        )
        combo2 = ttk.Combobox(
            control_frame, values=self.assets, state="readonly", width=20
        )
        combo2.pack(side=tk.LEFT, padx=5)

        result_label = ttk.Label(
            control_frame, text=" Select two assets ", style="Big.TLabel"
        )
        result_label.pack(side=tk.LEFT, padx=30)

        plot_frame = ttk.Frame(frame)
        plot_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        figure = plt.Figure(figsize=FIGURE_SIZE, dpi=FIGURE_DPI)
        ax = figure.add_subplot(111)
        canvas = FigureCanvasTkAgg(figure, master=plot_frame)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        state = _HeatmapTabState(matrix, figure, ax, canvas, combo1, combo2, result_label)
        self._tab_states[key] = state

        combo1.bind(
            "<<ComboboxSelected>>", lambda _e: self._update_view_generic(state)
        )
        combo2.bind(
            "<<ComboboxSelected>>", lambda _e: self._update_view_generic(state)
        )
        ttk.Button(
            control_frame,
            text="Save Image",
            command=lambda: self._save_image_generic(state, label_text),
        ).pack(side=tk.RIGHT, padx=5)

        self._draw_heatmap_generic(state, label_text)

    def _draw_heatmap_generic(
        self, state: _HeatmapTabState, label_text: str
    ) -> None:
        sns.set_theme(style="white")

        def format_text(val: float) -> str:
            if val == 1.0:
                return "1.0"
            r2 = (val**2) * 100
            return f"{val:.2f}\n{r2:.0f}%"

        annot_labels = state.matrix.applymap(format_text)

        sns.heatmap(
            state.matrix,
            annot=annot_labels,
            fmt="",
            cmap="RdYlGn",
            center=0,
            linewidths=0.5,
            ax=state.ax,
            cbar_kws={"shrink": 0.8, "label": "Correlation"},
            annot_kws={"size": 7},
        )

        state.ax.set_title(f"Correlation Matrix ({label_text})", fontsize=16, pad=20)
        state.ax.tick_params(axis="x", rotation=45, labelsize=8)
        state.ax.tick_params(axis="y", labelsize=8)
        state.figure.tight_layout()

        state.canvas.mpl_connect(
            "button_press_event",
            lambda e: self._on_heatmap_click_generic(e, state),
        )

    def _on_heatmap_click_generic(
        self, event: object, state: _HeatmapTabState
    ) -> None:
        if event.inaxes != state.ax:
            return
        if event.xdata is None or event.ydata is None:
            return
        col_idx = int(event.xdata)
        row_idx = int(event.ydata)

        if 0 <= col_idx < len(self.assets) and 0 <= row_idx < len(self.assets):
            state.combo1.set(self.assets[row_idx])
            state.combo2.set(self.assets[col_idx])
            self._update_view_generic(state)

    def _update_view_generic(self, state: _HeatmapTabState) -> None:
        asset1 = state.combo1.get()
        asset2 = state.combo2.get()
        if not (asset1 and asset2):
            return

        val = state.matrix.loc[asset1, asset2]
        r2 = (val**2) * 100

        if abs(val) < WEAK_CORRELATION_DISPLAY:
            color = "gray"
        elif val > 0:
            color = "green"
        else:
            color = "red"

        state.result_label.config(
            text=f"Correlation: {val:.4f} | Similarity: {r2:.1f}%",
            foreground=color,
        )

        if state.highlight_rect is not None:
            state.highlight_rect.remove()

        row_idx = self.assets.index(asset1)
        col_idx = self.assets.index(asset2)

        state.highlight_rect = mpl_patches.Rectangle(
            (col_idx, row_idx),
            1,
            1,
            fill=False,
            edgecolor=COLOR_HIGHLIGHT,
            linewidth=4,
            zorder=100,
        )
        state.ax.add_patch(state.highlight_rect)
        state.canvas.draw()

    def _save_image_generic(
        self, state: _HeatmapTabState, label_text: str
    ) -> None:
        tag = label_text.replace(" ", "_").lower()
        filename = f"correlation_{tag}_{datetime.now().strftime('%Y_%m_%d_%H%M')}.png"
        state.figure.savefig(filename, dpi=EXPORT_DPI, bbox_inches="tight")
        messagebox.showinfo("Saved", f"Image saved as:\n{filename}")

    # ------------------------------------------------------------------ #
    #  Strong correlations tab
    # ------------------------------------------------------------------ #

    def _setup_strong_corr_tab(self, parent_frame: ttk.Frame) -> None:
        corr_matrix = self.corr_short
        container = ttk.Frame(parent_frame, padding="20")
        container.pack(fill=tk.BOTH, expand=True)

        info_frame = ttk.LabelFrame(container, text="Legend", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            info_frame,
            text=(
                "- ALL correlations within the same sector (Intra-Market) are shown.\n"
                "- For cross-sector (Inter-Market), irrelevant ones (0.2 to 0.5) are filtered out.\n"
                "- R\u00b2 (Similarity): Percentage of shared movement."
            ),
            font=("Segoe UI", 9),
            justify=tk.LEFT,
        ).pack(anchor=tk.W)

        columns = ("Pair", "Corr", "R2", "Interpretation")
        tree = ttk.Treeview(
            container, columns=columns, show="tree headings", height=20
        )

        tree.heading("#0", text="Sector / Market")
        tree.heading("Pair", text="Assets Compared")
        tree.heading("Corr", text="Correlation (r)")
        tree.heading("R2", text="Similarity (R\u00b2)")
        tree.heading("Interpretation", text="Strategy")

        tree.column("#0", width=200, anchor="w")
        tree.column("Pair", width=200, anchor="center")
        tree.column("Corr", width=100, anchor="center")
        tree.column("R2", width=100, anchor="center")
        tree.column("Interpretation", width=250, anchor="center")

        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        cat_map = build_category_map(self.assets)
        grouped_data = group_correlations(self.assets, corr_matrix, cat_map)

        for sector, items in grouped_data.items():
            if not items:
                continue
            items.sort(key=lambda x: (x[0].split(" vs ")[0], -abs(x[1])))
            parent_id = tree.insert(
                "", tk.END, text=f"{sector} ({len(items)})", open=True
            )
            for pair, val, r2, tipo, tag in items:
                tree.insert(
                    parent_id,
                    tk.END,
                    values=(pair, f"{val:.2f}", f"{r2:.1f}%", tipo),
                    tags=(tag,),
                )

        tree.tag_configure(
            "pos_strong", foreground="#006400", font=("Segoe UI", 9, "bold")
        )
        tree.tag_configure("pos_mod", foreground="#228B22")
        tree.tag_configure(
            "neg_strong", foreground="#8B0000", font=("Segoe UI", 9, "bold")
        )
        tree.tag_configure("neg_mod", foreground="#CD5C5C")
        tree.tag_configure("neg_weak", foreground="#E9967A")
        tree.tag_configure("null", foreground="#555555")
        tree.tag_configure("weak", foreground="#999999")



def run_app(corr_short: pd.DataFrame, corr_medium: pd.DataFrame) -> None:
    """Launch the Tkinter GUI application."""
    root = tk.Tk()
    style = ttk.Style(root)

    available_themes = style.theme_names()
    for theme in ("vista", "xpnative", "clam", "alt"):
        if theme in available_themes:
            try:
                style.theme_use(theme)
            except tk.TclError:
                continue
            break

    try:
        root.state("zoomed")
    except tk.TclError:
        root.geometry(WINDOW_FALLBACK_GEOMETRY)

    CorrelationApp(root, corr_short, corr_medium)
    root.mainloop()
