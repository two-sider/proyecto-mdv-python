import logging
import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from src.data.settings_repository import SettingsRepository
from src.data.task_repository import TaskRepository
from src.model.task import Task


class TaskManagerView:
    def __init__(
        self,
        repository: TaskRepository,
        settings_repository: SettingsRepository,
        local_storage_path: Path,
        logger: logging.Logger | None = None,
    ) -> None:
        self.repository = repository
        self.settings_repository = settings_repository
        self.local_storage_path = local_storage_path
        self.logger = logger or logging.getLogger(__name__)
        self.root = tk.Tk()
        self.root.title("TaskFlow MDV")
        self.root.geometry("980x640")
        self.root.minsize(900, 560)

        self.editing_task_id: int | None = None
        self.theme_var = tk.StringVar(value=self.settings_repository.load_theme())
        self.title_var = tk.StringVar()
        self.priority_var = tk.StringVar(value="Media")
        self.due_date_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="Todas")
        self.search_var = tk.StringVar()
        self.sort_var = tk.StringVar(value="Fecha de creacion")
        self.sync_folder_var = tk.StringVar()
        self.sync_status_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Sin seleccion. Crea o elige una tarea para ver su detalle.")
        self.detail_title_var = tk.StringVar(value="Sin tarea seleccionada")
        self.detail_priority_var = tk.StringVar(value="Prioridad: -")
        self.detail_due_date_var = tk.StringVar(value="Vence: -")
        self.detail_completion_var = tk.StringVar(value="Estado: -")
        self.detail_alert_var = tk.StringVar(value="Alerta: -")
        self.detail_notes_var = tk.StringVar(value="Notas: -")
        self.summary_var = tk.StringVar()
        self.pending_var = tk.StringVar()
        self.completed_var = tk.StringVar()
        self.theme_tokens = self._get_theme_tokens(self.theme_var.get())

        self._configure_styles()
        self._build_layout()
        self._apply_theme()
        self._update_sync_status()
        self._refresh_tasks()

    def run(self) -> None:
        self.root.mainloop()

    def _configure_styles(self) -> None:
        style = ttk.Style()
        self.style = style
        style.theme_use("clam")
        style.configure("Heading.TLabel", font=("Segoe UI Semibold", 24))
        style.configure("Subheading.TLabel", font=("Segoe UI", 11))
        style.configure("CardTitle.TLabel", font=("Segoe UI", 10))
        style.configure("CardValue.TLabel", font=("Segoe UI Semibold", 20))
        style.configure("Section.TLabel", font=("Segoe UI Semibold", 12))
        style.configure("Status.TLabel", font=("Segoe UI", 10))
        style.configure("DetailTitle.TLabel", font=("Segoe UI Semibold", 14))
        style.configure("Treeview", rowheight=32, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI Semibold", 10))

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, style="App.TFrame", padding=20)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(1, weight=1)

        header = ttk.Frame(container, style="App.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 18))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="TaskFlow MDV", style="Heading.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            header,
            text="Gestion visual de tareas con persistencia local en JSON.",
            style="Subheading.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))
        ttk.Label(
            header,
            text="Las incidencias y errores se registran en logs/taskflow.log.",
            style="Subheading.TLabel",
        ).grid(row=2, column=0, sticky="w", pady=(4, 0))
        theme_frame = ttk.Frame(header, style="App.TFrame")
        theme_frame.grid(row=0, column=1, rowspan=3, sticky="e")
        ttk.Label(theme_frame, text="Tema", style="Subheading.TLabel").grid(
            row=0, column=0, sticky="e", padx=(0, 8)
        )
        self.theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=("clara", "oscura", "blue-coding"),
            state="readonly",
            width=14,
        )
        self.theme_combo.grid(row=0, column=1, sticky="e")
        self.theme_combo.bind("<<ComboboxSelected>>", self._handle_theme_change)

        content = ttk.Frame(container, style="App.TFrame")
        content.grid(row=1, column=0, columnspan=2, sticky="nsew")
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)

        self._build_task_panel(content)
        self._build_control_panel(content)

    def _build_task_panel(self, parent: ttk.Frame) -> None:
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=18)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(2, weight=1)

        cards = ttk.Frame(panel, style="Panel.TFrame")
        cards.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        cards.columnconfigure((0, 1, 2), weight=1)

        self._build_card(cards, 0, "Total", self.summary_var)
        self._build_card(cards, 1, "Pendientes", self.pending_var)
        self._build_card(cards, 2, "Completadas", self.completed_var)

        filter_frame = ttk.Frame(panel, style="Panel.TFrame")
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        filter_frame.columnconfigure(3, weight=1)

        ttk.Label(filter_frame, text="Filtro", style="Status.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )
        filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=("Todas", "Pendientes", "Completadas", "Alta", "Media", "Baja"),
            state="readonly",
        )
        filter_combo.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        filter_combo.bind("<<ComboboxSelected>>", self._handle_filter_change)

        sort_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.sort_var,
            values=("Fecha de creacion", "Prioridad", "Vencimiento", "Estado", "Titulo"),
            state="readonly",
        )
        sort_combo.grid(row=0, column=2, sticky="ew", padx=(0, 10))
        sort_combo.bind("<<ComboboxSelected>>", self._handle_filter_change)

        search_entry = tk.Entry(
            filter_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 10),
            relief="flat",
            bg="#fffdf8",
            fg="#1f1f1f",
            insertbackground="#1f1f1f",
            highlightthickness=1,
            highlightbackground="#d4c7b6",
            highlightcolor="#1f3c88",
        )
        search_entry.grid(row=0, column=3, sticky="ew")
        search_entry.bind("<KeyRelease>", self._handle_filter_change)

        clear_filters_button = tk.Button(
            filter_frame,
            text="Limpiar filtros",
            command=self._reset_filters,
            bg="#6b7280",
            fg="white",
            activebackground="#6b7280",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            font=("Segoe UI Semibold", 9),
            padx=10,
            pady=8,
        )
        clear_filters_button.grid(row=0, column=4, sticky="e", padx=(10, 0))

        table_frame = ttk.Frame(panel, style="Panel.TFrame")
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("id", "title", "priority", "due_date", "status")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Tarea")
        self.tree.heading("priority", text="Prioridad")
        self.tree.heading("due_date", text="Vence")
        self.tree.heading("status", text="Estado")
        self.tree.column("id", width=70, anchor="center", stretch=False)
        self.tree.column("title", width=360, minwidth=220, anchor="w", stretch=True)
        self.tree.column("priority", width=120, minwidth=100, anchor="center", stretch=False)
        self.tree.column("due_date", width=120, minwidth=100, anchor="center", stretch=False)
        self.tree.column("status", width=130, minwidth=110, anchor="center", stretch=False)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._on_select_task)
        self.tree.bind("<Configure>", self._handle_tree_resize)
        self.tree.tag_configure("overdue", background="#f8d7da", foreground="#6a1b1b")
        self.tree.tag_configure("due_today", background="#ffe9b3", foreground="#6b4b00")
        self.tree.tag_configure("due_soon", background="#fff4d6", foreground="#6b4b00")
        self.tree.tag_configure("priority_high", background="#fbe4e6", foreground="#7f1d1d")
        self.tree.tag_configure("completed", background="#e3f4e8", foreground="#1f5132")

        vertical_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")

        horizontal_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.tree.xview,
        )
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew", pady=(8, 0))

        self.tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

    def _build_control_panel(self, parent: ttk.Frame) -> None:
        outer_panel = ttk.Frame(parent, style="Panel.TFrame")
        outer_panel.grid(row=0, column=1, sticky="nsew")
        outer_panel.columnconfigure(0, weight=1)
        outer_panel.rowconfigure(0, weight=1)

        self.control_canvas = tk.Canvas(
            outer_panel,
            bg="#fffaf2",
            highlightthickness=0,
            bd=0,
        )
        self.control_canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(outer_panel, orient="vertical", command=self.control_canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.control_canvas.configure(yscrollcommand=scrollbar.set)

        panel = ttk.Frame(self.control_canvas, style="Panel.TFrame", padding=18)
        panel.columnconfigure(0, weight=1)

        panel_window = self.control_canvas.create_window((0, 0), window=panel, anchor="nw")
        panel.bind(
            "<Configure>",
            lambda _event: self.control_canvas.configure(scrollregion=self.control_canvas.bbox("all")),
        )
        self.control_canvas.bind(
            "<Configure>",
            lambda event: self.control_canvas.itemconfigure(panel_window, width=event.width),
        )
        self._bind_mousewheel(self.control_canvas)

        ttk.Label(panel, text="Nueva tarea", style="Section.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            panel,
            text="Escribe una descripcion clara y agregala a la lista.",
            style="Status.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 10))

        entry = tk.Entry(
            panel,
            textvariable=self.title_var,
            font=("Segoe UI", 11),
            relief="flat",
            bg="#fffdf8",
            fg="#1f1f1f",
            insertbackground="#1f1f1f",
            highlightthickness=1,
            highlightbackground="#d4c7b6",
            highlightcolor="#1f3c88",
        )
        entry.grid(row=2, column=0, sticky="ew")
        entry.bind("<Return>", self._handle_add_task)
        entry.focus_set()

        meta_frame = ttk.Frame(panel, style="Panel.TFrame")
        meta_frame.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        meta_frame.columnconfigure((0, 1), weight=1)

        ttk.Label(meta_frame, text="Prioridad", style="Status.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )
        ttk.Label(meta_frame, text="Vence (YYYY-MM-DD)", style="Status.TLabel").grid(
            row=0, column=1, sticky="w"
        )

        priority_combo = ttk.Combobox(
            meta_frame,
            textvariable=self.priority_var,
            values=("Alta", "Media", "Baja"),
            state="readonly",
        )
        priority_combo.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        due_date_entry = tk.Entry(
            meta_frame,
            textvariable=self.due_date_var,
            font=("Segoe UI", 10),
            relief="flat",
            bg="#fffdf8",
            fg="#1f1f1f",
            insertbackground="#1f1f1f",
            highlightthickness=1,
            highlightbackground="#d4c7b6",
            highlightcolor="#1f3c88",
        )
        due_date_entry.grid(row=1, column=1, sticky="ew")

        ttk.Label(panel, text="Notas", style="Status.TLabel").grid(
            row=4, column=0, sticky="w", pady=(12, 6)
        )
        self.notes_text = tk.Text(
            panel,
            height=5,
            font=("Segoe UI", 10),
            relief="flat",
            bg="#fffdf8",
            fg="#1f1f1f",
            insertbackground="#1f1f1f",
            highlightthickness=1,
            highlightbackground="#d4c7b6",
            highlightcolor="#1f3c88",
            wrap="word",
        )
        self.notes_text.grid(row=5, column=0, sticky="ew")

        add_button = tk.Button(
            panel,
            text="Guardar tarea",
            command=self._save_task,
            bg="#1f3c88",
            fg="white",
            activebackground="#274a9f",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            font=("Segoe UI Semibold", 10),
            padx=12,
            pady=10,
        )
        add_button.grid(row=6, column=0, sticky="ew", pady=(12, 20))
        self.save_button = add_button

        ttk.Separator(panel, orient="horizontal").grid(row=7, column=0, sticky="ew", pady=6)

        ttk.Label(panel, text="Acciones", style="Section.TLabel").grid(
            row=8, column=0, sticky="w", pady=(8, 0)
        )
        ttk.Label(
            panel,
            text="Selecciona una tarea de la tabla para operar sobre ella.",
            style="Status.TLabel",
        ).grid(row=9, column=0, sticky="w", pady=(4, 12))

        self.edit_button = self._build_action_button(
            panel,
            row=10,
            text="Cargar para editar",
            background="#5b4abf",
            command=self._load_selected_task_for_edit,
        )
        self.complete_button = self._build_action_button(
            panel,
            row=11,
            text="Marcar como completada",
            background="#2d6a4f",
            command=self._complete_selected_task,
        )
        self.reopen_button = self._build_action_button(
            panel,
            row=12,
            text="Reabrir tarea",
            background="#9a6700",
            command=self._reopen_selected_task,
        )
        self.delete_button = self._build_action_button(
            panel,
            row=13,
            text="Eliminar tarea",
            background="#a63c3c",
            command=self._delete_selected_task,
        )
        self.duplicate_button = self._build_action_button(
            panel,
            row=14,
            text="Duplicar tarea",
            background="#0f766e",
            command=self._duplicate_selected_task,
        )
        self.cancel_edit_button = self._build_action_button(
            panel,
            row=15,
            text="Cancelar edicion",
            background="#6b7280",
            command=self._cancel_edit_mode,
        )

        ttk.Separator(panel, orient="horizontal").grid(
            row=16, column=0, sticky="ew", pady=(18, 10)
        )
        ttk.Label(panel, text="Sincronizacion", style="Section.TLabel").grid(row=17, column=0, sticky="w")
        ttk.Label(
            panel,
            text="Usa una carpeta de Google Drive para compartir el mismo archivo entre equipos.",
            style="Status.TLabel",
            wraplength=280,
            justify="left",
        ).grid(row=18, column=0, sticky="w", pady=(4, 8))
        ttk.Label(
            panel,
            textvariable=self.sync_folder_var,
            style="Status.TLabel",
            wraplength=280,
            justify="left",
        ).grid(row=19, column=0, sticky="w")
        ttk.Label(
            panel,
            textvariable=self.sync_status_var,
            style="Status.TLabel",
            wraplength=280,
            justify="left",
        ).grid(row=20, column=0, sticky="w", pady=(4, 12))

        self.connect_drive_button = self._build_action_button(
            panel,
            row=21,
            text="Conectar Google Drive",
            background="#2563eb",
            command=self._connect_google_drive_folder,
        )
        self.use_local_button = self._build_action_button(
            panel,
            row=22,
            text="Usar almacenamiento local",
            background="#475569",
            command=self._use_local_storage,
        )

        ttk.Separator(panel, orient="horizontal").grid(
            row=23, column=0, sticky="ew", pady=(18, 10)
        )
        ttk.Label(panel, text="Datos", style="Section.TLabel").grid(row=24, column=0, sticky="w")
        ttk.Label(
            panel,
            text="Exporta un respaldo JSON o importa tareas desde otro archivo.",
            style="Status.TLabel",
        ).grid(row=25, column=0, sticky="w", pady=(4, 12))

        self.export_button = self._build_action_button(
            panel,
            row=26,
            text="Exportar tareas",
            background="#146c94",
            command=self._export_tasks,
        )
        self.import_button = self._build_action_button(
            panel,
            row=27,
            text="Importar tareas",
            background="#7c5c1d",
            command=self._import_tasks,
        )

        ttk.Separator(panel, orient="horizontal").grid(
            row=28, column=0, sticky="ew", pady=(18, 10)
        )
        ttk.Label(panel, text="Estado", style="Section.TLabel").grid(row=29, column=0, sticky="w")
        ttk.Label(
            panel,
            textvariable=self.detail_title_var,
            style="DetailTitle.TLabel",
            wraplength=280,
            justify="left",
        ).grid(row=30, column=0, sticky="w", pady=(8, 0))
        ttk.Label(
            panel,
            textvariable=self.detail_priority_var,
            style="Status.TLabel",
            wraplength=280,
            justify="left",
        ).grid(row=31, column=0, sticky="w", pady=(6, 0))
        ttk.Label(
            panel,
            textvariable=self.detail_due_date_var,
            style="Status.TLabel",
            wraplength=280,
            justify="left",
        ).grid(row=32, column=0, sticky="w", pady=(4, 0))
        ttk.Label(
            panel,
            textvariable=self.detail_completion_var,
            style="Status.TLabel",
            wraplength=280,
            justify="left",
        ).grid(row=33, column=0, sticky="w", pady=(4, 0))
        ttk.Label(
            panel,
            textvariable=self.detail_alert_var,
            style="Status.TLabel",
            wraplength=280,
            justify="left",
        ).grid(row=34, column=0, sticky="w", pady=(4, 0))
        ttk.Label(
            panel,
            textvariable=self.detail_notes_var,
            style="Status.TLabel",
            wraplength=280,
            justify="left",
        ).grid(row=35, column=0, sticky="w", pady=(4, 0))
        ttk.Label(
            panel,
            textvariable=self.status_var,
            style="Status.TLabel",
            wraplength=280,
            justify="left",
        ).grid(row=36, column=0, sticky="w", pady=(12, 0))

        self._set_action_state("disabled")
        self.cancel_edit_button.config(state="disabled")

    def _bind_mousewheel(self, widget: tk.Widget) -> None:
        widget.bind("<Enter>", lambda _event: self._activate_mousewheel(widget))
        widget.bind("<Leave>", lambda _event: self._deactivate_mousewheel())

    def _activate_mousewheel(self, widget: tk.Widget) -> None:
        self.root.bind_all("<MouseWheel>", lambda event: self._on_mousewheel(widget, event))

    def _deactivate_mousewheel(self) -> None:
        self.root.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, widget: tk.Widget, event: tk.Event) -> None:
        widget.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _build_card(self, parent: ttk.Frame, column: int, label: str, variable: tk.StringVar) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        card.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 10, 0))
        ttk.Label(card, text=label, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(card, textvariable=variable, style="CardValue.TLabel").pack(anchor="w", pady=(10, 0))

    def _build_action_button(
        self,
        parent: ttk.Frame,
        row: int,
        text: str,
        background: str,
        command,
    ) -> tk.Button:
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=background,
            fg="white",
            activebackground=background,
            activeforeground="white",
            disabledforeground="#e7ded0",
            relief="flat",
            cursor="hand2",
            font=("Segoe UI Semibold", 10),
            padx=12,
            pady=10,
        )
        button.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        return button

    def _refresh_tasks(self) -> None:
        selected_ids = self.tree.selection()
        selected_id = int(selected_ids[0]) if selected_ids else None
        tasks = self._get_filtered_tasks()
        self.tree.delete(*self.tree.get_children())

        for task in tasks:
            status = "Completada" if task.completed else "Pendiente"
            due_date = task.due_date or "-"
            tags = self._get_task_tags(task)
            self.tree.insert(
                "",
                "end",
                iid=str(task.task_id),
                values=(task.task_id, task.title, task.priority, due_date, status),
                tags=tags,
            )

        all_tasks = self.repository.list_tasks()
        completed_count = sum(task.completed for task in all_tasks)
        pending_count = len(all_tasks) - completed_count
        self.summary_var.set(str(len(all_tasks)))
        self.pending_var.set(str(pending_count))
        self.completed_var.set(str(completed_count))
        self._set_action_state("disabled")
        if selected_id is not None:
            self._restore_selection(selected_id)
        else:
            self._set_empty_detail()

    def _handle_add_task(self, _event: tk.Event) -> None:
        self._save_task()

    def _save_task(self) -> None:
        title = self.title_var.get().strip()
        notes = self.notes_text.get("1.0", "end").strip()
        if not title:
            self.status_var.set("El titulo no puede quedar vacio.")
            return
        due_date = self.due_date_var.get().strip()
        if due_date and not self._is_valid_due_date(due_date):
            self.status_var.set("La fecha debe tener formato YYYY-MM-DD.")
            return

        try:
            if self.editing_task_id is None:
                task = self.repository.add_task(
                    title,
                    priority=self.priority_var.get(),
                    due_date=due_date,
                    notes=notes,
                )
                self.logger.info("Tarea creada: id=%s titulo=%s", task.task_id, task.title)
                self.status_var.set(f"Tarea #{task.task_id} creada correctamente.")
                selected_id = task.task_id
            else:
                self.repository.update_task(
                    self.editing_task_id,
                    title=title,
                    priority=self.priority_var.get(),
                    due_date=due_date,
                    notes=notes,
                )
                self.logger.info("Tarea editada: id=%s titulo=%s", self.editing_task_id, title)
                self.status_var.set(f"Tarea #{self.editing_task_id} actualizada correctamente.")
                selected_id = self.editing_task_id

            self._clear_form()
            self._refresh_tasks()
            self._restore_selection(selected_id)
        except Exception as error:
            self.logger.exception("Error al guardar tarea")
            self.status_var.set(f"Error al guardar la tarea: {error}")

    def _complete_selected_task(self) -> None:
        task = self._get_selected_task()
        if task is None:
            return
        if task.completed:
            self.status_var.set("La tarea seleccionada ya estaba completada.")
            return

        try:
            self.repository.set_task_completed(task.task_id, True)
            self.logger.info("Tarea completada: id=%s", task.task_id)
            self.status_var.set(f"Tarea #{task.task_id} marcada como completada.")
            self._refresh_tasks()
            self._restore_selection(task.task_id)
        except Exception as error:
            self.logger.exception("Error al completar tarea")
            self.status_var.set(f"Error al completar la tarea: {error}")

    def _reopen_selected_task(self) -> None:
        task = self._get_selected_task()
        if task is None:
            return
        if not task.completed:
            self.status_var.set("La tarea seleccionada ya estaba pendiente.")
            return

        try:
            self.repository.set_task_completed(task.task_id, False)
            self.logger.info("Tarea reabierta: id=%s", task.task_id)
            self.status_var.set(f"Tarea #{task.task_id} reabierta.")
            self._refresh_tasks()
            self._restore_selection(task.task_id)
        except Exception as error:
            self.logger.exception("Error al reabrir tarea")
            self.status_var.set(f"Error al reabrir la tarea: {error}")

    def _delete_selected_task(self) -> None:
        task = self._get_selected_task()
        if task is None:
            return

        confirmed = messagebox.askyesno(
            "Eliminar tarea",
            f"Se eliminara la tarea #{task.task_id}: {task.title}",
            parent=self.root,
        )
        if not confirmed:
            self.status_var.set("Eliminacion cancelada.")
            return

        try:
            self.repository.delete_task(task.task_id)
            self.logger.info("Tarea eliminada: id=%s", task.task_id)
            self.status_var.set(f"Tarea #{task.task_id} eliminada.")
            if self.editing_task_id == task.task_id:
                self._clear_form()
            self._refresh_tasks()
        except Exception as error:
            self.logger.exception("Error al eliminar tarea")
            self.status_var.set(f"Error al eliminar la tarea: {error}")

    def _duplicate_selected_task(self) -> None:
        task = self._get_selected_task()
        if task is None:
            return

        try:
            duplicated = self.repository.duplicate_task(task.task_id)
            if duplicated is None:
                self.status_var.set("La tarea seleccionada ya no existe.")
                self._refresh_tasks()
                return

            self.logger.info(
                "Tarea duplicada: origen=%s duplicado=%s",
                task.task_id,
                duplicated.task_id,
            )
            self.status_var.set(f"Tarea #{task.task_id} duplicada como #{duplicated.task_id}.")
            self._refresh_tasks()
            self._restore_selection(duplicated.task_id)
        except Exception as error:
            self.logger.exception("Error al duplicar tarea")
            self.status_var.set(f"Error al duplicar la tarea: {error}")

    def _load_selected_task_for_edit(self) -> None:
        task = self._get_selected_task()
        if task is None:
            return

        self.editing_task_id = task.task_id
        self.title_var.set(task.title)
        self.priority_var.set(task.priority)
        self.due_date_var.set(task.due_date)
        self.notes_text.delete("1.0", "end")
        self.notes_text.insert("1.0", task.notes)
        self.save_button.config(text="Guardar cambios")
        self.cancel_edit_button.config(state="normal")
        self.status_var.set(f"Editando tarea #{task.task_id}.")
        self.logger.info("Modo edicion activado: id=%s", task.task_id)

    def _cancel_edit_mode(self) -> None:
        self._clear_form()
        self.status_var.set("Edicion cancelada.")

    def _reset_filters(self) -> None:
        self.filter_var.set("Todas")
        self.sort_var.set("Fecha de creacion")
        self.search_var.set("")
        self.status_var.set("Filtros reiniciados.")
        self._refresh_tasks()

    def _connect_google_drive_folder(self) -> None:
        selected_folder = filedialog.askdirectory(
            parent=self.root,
            title="Selecciona tu carpeta de Google Drive",
        )
        if not selected_folder:
            self.status_var.set("Conexion con Google Drive cancelada.")
            return

        sync_storage_path = self._build_sync_storage_path(selected_folder)

        try:
            current_storage_path = self.repository.storage_path
            if current_storage_path != sync_storage_path and sync_storage_path.exists():
                decision = messagebox.askyesnocancel(
                    "Google Drive detectado",
                    (
                        "La carpeta seleccionada ya tiene tareas guardadas.\n"
                        "Si eliges 'Si', se usaran las tareas de Google Drive.\n"
                        "Si eliges 'No', las tareas actuales se copiaran a Google Drive."
                    ),
                    parent=self.root,
                )
                if decision is None:
                    self.status_var.set("Conexion con Google Drive cancelada.")
                    return
                if decision is False:
                    self.repository.export_tasks(sync_storage_path)
            elif current_storage_path != sync_storage_path:
                self.repository.export_tasks(sync_storage_path)

            self.repository.set_storage_path(sync_storage_path)
            self.settings_repository.save_sync_folder(selected_folder)
            self._clear_form()
            self._update_sync_status()
            self._refresh_tasks()
            self.logger.info("Sincronizacion Google Drive activada: carpeta=%s", selected_folder)
            self.status_var.set("Google Drive conectado. Los cambios se guardaran en la carpeta sincronizada.")
        except Exception as error:
            self.logger.exception("Error al conectar Google Drive")
            self.status_var.set(f"Error al conectar Google Drive: {error}")

    def _use_local_storage(self) -> None:
        current_sync_folder = self.settings_repository.load_sync_folder()
        if not current_sync_folder and self.repository.storage_path == self.local_storage_path:
            self.status_var.set("La app ya esta usando almacenamiento local.")
            return

        try:
            if self.repository.storage_path != self.local_storage_path:
                self.repository.export_tasks(self.local_storage_path)

            self.repository.set_storage_path(self.local_storage_path)
            self.settings_repository.save_sync_folder("")
            self._clear_form()
            self._update_sync_status()
            self._refresh_tasks()
            self.logger.info("Sincronizacion Google Drive desactivada")
            self.status_var.set("La app volvio a usar almacenamiento local.")
        except Exception as error:
            self.logger.exception("Error al volver a almacenamiento local")
            self.status_var.set(f"Error al volver a almacenamiento local: {error}")

    def _build_sync_storage_path(self, sync_folder: str) -> Path:
        return Path(sync_folder) / "TaskFlowMDV" / "tasks.json"

    def _update_sync_status(self) -> None:
        sync_folder = self.settings_repository.load_sync_folder()
        if sync_folder:
            self.sync_folder_var.set(f"Carpeta: {sync_folder}")
            self.sync_status_var.set("Estado: sincronizacion activa mediante Google Drive.")
            return

        self.sync_folder_var.set("Carpeta: almacenamiento local del proyecto")
        self.sync_status_var.set("Estado: sin sincronizacion en la nube.")

    def _export_tasks(self) -> None:
        default_name = f"taskflow-backup-{date.today().isoformat()}.json"
        export_target = filedialog.asksaveasfilename(
            parent=self.root,
            title="Exportar tareas",
            defaultextension=".json",
            initialfile=default_name,
            filetypes=[("Archivos JSON", "*.json")],
        )
        if not export_target:
            self.status_var.set("Exportacion cancelada.")
            return

        try:
            exported_count = self.repository.export_tasks(Path(export_target))
            self.logger.info("Tareas exportadas: destino=%s cantidad=%s", export_target, exported_count)
            self.status_var.set(f"Se exportaron {exported_count} tarea(s) a {Path(export_target).name}.")
        except Exception as error:
            self.logger.exception("Error al exportar tareas")
            self.status_var.set(f"Error al exportar las tareas: {error}")

    def _import_tasks(self) -> None:
        import_source = filedialog.askopenfilename(
            parent=self.root,
            title="Importar tareas",
            filetypes=[("Archivos JSON", "*.json")],
        )
        if not import_source:
            self.status_var.set("Importacion cancelada.")
            return

        import_mode = messagebox.askyesnocancel(
            "Importar tareas",
            (
                "Si eliges 'Si', la lista actual se reemplazara.\n"
                "Si eliges 'No', las tareas importadas se agregaran al final."
            ),
            parent=self.root,
        )
        if import_mode is None:
            self.status_var.set("Importacion cancelada.")
            return

        mode = "replace" if import_mode else "merge"

        try:
            imported_count = self.repository.import_tasks(Path(import_source), mode=mode)
            self._clear_form()
            self._refresh_tasks()
            self.logger.info(
                "Tareas importadas: origen=%s cantidad=%s modo=%s",
                import_source,
                imported_count,
                mode,
            )
            action = "reemplazaron" if mode == "replace" else "agregaron"
            self.status_var.set(
                f"Se importaron {imported_count} tarea(s) desde {Path(import_source).name} y se {action} correctamente."
            )
        except Exception as error:
            self.logger.exception("Error al importar tareas")
            self.status_var.set(f"Error al importar las tareas: {error}")

    def _restore_selection(self, task_id: int) -> None:
        item_id = str(task_id)
        if item_id in self.tree.get_children():
            self.tree.selection_set(item_id)
            self.tree.focus(item_id)
            self.tree.see(item_id)
            self._on_select_task()

    def _on_select_task(self, _event: tk.Event | None = None) -> None:
        task = self._get_selected_task()
        if task is None:
            self._set_action_state("disabled")
            return

        self._set_action_state("normal")
        if task.completed:
            self.complete_button.config(state="disabled")
            self.status_var.set("Puedes reabrirla o eliminarla.")
        else:
            self.reopen_button.config(state="disabled")
            self.status_var.set("Puedes completarla o eliminarla.")
        self._set_task_detail(task)

    def _set_action_state(self, state: str) -> None:
        self.edit_button.config(state=state)
        self.complete_button.config(state=state)
        self.reopen_button.config(state=state)
        self.delete_button.config(state=state)
        self.duplicate_button.config(state=state)

    def _get_selected_task(self) -> Task | None:
        selection = self.tree.selection()
        if not selection:
            self.status_var.set("Selecciona una tarea para usar las acciones.")
            return None

        task_id = int(selection[0])
        task = self.repository.find_task(task_id)
        if task is not None:
            return task

        self.status_var.set("La tarea seleccionada ya no existe.")
        self._refresh_tasks()
        return None

    def _get_filtered_tasks(self) -> list[Task]:
        tasks = self.repository.list_tasks()
        search = self.search_var.get().strip().lower()
        current_filter = self.filter_var.get()

        if current_filter == "Pendientes":
            tasks = [task for task in tasks if not task.completed]
        elif current_filter == "Completadas":
            tasks = [task for task in tasks if task.completed]
        elif current_filter in {"Alta", "Media", "Baja"}:
            tasks = [task for task in tasks if task.priority == current_filter]

        if search:
            tasks = [
                task
                for task in tasks
                if search in task.title.lower() or search in task.notes.lower()
            ]

        tasks = self._sort_tasks(tasks)

        return tasks

    def _handle_filter_change(self, _event: tk.Event | None = None) -> None:
        self.status_var.set("Vista actualizada con los filtros aplicados.")
        self._refresh_tasks()

    def _handle_theme_change(self, _event: tk.Event | None = None) -> None:
        theme = self.theme_var.get()
        self.theme_tokens = self._get_theme_tokens(theme)
        self.settings_repository.save_theme(theme)
        self._apply_theme()
        self.logger.info("Tema actualizado: %s", theme)
        self.status_var.set(f"Tema aplicado: {theme}.")

    def _handle_tree_resize(self, event: tk.Event) -> None:
        available_width = max(int(event.width), 620)
        fixed_width = 70 + 120 + 120 + 130
        title_width = max(220, available_width - fixed_width - 12)
        self.tree.column("title", width=title_width)

    def _set_task_detail(self, task: Task) -> None:
        self.detail_title_var.set(task.title)
        self.detail_priority_var.set(f"Prioridad: {task.priority}")
        self.detail_due_date_var.set(f"Vence: {task.due_date or 'Sin fecha definida'}")
        completion = "Completada" if task.completed else "Pendiente"
        self.detail_completion_var.set(f"Estado: {completion}")
        self.detail_alert_var.set(f"Alerta: {self._build_due_date_alert(task)}")
        self.detail_notes_var.set(f"Notas: {task.notes or 'Sin notas'}")

    def _set_empty_detail(self) -> None:
        self.detail_title_var.set("Sin tarea seleccionada")
        self.detail_priority_var.set("Prioridad: -")
        self.detail_due_date_var.set("Vence: -")
        self.detail_completion_var.set("Estado: -")
        self.detail_alert_var.set("Alerta: -")
        self.detail_notes_var.set("Notas: -")

    def _is_valid_due_date(self, due_date: str) -> bool:
        parts = due_date.split("-")
        if len(parts) != 3:
            return False
        year, month, day = parts
        if not (year.isdigit() and month.isdigit() and day.isdigit()):
            return False
        if not (len(year) == 4 and len(month) == 2 and len(day) == 2):
            return False
        try:
            date.fromisoformat(due_date)
        except ValueError:
            return False
        return True

    def _build_due_date_alert(self, task: Task) -> str:
        if not task.due_date:
            return "Sin fecha de vencimiento"
        try:
            due = date.fromisoformat(task.due_date)
        except ValueError:
            self.logger.warning("Tarea con fecha invalida detectada: id=%s fecha=%s", task.task_id, task.due_date)
            return "Fecha invalida"

        delta = (due - date.today()).days
        if task.completed:
            return "Completada"
        if delta < 0:
            return f"Atrasada por {abs(delta)} dia(s)"
        if delta == 0:
            return "Vence hoy"
        if delta <= 3:
            return f"Vence en {delta} dia(s)"
        return "En plazo"

    def _clear_form(self) -> None:
        self.editing_task_id = None
        self.title_var.set("")
        self.priority_var.set("Media")
        self.due_date_var.set("")
        self.notes_text.delete("1.0", "end")
        self.save_button.config(text="Guardar tarea")
        self.cancel_edit_button.config(state="disabled")

    def _apply_theme(self) -> None:
        tokens = self.theme_tokens
        self.root.configure(bg=tokens["app_bg"])
        self.style.configure("App.TFrame", background=tokens["app_bg"])
        self.style.configure("Panel.TFrame", background=tokens["panel_bg"])
        self.style.configure("Card.TFrame", background=tokens["card_bg"])
        self.style.configure("Heading.TLabel", background=tokens["app_bg"], foreground=tokens["heading_fg"])
        self.style.configure("Subheading.TLabel", background=tokens["app_bg"], foreground=tokens["subheading_fg"])
        self.style.configure("CardTitle.TLabel", background=tokens["card_bg"], foreground=tokens["card_title_fg"])
        self.style.configure("CardValue.TLabel", background=tokens["card_bg"], foreground=tokens["card_value_fg"])
        self.style.configure("Section.TLabel", background=tokens["panel_bg"], foreground=tokens["section_fg"])
        self.style.configure("Status.TLabel", background=tokens["panel_bg"], foreground=tokens["status_fg"])
        self.style.configure("DetailTitle.TLabel", background=tokens["panel_bg"], foreground=tokens["detail_fg"])
        self.style.configure(
            "Treeview",
            background=tokens["tree_bg"],
            fieldbackground=tokens["tree_bg"],
            foreground=tokens["tree_fg"],
            bordercolor=tokens["border"],
        )
        self.style.configure(
            "Treeview.Heading",
            background=tokens["tree_heading_bg"],
            foreground=tokens["tree_heading_fg"],
        )
        self.style.map(
            "Treeview",
            background=[("selected", tokens["selected_bg"])],
            foreground=[("selected", tokens["selected_fg"])],
        )

        self.tree.tag_configure("overdue", background=tokens["overdue_bg"], foreground=tokens["overdue_fg"])
        self.tree.tag_configure("due_today", background=tokens["today_bg"], foreground=tokens["today_fg"])
        self.tree.tag_configure("due_soon", background=tokens["soon_bg"], foreground=tokens["soon_fg"])
        self.tree.tag_configure("priority_high", background=tokens["high_bg"], foreground=tokens["high_fg"])
        self.tree.tag_configure("completed", background=tokens["done_bg"], foreground=tokens["done_fg"])

        self.control_canvas.configure(bg=tokens["panel_bg"])
        self.notes_text.configure(
            bg=tokens["input_bg"],
            fg=tokens["input_fg"],
            insertbackground=tokens["input_fg"],
            highlightbackground=tokens["border"],
            highlightcolor=tokens["accent"],
        )

        for entry in self.root.winfo_children():
            self._apply_theme_to_entries(entry, tokens)

    def _apply_theme_to_entries(self, widget: tk.Widget, tokens: dict[str, str]) -> None:
        for child in widget.winfo_children():
            if type(child) is tk.Entry:
                child.configure(
                    bg=tokens["input_bg"],
                    fg=tokens["input_fg"],
                    insertbackground=tokens["input_fg"],
                    highlightbackground=tokens["border"],
                    highlightcolor=tokens["accent"],
                )
            elif type(child) is tk.Button:
                self._apply_button_theme(child, tokens)
            elif type(child) is tk.Canvas:
                child.configure(bg=tokens["panel_bg"])
            self._apply_theme_to_entries(child, tokens)

    def _apply_button_theme(self, button: tk.Button, tokens: dict[str, str]) -> None:
        button_text = button.cget("text")
        palette = {
            "Guardar tarea": tokens["accent"],
            "Guardar cambios": tokens["accent"],
            "Cargar para editar": tokens["edit_btn"],
            "Marcar como completada": tokens["success_btn"],
            "Reabrir tarea": tokens["warning_btn"],
            "Eliminar tarea": tokens["danger_btn"],
            "Duplicar tarea": tokens["secondary_btn"],
            "Cancelar edicion": tokens["neutral_btn"],
            "Conectar Google Drive": tokens["drive_btn"],
            "Usar almacenamiento local": tokens["local_btn"],
            "Exportar tareas": tokens["info_btn"],
            "Importar tareas": tokens["import_btn"],
        }
        background = palette.get(button_text, tokens["accent"])
        button.configure(
            bg=background,
            fg=tokens["button_fg"],
            activebackground=background,
            activeforeground=tokens["button_fg"],
            disabledforeground=tokens["button_disabled_fg"],
        )

    def _get_theme_tokens(self, theme: str) -> dict[str, str]:
        palettes = {
            "clara": {
                "app_bg": "#f4efe6",
                "panel_bg": "#fffaf2",
                "card_bg": "#1f3c88",
                "heading_fg": "#1c1c1c",
                "subheading_fg": "#5f5a52",
                "card_title_fg": "#f1f5ff",
                "card_value_fg": "#ffffff",
                "section_fg": "#1c1c1c",
                "status_fg": "#6f665c",
                "detail_fg": "#1f1f1f",
                "tree_bg": "#fffdf8",
                "tree_fg": "#1f1f1f",
                "tree_heading_bg": "#ecdcc7",
                "tree_heading_fg": "#2b2b2b",
                "selected_bg": "#c9ddff",
                "selected_fg": "#10233f",
                "input_bg": "#fffdf8",
                "input_fg": "#1f1f1f",
                "border": "#d4c7b6",
                "accent": "#1f3c88",
                "edit_btn": "#5b4abf",
                "success_btn": "#2d6a4f",
                "warning_btn": "#9a6700",
                "danger_btn": "#a63c3c",
                "secondary_btn": "#0f766e",
                "neutral_btn": "#6b7280",
                "drive_btn": "#2563eb",
                "local_btn": "#475569",
                "info_btn": "#146c94",
                "import_btn": "#7c5c1d",
                "button_fg": "#ffffff",
                "button_disabled_fg": "#e7ded0",
                "overdue_bg": "#f8d7da",
                "overdue_fg": "#6a1b1b",
                "today_bg": "#ffe9b3",
                "today_fg": "#6b4b00",
                "soon_bg": "#fff4d6",
                "soon_fg": "#6b4b00",
                "high_bg": "#fbe4e6",
                "high_fg": "#7f1d1d",
                "done_bg": "#e3f4e8",
                "done_fg": "#1f5132",
            },
            "oscura": {
                "app_bg": "#11161b",
                "panel_bg": "#1b232c",
                "card_bg": "#233041",
                "heading_fg": "#f2f5f7",
                "subheading_fg": "#9db0bf",
                "card_title_fg": "#b9d2ea",
                "card_value_fg": "#ffffff",
                "section_fg": "#e7eef4",
                "status_fg": "#afbcc6",
                "detail_fg": "#f2f5f7",
                "tree_bg": "#182028",
                "tree_fg": "#ecf2f8",
                "tree_heading_bg": "#273645",
                "tree_heading_fg": "#ecf2f8",
                "selected_bg": "#35506b",
                "selected_fg": "#ffffff",
                "input_bg": "#121920",
                "input_fg": "#eef3f7",
                "border": "#384857",
                "accent": "#3b82f6",
                "edit_btn": "#6366f1",
                "success_btn": "#2f855a",
                "warning_btn": "#b7791f",
                "danger_btn": "#c53030",
                "secondary_btn": "#0f8b82",
                "neutral_btn": "#4b5563",
                "drive_btn": "#3b82f6",
                "local_btn": "#64748b",
                "info_btn": "#1d6fa5",
                "import_btn": "#8c6a1f",
                "button_fg": "#ffffff",
                "button_disabled_fg": "#b4c0ca",
                "overdue_bg": "#5a1f26",
                "overdue_fg": "#ffd8dc",
                "today_bg": "#61451b",
                "today_fg": "#ffe7b3",
                "soon_bg": "#4d431f",
                "soon_fg": "#ffefbf",
                "high_bg": "#4d2730",
                "high_fg": "#ffd6dd",
                "done_bg": "#1e4734",
                "done_fg": "#d7ffe7",
            },
            "blue-coding": {
                "app_bg": "#07111f",
                "panel_bg": "#0d1b2f",
                "card_bg": "#12345a",
                "heading_fg": "#d8f0ff",
                "subheading_fg": "#7db8d8",
                "card_title_fg": "#8dd7ff",
                "card_value_fg": "#ecfbff",
                "section_fg": "#c3ebff",
                "status_fg": "#8bb8cf",
                "detail_fg": "#f1fbff",
                "tree_bg": "#0a1526",
                "tree_fg": "#d7f4ff",
                "tree_heading_bg": "#16304f",
                "tree_heading_fg": "#d7f4ff",
                "selected_bg": "#1f4f82",
                "selected_fg": "#ffffff",
                "input_bg": "#081220",
                "input_fg": "#d7f4ff",
                "border": "#1f4165",
                "accent": "#1d72d8",
                "edit_btn": "#3454d1",
                "success_btn": "#13795b",
                "warning_btn": "#bf8b16",
                "danger_btn": "#c94c4c",
                "secondary_btn": "#139089",
                "neutral_btn": "#4f6d8a",
                "drive_btn": "#2b8fff",
                "local_btn": "#5c728a",
                "info_btn": "#0f7abf",
                "import_btn": "#9a741c",
                "button_fg": "#f4fbff",
                "button_disabled_fg": "#afc8da",
                "overdue_bg": "#4e2131",
                "overdue_fg": "#ffd5e1",
                "today_bg": "#5a4216",
                "today_fg": "#ffe7ad",
                "soon_bg": "#3d4318",
                "soon_fg": "#f3ffc1",
                "high_bg": "#2c254d",
                "high_fg": "#d6d3ff",
                "done_bg": "#163f3a",
                "done_fg": "#c8fff5",
            },
        }
        return palettes.get(theme, palettes["clara"])

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        sort_by = self.sort_var.get()
        priority_order = {"Alta": 0, "Media": 1, "Baja": 2}

        if sort_by == "Prioridad":
            return sorted(tasks, key=lambda task: (priority_order.get(task.priority, 9), task.task_id))
        if sort_by == "Vencimiento":
            return sorted(tasks, key=lambda task: (task.due_date == "", task.due_date or "9999-12-31", task.task_id))
        if sort_by == "Estado":
            return sorted(tasks, key=lambda task: (task.completed, task.task_id))
        if sort_by == "Titulo":
            return sorted(tasks, key=lambda task: (task.title.lower(), task.task_id))
        return sorted(tasks, key=lambda task: task.task_id)

    def _get_task_tags(self, task: Task) -> tuple[str, ...]:
        if task.completed:
            return ("completed",)
        if task.due_date:
            try:
                due = date.fromisoformat(task.due_date)
                delta = (due - date.today()).days
                if delta < 0:
                    return ("overdue",)
                if delta == 0:
                    return ("due_today",)
                if delta <= 3:
                    return ("due_soon",)
            except ValueError:
                pass
        if task.priority == "Alta":
            return ("priority_high",)
        return tuple()
