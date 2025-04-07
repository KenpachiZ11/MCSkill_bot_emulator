import os
import subprocess
import pyautogui
import time
import json
from pynput.keyboard import Key, Controller
import datetime
import threading
import argparse
import sys

# Путь к файлу конфигурации
config_file = "config.json"

# Чтение данных из JSON-файла
try:
    with open(config_file, "r") as f:
        config = json.load(f)
except FileNotFoundError:
    print(f"Файл конфигурации '{config_file}' не найден.")
    exit()
except json.JSONDecodeError:
    print(f"Ошибка при чтении JSON из файла '{config_file}'.")
    exit()

# Извлечение параметров из конфигурации
launcher_path = r"C:\\Users\\mrdan\\OneDrive\\Рабочий стол\\McSkill.exe"  # Путь задан в коде
window_title = config["window_title"]
launcher_window_title = config["launcher_window_title"]
first_start_time = config["first_start_time"]
first_close_time = config["first_close_time"]
second_start_time = config["second_start_time"]
second_close_time = config["second_close_time"]
delays = config["delays"]
coordinates = config["coordinates"]

# Задержка после каждого вызова функции PyAutoGUI
pyautogui.PAUSE = 0.1

# Функция для выполнения клика с заданными координатами
def perform_click(coord_name, delay_index=None):
    try:
        x, y = coordinates[coord_name]
        print(f"Перемещаю курсор к координатам ({coord_name}) ...")
        pyautogui.moveTo(x, y, duration=delays["mousemove_duration"])
        if delay_index is not None:
            time.sleep(delays["mousemove_delays"][delay_index])
        print(f"Курсор перемещен к координатам ({coord_name}): X={x}, Y={y}")
        print(f"Выполняю клик ({coord_name}) ...")
        # pyautogui.click()
        pyautogui.mouseDown()
        time.sleep(0.1)
        pyautogui.mouseUp()
        print(f"Клик ({coord_name}) выполнен!")
        time.sleep(0.5)  # Дополнительная задержка после клика
    except Exception as e:
        print(f"Произошла ошибка при выполнении клика ({coord_name}): {e}")

# Функция для выполнения двойного клика с заданными координатами
def perform_double_click(coord_name):
    try:
        x, y = coordinates[coord_name]
        print(f"Перемещаю курсор для двойного клика к координатам ({coord_name}) ...")
        pyautogui.moveTo(x, y, duration=delays["mousemove_duration"])
        print(f"Курсор перемещен для двойного клика к координатам ({coord_name}): X={x}, Y={y}")
        print(f"Выполняю двойной клик ({coord_name}) ...")
        pyautogui.doubleClick()
        print(f"Двойной клик ({coord_name}) выполнен!")
        time.sleep(0.5) # Дополнительная задержка после двойного клика
    except Exception as e:
        print(f"Произошла ошибка при выполнении двойного клика ({coord_name}): {e}")

def wait_for_time(target_time):
    """Ждет наступления заданного времени."""
    while True:
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        print(f"Текущее время: {current_time}, Target time: {target_time}")  # Добавлено для отладки
        if current_time == target_time:
            print(f"Наступило время {target_time}.  Запуск скрипта...")
            break
        else:
            print(f"Текущее время: {current_time}. Ожидание {target_time}...")
            time.sleep(60)  # Проверяем каждую минуту

def emulate_lkm_press():
    """Эмулирует зажатую ЛКМ до закрытия лаунчера, с перерывами."""
    global launcher_closed
    try:
        print("Запускаю цикл эмуляции зажатой ЛКМ ...")

        while not launcher_closed:
            print("Зажимаю ЛКМ на 1 минуту...")
            pyautogui.mouseDown()  # Нажимаем и держим ЛКМ
            time.sleep(60) # Работаем минуту

            pyautogui.mouseUp()  # Отпускаем ЛКМ
            print("ЛКМ отпущена. Пауза 2 секунды...")
            time.sleep(2)  # Пауза 2 секунды

    except Exception as e:
        print(f"Произошла ошибка при эмуляции зажатой ЛКМ: {e}")

def check_time_and_close():
    """Проверяет время и закрывает лаунчер."""
    global launcher_closed
    while True:
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        if current_time == first_close_time or current_time == second_close_time:
            print("Время закрывать лаунчер!")
            try:
                # Отпускаем ЛКМ
                print("Отпускаю ЛКМ...")
                pyautogui.mouseUp()
                time.sleep(1)  # Небольшая задержка

                # Нажимаем ESC
                print("Нажимаю ESC перед закрытием лаунчера...")
                keyboard = Controller()
                keyboard.press(Key.esc)
                keyboard.release(Key.esc)
                time.sleep(1)  # Небольшая задержка

                # Активируем окно лаунчера
                windows = pyautogui.getWindowsWithTitle(launcher_window_title)
                if windows:
                    window = windows[0]
                    window.activate()
                    time.sleep(1)

                    # Эмулируем нажатие Alt+F4
                    pyautogui.hotkey('alt', 'f4')
                    print("Лаунчер Minecraft закрыт с помощью Alt+F4.")
                    launcher_closed = True
                    break
                else:
                    print(f"Окно с заголовком '{launcher_window_title}' не найдено.")
                    launcher_closed = True
                    break

            except Exception as e:
                print(f"Произошла ошибка при закрытии лаунчера: {e}")
                launcher_closed = True
                break

        time.sleep(60)

