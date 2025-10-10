import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PySide6.QtGui import QFont

class FileSystemTerminal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Файловый терминал")
        self.resize(800, 500)

        # --- Корневая папка main ---
        self.root_path = os.path.join(os.getcwd(), "main")
        os.makedirs(self.root_path, exist_ok=True)
        self.current_path = self.root_path

        # --- Интерфейс ---
        layout = QVBoxLayout(self)

        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 12))  # шрифт через QFont
        layout.addWidget(self.output)

        self.entry = QLineEdit(self)
        self.entry.setFont(QFont("Consolas", 12))  # шрифт через QFont
        layout.addWidget(self.entry)
        self.entry.returnPressed.connect(self.handle_command)
        self.entry.setFocus()  # фокус на поле ввода

        # Стартовый текст
        self.print_line("💻 Файловый терминал")
        self.print_line(f"📦 Корневая директория: {self.root_path}")
        self.show_dir_info()

    # -------------------------------------------------------
    def handle_command(self):
        command = self.entry.text().strip()
        if not command:
            return
        self.print_line(f"> {command}")
        self.entry.clear()

        parts = command.split()
        cmd = parts[0].lower()

        try:
            if cmd == "выход":
                QApplication.quit()
                return

            elif cmd == "нд":
                parent = os.path.dirname(self.current_path)
                if os.path.commonpath([parent, self.root_path]) != self.root_path:
                    self.print_line("❌ Ошибка: нельзя подняться выше 'main'.")
                elif parent == self.current_path:
                    self.print_line("❌ Вы уже в корне дерева.")
                else:
                    self.current_path = parent
                    self.show_dir_info()

            elif cmd == "вд":
                if len(parts) < 2:
                    self.print_line("❌ Укажите имя папки.")
                    return
                target = os.path.join(self.current_path, parts[1])
                if os.path.isdir(target):
                    self.current_path = target
                    self.show_dir_info()
                else:
                    self.print_line("❌ Папка не найдена.")

            elif cmd == "имя":
                if len(parts) < 3:
                    self.print_line("❌ Использование: имя <старое> <новое>")
                    return
                old_name = os.path.join(self.current_path, parts[1])
                new_name = os.path.join(self.current_path, parts[2])
                if not os.path.exists(old_name):
                    self.print_line("❌ Файл или папка не существует.")
                    return
                os.rename(old_name, new_name)
                self.print_line(f"✅ Переименовано: {parts[1]} → {parts[2]}")

            elif cmd == "инфо":
                self.show_dir_info()

            else:
                self.print_line("❌ Неизвестная команда. Доступные команды:")
                self.print_line("  Нд — подняться на уровень вверх")
                self.print_line("  Вд <папка> — перейти в подпапку")
                self.print_line("  имя <старое> <новое> — переименовать файл/папку")
                self.print_line("  Инфо — показать содержимое текущей папки")
                self.print_line("  выход — закрыть программу")

        except Exception as e:
            self.print_line(f"⚠️ Ошибка: {e}")

    # -------------------------------------------------------
    def show_dir_info(self):
        rel = os.path.relpath(self.current_path, start=self.root_path)
        if rel == ".":
            rel = "main"
        self.print_line(f"\n📂 Текущая директория: {rel}")

        entries = os.listdir(self.current_path)
        if not entries:
            self.print_line(" (папка пуста)")
            return

        dirs = [e for e in entries if os.path.isdir(os.path.join(self.current_path, e))]
        files = [e for e in entries if os.path.isfile(os.path.join(self.current_path, e))]

        self.print_line("Папки:")
        for d in dirs:
            self.print_line(f"  [ПАПКА] {d}")

        self.print_line("\nФайлы:")
        for f in files:
            ext = os.path.splitext(f)[1] or "(без расширения)"
            self.print_line(f"  {f} — {ext}")

    # -------------------------------------------------------
    def print_line(self, text):
        self.output.append(text)
        self.output.verticalScrollBar().setValue(self.output.verticalScrollBar().maximum())


# -------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    terminal = FileSystemTerminal()
    terminal.show()
    sys.exit(app.exec())
