import flet as ft
from recorder import Recorder
from settings import load_settings, save_settings
from uploader import upload_file
import time
import threading

def start_app():
    def main(page: ft.Page):
        page.title = "RecorderGorod"
        page.window_icon = "mic.ico"
        page.bgcolor = "#1e1e1e"
        page.window_width = 300
        page.window_height = 400

        settings = load_settings()
        recorder = Recorder()
        is_recording = False
        start_time = None

        # Создаем больше блоков уровня звука с фиксированными размерами
        bars = [ft.Container(height=100, bgcolor="#555555", width=10) for _ in range(20)]

        settings_button = ft.IconButton(
            icon=ft.icons.SETTINGS,
            icon_size=30,
            tooltip="Настройки",
            on_click=lambda e: open_settings()
        )

        title = ft.Text("RecorderGorod", color="white", size=28, weight="bold")

        record_button = ft.ElevatedButton(
            text="Начать запись",
            icon=ft.icons.MIC,
            bgcolor="#ff5555",
            color="white",
            on_click=lambda e: toggle_recording(),
        )

        timer_label = ft.Text("00:00:00", color="white", size=20)

        # Обновляем разметку с блоками уровня звука
        page.add(
            ft.Row([settings_button], alignment=ft.MainAxisAlignment.END),
            ft.Column(
                [
                    title,
                    record_button,
                    timer_label,
                    ft.Row(bars, alignment=ft.MainAxisAlignment.CENTER, spacing=3),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,  # Увеличиваем отступы
            ),
        )

        def open_settings():
            page.window_width = 400
            page.window_height = 500

            def save_and_close(e):
                mic_index = int(mic_dropdown.value.split('(')[-1].strip(')'))
                settings["microphone"] = mic_index
                settings["save_path"] = path_input.value
                settings["api_key"] = api_key_input.value
                save_settings(settings)
                page.dialog.open = False
                restore_window_size()

            mic_dropdown = ft.Dropdown(
                label="Микрофон",
                options=[ft.dropdown.Option(mic) for mic in get_unique_microphones(recorder)],
                value=settings.get("microphone", "")
            )

            path_input = ft.TextField(
                label="Путь сохранения",
                value=settings.get("save_path", ""),
                bgcolor="#2e2e2e",
                color="white"
            )

            api_key_input = ft.TextField(
                label="API ключ",
                value=settings.get("api_key", ""),
                bgcolor="#2e2e2e",
                color="white"
            )

            save_button = ft.ElevatedButton(
                text="Сохранить",
                icon=ft.icons.SAVE,
                bgcolor="#2e2e2e",
                color="white",
                on_click=save_and_close,
            )

            settings_dialog = ft.AlertDialog(
                title=ft.Text("Настройки"),
                content=ft.Column([mic_dropdown, path_input, api_key_input], spacing=10),
                actions=[save_button],
                on_dismiss=lambda e: restore_window_size()
            )

            page.dialog = settings_dialog
            settings_dialog.open = True
            page.update()

        def restore_window_size():
            page.window_width = 300
            page.window_height = 400
            page.update()

        def toggle_recording():
            nonlocal is_recording, start_time
            if not settings.get("microphone") or not settings.get("save_path") or not settings.get("api_key"):
                show_message("Ошибка", "Пожалуйста, убедитесь, что выбран микрофон, указано место для сохранения и введен API-ключ.")
                return

            if not is_recording:
                try:
                    recorder.start_recording(int(settings.get("microphone")), settings.get("save_path"))
                except Exception as e:
                    show_message("Ошибка записи", str(e))
                    return

                start_time = time.time()
                is_recording = True
                record_button.text = "Остановить запись"
                record_button.bgcolor = "#5555ff"
                start_timer()
                start_waveform()
            else:
                is_recording = False
                record_button.text = "Начать запись"
                record_button.bgcolor = "#ff5555"
                recorder.stop_recording()
                success, message = upload_file(recorder.output_file)
                show_message("Отправка завершена" if success else "Ошибка отправки", message)
                timer_label.value = "00:00:00"
                page.update()

        def start_timer():
            if is_recording:
                elapsed_time = int(time.time() - start_time)
                timer_label.value = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
                page.update()
                threading.Timer(1, start_timer).start()

        def start_waveform():
            if is_recording:
                volume = recorder.get_volume_level()
                for i, bar in enumerate(bars):
                    if volume > (i + 1) * 0.05:  # Увеличиваем чувствительность шкалы
                        bar.bgcolor = "#00ff00"
                    else:
                        bar.bgcolor = "#555555"
                page.update()
                threading.Timer(0.1, start_waveform).start()

        def show_message(title, message):
            dialog = ft.AlertDialog(
                title=ft.Text(title),
                content=ft.Text(message),
                actions=[ft.TextButton("OK", on_click=lambda e: close_dialog(dialog))],
            )
            page.dialog = dialog
            dialog.open = True
            page.update()

        def close_dialog(dialog):
            dialog.open = False
            page.update()

        def get_unique_microphones(recorder):
            """Функция для получения уникальных микрофонов без дублирования."""
            unique_mics = {}
            for mic in recorder.get_microphones():
                name = mic.split('(')[0].strip()
                if name not in unique_mics:
                    unique_mics[name] = mic
            return unique_mics.values()

    ft.app(target=main)
