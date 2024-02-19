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
        mask = np.zeros_like(self.image)

        # Fill the mask with white pixels inside the polygon
        cv2.fillPoly(mask, [polygon_vertices], (255, 255, 255))

        # Bitwise AND operation between the mask and the original image
        result = cv2.bitwise_and(self.image, mask)

        # Find the bounding box of the polygon
        x, y, w, h = cv2.boundingRect(polygon_vertices)

        # Crop the region of interest from the result image
        cropped_image = result[y:y+h, x:x+w]

        # Apply bilateral filter
        smoothed_image = cv2.bilateralFilter(cropped_image, d=9, sigmaColor=75, sigmaSpace=75)

        # Encode the cropped image as a byte buffer
        success, buffer = cv2.imencode('.png', smoothed_image)

        if success:
            return buffer.tobytes()
        else:
            print("Failed to encode image to bytes")
            return None