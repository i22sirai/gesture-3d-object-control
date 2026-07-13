import math


def get_point(hand_landmarks, index, w, h):
    lm = hand_landmarks.landmark[index]
    return int(lm.x * w), int(lm.y * h)


def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def is_pinch(hand_landmarks, w, h, threshold=40):
    thumb_tip = get_point(hand_landmarks, 4, w, h)
    index_tip = get_point(hand_landmarks, 8, w, h)
    return distance(thumb_tip, index_tip) < threshold


def get_pinch_center(hand_landmarks, w, h):
    thumb_tip = get_point(hand_landmarks, 4, w, h)
    index_tip = get_point(hand_landmarks, 8, w, h)

    return (
        (thumb_tip[0] + index_tip[0]) / 2,
        (thumb_tip[1] + index_tip[1]) / 2
    )


def get_index_tip(hand_landmarks, w, h):
    return get_point(hand_landmarks, 8, w, h)


def is_index_only(hand_landmarks, w, h):
    index_tip = get_point(hand_landmarks, 8, w, h)
    index_pip = get_point(hand_landmarks, 6, w, h)

    middle_tip = get_point(hand_landmarks, 12, w, h)
    middle_pip = get_point(hand_landmarks, 10, w, h)

    ring_tip = get_point(hand_landmarks, 16, w, h)
    ring_pip = get_point(hand_landmarks, 14, w, h)

    pinky_tip = get_point(hand_landmarks, 20, w, h)
    pinky_pip = get_point(hand_landmarks, 18, w, h)

    index_extended = index_tip[1] < index_pip[1]
    middle_folded = middle_tip[1] > middle_pip[1]
    ring_folded = ring_tip[1] > ring_pip[1]
    pinky_folded = pinky_tip[1] > pinky_pip[1]

    return index_extended and middle_folded and ring_folded and pinky_folded