import colorsys
import os
import shutil
from os.path import join
from random import random, shuffle
from subprocess import Popen

import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from PIL.ImageDraw import Draw
from django.conf import settings
from unidecode import unidecode

from app.models import UploadedSong
from app.pca import pca, normalize

rgb_to_hsv = np.vectorize(colorsys.rgb_to_hsv)
hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)


class VideoMaker:
    frame_rate = 30

    def __init__(self, song: UploadedSong):
        self.song = song

        audio_data, self.sample_rate = librosa.load(self.song.file.path)
        self.hop_length = int(self.sample_rate // self.frame_rate)

        y_harmonic, y_percussive = librosa.effects.hpss(audio_data)
        self.chromatogram = librosa.feature.chroma_cqt(y=y_harmonic, sr=self.sample_rate, hop_length=self.hop_length)

        samples_per_frame = len(audio_data) // len(self.chromatogram[0])
        volumes = [np.max(np.abs(audio_data[i:i + samples_per_frame]))
                   for i in range(0, len(audio_data), samples_per_frame)]
        volumes = np.array(list(self.average_array(volumes, r=60)))
        max_peak = np.max(volumes)
        self.volumes = volumes / max_peak

    def create_video(self):
        averaged = self.get_averaged_chromatogram()
        colors = self.get_colors(averaged)
        colors = self.shuffle_colors(colors)

        if settings.DEBUG:
            self.show_overview(colors)

        return self.make_video(averaged, colors)

    def average_array(self, array, r=15):
        for i in range(len(array)):
            around = array[max(0, i - r):i + 1 + r]
            yield np.mean([np.mean(around), np.median(around)])

    def get_averaged_chromatogram(self):
        averaged = [list(self.average_array(tones)) for tones in self.chromatogram]
        return np.transpose(averaged)

    def get_colors(self, chromatogram):
        return np.around(normalize(pca(chromatogram, dimensions=3)[0]) * 255).astype(int)

    def shuffle_colors(self, colors):
        r, g, b = np.transpose(colors)
        h, s, v = rgb_to_hsv(r, g, b)
        h += random()
        h %= 1
        r, g, b = hsv_to_rgb(h, s, v)
        colors = [r, g, b]
        shuffle(colors)
        return np.array(colors).T.round().astype(int)

    def show_overview(self, colors):
        overview_height = int(len(colors) / 1.6)
        overview = Image.new("RGB", (len(colors), overview_height))

        for i, color in enumerate(colors):
            for o in range(overview_height):
                overview.putpixel((i, o), tuple(color))

        plt.figure(figsize=(10, 6))

        plt.subplot(2, 1, 1)
        plt.title(f'Colors of {self.song.name}')
        plt.imshow(np.asarray(overview), interpolation='antialiased', aspect='auto')

        plt.subplot(2, 1, 2)
        plt.title('Chroma')
        librosa.display.specshow(self.chromatogram, sr=self.sample_rate, hop_length=self.hop_length, y_axis='chroma',
                                 vmin=0.0, vmax=1.0, x_axis='time')

        plt.tight_layout()
        plt.show()

    # for c in range(3):
    #     s = 0
    #     s2 = 0
    #     for tone in range(12):
    #         s += coefs[c][tone] * cc[tone]
    #         s2 += (coefs[c][tone] * cc2[tone] + coefs[c][tone] * cc[tone]) / 2
    #     color.append(int(s))
    #     color2.append(int(s2))
    #
    # color = tuple(color2)
    def make_video(self, chromatogram, colors):
        images_path = join(settings.BASE_DIR, 'images')
        try:
            shutil.rmtree(images_path, ignore_errors=True)
        except FileNotFoundError:
            pass
        os.mkdir(images_path)

        name = unidecode(self.song.name).lower()

        for i, (frame, color, volume) in enumerate(zip(chromatogram, colors, self.volumes)):
            w, h = 426, 240
            image = Image.new("RGB", (w, h), (0, 0, 0))
            draw = Draw(image)
            ww, hh = draw.textsize(name)
            draw.text(((w - ww) // 2, (h - hh) // 2), name)
            line = [0, h]
            for ii, tone in enumerate(frame):
                line.append(int((ii + 1) * w / 13))
                line.append(h - 60 * tone * (0.5 + volume / 2))
            line += [w, h]
            draw.line(line, width=1, fill=tuple(color))
            image.save(join(images_path, f'img{i:09}.png'))

        video_path = join(settings.BASE_DIR, 'video.mp4')
        process = Popen(['ffmpeg',
                         '-y',
                         '-r', f'{self.frame_rate}',
                         '-i', f'{join(images_path, "img%09d.png")}',
                         '-i', f'{self.song.file.path}',
                         video_path])
        process.wait()
        return video_path

    # coefs = []
    # for c in range(3):
    #     r1 = [line[0] for line in data[name]]
    #     r2 = [line[1][c] for line in data[name]]
    #
    #     m = np.linalg.lstsq(r1, r2, rcond=None)[0]
    #     coefs.append(m)
    # print(coefs)
