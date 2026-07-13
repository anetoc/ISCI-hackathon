from scripts.validate_submission_video import assess_video


def _probe(*, duration: float = 150.0, audio: bool = True) -> dict:
    streams = [
        {
            "codec_type": "video",
            "codec_name": "h264",
            "width": 1920,
            "height": 1080,
            "r_frame_rate": "30/1",
        }
    ]
    if audio:
        streams.append(
            {
                "codec_type": "audio",
                "codec_name": "aac",
                "sample_rate": "48000",
                "channels": 2,
            }
        )
    return {"streams": streams, "format": {"duration": str(duration)}}


def test_submission_video_contract_accepts_audible_full_hd_export() -> None:
    assert assess_video(_probe(), mean_volume_db=-22.0, max_volume_db=-3.0) == []


def test_submission_video_contract_rejects_silent_audio_bed() -> None:
    failures = assess_video(_probe(), mean_volume_db=-91.0, max_volume_db=-91.0)
    assert any("mean audio level" in failure for failure in failures)
    assert any("peak audio level" in failure for failure in failures)


def test_submission_video_contract_rejects_overlong_or_audio_free_export() -> None:
    failures = assess_video(_probe(duration=181.0, audio=False), None, None)
    assert any("duration" in failure for failure in failures)
    assert "audio stream is missing" in failures
