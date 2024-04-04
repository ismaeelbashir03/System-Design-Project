# IMPORTS
from PIL import UnidentifiedImageError, Image
import torchvision.transforms.functional as TF
import torch
import torchvision
from torch import nn
import os
from torch.utils.data import DataLoader
from torchvision import transforms
from torchvision.datasets import ImageFolder
from io import BytesIO
import base64

class CustomImageFolder(ImageFolder):
    def __getitem__(self, index):
        try:
            return super().__getitem__(index)
        except UnidentifiedImageError:
            print(f"Skipping file due to error: {self.imgs[index][0]}")
            return None  # You might want to return a placeholder image or handle differently
        
class WasteClassification:

    def __init__(self, 
            model_1_path="classification/new_vit/fine_tuned_vit_new_model.pth", 
            model_2_path="classification/new_vit_cup_classification/fine_tuned_vit_cup_model.pth", 
            class_1_names = ['cardboard', 'ewaste', 'glass', 'other', 'metal', 'paper', 'plastic'],
            class_2_names = ['cups', 'no_cups'],
            BATCH_SIZE=1,
            device="cuda" if torch.cuda.is_available() else "cpu"
        ):
        """
        Waste Classification model

        Args:

        model_1_path (str): Path to the first model's state dict
        model_2_path (str): Path to the second model's state dict
        class_names (list): List of class names
        """

        # SETTINGS
        self.BATCH_SIZE = BATCH_SIZE
        self.device = device

        # initialize the same model architecture as used for training
        pretrained_vit_weights = torchvision.models.ViT_B_16_Weights.DEFAULT 
        self.pretrained_vit_transforms = pretrained_vit_weights.transforms()

        self.model_1 = torchvision.models.vit_b_16(weights=pretrained_vit_weights).to(device)
        self.model_2 = torchvision.models.vit_b_16(weights=pretrained_vit_weights).to(device)

        self.class_1_names = class_1_names
        self.class_2_names = class_2_names

        self.model_1.heads = nn.Linear(in_features=768, out_features=len(self.class_1_names)).to(device)
        self.model_2.heads = nn.Linear(in_features=768, out_features=len(self.class_2_names)).to(device)

        # load the trained model's state dict
        model_state_dict = torch.load(model_1_path, map_location=device)
        self.model_1.load_state_dict(model_state_dict)
        
        model_state_dict = torch.load(model_2_path, map_location=device)
        self.model_2.load_state_dict(model_state_dict)

        self.model_1.eval()
        self.model_2.eval()

    # When using this dataset with a DataLoader, make sure to filter out None values
    def collate_fn(self, batch):
        """
        Filter out None values from the batch
        """
        batch = [item for item in batch if item is not None]
        return torch.utils.data.dataloader.default_collate(batch)

    # Function to create dataloaders
    def get_image(self, image_path: str, transform: transforms.Compose, batch_size: int, num_workers: int = os.cpu_count()):
        """
        Get image from the image path

        Args:
        image_path (str): Path to the test data
        """
        dataset = CustomImageFolder(root=image_path, transform=transform)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers, collate_fn=self.collate_fn)
        print(f"Found {len(dataset)} images in {image_path}/{dataset.classes}")

        # return just the image
        for inputs, labels in dataloader:
            return inputs
        
    def base64_to_image(self, base64_string: str):
        """
        Convert base64 string to image

        Args:
        base64_string (str): Base64 string
        """
        image = Image.open(BytesIO(base64.b64decode(base64_string)))
        return image

    def classify_from_path(self, image_path: str):
        """
        Classify the test data

        Args:
        test_data (str): Path to the test data
        """
        # Load your data
        image = self.get_image(image_path, transform=self.pretrained_vit_transforms, batch_size=self.BATCH_SIZE)

        # Send the image to the device     
        image = image.to(self.device)
        
        # get the ouputs of the models
        outputs = self.model_1(image)
        _, predicted_1 = torch.max(outputs.data, 1)

        outputs_2 = self.model_2(image)
        _, predicted_2 = torch.max(outputs_2.data, 1)

        print(f"Model 1: {self.class_1_names[predicted_1]}")
        print(f"Model 2: {self.class_2_names[predicted_2]}")

        return self.class_1_names[predicted_1], self.class_2_names[predicted_2]
    
    def classify(self, image: Image.Image):
        """
        Classify the test data

        Args:
        test_data (str): Path to the test data
        """

        # transform the image
        transformed_image = self.pretrained_vit_transforms(image)

        # Add a batch dimension
        transformed_image = transformed_image.unsqueeze(0)

        # Send the image to the device
        image = transformed_image.to(self.device)
        
        # get the ouputs of the models
        outputs = self.model_1(image)
        _, predicted_1 = torch.max(outputs.data, 1)

        outputs_2 = self.model_2(image)
        _, predicted_2 = torch.max(outputs_2.data, 1)

        return self.class_1_names[predicted_1], self.class_2_names[predicted_2]


# TESTING
# if __name__ == "__main__":     
#     # Initialize the model
#     waste_classification = WasteClassification()

#     # Classify the test data
#     waste_classification.classify_from_path(image_path="classification/input")