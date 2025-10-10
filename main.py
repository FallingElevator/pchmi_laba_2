import os
import sys

def list_dir(path):
    """Выводит содержимое каталога с подписями."""
    print(f"\n📂 Текущая директория: {os.path.relpath(path, start=root_path)}\n")
    entries = os.listdir(path)
    if not entries:
        print(" (папка пуста)")
        return

    dirs = [e for e in entries if os.path.isdir(os.path.join(path, e))]
    files = [e for e in entries if os.path.isfile(os.path.join(path, e))]

    print("Папки:")
    for d in dirs:
        print(f"  [ПАПКА] {d}")

    print("\nФайлы:")
    for f in files:
        ext = os.path.splitext(f)[1] or "(без расширения)"
        print(f"  {f} — {ext}")


def main():
    global root_path
    root_path = os.path.join(os.getcwd(), "main")

    # Создаем папку main, если её нет
    os.makedirs(root_path, exist_ok=True)

    current_path = root_path
    print("💻 Консоль файловой системы (введите 'выход' для завершения)\n")
    print(f"📦 Корневая директория: {root_path}\n")

    list_dir(current_path)

    while True:
        command = input("\n> ").strip()
        if not command:
            continue

        if command.lower() == "выход":
            print("👋 Завершение работы.")
            break

        parts = command.split()
        cmd = parts[0].lower()

        try:
            if cmd == "нд":
                parent = os.path.dirname(current_path)
                # Проверяем, не выходим ли за пределы main
                if os.path.commonpath([parent, root_path]) != root_path:
                    print("❌ Ошибка: нельзя подняться выше папки 'main'.")
                elif parent == current_path:
                    print("❌ Ошибка: вы находитесь в корне дерева.")
                else:
                    current_path = parent
                    list_dir(current_path)

            elif cmd == "вд":
                if len(parts) < 2:
                    print("❌ Ошибка: не указано имя папки.")
                    continue
                target = os.path.join(current_path, parts[1])
                if os.path.isdir(target):
                    current_path = target
                    list_dir(current_path)
                else:
                    print("❌ Ошибка: папка не найдена.")

            elif cmd == "имя":
                if len(parts) < 3:
                    print("❌ Ошибка: использование — имя <старое> <новое>")
                    continue
                old_name = os.path.join(current_path, parts[1])
                new_name = os.path.join(current_path, parts[2])
                if not os.path.exists(old_name):
                    print("❌ Ошибка: файл не существует.")
                    continue
                try:
                    os.rename(old_name, new_name)
                    print(f"✅ Файл переименован в: {parts[2]}")
                except Exception as e:
                    print(f"❌ Ошибка при переименовании: {e}")

            elif cmd == "инфо":
                list_dir(current_path)

            else:
                print("❌ Неизвестная команда. Доступные команды:")
                print("  Нд — подняться на уровень вверх (до 'main')")
                print("  Вд <папка> — перейти в подпапку")
                print("  имя <старое> <новое> — переименовать файл")
                print("  Инфо — показать содержимое текущей папки")
                print("  выход — завершить работу")

        except Exception as e:
            print(f"⚠️ Неожиданная ошибка: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Программа завершена пользователем.")
        sys.exit(0)
