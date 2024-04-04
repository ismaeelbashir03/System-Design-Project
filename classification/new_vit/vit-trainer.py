# IMPORTS
import torch
import torchvision
from torch import nn
import os
import matplotlib.pyplot as plt
from torchinfo import summary
from torchvision import datasets, transforms
from torch.utils.data import DataLoader


# ENGINE SETUP
try:
    from going_modular.going_modular import engine
except:
    # Get the going_modular scripts
    print("[INFO] Couldn't find going_modular scripts... downloading them from GitHub...")
    os.system("git clone https://github.com/mrdbourke/pytorch-deep-learning")
    os.system("mv pytorch-deep-learning/going_modular .")
    os.system("rm -rf pytorch-deep-learning")
    from going_modular.going_modular import engine


# ===== SETTINGS =====
# DEVICE
device = "cuda"

# HYPERPARAMETERS
BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 1e-3

# SEED
SEED = 42

# DATASET FOLDER 
train_dir = '/kaggle/input/trash-box-train/TrashBox_train_set'
test_dir = '/kaggle/input/trash-box-test/TrashBox_testandvalid_set/val'

if __name__ == "__main__":

    # ===== LOADING THE MODEL  =====

    # loading the pretrained model
    pretrained_vit_weights = torchvision.models.ViT_B_16_Weights.DEFAULT # or 'imagenet21k+imagenet2012' for 21k weights
    pretrained_vit = torchvision.models.vit_b_16(weights=pretrained_vit_weights).to(device)

    # freezing the weights
    for parameter in pretrained_vit.parameters():
        parameter.requires_grad = False
        
    # specifiying the number of classes and the class names
    class_names = os.listdir(train_dir)

    print(class_names)

    # specifiying the paramters of the head layer
    # Set the seed
    torch.manual_seed(SEED)
    torch.cuda.manual_seed(SEED)
    pretrained_vit.heads = nn.Linear(in_features=768, out_features=len(class_names)).to(device)

    # get automatic transforms from pretrained ViT weights
    pretrained_vit_transforms = pretrained_vit_weights.transforms()


    # ===== LOADING THE DATA  =====
    
    from torchvision.datasets import ImageFolder
    from PIL import Image, UnidentifiedImageError

    class CustomImageFolder(ImageFolder):
        def __getitem__(self, index):
            try:
                return super().__getitem__(index)
            except UnidentifiedImageError:
                print(f"Skipping file due to error: {self.imgs[index][0]}")
                return None  # You might want to return a placeholder image or handle differently

    # Then, use your custom dataset class
    train_data = CustomImageFolder(train_dir, transform=pretrained_vit_transforms)
    test_data = CustomImageFolder(test_dir, transform=pretrained_vit_transforms)

    # When using this dataset with a DataLoader, make sure to filter out None values
    def collate_fn(batch):
        batch = [item for item in batch if item is not None]
        return torch.utils.data.dataloader.default_collate(batch)

    # greate a function to preprocess the data
    def create_dataloaders(train_data: str, test_data: str, transform: transforms.Compose, batch_size: int, num_workers: int=os.cpu_count()):
        
        # get class names
        class_names = train_data.classes

        # turn images into data loaders
        train_dataloader = DataLoader(
            train_data,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=True,
            collate_fn=collate_fn
        )
        
        test_dataloader = DataLoader(
            test_data,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=True,
            collate_fn=collate_fn
        )

        return train_dataloader, test_dataloader, class_names

    # create data loaders
    train_dataloader_pretrained, test_dataloader_pretrained, class_names = create_dataloaders(train_data=train_data,
        test_data = test_data,
        transform=pretrained_vit_transforms,
        batch_size=BATCH_SIZE
    )


    # ===== TRAINING THE MODEL  =====

    # a summary of the model we are going to use
    summary(model=pretrained_vit, 
        # (batch_size, color_channels, height, width)
        input_size=(32, 3, 224, 224),
        col_names=["input_size", "output_size", "num_params", "trainable"],
        col_width=20,
        row_settings=["var_names"]
    )

    # train the classifier head of the pretrained ViT model
    # Set the seed
    torch.manual_seed(SEED)
    torch.cuda.manual_seed(SEED)
    pretrained_vit_results = engine.train(model=pretrained_vit,
        train_dataloader=train_dataloader_pretrained,
        test_dataloader=test_dataloader_pretrained,
        optimizer=torch.optim.Adam(params=pretrained_vit.parameters(), lr=LEARNING_RATE),
        loss_fn=torch.nn.CrossEntropyLoss(),
        epochs=EPOCHS,
        device=device
    )

    # save the model
    torch.save(pretrained_vit.state_dict(), 'fine_tuned_vit_model.pth')


    # ===== PLOTTING THE RESULTS  =====

    # Plot the loss curves
    pretrained_vit_results

    loss = pretrained_vit_results["train_loss"]
    test_loss = pretrained_vit_results["test_loss"]

    accuracy = pretrained_vit_results["train_acc"]
    test_accuracy = pretrained_vit_results["test_acc"]

    epochs = range(len(pretrained_vit_results["train_loss"]))

    plt.figure(figsize=(15, 7))

    # Plot loss
    plt.subplot(1, 2, 1)
    plt.plot(epochs, loss, label="train_loss")
    plt.plot(epochs, test_loss, label="test_loss")
    plt.title("Loss")
    plt.xlabel("Epochs")
    plt.legend()

    # Plot accuracy
    plt.subplot(1, 2, 2)
    plt.plot(epochs, accuracy, label="train_accuracy")
    plt.plot(epochs, test_accuracy, label="test_accuracy")
    plt.title("Accuracy")
    plt.xlabel("Epochs")
    plt.legend()