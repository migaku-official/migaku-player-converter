import os
import platform
import pprint
import sys
from pathlib import Path
from shutil import which
from typing import Any, Optional

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

ffprobe_command: str = ""
ffmpeg_command: str = ""


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


if os.path.isfile(resource_path("./ffprobe")):
    ffprobe_command = resource_path("./ffprobe")
if os.path.isfile(resource_path("./ffmpeg")):
    ffmpeg_command = resource_path("./ffmpeg")
if platform.system() == "Windows":
    ffprobe_command = "ffprobe.exe"
    ffmpeg_command = "ffmpeg.exe"


if not ffprobe_command:
    if temp_ffprobe_command := which("ffprobe"):
        ffprobe_command = temp_ffprobe_command
if not ffmpeg_command:
    if temp_ffmpeg_command := which("ffmpeg"):
        ffmpeg_command = temp_ffmpeg_command

missing_program = ""
if not ffprobe_command:
    missing_program = "ffprobe"
if not ffmpeg_command:
    missing_program = "ffmpeg"
if missing_program:
    QMessageBox.critical(
        None,
        "Migaku Error Dialog",
        f"It seems {missing_program} is not installed. Please retry after installing",
        buttons=QMessageBox.Ok,
    )
    sys.exit(1)

subtitle_text_codec_names = ["srt", "ass", "ssa", "subrip"]

video_file_endings = [
    ".webm",
    ".mkv",
    ".flv",
    ".flv",
    ".vob",
    ".ogv",
    ".ogg",
    ".drc",
    ".gif",
    ".gifv",
    ".mng",
    ".avi",
    ".MTS",
    ".M2TS",
    ".TS",
    ".mov",
    ".qt",
    ".wmv",
    ".yuv",
    ".rm",
    ".rmvb",
    ".viv",
    ".asf",
    ".amv",
    ".mp4",
    ".m4p",
    ".m4v",
    ".mpg",
    ".mp2",
    ".mpeg",
    ".mpe",
    ".mpv",
    ".mpg",
    ".mpeg",
    ".m2v",
    ".m4v",
    ".svi",
    ".3gp",
    ".3g2",
    ".mxf",
    ".roq",
    ".nsv",
    ".flv",
    ".f4v",
    ".f4p",
    ".f4a",
    ".f4b",
]


class LanguageSelector(QDialog):
    def __init__(self, streams: list[dict[str, Any]]):
        super().__init__()
        self.setWindowTitle("Migaku Audio Stream Selector")
        self.setWindowFlags(Qt.Dialog)

        message = QLabel("Please select the appropriate audio stream")
        self.combobox = QComboBox(self)
        self.combo_dict = {}
        for index, stream in enumerate(streams):
            title = stream["tags"]["title"] if "title" in stream["tags"] else ""
            language = stream["tags"]["language"] if "language" in stream["tags"] else ""

            if not language:
                language = stream["tags"]["HANDLER_NAME"] if "HANDLER_NAME" in stream["tags"] else ""
            dict_key = " - ".join([x for x in [str(index), title, language] if x])
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
    file_extension = Path(filename).suffix
    return any((ext == file_extension for ext in video_file_endings))


def decide_on_audio_stream(streams: list[dict[str, Any]]):
    valid_streams = [stream for stream in streams if stream["codec_type"] == "audio"]

    if len(valid_streams) == 1:
        return valid_streams[0]["index"]
    no_commentary_streams: list[dict[str, Any]] = [
        stream
        for stream in valid_streams
        if "title" not in stream["tags"] or "commentary" not in stream["tags"]["title"].lower()
    ]

    if len(no_commentary_streams) == 1:
        return no_commentary_streams[0]["index"]
    global saved_audio_index
    global save_audio_index
    if save_audio_index:
        print(f"used saved index {saved_audio_index}")
        return saved_audio_index
    else:
        language_select_dialog = LanguageSelector(valid_streams)
        if execed := language_select_dialog.exec():
            selected_stream = language_select_dialog.combobox.currentText()
            stream_index = language_select_dialog.combo_dict[selected_stream]
            saved_audio_index = stream_index
            save_audio_index = True
            return stream_index
        else:
            print("language selection canceled")
            sys.exit(0)