def run_minecraft():
    """Запускает Minecraft и выполняет действия."""
    global launcher_closed
    launcher_closed = False # Reset launcher_closed before each run
    try:
        process = subprocess.Popen(launcher_path)
        print(f"Лаунчер Minecraft запущен: {launcher_path}")
    except FileNotFoundError:
        print(f"Файл не найден: {launcher_path}")
        return # Exit this function if the launcher isn't found
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return # Exit this function if there is an error

    # Даем время для запуска лаунчера и переключения в Minecraft
    time.sleep(delays["initial_delay"])

    # Попытка активировать окно Minecraft
    try:
        windows = pyautogui.getWindowsWithTitle(window_title)
        if windows:
            window = windows[0]
            window.activate()
            print(f"Окно '{window_title}' активировано.")
            time.sleep(delays["activate_window_delay"])
        else:
            print(f"Окно с заголовком '{window_title}' не найдено.")
    except Exception as e:
        print(f"Произошла ошибка при активации окна: {e}")

    # Выполнение кликов и перемещений мыши с использованием конфигурации
    perform_click("coord1", 0)
    time.sleep(2)
    perform_click("coord2", 1)
    time.sleep(15)
    perform_click("coord3", 2)
    time.sleep(60)
    perform_click("coord4", 3)
    time.sleep(3)
    perform_double_click("double_click")
    time.sleep(1)
    time.sleep(delays["esc_delay"])

    # Нажатие клавиши ESC с использованием pynput
    try:
        print("Нажимаю клавишу ESC с помощью pynput ...")
        keyboard = Controller()
        keyboard.press(Key.esc)
        keyboard.release(Key.esc)
        print("Клавиша ESC нажата с помощью pynput!")
        time.sleep(0.5)
    except Exception as e:
        print(f"Произошла ошибка при нажатии клавиши ESC с помощью pynput: {e}")

    time.sleep(2)
    perform_click("click5")

    # Задержка перед зажатием ЛКМ
    print(f"Ожидаю {delays['lkm_delay']} секунды перед зажатием ЛКМ ...")
    time.sleep(delays["lkm_delay"])

    # Запускаем эмуляцию ЛКМ в отдельном потоке
    lkm_thread = threading.Thread(target=emulate_lkm_press)
    lkm_thread.daemon = True
    lkm_thread.start()

    # Ждем, пока лаунчер не будет закрыт (поток check_time_and_close завершит работу)
    while not launcher_closed:
        time.sleep(1) # Small delay to prevent busy-waiting

# Используем argparse для добавления аргумента командной строки
parser = argparse.ArgumentParser(description="Автоматизация Minecraft.")
parser.add_argument('--force', action='store_true', help='Запустить скрипт немедленно, игнорируя расписание.')
args = parser.parse_args()

print(f"args.force: {args.force}")  # Добавлено для отладки

# Создаем и запускаем поток для проверки времени и закрытия лаунчера
time_check_thread = threading.Thread(target=check_time_and_close)
time_check_thread.daemon = True
time_check_thread.start()

# Основной цикл работы скрипта
current_stage = 1 # 1 - waiting for first start, 2 - waiting for second start

while True:
    # Отслеживание курсора
    print("Отслеживаю курсор. Нажмите Ctrl+C, чтобы остановить.")
    try:
        print("Цикл отслеживания запущен")
        while True:
            x, y = pyautogui.position()
            position_str = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            time_str = f"Текущее время: {current_time}"
            output_str = f"{position_str} | {time_str}"
            print(output_str, end='', flush=True)
            print('\b' * len(output_str), end='', flush=True)
            time.sleep(0.1)

            if args.force:
                print("Аргумент --force указан. Запуск Minecraft...")
                run_minecraft()
                print("Minecraft завершен. Перезапуск через 60 секунд...")
                time.sleep(60)  # Wait before restarting
            else:
                print("Проверяем расписание...")
                now = datetime.datetime.now()
                current_time = now.strftime("%H:%M")

                if current_stage == 1:
                    if current_time == first_start_time:
                        print(f"Наступило время первого запуска ({first_start_time}). Запуск Minecraft...")
                        run_minecraft()
                        current_stage = 2 # Move to stage 2
                    else:
                        wait_for_time(first_start_time)
                        run_minecraft()
                        current_stage = 2
                elif current_stage == 2:
                    if current_time == second_start_time:
                        print(f"Наступило время второго запуска ({second_start_time}). Запуск Minecraft...")
                        run_minecraft()
                        current_stage = 1 # Move back to stage 1 for the loop to start over
                    else:
                        wait_for_time(second_start_time)
                        run_minecraft()
                        current_stage = 1

                # After running, wait for close time:
                while True:
                    now = datetime.datetime.now()
                    current_time = now.strftime("%H:%M")
                    if current_time == first_close_time or current_time == second_close_time:
                        break  # Exit the loop and run again

                    time.sleep(60)  # Check every minute for close time

    except KeyboardInterrupt:
        print("\nОтслеживание остановлено.")
        break  # Break out of the outer loop too

    print("Скрипт перезапускается...")