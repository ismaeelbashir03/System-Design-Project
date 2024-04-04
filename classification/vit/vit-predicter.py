# IMPORTS
import torch
import torchvision
from torch import nn
import os
import matplotlib.pyplot as plt
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import seaborn as sns
from sklearn.metrics import confusion_matrix

# SETTINGS
BATCH_SIZE = 1
device = "cuda" if torch.cuda.is_available() else "mps"

if __name__ == "__main__":
    # initialize the same model architecture as used for training
    pretrained_vit_weights = torchvision.models.ViT_B_16_Weights.DEFAULT 
    pretrained_vit_transforms = pretrained_vit_weights.transforms()
    model = torchvision.models.vit_b_16(weights=pretrained_vit_weights).to(device)
    class_names = ['aluminium', 'carton', 'glass', 'organic', 'other plastic', 'paper and cardboard', 'plastic']
    model.heads = nn.Linear(in_features=768, out_features=len(class_names)).to(device)

    # load the trained model's state dict
    model_state_dict = torch.load('classification/fine_tuned_vit_model.pth', map_location=device)
    model.load_state_dict(model_state_dict)
    model.eval()

    classes = ['aluminium', 'carton', 'glass', 'organic', 'other plastic', 'paper and cardboard', 'plastic']
    test_dir = "classification/test"

    def create_dataloaders(test_dir: str, transform: transforms.Compose, batch_size: int, num_workers: int = os.cpu_count()):
        test_data = datasets.ImageFolder(test_dir, transform=transform)
        test_dataloader = DataLoader(test_data, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=True)
        return test_dataloader, test_data.classes

    # load data
    test_dataloader, class_names = create_dataloaders(test_dir=test_dir, transform=pretrained_vit_transforms, batch_size=BATCH_SIZE)


    # Evaluate the model
    def evaluate_model(model, dataloader, classes):
        correct = 0
        total = 0
        predictions = []
        actuals = []

        model.eval()

        with torch.no_grad():
            counter = 0
            for images, labels in dataloader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                predictions.extend(predicted.view(-1).cpu().numpy())
                actuals.extend(labels.view(-1).cpu().numpy())
                counter += 1
                if counter % 1 == 0:
                    print(f'Processed {counter} images')
                

        accuracy = 100 * correct / total
        return accuracy, actuals, predictions


    # get accuracy and get the true vs predicted labels
    accuracy, actuals, predictions = evaluate_model(model, test_dataloader, classes)

    print(f'Accuracy of the model on the test images: {accuracy}%')

    # Convert to tensors
    actuals_tensor = torch.tensor(actuals)
    predictions_tensor = torch.tensor(predictions)

    # Calculate accuracy
    accuracy_pytorch = (actuals_tensor == predictions_tensor).float().mean()
    print(f'Accuracy (PyTorch): {accuracy_pytorch.item() * 100}%')

    # Generate confusion matrix
    cm = confusion_matrix(actuals, predictions)

    # Plot confusion matrix
    def plot_confusion_matrix(cm, class_names):
        plt.figure(figsize=(10, 7))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
        plt.xlabel('Predicted Labels')
        plt.ylabel('True Labels')
        plt.title('Confusion Matrix')
        plt.savefig("vit-test-conf-matrix.png", format='png', dpi=300)
        plt.show()

    plot_confusion_matrix(cm, classes)