def convert_to_migaku_video(input_file):
    assert ffprobe_command
    streams = ffmpeg.probe(input_file, cmd=ffprobe_command)["streams"]
    keep_video = False
    keep_audio = False
    subtitle_indices = []
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
The video codec "hevc" (also called "h265") contained in your file is incompatible with Migaku Player.
Converting it may take a long time and take up significant resources.
You can circumvent this in the future by downloading files that are encoded with "h264".

Do you want to continue?
                        """,
                        buttons=QMessageBox.Yes | QMessageBox.Cancel,
                        defaultButton=QMessageBox.Yes,
                    )
                    if button == QMessageBox.Cancel:
                        print("video codec canceled")
                        sys.exit(0)
                    else:
                        confirmed_hevc_codec_conversion = True
            print(f"video codec is {stream['codec_name']}, will {'' if keep_video else 'not '}be kept")

        if stream["codec_type"] == "audio" and stream["index"] == audio_index:
            if stream["codec_name"] in ["aac", "mp3", "opus", "flac", "ac3", "vorbis"]:
                keep_audio = True
            print(f"audio codec is {stream['codec_name']}, will {'' if keep_audio else 'not '}be kept")
        if stream["codec_type"] == "subtitle":
            if stream["codec_name"] in subtitle_text_codec_names:
                subtitle_indices.append(stream["index"])
            else:
                print(f"subtitle codec is {stream['codec_name']}, will not be kept")

    ffmpeg_args = {"filename": output_file, "strict": "-2", "scodec": "mov_text"}
    if keep_audio:
        ffmpeg_args["acodec"] = "copy"
    if keep_video:
        ffmpeg_args["vcodec"] = "copy"

    input = ffmpeg.input(input_file)
    output_video = input["v:0"]
    output_audio = input[str(audio_index)]
    output_subtitles = [input[str(index)] for index in subtitle_indices]

    ffmpeg.output(output_video, output_audio, *output_subtitles, **ffmpeg_args).overwrite_output().run(
        cmd=ffmpeg_command
    )
    for subtitle_index in subtitle_indices:
        language = streams[subtitle_index]["tags"]["language"] if "language" in streams[subtitle_index]["tags"] else ""
        suffix = f".{str(subtitle_index)}_{language}.srt"
        subtitle = input[str(subtitle_index)]
        name = filename.with_suffix(suffix)
        print(name)

        ffmpeg.output(subtitle, filename=name).run(cmd=ffmpeg_command)


def print_ffprobe(input_file):
    pp = pprint.PrettyPrinter(indent=4, width=178, sort_dicts=False)
    streams = ffmpeg.probe(input_file, cmd=ffprobe_command)["streams"]
    for stream in streams:
        if stream["codec_type"] == "video":
            pp.pprint(stream)
        if stream["codec_type"] == "audio":
            pp.pprint(stream)
        if stream["codec_type"] == "subtitle":
            pp.pprint(stream)


current_dir_files = os.listdir(os.curdir)
if (
    platform.system() == "Darwin"
    and getattr(sys, "frozen", False)
    and "Contents" in str(os.path.abspath(getattr(sys, "executable", os.curdir)))
):
    bundle_dir = Path(os.path.dirname(os.path.abspath(getattr(sys, "executable", os.curdir))))
    basepath = str(bundle_dir.parent.parent.parent.absolute())
    current_dir_files = os.listdir(basepath)
    current_dir_files = [os.path.join(basepath, file) for file in current_dir_files]
current_dir_video_files = list(filter(check_if_video_file, current_dir_files))
current_dir_video_files_not_converted = [file for file in current_dir_video_files if "migaku_player_ready" not in file]


for file in current_dir_video_files_not_converted:
    # print_ffprobe(file)
    convert_to_migaku_video(file)
