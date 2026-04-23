import logging
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from src.data.task_repository import TaskRepository
from src.model.task import Task


class TaskManagerView:
    def __init__(self, repository: TaskRepository, logger: logging.Logger | None = None) -> None:
        self.repository = repository
        self.logger = logger or logging.getLogger(__name__)
        self.root = tk.Tk()
        self.root.title("TaskFlow MDV")
        self.root.geometry("980x640")
        self.root.minsize(900, 560)
        self.root.configure(bg="#f4efe6")

        self.editing_task_id: int | None = None
        self.title_var = tk.StringVar()
        self.priority_var = tk.StringVar(value="Media")
        self.due_date_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="Todas")
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Sin seleccion. Crea o elige una tarea para ver su detalle.")
        self.detail_title_var = tk.StringVar(value="Sin tarea seleccionada")
        self.detail_priority_var = tk.StringVar(value="Prioridad: -")
        self.detail_due_date_var = tk.StringVar(value="Vence: -")
        self.detail_completion_var = tk.StringVar(value="Estado: -")
        self.detail_alert_var = tk.StringVar(value="Alerta: -")
        self.summary_var = tk.StringVar()
        self.pending_var = tk.StringVar()
        self.completed_var = tk.StringVar()

        self._configure_styles()
        self._build_layout()
        self._refresh_tasks()

    def run(self) -> None:
        self.root.mainloop()

    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("App.TFrame", background="#f4efe6")
        style.configure("Panel.TFrame", background="#fffaf2")
        style.configure("Card.TFrame", background="#1f3c88")
        style.configure(
            "Heading.TLabel",
            background="#f4efe6",
            foreground="#1c1c1c",
            font=("Segoe UI Semibold", 24),
        )
        style.configure(
            "Subheading.TLabel",
            background="#f4efe6",
            foreground="#5f5a52",
            font=("Segoe UI", 11),
        )
        style.configure(
            "CardTitle.TLabel",
            background="#1f3c88",
            foreground="#f1f5ff",
            font=("Segoe UI", 10),
        )
        style.configure(
            "CardValue.TLabel",
            background="#1f3c88",
            foreground="#ffffff",
            font=("Segoe UI Semibold", 20),
        )
        style.configure(
            "Section.TLabel",
            background="#fffaf2",
            foreground="#1c1c1c",
            font=("Segoe UI Semibold", 12),
        )
        style.configure(
            "Status.TLabel",
            background="#fffaf2",
            foreground="#6f665c",
            font=("Segoe UI", 10),
        )
        style.configure(
            "DetailTitle.TLabel",
            background="#fffaf2",
            foreground="#1f1f1f",
            font=("Segoe UI Semibold", 14),
        )
        style.configure(
            "Treeview",
            background="#fffdf8",
            fieldbackground="#fffdf8",
            foreground="#1f1f1f",
            rowheight=32,
            bordercolor="#d9cfbf",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Treeview.Heading",
            background="#ecdcc7",
            foreground="#2b2b2b",
            font=("Segoe UI Semibold", 10),
        )
        style.map(
            "Treeview",
            background=[("selected", "#c9ddff")],
            foreground=[("selected", "#10233f")],
        )

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
        filter_frame.columnconfigure(1, weight=1)

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
        search_entry.grid(row=0, column=2, sticky="ew")
        search_entry.bind("<KeyRelease>", self._handle_filter_change)

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

        canvas = tk.Canvas(
            outer_panel,
            bg="#fffaf2",
            highlightthickness=0,
            bd=0,
        )
        canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(outer_panel, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        panel = ttk.Frame(canvas, style="Panel.TFrame", padding=18)
        panel.columnconfigure(0, weight=1)

        panel_window = canvas.create_window((0, 0), window=panel, anchor="nw")
        panel.bind(
            "<Configure>",
            lambda _event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(panel_window, width=event.width),
        )
        self._bind_mousewheel(canvas)

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
        add_button.grid(row=4, column=0, sticky="ew", pady=(12, 20))
        self.save_button = add_button

        ttk.Separator(panel, orient="horizontal").grid(row=5, column=0, sticky="ew", pady=6)

        ttk.Label(panel, text="Acciones", style="Section.TLabel").grid(
            row=6, column=0, sticky="w", pady=(8, 0)
        )
        ttk.Label(
            panel,
            text="Selecciona una tarea de la tabla para operar sobre ella.",
            style="Status.TLabel",
        ).grid(row=7, column=0, sticky="w", pady=(4, 12))

        self.edit_button = self._build_action_button(
            panel,
            row=8,
            text="Cargar para editar",
            background="#5b4abf",
            command=self._load_selected_task_for_edit,
        )
        self.complete_button = self._build_action_button(
            panel,
            row=9,
            text="Marcar como completada",
            background="#2d6a4f",
            command=self._complete_selected_task,
        )
        self.reopen_button = self._build_action_button(
            panel,
            row=10,
            text="Reabrir tarea",
            background="#9a6700",
            command=self._reopen_selected_task,
        )
        self.delete_button = self._build_action_button(
            panel,
            row=11,
            text="Eliminar tarea",
            background="#a63c3c",
            command=self._delete_selected_task,
        )
        self.cancel_edit_button = self._build_action_button(
            panel,
            row=12,
            text="Cancelar edicion",
            background="#6b7280",
            command=self._cancel_edit_mode,
        )

        ttk.Separator(panel, orient="horizontal").grid(
            row=13, column=0, sticky="ew", pady=(18, 10)
        )
        ttk.Label(panel, text="Estado", style="Section.TLabel").grid(row=14, column=0, sticky="w")
        ttk.Label(
            panel,
            textvariable=self.detail_title_var,
            style="DetailTitle.TLabel",
            wraplength=280,
            justify="left",
        ).grid(row=15, column=0, sticky="w", pady=(8, 0))
        ttk.Label(
            panel,
            textvariable=self.detail_priority_var,
            style="Status.TLabel",
            wraplength=280,
            justify="left",
        ).grid(row=16, column=0, sticky="w", pady=(6, 0))
        ttk.Label(
            panel,
            textvariable=self.detail_due_date_var,
            style="Status.TLabel",
            wraplength=280,
            justify="left",
        ).grid(row=17, column=0, sticky="w", pady=(4, 0))
        ttk.Label(
            panel,
            textvariable=self.detail_completion_var,
            style="Status.TLabel",
            wraplength=280,
            justify="left",
        ).grid(row=18, column=0, sticky="w", pady=(4, 0))
        ttk.Label(
            panel,
            textvariable=self.detail_alert_var,
            style="Status.TLabel",
            wraplength=280,
            justify="left",
        ).grid(row=19, column=0, sticky="w", pady=(4, 0))
        ttk.Label(
            panel,
            textvariable=self.status_var,
            style="Status.TLabel",
            wraplength=280,
            justify="left",
        ).grid(row=20, column=0, sticky="w", pady=(12, 0))

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
            self.tree.insert(
                "",
                "end",
                iid=str(task.task_id),
                values=(task.task_id, task.title, task.priority, due_date, status),
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

    def _load_selected_task_for_edit(self) -> None:
        task = self._get_selected_task()
        if task is None:
            return

        self.editing_task_id = task.task_id
        self.title_var.set(task.title)
        self.priority_var.set(task.priority)
        self.due_date_var.set(task.due_date)
        self.save_button.config(text="Guardar cambios")
        self.cancel_edit_button.config(state="normal")
        self.status_var.set(f"Editando tarea #{task.task_id}.")
        self.logger.info("Modo edicion activado: id=%s", task.task_id)

    def _cancel_edit_mode(self) -> None:
        self._clear_form()
        self.status_var.set("Edicion cancelada.")

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
            tasks = [task for task in tasks if search in task.title.lower()]

        return tasks

    def _handle_filter_change(self, _event: tk.Event | None = None) -> None:
        self.status_var.set("Vista actualizada con los filtros aplicados.")
        self._refresh_tasks()

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

    def _set_empty_detail(self) -> None:
        self.detail_title_var.set("Sin tarea seleccionada")
        self.detail_priority_var.set("Prioridad: -")
        self.detail_due_date_var.set("Vence: -")
        self.detail_completion_var.set("Estado: -")
        self.detail_alert_var.set("Alerta: -")

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
        self.save_button.config(text="Guardar tarea")
        self.cancel_edit_button.config(state="disabled")
