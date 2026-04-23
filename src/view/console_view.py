from src.data.task_repository import TaskRepository


class ConsoleView:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def run(self) -> None:
        while True:
            self._show_menu()
            option = input("Selecciona una opcion: ").strip()

            if option == "1":
                self._list_tasks()
            elif option == "2":
                self._add_task()
            elif option == "3":
                self._complete_task()
            elif option == "4":
                print("Saliendo de la aplicacion.")
                break
            else:
                print("Opcion invalida.")

            print()

    def _show_menu(self) -> None:
        print("=== Gestor de tareas MDV ===")
        print("1. Listar tareas")
        print("2. Agregar tarea")
        print("3. Completar tarea")
        print("4. Salir")

    def _list_tasks(self) -> None:
        tasks = self.repository.list_tasks()
        if not tasks:
            print("No hay tareas registradas.")
            return

        for task in tasks:
            status = "OK" if task.completed else "PENDIENTE"
            print(f"[{task.task_id}] {task.title} - {status}")

    def _add_task(self) -> None:
        title = input("Titulo de la tarea: ").strip()
        if not title:
            print("El titulo no puede estar vacio.")
            return

        task = self.repository.add_task(title)
        print(f"Tarea creada con ID {task.task_id}.")

    def _complete_task(self) -> None:
        task_id = input("ID de la tarea a completar: ").strip()
        if not task_id.isdigit():
            print("Debes ingresar un numero valido.")
            return

        if self.repository.complete_task(int(task_id)):
            print("Tarea marcada como completada.")
        else:
            print("No existe una tarea con ese ID.")
