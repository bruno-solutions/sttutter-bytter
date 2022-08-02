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
    "cluster_window_miliseconds": 75,
    "detection_window_miliseconds": 10,
    "low_threshold": -20.0,
    "drift_decibels": 0.1,
    "clip_size_miliseconds": 9000,
    "beat_count": 4,
    "attack_miliseconds": 50,
    "decay_miliseconds": 50,
    "pad_duration_miliseconds": 250,
    "fade_in_miliseconds": 500,
    "fade_out_miliseconds": 500
}

logic_mutable: [{}] = []
