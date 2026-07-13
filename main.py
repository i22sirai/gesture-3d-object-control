import socket
import cv2
import mediapipe as mp
import math
from hand_gesture import (
    is_pinch,
    get_pinch_center,
    get_index_tip,
    is_index_only
)


UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

cap = cv2.VideoCapture(1)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

base_distance = None
start_scale = 1.0
current_scale = 1.0
is_scaling = False

prev_index_pos = None

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        left_hand = None
        right_hand = None

        move_select = 0
        rotate_mode = 0
        rotate_dx = 0.0
        rotate_dy = 0.0
        scale = current_scale

        h, w, _ = frame.shape

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(
                results.multi_hand_landmarks,
                results.multi_handedness
            ):
                label = handedness.classification[0].label

                # あなたの環境では左右が逆に認識されるため、ここを入れ替えています
                if label == "Right":
                    left_hand = hand_landmarks
                elif label == "Left":
                    right_hand = hand_landmarks

                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

            left_pinch = False
            right_pinch = False

            if left_hand is not None:
                left_pinch = is_pinch(left_hand, w, h)

            if right_hand is not None:
                right_pinch = is_pinch(right_hand, w, h)

            # 左手つまみ：選択・移動
            if left_pinch:
                move_select = 1

            # 右手人差し指のみ：回転
            if right_hand is not None and is_index_only(right_hand, w, h):
                rotate_mode = 1
                index_pos = get_index_tip(right_hand, w, h)

                if prev_index_pos is None:
                    # 回転開始地点を記録
                    prev_index_pos = index_pos

                rotate_dx = index_pos[0] - prev_index_pos[0]
                rotate_dy = index_pos[1] - prev_index_pos[1]

                # 小さな手ブレを無視
                if abs(rotate_dx) < 3:
                    rotate_dx = 0.0
                if abs(rotate_dy) < 3:
                    rotate_dy = 0.0

            else:
                prev_index_pos = None

            # 両手つまみ：拡大縮小
            if left_hand is not None and right_hand is not None and left_pinch and right_pinch:
                lx, ly = get_pinch_center(left_hand, w, h)
                rx, ry = get_pinch_center(right_hand, w, h)

                distance = math.sqrt((rx - lx) ** 2 + (ry - ly) ** 2)

                if not is_scaling:
                    base_distance = distance
                    start_scale = current_scale
                    is_scaling = True

                if base_distance is not None and base_distance > 0:
                    scale = start_scale * (distance / base_distance)
                    scale = max(0.2, min(scale, 5.0))
                    current_scale = scale

            else:
                is_scaling = False
                base_distance = None
                scale = current_scale

        else:
            is_scaling = False
            base_distance = None
            prev_index_pos = None
            scale = current_scale

        message = f"{move_select},{rotate_mode},{rotate_dx:.2f},{rotate_dy:.2f},{scale:.2f}"
        sock.sendto(message.encode("utf-8"), (UDP_IP, UDP_PORT))

        cv2.putText(
            frame,
            f"move:{move_select} rot:{rotate_mode} dx:{rotate_dx:.1f} dy:{rotate_dy:.1f} scale:{scale:.2f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.imshow("Hand Gesture", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            print("ESC pressed. Exiting...")
            break

except KeyboardInterrupt:
    print("Keyboard Interrupt")

finally:
    print("Releasing camera and closing windows...")
    cap.release()
    cv2.destroyAllWindows()
    sock.close()