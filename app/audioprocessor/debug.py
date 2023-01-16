from audioprocessor.normalizer import Normalizer


# https://librosa.org/doc/main/generated/librosa.to_mono.html
# https://librosa.org/doc/main/generated/librosa.onset.onset_strength.html
# https://librosa.org/doc/main/generated/librosa.beat.tempo.html
def debug_get_real_time_tempo(recording):
    import librosa
    monaural_samples = Normalizer.monaural_normalization(recording)
    onset_env = librosa.onset.onset_strength(y=monaural_samples, sr=recording.frame_rate)
    return librosa.beat.tempo(onset_envelope=onset_env, sr=recording.frame_rate, aggregate=None)


# https://librosa.org/doc/main/generated/librosa.to_mono.html
# https://librosa.org/doc/main/generated/librosa.beat.beat_track.html
def debug_get_tempo(recording):
    import librosa
    monaural_samples = Normalizer.monaural_normalization(recording)
    return librosa.beat.beat_track(y=monaural_samples, sr=recording.frame_rate)[0]


# https://librosa.org/doc/main/generated/librosa.to_mono.html
# https://librosa.org/doc/main/generated/librosa.beat.beat_track.html
# https://librosa.org/doc/main/generated/librosa.frames_to_time.html
def debug_get_beat_time(recording):
    import librosa
    monaural_samples = Normalizer.monaural_normalization(recording)
    beats = librosa.beat.beat_track(y=monaural_samples, sr=recording.frame_rate)[1]
    return librosa.frames_to_time(beats, sr=recording.frame_rate)


# https://librosa.org/doc/main/generated/librosa.to_mono.html
# https://librosa.org/doc/main/generated/librosa.yin.html
def debug_get_pitch(recording):
    import librosa
    monaural_samples = Normalizer.monaural_normalization(recording)
    return librosa.yin(monaural_samples, fmin=40, fmax=2200, sr=recording.frame_rate, frame_length=2048)


# https://librosa.org/doc/main/generated/librosa.to_mono.html
# https://librosa.org/doc/main/generated/librosa.amplitude_to_db.html
def debug_get_volume(recording):
    import librosa
    monaural_samples = Normalizer.monaural_normalization(recording)
    return librosa.amplitude_to_db(S=monaural_samples, ref=0)
