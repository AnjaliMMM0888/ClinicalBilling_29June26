import cv2
from pyzbar.pyzbar import decode


def scan_barcode_live():
    cap = cv2.VideoCapture(0)

    barcode_data = None

    while True:
        success, frame = cap.read()
        if not success:
            break

        decoded_objects = decode(frame)

        for obj in decoded_objects:
            barcode_data = obj.data.decode("utf-8")

            x, y, w, h = obj.rect
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

            cv2.putText(
                frame,
                barcode_data,
                (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0,255,0),
                2
            )

            cv2.imshow("Scanner", frame)
            cv2.waitKey(1000)

            cap.release()
            cv2.destroyAllWindows()
            return barcode_data

        cv2.imshow("Scanner", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    return None