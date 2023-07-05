from pathlib import Path
import re
from dataclasses import dataclass
import subprocess
from typing import List, Optional
from enum import Enum


class TrackType(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    SUBTITLES = "subtitles"


@dataclass
class VideoProps:
    pixel_width: int
    pixel_height: int
    display_width: int
    display_height: int


@dataclass
class AudioProps:
    sampling_frequency: int
    channels: int
    output_sampling_frequency: int


@dataclass
class Track:
    track_number: int
    track_uid: str
    track_type: TrackType
    codec_id: str
    language: str
    default_duration: Optional[str] = None
    video_props: Optional[VideoProps] = None
    audio_props: Optional[AudioProps] = None

    def is_language_set(self) -> bool:
        return self.language.lower() != "und"

    def __str__(self) -> str:
        return f"Track {self.track_number} ({self.track_type}): {self.language}"


@dataclass
class MkvInfo:
    file_path: Path
    tracks: List[Track]

    def get_audio_tracks(self) -> List[Track]:
        audio_tracks = []
        for track in self.tracks:
            if track.track_type == TrackType.AUDIO:
                audio_tracks.append(track)
        return audio_tracks

    def get_subtitle_tracks(self) -> List[Track]:
        subtitle_tracks = []
        for track in self.tracks:
            if track.track_type == TrackType.SUBTITLES:
                subtitle_tracks.append(track)
        return subtitle_tracks

    def __str__(self) -> str:
        tracks_str = "\n".join(str(track) for track in self.tracks)
        return f"{self.file_path}:\n{tracks_str}"


def parse_tracks(text: str) -> List[Track]:
    tracks = []
    track_matches = re.findall(r"\+ Track\n(?:\|  .+\n)+", text)
    if len(track_matches) == 0:
        print("No tracks found.")
        return tracks
    for track_match in track_matches:
        track_number_match_1 = re.search(r"Track number: \d+ \(.+?(\d+)\)", track_match)
        if track_number_match_1 is not None:
            track_number = int(track_number_match_1.group(1))
        else:
            track_number_match_2 = re.search(r"Track number: (\d+)", track_match)
            if track_number_match_2 is None:
                print("No track number found.")
                continue
            track_number = int(track_number_match_2.group(1))
        track_uid_match = re.search(r"Track UID: (\d+)", track_match)
        if track_uid_match is None:
            print("No track uid found.")
            continue
        track_uid = track_uid_match.group(1)
        track_type_match = re.search(r"Track type: ([a-z]+)", track_match)
        if track_type_match is None:
            print("No track type found.")
            continue
        track_type = TrackType(track_type_match.group(1))
        codec_id_match = re.search(r"Codec ID: (\w+)", track_match)
        if codec_id_match is None:
            print("No codec id found.")
            continue
        codec_id = codec_id_match.group(1)
        default_duration_match = re.search(r"Default duration: (.+)", track_match)
        default_duration = (
            default_duration_match.group(1) if default_duration_match else None
        )
        language_match = re.search(r"Language.+: (\w+)", track_match)
        language = language_match.group(1) if language_match else "und"

        if track_type == TrackType.VIDEO:
            pixel_width_match = re.search(r"Pixel width: (\d+)", track_match)
            if pixel_width_match is None:
                print("No pixel width found.")
                continue
            pixel_width = int(pixel_width_match.group(1))
            pixel_height_match = re.search(r"Pixel height: (\d+)", track_match)
            if pixel_height_match is None:
                print("No pixel height found.")
                continue
            pixel_height = int(pixel_height_match.group(1))
            display_width_match = re.search(r"Display width: (\d+)", track_match)
            if display_width_match is None:
                print("No display width found.")
                continue
            display_width = int(display_width_match.group(1))
            display_height_match = re.search(r"Display height: (\d+)", track_match)
            if display_height_match is None:
                print("No display height found.")
                continue
            display_height = int(display_height_match.group(1))

            video_props = VideoProps(
                pixel_width=pixel_width,
                pixel_height=pixel_height,
                display_width=display_width,
                display_height=display_height,
            )
        else:
            video_props = None

        if track_type == TrackType.AUDIO:
            sampling_frequency_match = re.search(
                r"Sampling frequency: (\d+)", track_match
            )
            if sampling_frequency_match is None:
                print("No sampling frequency found.")
                continue
            sampling_frequency = int(sampling_frequency_match.group(1))
            channels_match = re.search(r"Channels: (\d+)", track_match)
            if channels_match is None:
                print("No channels found.")
                continue
            channels = int(channels_match.group(1))
            output_sampling_frequency_match = re.search(
                r"Output sampling frequency: (\d+)", track_match
            )
            if output_sampling_frequency_match is None:
                print("No output sampling frequency found.")
                continue
            output_sampling_frequency = int(output_sampling_frequency_match.group(1))

            audio_props = AudioProps(
                sampling_frequency=sampling_frequency,
                channels=channels,
                output_sampling_frequency=output_sampling_frequency,
            )
        else:
            audio_props = None

        tracks.append(
            Track(
                track_number=track_number,
                track_uid=track_uid,
                track_type=track_type,
                codec_id=codec_id,
                language=language,
                default_duration=default_duration,
                video_props=video_props,
                audio_props=audio_props,
            )
        )

    return tracks


def get_mkv_info(file_path: Path) -> MkvInfo:
    mkvinfo_output = subprocess.check_output(
        ["mkvinfo", str(file_path)], stderr=subprocess.STDOUT
    )
    mkvinfo_text = mkvinfo_output.decode("utf-8")
    tracks = parse_tracks(mkvinfo_text)
    return MkvInfo(file_path=file_path, tracks=tracks)
