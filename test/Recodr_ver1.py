import subprocess
import os
import keyboard
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from datetime import datetime
import json

# Файл для сохранения настроек
settings_file = 'settings.json'

# Глобальные переменные для настроек
settings = {
    'microphone': 'Микрофон (2- USB Audio)',
    'save_path': r'C:\zapis'
}

process = None
recording_window = None


# Загрузка настроек из файла
def load_settings():
    global settings
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            settings = json.load(f)


# Сохранение настроек в файл
def save_settings():
    global settings
    with open(settings_file, 'w') as f:
        json.dump(settings, f)


# Функция для генерации имени файла с датой и временем
def generate_filename():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(settings['save_path'], f"output_{timestamp}.wav")


# Функция для создания и управления окном записи
def create_recording_window():
    global recording_window
    recording_window = tk.Tk()
    recording_window.title("Запись")
    recording_window.geometry("300x150")
    recording_window.configure(bg='#282828')
    recording_window.attributes('-topmost', True)
    recording_window.protocol("WM_DELETE_WINDOW", disable_close)

    label = tk.Label(recording_window, text="Идет запись...", font=("Arial", 24), fg='white', bg='#282828')
    label.pack(padx=20, pady=20)

    recording_window.mainloop()


# Начать запись
def start_recording():
    global process
    output_file = generate_filename()

    threading.Thread(target=create_recording_window).start()

    process = subprocess.Popen(
        [ffmpeg_path, '-f', 'dshow', '-i', f'audio={settings["microphone"]}', output_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    print(f"Запись началась... Файл будет сохранен как: {output_file}")


# Остановить запись
def stop_recording():
    global process, recording_window
    if process:
        process.terminate()
        process.wait()
        print("Запись завершена.")

        if recording_window is not None:
            recording_window.after(0, recording_window.quit)
            recording_window.after(0, recording_window.destroy)
            recording_window = None

        process = None


# Переключение записи (запуск или остановка)
def toggle_recording():
    if process is None:
        start_recording()
    else:
        stop_recording()


# Отключение возможности закрытия окна пользователем
def disable_close():
    pass


# Настройки приложения
def open_settings_window():
    def save_and_close():
        settings['microphone'] = mic_entry.get()
        settings['save_path'] = path_entry.get()
        save_settings()
        settings_window.destroy()

    settings_window = tk.Tk()
    settings_window.title("Настройки")
    settings_window.geometry("400x200")

    tk.Label(settings_window, text="Микрофон:").pack(pady=5)
    mic_entry = tk.Entry(settings_window, width=50)
    mic_entry.pack(pady=5)
    mic_entry.insert(0, settings['microphone'])

    tk.Label(settings_window, text="Путь для сохранения:").pack(pady=5)
    path_entry = tk.Entry(settings_window, width=50)
    path_entry.pack(pady=5)
    path_entry.insert(0, settings['save_path'])

    def choose_directory():
        directory = filedialog.askdirectory()
        if directory:
            path_entry.delete(0, tk.END)
            path_entry.insert(0, directory)

    tk.Button(settings_window, text="Выбрать папку", command=choose_directory).pack(pady=5)
    tk.Button(settings_window, text="Сохранить и закрыть", command=save_and_close).pack(pady=20)

    settings_window.mainloop()


# Привязка кнопки для запуска/остановки записи
keyboard.add_hotkey('F9', toggle_recording)

# Создание главного окна интерфейса
root = tk.Tk()
root.title("Аудио рекордер")
root.geometry("300x150")

tk.Button(root, text="Настройки", command=open_settings_window).pack(pady=20)
tk.Label(root, text="Нажмите F9 для начала/остановки записи", font=("Arial", 12)).pack(pady=20)

load_settings()  # Загрузка настроек при запуске

print("Скрипт запущен. Нажмите F9 для начала/остановки записи.")

root.mainloop()
