# IMPORTS
import cv2
from classification import WasteClassification
from PIL import Image


if __name__ == "__main__":
    
    # Initialize the model
    waste_classification = WasteClassification()

    # get the webcam feed
    cap = cv2.VideoCapture(1)

    # loop through the webcam feed
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # convert the frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # convert the frame to PIL image
        pil_img = Image.fromarray(rgb_frame)

        print("Predicting frame...")
        
        # get accuracy and get the true vs predicted labels
        predicted = waste_classification.classify(pil_img)

        print("Predicted: ", predicted)

        # show the frame
        cv2.imshow('frame', frame)


    


        