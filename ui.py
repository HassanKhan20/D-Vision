import cv2


class Overlay:
    @staticmethod
    def draw_overlays(frame, face_locations, matches):
        for box, (person, conf) in zip(face_locations, matches):
            if not person or conf < 0.91:
                continue  # No green box for unsure matches

            top, right, bottom, left = box
            name = person.name
            seen = f"Seen {person.seen_count}x"
            last_seen = f"Last seen: {person.last_seen or '--'}"

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            cv2.putText(frame, name, (left, top - 10),
                        cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 0), 2)

            cv2.putText(frame, seen, (left, bottom + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)

            cv2.putText(frame, last_seen, (left, bottom + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 255), 1)

        return frame

    @staticmethod
    def draw_instructions(frame, text):
        cv2.putText(frame, text, (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    @staticmethod
    def draw_status_message(frame, text):
        cv2.putText(frame, text, (20, 400),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
