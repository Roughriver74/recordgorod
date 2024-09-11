import sounddevice as sd
import numpy as np
import wave
import os
from datetime import datetime

class Recorder:
    def __init__(self):
        self.is_recording = False
        self.output_file = ""
        self.stream = None
        self.frames = []
        self.amplification_factor = 2.0  # Коэффициент усиления

    def start_recording(self, mic_index, save_path):
        if self.is_recording:
            raise RuntimeError("Recording is already in progress.")

        self.output_file = os.path.join(save_path, f"record_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")

        try:
            device_info = sd.query_devices(mic_index, 'input')
            samplerate = 16000  # Пониженная частота дискретизации для уменьшения размера файла
            channels = 1  # Ограничим запись одним каналом
        except Exception as e:
            raise RuntimeError(f"Could not query device: {e}")

        self.stream = sd.InputStream(
            device=mic_index,
            channels=channels,
            samplerate=samplerate,
            callback=self.audio_callback,
            blocksize=1024,  # Устанавливаем размер блока
            dtype='int16',   # Формат данных
            latency='low',   # Уменьшаем задержку
        )

        self.frames = []
        self.is_recording = True

        try:
            self.stream.start()
        except Exception as e:
            raise RuntimeError(f"Could not start recording: {e}")

    def stop_recording(self):
        if not self.is_recording:
            return

        self.is_recording = False
        try:
            self.stream.stop()
            self.stream.close()
        except Exception as e:
            raise RuntimeError(f"Could not stop recording: {e}")

        with wave.open(self.output_file, 'wb') as wf:
            wf.setnchannels(1)  # Один канал (моно)
            wf.setsampwidth(2)  # 16-битная запись
            wf.setframerate(16000)  # Пониженная частота дискретизации
            wf.writeframes(b''.join(self.frames))

    def audio_callback(self, indata, frames, time, status):
        if self.is_recording:
            # Применение усиления к аудио данным
            amplified_data = indata * self.amplification_factor
            amplified_data = np.clip(amplified_data, -32768, 32767)  # Ограничиваем значения для предотвращения искажений
            self.frames.append(amplified_data.astype(np.int16).tobytes())

    def get_volume_level(self):
        if self.is_recording and self.frames:
            data = np.frombuffer(self.frames[-1], dtype=np.int16)
            return np.linalg.norm(data) / 32768.0  # Нормализация уровня звука от 0 до 1
        return 0

    def get_microphones(self):
        devices = sd.query_devices()
        mic_list = []
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                mic_list.append(f"{device['name']} ({i})")
        return mic_list
