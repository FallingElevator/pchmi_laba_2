import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QTreeView, QTextEdit, QLineEdit,
                               QPushButton, QLabel, QFileSystemModel,
                               QSplitter, QMessageBox, QMenu, QDialog,
                               QDialogButtonBox, QFormLayout, QListWidget,
                               QInputDialog)
from PySide6.QtGui import QAction, QFont, QIcon
from PySide6.QtCore import Qt, QDir, QItemSelectionModel


class RenameDialog(QDialog):
    def __init__(self, current_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Переименовать")
        self.setModal(True)
        self.resize(300, 100)

        layout = QFormLayout(self)

        self.old_name_label = QLabel(current_name)
        self.new_name_input = QLineEdit(current_name)

        layout.addRow("Текущее имя:", self.old_name_label)
        layout.addRow("Новое имя:", self.new_name_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addRow(buttons)

    def get_new_name(self):
        return self.new_name_input.text().strip()


class GroupRenameDialog(QDialog):
    def __init__(self, file_count, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Групповое переименование")
        self.setModal(True)
        self.resize(400, 150)

        layout = QFormLayout(self)

        self.file_count_label = QLabel(f"Будет переименовано файлов: {file_count}")
        self.new_name_input = QLineEdit()
        self.new_name_input.setPlaceholderText("Введите новое базовое имя")

        layout.addRow(self.file_count_label)
        layout.addRow("Базовое имя:", self.new_name_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addRow(buttons)

    def get_new_name(self):
        return self.new_name_input.text().strip()


class FileManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Файловый менеджер")
        self.resize(1000, 700)

        # Корневая папка main
        self.root_path = os.path.join(os.getcwd(), "main")
        os.makedirs(self.root_path, exist_ok=True)
        self.current_path = self.root_path

        self.setup_ui()
        self.setup_file_system()

    def setup_ui(self):
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        main_layout = QVBoxLayout(central_widget)

        # Панель пути
        path_layout = QHBoxLayout()
        self.path_label = QLabel(f"Текущий путь: {self.get_relative_path()}")
        self.path_label.setFont(QFont("Arial", 10))

        self.up_button = QPushButton("Наверх")
        self.up_button.clicked.connect(self.go_up)
        self.up_button.setFixedWidth(80)

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.refresh_view)
        self.refresh_button.setFixedWidth(80)

        path_layout.addWidget(self.path_label)
        path_layout.addStretch()
        path_layout.addWidget(self.up_button)
        path_layout.addWidget(self.refresh_button)

        main_layout.addLayout(path_layout)

        # Splitter для дерева файлов и информации
        splitter = QSplitter(Qt.Horizontal)

        # Левая панель - дерево файлов
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        left_layout.addWidget(QLabel("Структура папок:"))

        self.tree_view = QTreeView()
        self.tree_view.setFont(QFont("Consolas", 10))
        self.tree_view.doubleClicked.connect(self.on_item_double_clicked)
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)

        # Включаем множественное выделение с поддержкой Shift
        self.tree_view.setSelectionMode(QTreeView.ExtendedSelection)

        left_layout.addWidget(self.tree_view)

        # Правая панель - информация
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        right_layout.addWidget(QLabel("Информация о папке:"))

        self.info_text = QTextEdit()
        self.info_text.setFont(QFont("Consolas", 10))
        self.info_text.setReadOnly(True)

        right_layout.addWidget(self.info_text)

        # Командная строка
        command_layout = QHBoxLayout()
        command_layout.addWidget(QLabel("Команда:"))

        self.command_input = QLineEdit()
        self.command_input.setFont(QFont("Consolas", 10))
        self.command_input.returnPressed.connect(self.execute_command)

        self.execute_button = QPushButton("Выполнить")
        self.execute_button.clicked.connect(self.execute_command)
        self.execute_button.setFixedWidth(100)

        command_layout.addWidget(self.command_input)
        command_layout.addWidget(self.execute_button)

        # Добавляем все в splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 600])

        main_layout.addWidget(splitter)
        main_layout.addLayout(command_layout)

        # Создаем меню
        self.create_menu()

    def create_menu(self):
        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu("Файл")

        new_folder_action = QAction("Создать папку", self)
        new_folder_action.triggered.connect(self.create_new_folder)
        file_menu.addAction(new_folder_action)

        # Добавляем действие для группового переименования
        group_rename_action = QAction("Групповое переименование", self)
        group_rename_action.triggered.connect(self.group_rename_selected)
        file_menu.addAction(group_rename_action)

        file_menu.addSeparator()

        refresh_action = QAction("Обновить", self)
        refresh_action.triggered.connect(self.refresh_view)
        file_menu.addAction(refresh_action)

        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню Помощь
        help_menu = menubar.addMenu("Помощь")

        help_action = QAction("Справка по командам", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

    def setup_file_system(self):
        # Модель файловой системы
        self.model = QFileSystemModel()
        self.model.setRootPath(self.root_path)
        self.model.setNameFilters([])  # Показывать все файлы
        self.model.setNameFilterDisables(False)

        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(self.root_path))

        # Скрываем колонки размера, типа и даты изменения
        self.tree_view.hideColumn(1)  # Размер
        self.tree_view.hideColumn(2)  # Тип
        self.tree_view.hideColumn(3)  # Дата изменения

        self.update_info()

    def get_relative_path(self):
        rel_path = os.path.relpath(self.current_path, start=self.root_path)
        return rel_path if rel_path != "." else "main"

    def update_info(self):
        self.path_label.setText(f"Текущий путь: {self.get_relative_path()}")
        self.show_dir_info()

    def show_dir_info(self):
        rel = self.get_relative_path()
        info_text = f"📂 Текущая директория: {rel}\n\n"

        try:
            entries = os.listdir(self.current_path)
            if not entries:
                info_text += " (папка пуста)"
            else:
                dirs = [e for e in entries if os.path.isdir(os.path.join(self.current_path, e))]
                files = [e for e in entries if os.path.isfile(os.path.join(self.current_path, e))]

                info_text += "📁 Папки:\n"
                for d in dirs:
                    info_text += f"  📂 {d}\n"

                info_text += "\n📄 Файлы:\n"
                for f in files:
                    ext = os.path.splitext(f)[1] or "(без расширения)"
                    info_text += f"  📄 {f} — {ext}\n"

        except PermissionError:
            info_text += "❌ Нет доступа к этой папке"

        self.info_text.setText(info_text)

    def go_up(self):
        parent = os.path.dirname(self.current_path)
        if os.path.commonpath([parent, self.root_path]) != self.root_path:
            QMessageBox.warning(self, "Ошибка", "Нельзя подняться выше 'main'.")
        elif parent == self.current_path:
            QMessageBox.information(self, "Информация", "Вы уже в корне дерева.")
        else:
            self.current_path = parent
            self.tree_view.setRootIndex(self.model.index(self.current_path))
            self.update_info()

    def on_item_double_clicked(self, index):
        path = self.model.filePath(index)
        if os.path.isdir(path):
            self.current_path = path
            self.tree_view.setRootIndex(index)
            self.update_info()

    def show_context_menu(self, position):
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return

        path = self.model.filePath(index)
        menu = QMenu(self)

        if os.path.isdir(path):
            rename_action = QAction("Переименовать", self)
            rename_action.triggered.connect(lambda: self.rename_item(path))
            menu.addAction(rename_action)

            open_action = QAction("Открыть", self)
            open_action.triggered.connect(lambda: self.open_directory(path))
            menu.addAction(open_action)
        else:
            rename_action = QAction("Переименовать файл", self)
            rename_action.triggered.connect(lambda: self.rename_item(path))
            menu.addAction(rename_action)

        # Добавляем действие для группового переименования выделенных файлов
        selected_indexes = self.tree_view.selectionModel().selectedIndexes()
        if len(selected_indexes) > 1:
            group_rename_action = QAction("Групповое переименование выделенных", self)
            group_rename_action.triggered.connect(self.group_rename_selected)
            menu.addAction(group_rename_action)

        menu.exec_(self.tree_view.viewport().mapToGlobal(position))

    def rename_item(self, path):
        current_name = os.path.basename(path)
        dialog = RenameDialog(current_name, self)
        if dialog.exec_() == QDialog.Accepted:
            new_name = dialog.get_new_name()
            if new_name and new_name != current_name:
                try:
                    new_path = os.path.join(os.path.dirname(path), new_name)
                    os.rename(path, new_path)
                    self.refresh_view()
                    QMessageBox.information(self, "Успех", f"Успешно переименовано в: {new_name}")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось переименовать: {e}")

    def group_rename_selected(self):
        """Групповое переименование выделенных файлов через интерфейс"""
        selected_indexes = self.tree_view.selectionModel().selectedIndexes()

        # Фильтруем только файлы (не папки) и убираем дубликаты
        file_paths = []
        for index in selected_indexes:
            if index.column() == 0:  # Только первую колонку (имя)
                path = self.model.filePath(index)
                if os.path.isfile(path):
                    file_paths.append(path)

        if not file_paths:
            QMessageBox.information(self, "Информация", "Выберите файлы для переименования.")
            return

        # Сортируем файлы по имени для последовательной нумерации
        file_paths.sort()

        dialog = GroupRenameDialog(len(file_paths), self)
        if dialog.exec_() == QDialog.Accepted:
            new_base_name = dialog.get_new_name()
            if not new_base_name:
                QMessageBox.warning(self, "Ошибка", "Введите базовое имя.")
                return

            self.perform_group_rename(file_paths, new_base_name)

    def perform_group_rename(self, file_paths, new_base_name):
        """Выполняет групповое переименование файлов"""
        success_count = 0
        warning_messages = []

        for i, old_path in enumerate(file_paths, 1):
            if not os.path.exists(old_path):
                warning_messages.append(f"Файл не существует: {os.path.basename(old_path)}")
                continue

            # Получаем расширение файла
            _, ext = os.path.splitext(old_path)

            # Формируем новое имя: базовое_имя_номер.расширение
            new_name = f"{new_base_name}_{i}{ext}"
            new_path = os.path.join(os.path.dirname(old_path), new_name)

            try:
                os.rename(old_path, new_path)
                success_count += 1
            except Exception as e:
                warning_messages.append(f"Ошибка переименования {os.path.basename(old_path)}: {e}")

        # Показываем результаты
        result_message = f"Успешно переименовано: {success_count} файлов"
        if warning_messages:
            result_message += f"\n\nПредупреждения:\n" + "\n".join(warning_messages)

        QMessageBox.information(self, "Результат", result_message)
        self.refresh_view()

    def open_directory(self, path):
        self.current_path = path
        self.tree_view.setRootIndex(self.model.index(path))
        self.update_info()

    def create_new_folder(self):
        name, ok = QInputDialog.getText(self, "Создать папку", "Введите имя папки:")
        if ok and name:
            try:
                new_folder_path = os.path.join(self.current_path, name)
                os.makedirs(new_folder_path, exist_ok=True)
                self.refresh_view()
                QMessageBox.information(self, "Успех", f"Папка '{name}' создана")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать папку: {e}")

    def refresh_view(self):
        self.model.setRootPath(self.root_path)  # Обновляем модель
        self.tree_view.setRootIndex(self.model.index(self.current_path))
        self.update_info()

    def execute_command(self):
        command = self.command_input.text().strip()
        if not command:
            return

        self.command_input.clear()
        self.info_text.append(f"> {command}")

        parts = command.split()
        cmd = parts[0].lower() if parts else ""

        try:
            if cmd == "выход":
                self.close()

            elif cmd == "нд":
                self.go_up()

            elif cmd == "вд":
                if len(parts) < 2:
                    self.info_text.append("❌ Укажите имя папки.")
                    return

                target = os.path.join(self.current_path, parts[1])
                if os.path.isdir(target):
                    self.current_path = target
                    self.tree_view.setRootIndex(self.model.index(self.current_path))
                    self.update_info()
                else:
                    self.info_text.append("❌ Папка не найдена.")

            elif cmd == "имя":
                if len(parts) < 3:
                    self.info_text.append("❌ Использование: имя <старое> <новое>")
                    return

                old_name = os.path.join(self.current_path, parts[1])
                new_name_full = ' '.join(parts[2:])
                new_name = os.path.join(self.current_path, new_name_full)

                if not os.path.exists(old_name):
                    self.info_text.append("❌ Файл или папка не существует.")
                    return

                os.rename(old_name, new_name)
                self.info_text.append(f"✅ Переименовано: {parts[1]} → {new_name_full}")
                self.refresh_view()

            elif cmd == "имягр":
                if len(parts) < 3:
                    self.info_text.append("❌ Использование: имягр <новое> <имя1> <имя2> <имя3> ...")
                    return

                new_base_name = parts[1]
                file_names = parts[2:]

                self.execute_group_rename_command(new_base_name, file_names)

            elif cmd == "инфо":
                self.show_dir_info()

            elif cmd == "помощь":
                self.show_help()

            else:
                self.info_text.append("❌ Неизвестная команда.")
                self.show_help()

        except Exception as e:
            self.info_text.append(f"⚠️ Ошибка: {e}")

    def execute_group_rename_command(self, new_base_name, file_names):
        """Выполняет групповое переименование из командной строки"""
        success_count = 0
        warning_messages = []

        for i, file_name in enumerate(file_names, 1):
            old_path = os.path.join(self.current_path, file_name)

            if not os.path.exists(old_path):
                warning_messages.append(f"Файл не существует: {file_name}")
                continue

            # Получаем расширение файла
            _, ext = os.path.splitext(old_path)

            # Формируем новое имя: базовое_имя_номер.расширение
            new_name = f"{new_base_name}_{i}{ext}"
            new_path = os.path.join(self.current_path, new_name)

            try:
                os.rename(old_path, new_path)
                success_count += 1
                self.info_text.append(f"✅ {file_name} → {new_name}")
            except Exception as e:
                warning_messages.append(f"Ошибка переименования {file_name}: {e}")

        # Выводим предупреждения
        for warning in warning_messages:
            self.info_text.append(f"⚠️ {warning}")

        if success_count > 0:
            self.info_text.append(f"✅ Успешно переименовано: {success_count} файлов")

        self.refresh_view()

    def show_help(self):
        help_text = """
📋 Доступные команды:

  Нд - подняться на уровень вверх
  Вд <папка> - перейти в подпапку
  имя <старое> <новое> - переименовать файл/папку
  имягр <новое> <имя1> <имя2> ... - групповое переименование файлов
  инфо - показать содержимое текущей папки
  помощь - показать эту справку
  выход - закрыть программу

💡 Советы:
- Двойной клик по папке в дереве открывает её
- Правая кнопка мыши открывает контекстное меню
- Используйте кнопку 'Наверх' для перехода в родительскую папку
- Для группового переименования выделите несколько файлов с помощью Shift/Ctrl
"""
        self.info_text.setText(help_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Современный стиль

    window = FileManagerApp()
    window.show()

    sys.exit(app.exec())