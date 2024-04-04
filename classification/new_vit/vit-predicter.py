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
    class_names = ['cardboard', 'ewaste', 'glass', 'other', 'metal', 'paper', 'plastic']
    model.heads = nn.Linear(in_features=768, out_features=len(class_names)).to(device)

    # load the trained model's state dict
    model_state_dict = torch.load('classification/new_vit/fine_tuned_vit_new_model.pth', map_location=device)
    model.load_state_dict(model_state_dict)
    model.eval()

    classes = ['cardboard', 'ewaste', 'glass', 'other', 'metal', 'paper', 'plastic']
    test_dir = "classification/data_processing/TrashBox-testandvalid-main/TrashBox_testandvalid_set/test"

    

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

                if classes[labels] == 'cardboard':
                    metrics['cardboard']['total'] += 1
                    if classes[predictions[-1]] == 'cardboard':
                        metrics['cardboard']['TP'] += 1

                        for _class in classes:
                            if _class != classes[predictions[-1]] or _class != classes[labels]:
                                metrics[_class]['TN'] += 1
                    else:
                        metrics['cardboard']['FN'] += 1
                        metrics[classes[predictions[-1]]]['FP'] += 1
    
                
                if classes[labels] == 'ewaste':
                    metrics['ewaste']['total'] += 1
                    if classes[predictions[-1]] == 'ewaste':
                        metrics['ewaste']['TP'] += 1

                        for _class in classes:
                            if _class != classes[predictions[-1]] or _class != classes[labels]:
                                metrics[_class]['TN'] += 1
                    else:
                        metrics['ewaste']['FN'] += 1
                        metrics[classes[predictions[-1]]]['FP'] += 1

                
                if classes[labels] == 'glass':
                    metrics['glass']['total'] += 1
                    if classes[predictions[-1]] == 'glass':
                        metrics['glass']['TP'] += 1

                        for _class in classes:
                            if _class != classes[predictions[-1]] or _class != classes[labels]:
                                metrics[_class]['TN'] += 1
                    else:
                        metrics['glass']['FN'] += 1
                        metrics[classes[predictions[-1]]]['FP'] += 1
                        

                
                # if classes[labels] == 'medical':
                #     metrics['medical']['total'] += 1
                #     if classes[predictions[-1]] == 'medical':
                #         metrics['medical']['TP'] += 1

                #         for _class in classes:
                #             if _class != classes[predictions[-1]] or _class != classes[labels]:
                #                 metrics[_class]['TN'] += 1
                #     else:
                #         metrics['medical']['FN'] += 1
                #         metrics[classes[predictions[-1]]]['FP'] += 1
                
                if classes[labels] == 'metal':
                    metrics['metal']['total'] += 1
                    if classes[predictions[-1]] == 'metal':
                        metrics['metal']['TP'] += 1

                        for _class in classes:
                            if _class != classes[predictions[-1]] or _class != classes[labels]:
                                metrics[_class]['TN'] += 1
                    else:
                        metrics['metal']['FN'] += 1
                        metrics[classes[predictions[-1]]]['FP'] += 1
                
                if classes[labels] == 'paper':
                    metrics['paper']['total'] += 1
                    if classes[predictions[-1]] == 'paper':
                        metrics['paper']['TP'] += 1
                        
                        for _class in classes:
                            if _class != classes[predictions[-1]] or _class != classes[labels]:
                                metrics[_class]['TN'] += 1
                    else:
                        metrics['paper']['FN'] += 1
                        metrics[classes[predictions[-1]]]['FP'] += 1
                
                if classes[labels] == 'plastic':
                    metrics['plastic']['total'] += 1
                    if classes[predictions[-1]] == 'plastic':
                        metrics['plastic']['TP'] += 1

                        for _class in classes:
                            if _class != classes[predictions[-1]] or _class != classes[labels]:
                                metrics[_class]['TN'] += 1
                    else:
                        metrics['plastic']['FN'] += 1
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
        cardboard_accuracy = 100 * metrics['cardboard']['TP'] / metrics['cardboard']['total']
        cardboard_precision = metrics['cardboard']['TP'] / (metrics['cardboard']['TP'] + metrics['cardboard']['FP'])
        cardboard_recall = metrics['cardboard']['TP'] / (metrics['cardboard']['TP'] + metrics['cardboard']['FN'])
        cardboard_f1 = 2 * (cardboard_precision * cardboard_recall) / (cardboard_precision + cardboard_recall)

        # ewaste metrics
        ewaste_accuracy = 100 * metrics['ewaste']['TP'] / metrics['ewaste']['total']
        ewaste_precision = metrics['ewaste']['TP'] / (metrics['ewaste']['TP'] + metrics['ewaste']['FP'])
        ewaste_recall = metrics['ewaste']['TP'] / (metrics['ewaste']['TP'] + metrics['ewaste']['FN'])
        ewaste_f1 = 2 * (ewaste_precision * ewaste_recall) / (ewaste_precision + ewaste_recall)

        # glass metrics
        glass_accuracy = 100 * metrics['glass']['TP'] / metrics['glass']['total']
        glass_precision = metrics['glass']['TP'] / (metrics['glass']['TP'] + metrics['glass']['FP'])
        glass_recall = metrics['glass']['TP'] / (metrics['glass']['TP'] + metrics['glass']['FN'])
        glass_f1 = 2 * (glass_precision * glass_recall) / (glass_precision + glass_recall)

        # medical metrics
        # medical_accuracy = 100 * metrics['medical']['TP'] / metrics['medical']['total']
        # medical_precision = metrics['medical']['TP'] / (metrics['medical']['TP'] + metrics['medical']['FP'])
        # medical_recall = metrics['medical']['TP'] / (metrics['medical']['TP'] + metrics['medical']['FN'])
        # medical_f1 = 2 * (medical_precision * medical_recall) / (medical_precision + medical_recall)

        # metal metrics
        metal_accuracy = 100 * metrics['metal']['TP'] / metrics['metal']['total']
        metal_precision = metrics['metal']['TP'] / (metrics['metal']['TP'] + metrics['metal']['FP'])
        metal_recall = metrics['metal']['TP'] / (metrics['metal']['TP'] + metrics['metal']['FN'])
        metal_f1 = 2 * (metal_precision * metal_recall) / (metal_precision + metal_recall)

        # paper metrics
        paper_accuracy = 100 * metrics["paper"]["TP"] / metrics["paper"]["total"]
        paper_precision = metrics['paper']['TP'] / (metrics['paper']['TP'] + metrics['paper']['FP'])
        paper_recall = metrics['paper']['TP'] / (metrics['paper']['TP'] + metrics['paper']['FN'])
        paper_f1 = 2 * (paper_precision * paper_recall) / (paper_precision + paper_recall)

        # plastic metrics
        plastic_accuracy = 100 * metrics["plastic"]["TP"] / metrics["plastic"]["total"]
        plastic_precision = metrics['plastic']['TP'] / (metrics['plastic']['TP'] + metrics['plastic']['FP'])
        plastic_recall = metrics['plastic']['TP'] / (metrics['plastic']['TP'] + metrics['plastic']['FN'])
        plastic_f1 = 2 * (plastic_precision * plastic_recall) / (plastic_precision + plastic_recall)
        
        # print table
        print(f'{"Total":<10} {"Accuracy":<10} {"Precision":<10} {"Recall":<10} {"F1":<10}')
        print(f'{"":<10} {total_accuracy:<10.5f} {total_precision:<10.5f} {total_recall:<10.5f} {total_f1:<10.5f}')
        print(f'{"Cardboard":<10} {cardboard_accuracy:<10.5f} {cardboard_precision:<10.5f} {cardboard_recall:<10.5f} {cardboard_f1:<10.5f}')
        print(f'{"Ewaste":<10} {ewaste_accuracy:<10.5f} {ewaste_precision:<10.5f} {ewaste_recall:<10.5f} {ewaste_f1:<10.5f}')
        print(f'{"Glass":<10} {glass_accuracy:<10.5f} {glass_precision:<10.5f} {glass_recall:<10.5f} {glass_f1:<10.5f}')
        print(f'{"Metal":<10} {metal_accuracy:<10.5f} {metal_precision:<10.5f} {metal_recall:<10.5f} {metal_f1:<10.5f}')
        print(f'{"Paper":<10} {paper_accuracy:<10.5f} {paper_precision:<10.5f} {paper_recall:<10.5f} {paper_f1:<10.5f}')
        print(f'{"Plastic":<10} {plastic_accuracy:<10.5f} {plastic_precision:<10.5f} {plastic_recall:<10.5f} {plastic_f1:<10.5f}')

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
        plt.figure(figsize=(10, 7))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
        sns.set_theme(font_scale=2)
        plt.xlabel('Predicted Labels')
        plt.ylabel('True Labels')
        plt.title('Confusion Matrix')
        plt.savefig(f"vit-test-conf-matrix({accuracy}).png", format='png', dpi=300, bbox_inches = "tight")
        plt.show()

    plot_confusion_matrix(cm, classes)
