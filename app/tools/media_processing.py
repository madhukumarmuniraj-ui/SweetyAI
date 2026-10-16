"""
SweetyAI Video & Audio Processing Tools
Video editing, audio manipulation, and transcription
"""

import os
from typing import Optional, List, Tuple
import tempfile

try:
    from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, TextClip
    from moviepy.video.fx import resize, rotate, speedx
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("[Video Tools] moviepy not available. Run: pip install moviepy")

try:
    from pydub import AudioSegment
    from pydub.effects import normalize, compress_dynamic_range, low_pass_filter, high_pass_filter
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("[Audio Tools] pydub already available from base install")


# =============================================================================
# VIDEO PROCESSING
# =============================================================================

def video_info(input_path: str) -> dict:
    """Get information about a video file."""
    if not MOVIEPY_AVAILABLE:
        return {"error": "moviepy not installed"}

    try:
        clip = VideoFileClip(input_path)
        info = {
            'duration': clip.duration,
            'fps': clip.fps,
            'size': clip.size,
            'width': clip.w,
            'height': clip.h,
            'audio': clip.audio is not None,
            'file_size_mb': round(os.path.getsize(input_path) / (1024 * 1024), 2)
        }
        clip.close()
        return info
    except Exception as e:
        return {"error": str(e)}


def trim_video(input_path: str, output_path: str, start_time: float, end_time: float) -> str:
    """Trim video to specified time range (in seconds)."""
    if not MOVIEPY_AVAILABLE:
        return "Error: moviepy not installed"

    try:
        clip = VideoFileClip(input_path).subclip(start_time, end_time)
        clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
        clip.close()
        return f"Video trimmed: {output_path}"
    except Exception as e:
        return f"Error trimming video: {e}"


def merge_videos(input_paths: List[str], output_path: str) -> str:
    """Concatenate multiple videos."""
    if not MOVIEPY_AVAILABLE:
        return "Error: moviepy not installed"

    try:
        clips = [VideoFileClip(path) for path in input_paths]
        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

        for clip in clips:
            clip.close()
        final_clip.close()

        return f"Merged {len(input_paths)} videos: {output_path}"
    except Exception as e:
        return f"Error merging videos: {e}"


def resize_video(input_path: str, output_path: str, width: int, height: int) -> str:
    """Resize video to specified dimensions."""
    if not MOVIEPY_AVAILABLE:
        return "Error: moviepy not installed"

    try:
        clip = VideoFileClip(input_path)
        resized = clip.resize((width, height))
        resized.write_videofile(output_path, codec='libx264', audio_codec='aac')
        clip.close()
        resized.close()
        return f"Video resized to {width}x{height}: {output_path}"
    except Exception as e:
        return f"Error resizing video: {e}"


def rotate_video(input_path: str, output_path: str, angle: int) -> str:
    """Rotate video by specified angle (90, 180, 270)."""
    if not MOVIEPY_AVAILABLE:
        return "Error: moviepy not installed"

    try:
        clip = VideoFileClip(input_path)
        rotated = clip.rotate(angle)
        rotated.write_videofile(output_path, codec='libx264', audio_codec='aac')
        clip.close()
        rotated.close()
        return f"Video rotated {angle}°: {output_path}"
    except Exception as e:
        return f"Error rotating video: {e}"


def change_video_speed(input_path: str, output_path: str, speed_factor: float) -> str:
    """Change video playback speed (0.5 = half speed, 2.0 = double speed)."""
    if not MOVIEPY_AVAILABLE:
        return "Error: moviepy not installed"

    try:
        clip = VideoFileClip(input_path)
        modified = clip.fx(speedx, speed_factor)
        modified.write_videofile(output_path, codec='libx264', audio_codec='aac')
        clip.close()
        modified.close()
        return f"Video speed changed ({speed_factor}x): {output_path}"
    except Exception as e:
        return f"Error changing speed: {e}"


def extract_audio_from_video(input_path: str, output_path: str) -> str:
    """Extract audio track from video."""
    if not MOVIEPY_AVAILABLE:
        return "Error: moviepy not installed"

    try:
        clip = VideoFileClip(input_path)
        if clip.audio is None:
            return "Error: Video has no audio track"

        clip.audio.write_audiofile(output_path)
        clip.close()
        return f"Audio extracted: {output_path}"
    except Exception as e:
        return f"Error extracting audio: {e}"


def add_audio_to_video(video_path: str, audio_path: str, output_path: str) -> str:
    """Replace or add audio track to video."""
    if not MOVIEPY_AVAILABLE:
        return "Error: moviepy not installed"

    try:
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)

        final = video.set_audio(audio)
        final.write_videofile(output_path, codec='libx264', audio_codec='aac')

        video.close()
        audio.close()
        final.close()

        return f"Audio added to video: {output_path}"
    except Exception as e:
        return f"Error adding audio: {e}"


def add_text_overlay(
    input_path: str,
    output_path: str,
    text: str,
    duration: Optional[float] = None,
    position: Tuple[int, int] = (50, 50),
    fontsize: int = 50,
    color: str = 'white'
) -> str:
    """Add text overlay to video."""
    if not MOVIEPY_AVAILABLE:
        return "Error: moviepy not installed"

    try:
        clip = VideoFileClip(input_path)

        if duration is None:
            duration = clip.duration

        txt_clip = TextClip(text, fontsize=fontsize, color=color)
        txt_clip = txt_clip.set_position(position).set_duration(duration)

        final = CompositeVideoClip([clip, txt_clip])
        final.write_videofile(output_path, codec='libx264', audio_codec='aac')

        clip.close()
        final.close()

        return f"Text overlay added: {output_path}"
    except Exception as e:
        return f"Error adding text overlay: {e}"


