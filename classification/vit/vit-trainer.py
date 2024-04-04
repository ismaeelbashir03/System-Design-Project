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
train_dir = 'classification/WasteImagesDataset'


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

    # greate a function to preprocess the data
    def create_dataloaders(train_dir: str, transform: transforms.Compose, batch_size: int, num_workers: int=os.cpu_count()):

        # load data from folders
        train_data = datasets.ImageFolder(train_dir, transform=transform)

        # get class names
        class_names = train_data.classes

        # turn images into data loaders
        train_dataloader = DataLoader(
            train_data,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=True,
        )

        return train_dataloader, class_names

    # create data loaders
    train_dataloader_pretrained, class_names = create_dataloaders(train_dir=train_dir,
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
        test_dataloader=train_dataloader_pretrained,
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