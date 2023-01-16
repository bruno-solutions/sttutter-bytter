from pathlib import Path

configuration_mutable = {
    "output_file_type": "wav",
    "work_root": str(Path.cwd()),
    "log_debug": True,
    "log_info": True,
    "log_warning": True,
    "log_error": True,
    "log_to_console": True,
    "log_file_separator": "-",
    "channels": 2,  # stereo
    "sample_width": 2,  # bytes, CD Quality
    "frame_rate": 44100,  # hz, CD quality
    "downloader_module": "aria2c",
    "clips_per_stage": 10,
    "cluster_window_milliseconds": 75,
    "detection_window_milliseconds": 10,
    "low_threshold": -20.0,
    "drift_decibels": 0.1,
    "clip_size_milliseconds": 9000,
    "beat_count": 4,
    "attack_milliseconds": 50,
    "decay_milliseconds": 50,
    "pad_duration_milliseconds": 250,
    "fade_in_milliseconds": 500,
    "fade_out_milliseconds": 500
}

logic_mutable: [{}] = []
