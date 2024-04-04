import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

# ===== SETTINGS =====
model = tf.keras.models.load_model("classification/waste_classifier_resnet.keras")
classes = ['aluminium', 'carton', 'glass', 'organic', 'other plastic', 'paper and carboard', 'plastic', 'textiles', 'wood']

# ===== TESTING THE MODEL  =====
# url = "https://images.unsplash.com/photo-1577705998148-6da4f3963bc8?ixid=MnwxMjA3fDB8MHxzZWFyY2h8Nnx8Y2FyZGJvYXJkfGVufDB8fDB8fA%3D%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60"
test_dir = "classification/test/"
AUTOTUNE = tf.data.AUTOTUNE
test_dataset = tf.keras.preprocessing.image_dataset_from_directory(test_dir, seed=42, batch_size=1, smart_resize=True)
test_dataset = test_dataset.prefetch(buffer_size=AUTOTUNE)

# ===== EVALUATING THE MODEL  =====

def plot_confusion_matrix(cm,
        target_names,
        title='Confusion matrix',
        cmap=None):
    import matplotlib.pyplot as plt
    import numpy as np
    import itertools

    accuracy = np.trace(cm) / float(np.sum(cm))
    misclass = 1 - accuracy

    if cmap is None:
        cmap = plt.get_cmap('Blues')

    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()

    if target_names is not None:
        tick_marks = np.arange(len(target_names))
        plt.xticks(tick_marks, target_names, rotation=45)
        plt.yticks(tick_marks, target_names)

    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            plt.text(j, i, "{:,}".format(cm[i, j]),
                     horizontalalignment="center",
                     color="black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label\naccuracy={:0.4f}; misclass={:0.4f}'.format(accuracy, misclass))
    plt.savefig("resnet-test-conf-matrix.png", format='png', dpi=300)
    plt.show()

plt.figure(figsize=(10, 10))
true = []
predictions = []

# get the number of images in the test dataset
SAMPLES = len(test_dataset)
PLOT = False

# loop through the test dataset and make predictions
for images, labels in test_dataset.take(SAMPLES):
    pred = model.predict(images)

    # loop through the images and labels and plot them
    for i in range(len(labels)):
        if PLOT:
            plt.imshow(images[i].numpy().astype("uint8"))

        true.append(labels[i])
        predictions.append(np.argmax(pred[i]))
        
        if PLOT:
            plt.title(classes[np.argmax(pred[i])])
            plt.axis("off")
            plt.show()

# print the accuracy
print("Accuracy: ", tf.reduce_mean(tf.cast(tf.equal(true, predictions), tf.float32)).numpy())

plot_confusion_matrix(tf.math.confusion_matrix(true, predictions), classes)