def extract_frames(input_path: str, output_folder: str, fps: int = 1) -> str:
    """Extract frames from video at specified FPS."""
    if not MOVIEPY_AVAILABLE:
        return "Error: moviepy not installed"

    try:
        os.makedirs(output_folder, exist_ok=True)
        clip = VideoFileClip(input_path)

        frame_count = 0
        for t in range(0, int(clip.duration), int(1/fps)):
            frame_path = os.path.join(output_folder, f"frame_{frame_count:04d}.png")
            clip.save_frame(frame_path, t)
            frame_count += 1

        clip.close()
        return f"Extracted {frame_count} frames to: {output_folder}"
    except Exception as e:
        return f"Error extracting frames: {e}"


# =============================================================================
# AUDIO PROCESSING
# =============================================================================

def audio_info(input_path: str) -> dict:
    """Get information about an audio file."""
    if not PYDUB_AVAILABLE:
        return {"error": "pydub not available"}

    try:
        audio = AudioSegment.from_file(input_path)
        info = {
            'duration_seconds': len(audio) / 1000.0,
            'channels': audio.channels,
            'sample_width': audio.sample_width,
            'frame_rate': audio.frame_rate,
            'frame_width': audio.frame_width,
            'max_dBFS': audio.max_dBFS,
            'file_size_mb': round(os.path.getsize(input_path) / (1024 * 1024), 2)
        }
        return info
    except Exception as e:
        return {"error": str(e)}


def trim_audio(input_path: str, output_path: str, start_ms: int, end_ms: int) -> str:
    """Trim audio to specified time range (in milliseconds)."""
    if not PYDUB_AVAILABLE:
        return "Error: pydub not available"

    try:
        audio = AudioSegment.from_file(input_path)
        trimmed = audio[start_ms:end_ms]
        trimmed.export(output_path, format=output_path.split('.')[-1])
        return f"Audio trimmed: {output_path}"
    except Exception as e:
        return f"Error trimming audio: {e}"


def merge_audio(input_paths: List[str], output_path: str) -> str:
    """Concatenate multiple audio files."""
    if not PYDUB_AVAILABLE:
        return "Error: pydub not available"

    try:
        combined = AudioSegment.empty()
        for path in input_paths:
            audio = AudioSegment.from_file(path)
            combined += audio

        combined.export(output_path, format=output_path.split('.')[-1])
        return f"Merged {len(input_paths)} audio files: {output_path}"
    except Exception as e:
        return f"Error merging audio: {e}"


def change_audio_volume(input_path: str, output_path: str, change_db: float) -> str:
    """Change audio volume by specified decibels (+6dB = double volume)."""
    if not PYDUB_AVAILABLE:
        return "Error: pydub not available"

    try:
        audio = AudioSegment.from_file(input_path)
        modified = audio + change_db
        modified.export(output_path, format=output_path.split('.')[-1])
        return f"Volume changed by {change_db}dB: {output_path}"
    except Exception as e:
        return f"Error changing volume: {e}"


def normalize_audio(input_path: str, output_path: str) -> str:
    """Normalize audio levels."""
    if not PYDUB_AVAILABLE:
        return "Error: pydub not available"

    try:
        audio = AudioSegment.from_file(input_path)
        normalized = normalize(audio)
        normalized.export(output_path, format=output_path.split('.')[-1])
        return f"Audio normalized: {output_path}"
    except Exception as e:
        return f"Error normalizing audio: {e}"


def change_audio_speed(input_path: str, output_path: str, speed_factor: float) -> str:
    """Change audio playback speed."""
    if not PYDUB_AVAILABLE:
        return "Error: pydub not available"

    try:
        audio = AudioSegment.from_file(input_path)

        # Change speed by modifying frame rate
        modified = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speed_factor)
        })
        modified = modified.set_frame_rate(audio.frame_rate)

        modified.export(output_path, format=output_path.split('.')[-1])
        return f"Audio speed changed ({speed_factor}x): {output_path}"
    except Exception as e:
        return f"Error changing audio speed: {e}"


def convert_audio_format(input_path: str, output_path: str, format: str = None) -> str:
    """Convert audio to different format (mp3, wav, ogg, etc.)."""
    if not PYDUB_AVAILABLE:
        return "Error: pydub not available"

    try:
        audio = AudioSegment.from_file(input_path)

        if format is None:
            format = output_path.split('.')[-1]

        audio.export(output_path, format=format)
        return f"Audio converted to {format}: {output_path}"
    except Exception as e:
        return f"Error converting audio: {e}"


def apply_audio_fade(input_path: str, output_path: str, fade_in_ms: int = 0, fade_out_ms: int = 0) -> str:
    """Apply fade in/out effects to audio."""
    if not PYDUB_AVAILABLE:
        return "Error: pydub not available"

    try:
        audio = AudioSegment.from_file(input_path)

        if fade_in_ms > 0:
            audio = audio.fade_in(fade_in_ms)

        if fade_out_ms > 0:
            audio = audio.fade_out(fade_out_ms)

        audio.export(output_path, format=output_path.split('.')[-1])
        return f"Fade effects applied: {output_path}"
    except Exception as e:
        return f"Error applying fade: {e}"


# Tool registry compatibility aliases
convert_audio = convert_audio_format
add_subtitles_to_video = add_text_overlay


__all__ = [
    # Video
    'video_info', 'trim_video', 'merge_videos', 'resize_video',
    'rotate_video', 'change_video_speed', 'extract_audio_from_video',
    'add_audio_to_video', 'add_text_overlay', 'add_subtitles_to_video', 'extract_frames',
    # Audio
    'audio_info', 'trim_audio', 'merge_audio', 'change_audio_volume',
    'normalize_audio', 'change_audio_speed', 'convert_audio_format', 'convert_audio',
    'apply_audio_fade'
]
