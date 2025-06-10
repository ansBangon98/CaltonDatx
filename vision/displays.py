import cv2

class Caption():
    def _display_caption(self, caption, x1, y1, frame):
        font_scale = 0.6
        text_color = (0, 255, 0)
        bg_color = (0, 0, 0)
        padding = 5
        font = cv2.FONT_HERSHEY_SIMPLEX
        (text_width, text_height), _ = cv2.getTextSize(caption, font, font_scale, thickness=1)
        box_x1 = x1 + 5
        box_y1 = y1 + 5
        box_x2 = box_x1 + text_width + 2 * padding
        box_y2 = box_y1 + text_height + 2 * padding
        cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), bg_color, thickness=-1)
        text_x = box_x1 + padding
        text_y = box_y1 + text_height + padding - 2
        cv2.putText(frame, caption, (text_x, text_y), font, font_scale, text_color, thickness=1, lineType=cv2.LINE_AA)
        return frame

class Track():
    def _create_body_box(self, frame, x1, y1, x2, y2):
        rectangle_color = (255, 0, 255)
        line_color = (0, 255, 0)
        line_width = 10
        line_tickness = 2
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), rectangle_color, 1)

        cv2.line(frame, (x1, y1), (x1 + line_width, y1), line_color, thickness=line_tickness)  # Left-Top Line
        cv2.line(frame, (x1, y1), (x1, y1 + line_width), line_color, thickness=line_tickness)  # Lef-Side

        cv2.line(frame, (x2, y1), (x2 - line_width, y1), line_color, thickness=line_tickness)  # Right-Top Line
        cv2.line(frame, (x2, y1), (x2, y1 + line_width), line_color, thickness=line_tickness)  # Lef-Side

        cv2.line(frame, (x1, y2), (x1 + line_width, y2), line_color, thickness=line_tickness)  # Left-Boto Line
        cv2.line(frame, (x1, y2), (x1, y2 - line_width), line_color, thickness=line_tickness)  # Lef-Side

        cv2.line(frame, (x2, y2), (x2 - line_width, y2), line_color, thickness=line_tickness)  # Right-Top Line
        cv2.line(frame, (x2, y2), (x2, y2 - line_width), line_color, thickness=line_tickness)  # Lef-Side
        return frame

    def _create_face_box(self, frame, x1, y1, x2, y2):
        thick = 2
        thick_width = 15
        line_color = (0, 255, 0)

        cv2.line(frame, (x1, y1), (x1 + thick_width, y1), line_color, thick)  # Left-Top Line
        cv2.line(frame, (x1, y1), (x1, y1 + thick_width), line_color, thick)  # Left-Side

        cv2.line(frame, (x2, y1), (x2 - thick_width, y1), line_color, thick)  # Right-Top Line
        cv2.line(frame, (x2, y1), (x2, y1 + thick_width), line_color, thick)  # Right-Side

        cv2.line(frame, (x1, y2), (x1 + thick_width, y2), line_color, thick)  # Left-Boto Line
        cv2.line(frame, (x1, y2), (x1, y2 - thick_width), line_color, thick)  # Left-Side

        cv2.line(frame, (x2, y2), (x2 - thick_width, y2), line_color, thick)  # Right-Top Line
        cv2.line(frame, (x2, y2), (x2, y2 - thick_width), line_color, thick)  # Right-Side
        return frame