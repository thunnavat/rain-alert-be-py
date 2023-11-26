import cv2
import numpy as np

class ImageCropper:
    def __init__(self, image_buffer):
        self.image_buffer = image_buffer
        self.image = self._decode_image()

    def _decode_image(self):
        nparr = np.frombuffer(self.image_buffer, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    def crop_polygon(self, polygon_vertices):
        # Create an empty mask with the same size as the image
        mask = np.zeros(self.image.shape[:2], dtype=np.uint8)

        # Fill the mask with white pixels inside the polygon
        cv2.fillPoly(mask, [polygon_vertices], 255)

        # Find the bounding box of the polygon
        x, y, w, h = cv2.boundingRect(polygon_vertices)

        # Create an RGBA image with a transparent background
        rgba_image = np.zeros((h, w, 4), dtype=np.uint8)
        rgba_image[:, :, :3] = self.image[y:y+h, x:x+w]  # Copy the RGB channels

        # Ensure the mask has the correct shape
        mask_roi = mask[y:y+h, x:x+w]

        # Set alpha channel based on the mask
        rgba_image[:, :, 3] = (mask_roi > 0).astype(np.uint8) * 255

        # Encode the cropped image as a byte buffer
        success, buffer = cv2.imencode('.jpg', rgba_image)

        if success:
            print("Image fetched and stored in buffer successfully")
            buffer.tobytes()
        else:
            print("Failed to encode image to bytes")
            return None


