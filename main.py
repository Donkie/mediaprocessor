import subprocess
from pathlib import Path

from mkvinfo import get_mkv_info


def process_file(input_path: Path, keep_original: bool):
    print(f" ### Processing file: {input_path.name} ### ")

    # Check if the file has embedded subtitles and if the subtitle track already has a
    # language set
    mkv_info = get_mkv_info(input_path)

    # Figure out if we need to update the subtitle language
    update_subtitle_language = True
    subtitle_tracks = mkv_info.get_subtitle_tracks()
    if len(subtitle_tracks) == 0:
        print(f"No subtitle tracks found in: {input_path}")
        update_subtitle_language = False

    if len(subtitle_tracks) > 1:
        print(f"Multiple subtitle tracks found in: {input_path}")
        # Let user pick which one to use
        while True:
            print("Please select which subtitle track to use, or type N to exit:")
            for i, subtitle_track in enumerate(subtitle_tracks):
                print(
                    f"{i}: TID: {subtitle_track.track_number}, "
                    f"Language: {subtitle_track.language}"
                )
            selection = input("Selection: ")
            if selection == "N":
                print("Exiting.")
                return
            try:
                selection = int(selection)
                if selection < 0 or selection >= len(subtitle_tracks):
                    raise ValueError()
                subtitle_tracks = [subtitle_tracks[selection]]
                break
            except ValueError:
                print("Invalid selection.")

    subtitle_track = subtitle_tracks[0]
    if subtitle_track.is_language_set():
        print(
            f'Subtitle language already set. It is set to: "{subtitle_track.language}"'
        )
        update_subtitle_language = False

    # Figure out if we need to update the audio track language
    update_audio_language = True
    audio_tracks = mkv_info.get_audio_tracks()
    if len(audio_tracks) == 0:
        print(f"No audio tracks found in: {input_path}")
        update_audio_language = False

    if len(audio_tracks) > 1:
        print(f"Multiple audio tracks found in: {input_path}")
        update_audio_language = False

    audio_track = audio_tracks[0]
    if audio_track.is_language_set():
        print(f'Audio language already set. It is set to: "{audio_track.language}"')
        update_audio_language = False

    if not update_subtitle_language and not update_audio_language:
        print("Nothing to do.")
        return

    # Backup original file by renaming it
    output_path = input_path.with_suffix(".mkv")
    backup_path = input_path.with_suffix(".mkv.original")
    input_path.rename(backup_path)
    input_path = backup_path

    cmdline = ["mkvmerge", "-o", output_path.as_posix()]
    if update_subtitle_language:
        print("Setting subtitle language to English")
        cmdline += ["--language", f"{subtitle_track.track_number}:eng"]
    if update_audio_language:
        print("Setting audio language to English")
        cmdline += ["--language", f"{audio_track.track_number}:eng"]
    cmdline += [input_path.as_posix()]

    # Merge modified subtitle track with original file
    # print(cmdline)
    subprocess.run(cmdline)

    print("Finished processing file.")

    if update_subtitle_language:
        en_srt_file = output_path.with_suffix(".en.srt")
        if en_srt_file.exists():
            print("Removing en.srt file")
            en_srt_file.unlink()

    if not keep_original:
        print("Removing original file. Use --keep-original to keep it.")
        input_path.unlink()


def process_folder(folder_path: Path, keep_original: bool):
    print(f"Processing folder: {folder_path}")

    for entry in folder_path.rglob("*.mkv"):
        process_file(entry, keep_original)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Please provide a folder path as an argument.")
        sys.exit(1)

    folder_path = Path(sys.argv[1])
    if not folder_path.exists() or not folder_path.is_dir():
        print(f"Folder does not exist: {folder_path}")
        sys.exit(1)

    keep_original = False
    if len(sys.argv) > 2:
        keep_original = sys.argv[2] == "--keep-original"

    process_folder(folder_path, keep_original)
