import cv2
from typing import List
from pathlib import Path


def sample_frames(
    video_path: str,
    start: float,
    end: float,
    fps: int = 1
) -> List[Path]:
    cap = cv2.VideoCapture(video_path)
    frames = []

    cap.set(cv2.CAP_PROP_POS_MSEC, start * 1000)
    current = start

    while current <= end:
        ret, frame = cap.read()
        if not ret:
            break

        frame_path = Path(f"/tmp/frame_{int(current)}.jpg")
        cv2.imwrite(str(frame_path), frame)
        frames.append(frame_path)

        current += 1 / fps
        cap.set(cv2.CAP_PROP_POS_MSEC, current * 1000)

    cap.release()
    return frames
