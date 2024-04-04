# IMPORTS
from collections import defaultdict
from PIL import UnidentifiedImageError
import torch
import torchvision
from torch import nn
import os
import matplotlib.pyplot as plt
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import seaborn as sns
from sklearn.metrics import confusion_matrix, precision_score, recall_score
from torchvision.datasets import ImageFolder

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

if __name__ == "__main__":
    # initialize the same model architecture as used for training
    pretrained_vit_weights = torchvision.models.ViT_B_16_Weights.DEFAULT 
    pretrained_vit_transforms = pretrained_vit_weights.transforms()
    model = torchvision.models.vit_b_16(weights=pretrained_vit_weights).to(device)
    class_names = os.listdir("classification/data_processing/cup_classification/test")
    model.heads = nn.Linear(in_features=768, out_features=len(class_names)).to(device)
    print(class_names)
    
    # load the trained model's state dict
    model_state_dict = torch.load('classification/new_vit_cup_classification/fine_tuned_vit_cup_model.pth', map_location=device)
    model.load_state_dict(model_state_dict)
    model.eval()

    classes = os.listdir("classification/data_processing/cup_classification/test")
    test_dir = "classification/data_processing/cup_classification/test"

    

    # Then, use your custom dataset class
    test_data = CustomImageFolder(test_dir, transform=pretrained_vit_transforms)

    # When using this dataset with a DataLoader, make sure to filter out None values
    def collate_fn(batch):
        batch = [item for item in batch if item is not None]
        return torch.utils.data.dataloader.default_collate(batch)

    # Function to create dataloaders
    def create_dataloaders(test_data: str, transform: transforms.Compose, batch_size: int, num_workers: int = os.cpu_count()):
        test_dataloader = DataLoader(test_data, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=True)
        return test_dataloader, test_data.classes

    # Load your data
    test_dataloader, class_names = create_dataloaders(test_data=test_data, transform=pretrained_vit_transforms, batch_size=BATCH_SIZE)


    # Evaluate the model
    def evaluate_model(model, dataloader, classes):
        correct = 0
        total = 0
        predictions = []
        actuals = []

        metrics = defaultdict(defaultdict)
        for _class in classes:
            metrics[_class] = defaultdict(int)
            metrics[_class]['TP'] = 0
            metrics[_class]['TN'] = 0
            metrics[_class]['FP'] = 0
            metrics[_class]['FN'] = 0
            metrics[_class]['total'] = 0

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

                if classes[labels] == 'cups':
                    metrics['cups']['total'] += 1
                    if classes[predictions[-1]] == 'cups':
                        metrics['cups']['TP'] += 1

                        for _class in classes:
                            if _class != classes[predictions[-1]] or _class != classes[labels]:
                                metrics[_class]['TN'] += 1
                    else:
                        metrics['cups']['FN'] += 1
                        metrics[classes[predictions[-1]]]['FP'] += 1
    
                
                if classes[labels] == 'no_cups':
                    metrics['no_cups']['total'] += 1
                    if classes[predictions[-1]] == 'no_cups':
                        metrics['no_cups']['TP'] += 1

                        for _class in classes:
                            if _class != classes[predictions[-1]] or _class != classes[labels]:
                                metrics[_class]['TN'] += 1
                    else:
                        metrics['no_cups']['FN'] += 1
                        metrics[classes[predictions[-1]]]['FP'] += 1

                
                counter += 1
                if counter % 100 == 0:
                    print(f'Processed {counter} images')
        
        print(f'Processed {counter} images')

        # calculating total metrics
        total_accuracy = 100 * correct / total
        total_precision = precision_score(actuals, predictions, average='weighted')
        total_recall = recall_score(actuals, predictions, average='weighted')
        total_f1 = 2 * (total_precision * total_recall) / (total_precision + total_recall)

        # cardboard metrics
        cups_accuracy = 100 * metrics['cups']['TP'] / metrics['cups']['total']
        cups_precision = metrics['cups']['TP'] / (metrics['cups']['TP'] + metrics['cups']['FP'])
        cups_recall = metrics['cups']['TP'] / (metrics['cups']['TP'] + metrics['cups']['FN'])
        cups_f1 = 2 * (cups_precision * cups_recall) / (cups_precision + cups_recall)

        # no_cups metrics
        no_cups_accuracy = 100 * metrics['no_cups']['TP'] / metrics['no_cups']['total']
        no_cups_precision = metrics['no_cups']['TP'] / (metrics['no_cups']['TP'] + metrics['no_cups']['FP'])
        no_cups_recall = metrics['no_cups']['TP'] / (metrics['no_cups']['TP'] + metrics['no_cups']['FN'])
        no_cups_f1 = 2 * (no_cups_precision * no_cups_recall) / (no_cups_precision + no_cups_recall)

        
        
        # print table
        print(f'{"Total":<10} {"Accuracy":<10} {"Precision":<10} {"Recall":<10} {"F1":<10}')
        print(f'{"":<10} {total_accuracy:<10.5f} {total_precision:<10.5f} {total_recall:<10.5f} {total_f1:<10.5f}')
        print(f'{"Cardboard":<10} {cups_accuracy:<10.5f} {cups_precision:<10.5f} {cups_recall:<10.5f} {cups_f1:<10.5f}')
        print(f'{"Ewaste":<10} {no_cups_accuracy:<10.5f} {no_cups_precision:<10.5f} {no_cups_recall:<10.5f} {no_cups_f1:<10.5f}')
        
        return total_accuracy, actuals, predictions


    # get accuracy and get the true vs predicted labels
    accuracy, actuals, predictions = evaluate_model(model, test_dataloader, classes)

    print(f'Accuracy of the model on the test images: {accuracy}%')


    # Generate confusion matrix
    cm = confusion_matrix(actuals, predictions)

    # save confusion matrix
    import numpy as np
    np.save(f"vit-test-conf-matrix({accuracy}).npy", cm)

    # Plot confusion matrix
    def plot_confusion_matrix(cm, class_names):
        sns.set_theme(font_scale=3)
        plt.figure(figsize=(10, 7))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
        plt.xlabel('Predicted Labels')
        plt.ylabel('True Labels')
        plt.title('Confusion Matrix')
        plt.savefig(f"vit-test-conf-matrix({accuracy}).png", format='png', dpi=300, bbox_inches = "tight")
        plt.show()

    plot_confusion_matrix(cm, classes)
