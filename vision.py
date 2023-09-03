from typing import List, Tuple, Union

import cv2
import numpy as np
from cv2.typing import MatLike

# create blob detector for detecting circles

params = cv2.SimpleBlobDetector_Params()
params.filterByConvexity = True
params.minConvexity = 0.7
params.filterByCircularity = True
params.minCircularity = 0.7
params.filterByArea = True
params.minArea = 400
detector = cv2.SimpleBlobDetector_create(params)


def process_image(frame: MatLike) -> Union[Tuple[Tuple[float, float], float, MatLike], None]:
    """
    :param frame: OpenCV frame
    :return: if a shape matching the criteria has been detected, a tuple
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    keypoints: List[cv2.KeyPoint] = detector.detect(gray)
    if len(keypoints) > 0:
        keypoint = max(keypoints, key=lambda kp: kp.size)
        cv2.circle(frame, [int(xi) for xi in keypoint.pt], radius=50, color=(255, 0, 0), thickness=4)
        frame_height, frame_width = frame.shape[:2]
        px = keypoint.pt[0] / frame_width - 0.5
        py = keypoint.pt[1] / frame_height - 0.5
        return (px, py), keypoint.size, cv2.drawKeypoints(frame, keypoints, np.array([]), (0, 255, 0),
                                                          cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    else:
        return None
