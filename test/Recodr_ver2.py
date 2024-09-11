import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.core.window import Window
import subprocess
import os
import json
import threading
from datetime import datetime
import pyaudio

# Файл для сохранения настроек
settings_file = 'settings.json'

# Глобальные переменные для настроек
settings = {
    'microphone': '',
    'save_path': r'C:\zapis'
}

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

# Класс для главного интерфейса
class RecorderApp(App):
    def build(self):
        load_settings()

        # Установка размеров окна
        Window.size = (300, 300)

        # Основной макет
        layout = BoxLayout(orientation='vertical', padding=5, spacing=5)

        # Поле выбора микрофона
        self.mic_label = Label(text="Микрофон:", font_size=14, size_hint=(1, 0.1))
        layout.add_widget(self.mic_label)

        self.mic_spinner = Spinner(text=settings['microphone'], values=self.get_microphones(), font_size=14, size_hint=(1, 0.2))
        layout.add_widget(self.mic_spinner)

        # Поле выбора пути сохранения
        self.path_label = Label(text="Путь:", font_size=14, size_hint=(1, 0.1))
        layout.add_widget(self.path_label)

        self.path_input = TextInput(text=settings['save_path'], multiline=False, font_size=14, size_hint=(1, 0.2))
        layout.add_widget(self.path_input)

        # Кнопка для выбора папки
        self.browse_button = Button(text="Папка", font_size=14, size_hint=(1, 0.15))
        self.browse_button.bind(on_release=self.choose_directory)
        layout.add_widget(self.browse_button)

        # Кнопка для управления записью
        self.record_button = Button(text="Запись", font_size=14, size_hint=(1, 0.15))
        self.record_button.bind(on_release=self.toggle_recording)
        layout.add_widget(self.record_button)

        # Информация о записи
        self.info_label = Label(text="", font_size=12, size_hint=(1, 0.15))
        layout.add_widget(self.info_label)

        return layout

    def get_microphones(self):
        p = pyaudio.PyAudio()
        mic_list = []
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                mic_list.append(device_info['name'].encode('utf-8').decode('utf-8', errors='ignore'))
        p.terminate()
        return mic_list

    def choose_directory(self, instance):
        filechooser = FileChooserListView()
        popup = Popup(title="Выберите папку", content=filechooser, size_hint=(0.9, 0.9))
        filechooser.bind(on_submit=self.select_path)
        popup.open()

    def select_path(self, instance, selection, touch):
        self.path_input.text = selection[0] if selection else settings['save_path']
        instance.parent.dismiss()

    def toggle_recording(self, instance):
        if self.record_button.text == "Запись":
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        microphone = self.mic_spinner.text
        save_path = self.path_input.text

        if not microphone or not save_path:
            self.info_label.text = "Пожалуйста, выберите микрофон и путь."
            return

        settings['microphone'] = microphone
        settings['save_path'] = save_path
        save_settings()

        output_file = self.generate_filename()

        self.recording_thread = threading.Thread(target=self.run_ffmpeg, args=(microphone, output_file))
        self.recording_thread.start()

        self.record_button.text = "Стоп"
        self.info_label.text = f"Запись началась... Файл будет сохранен как: {output_file}"

    def stop_recording(self):
        if hasattr(self, 'process') and self.process:
            self.process.terminate()
            self.recording_thread.join()

        self.record_button.text = "Запись"
        self.info_label.text = "Запись завершена."

    def generate_filename(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(settings['save_path'], f"output_{timestamp}.wav")

    def run_ffmpeg(self, microphone, output_file):
        self.process = subprocess.Popen(
            ['ffmpeg', '-f', 'dshow', '-i', f'audio={microphone}', output_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.process.communicate()

if __name__ == "__main__":
    RecorderApp().run()
