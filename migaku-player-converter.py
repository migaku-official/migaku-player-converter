import os
import platform
import pprint
import sys
from pathlib import Path
from typing import Any

import ffmpeg
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QVBoxLayout,
)

save_audio_index = False
saved_audio_index = 0

confirmed_hevc_codec_conversion = False

app = QApplication([])


ffprobe_command = "ffprobe"
ffmpeg_command = "ffmpeg"
if platform.system() == "Windows":
    ffprobe_command = "ffprobe.exe"
    ffmpeg_command = "ffmpeg.exe"


class LanguageSelector(QDialog):
    def __init__(self, streams: list[dict[str, Any]]):
        super().__init__()
        self.setWindowTitle("Migaku Audio Stream Selector")
        self.setWindowFlags(Qt.Dialog)

        message = QLabel("Please select the appropriate audio stream")
        self.combobox = QComboBox(self)
        self.combo_dict = {}
        for stream in streams:
            title = stream["tags"]["title"] if "title" in stream["tags"] else ""
            language = (
                stream["tags"]["language"] if "language" in stream["tags"] else ""
            )
            dict_key = ""
            if title and language:
                dict_key = title + " - " + language
            else:
                dict_key = title if title else language
            self.combo_dict[dict_key] = stream["index"]
        for key in self.combo_dict:
            self.combobox.addItem(key)
        qbuttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(qbuttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(message)
        self.layout.addWidget(self.combobox)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


def check_if_video_file(filename):
    try:
        probe = ffmpeg.probe(filename, cmd=ffprobe_command)
    except ffmpeg.Error:
        # print(e.stderr)
        return False
    video_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "video"), None
    )
    if video_stream is None:
        return False
    return True


def decide_on_audio_stream(streams: list[dict[str, Any]]):
    valid_streams = []
    for stream in streams:
        if stream["codec_type"] == "audio":
            valid_streams.append(stream)
    if len(valid_streams) == 1:
        return valid_streams[0]["index"]
    else:
        no_commentary_streams: list[dict[str, Any]] = []
        for stream in valid_streams:
            if (
                "title" not in stream["tags"]
                or "commentary" not in stream["tags"]["title"].lower()
            ):
                no_commentary_streams.append(stream)

        if len(no_commentary_streams) == 1:
            return no_commentary_streams[0]["index"]
        else:
            global saved_audio_index
            global save_audio_index
            if save_audio_index:
                print(f"used saved index {saved_audio_index}")
                return saved_audio_index
            else:
                language_select_dialog = LanguageSelector(valid_streams)
                execed = language_select_dialog.exec()
                if execed:
                    selected_stream = language_select_dialog.combobox.currentText()
                    stream_index = language_select_dialog.combo_dict[selected_stream]
                    saved_audio_index = stream_index
                    save_audio_index = True
                    return stream_index
                else:
                    sys.exit(0)


def convert_to_migaku_video(input_file):
    streams = ffmpeg.probe(input_file, cmd=ffprobe_command)["streams"]
    keep_video = False
    keep_audio = False
    audio_index = decide_on_audio_stream(streams)
    filename = Path(input_file)
    output_file = filename.with_suffix(".migaku_player_ready.mp4")
    for stream in streams:
        if stream["codec_type"] == "video":
            if stream["codec_name"] == "h264":
                keep_video = True
            if stream["codec_name"] == "hevc":
                global confirmed_hevc_codec_conversion
                if not confirmed_hevc_codec_conversion:
                    button = QMessageBox.warning(
                        None,
                        "Migaku Warning Dialog",
                        """
The video codec is incompatible with your browser.
Converting it may take a long time and take up significant resources.
Do you want to continue?""",
                        buttons=QMessageBox.Yes | QMessageBox.Cancel,
                        defaultButton=QMessageBox.Yes,
                    )
                    if button == QMessageBox.Cancel:
                        sys.exit(0)
                    else:
                        confirmed_hevc_codec_conversion = True
            print(
                f"video codec is {stream['codec_name']}, will {'' if keep_video else 'not '}be kept"
            )

        if stream["codec_type"] == "audio" and stream["index"] == audio_index:
            if stream["codec_name"] in ["aac", "mp3", "opus", "flac"]:
                keep_audio = True
            print(
                f"audio codec is {stream['codec_name']}, will {'' if keep_audio else 'not '}be kept"
            )

    ffmpeg_args = {"filename": output_file, "strict": "-2"}
    if keep_audio:
        ffmpeg_args["acodec"] = "copy"
    if keep_video:
        ffmpeg_args["vcodec"] = "copy"

    input = ffmpeg.input(input_file)
    output_video = input["v:0"]
    output_audio = input[str(audio_index)]

    ffmpeg.output(output_video, output_audio, **ffmpeg_args).overwrite_output().run(
        cmd=ffmpeg_command
    )


def print_ffprobe(input_file):
    pp = pprint.PrettyPrinter(indent=4, width=178, sort_dicts=False)
    streams = ffmpeg.probe(input_file)["streams"]
    for stream in streams:
        if stream["codec_type"] == "video":
            pp.pprint(stream)
        if stream["codec_type"] == "audio":
            pp.pprint(stream)


current_dir_files = os.listdir(os.curdir)
current_dir_video_files = list(filter(check_if_video_file, current_dir_files))

for file in current_dir_video_files:
    convert_to_migaku_video(file)


# pp.pprint(info["streams"])
