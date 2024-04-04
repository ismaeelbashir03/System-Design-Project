# IMPORTS
from PIL import UnidentifiedImageError, Image
import torch
import torchvision
from torch import nn
from torchvision.datasets import ImageFolder
import cv2

# SETTINGS
BATCH_SIZE = 1
device = "cuda" if torch.cuda.is_available() else "mps"

class CustomImageFolder(ImageFolder):
    def __getitem__(self, index):
        try:
            return super().__getitem__(index)
        except UnidentifiedImageError:
            print(f"Skipping file due to error: {self.imgs[index][0]}")
            return None  # You might want to return a placeholder image or handle differently
        
# Evaluate the model
def evaluate_model(model, image, classes):

    predictions = []

    model.eval()

    with torch.no_grad():
        image = pretrained_vit_transforms(image).unsqueeze(0).to(device)
        outputs = model(image)
        _, predicted = torch.max(outputs.data, 1)
        predictions.extend(predicted.view(-1).cpu().numpy())

    # get the class
    predicted = classes[predictions[0]]
    return predicted

if __name__ == "__main__":
    # initialize the same model architecture as used for training
    pretrained_vit_weights = torchvision.models.ViT_B_16_Weights.DEFAULT 
    pretrained_vit_transforms = pretrained_vit_weights.transforms()
    model = torchvision.models.vit_b_16(weights=pretrained_vit_weights).to(device)
    class_names = ['aluminium', 'carton', 'glass', 'organic', 'other plastic', 'paper and cardboard', 'plastic']
    model.heads = nn.Linear(in_features=768, out_features=len(class_names)).to(device)

    # load the trained model's state dict
    model_state_dict = torch.load('classification/new_vit/fine_tuned_vit_new_model.pth', map_location=device)
    model.load_state_dict(model_state_dict)
    model.eval()

    classes = ['aluminium', 'carton', 'glass', 'organic', 'other plastic', 'paper and cardboard', 'plastic']

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
        predicted = evaluate_model(model, pil_img, classes)

        print("Predicted: ", predicted)

        # show the frame
        cv2.imshow('frame', frame)


    


        