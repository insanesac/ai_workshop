def plot_loss(history):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(12, 6))
    plt.plot(history['loss'], label='Training Loss')
    plt.plot(history['val_loss'], label='Validation Loss')
    plt.title('Model Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend()
    plt.grid()
    plt.show()

def plot_accuracy(history):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(12, 6))
    plt.plot(history['accuracy'], label='Training Accuracy')
    plt.plot(history['val_accuracy'], label='Validation Accuracy')
    plt.title('Model Accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend()
    plt.grid()
    plt.show()

def visualize_predictions(images, predictions, true_labels, class_names):
    import matplotlib.pyplot as plt
    import numpy as np

    plt.figure(figsize=(15, 10))
    for i in range(len(images)):
        plt.subplot(3, 3, i + 1)
        plt.imshow(images[i])
        plt.title(f'Pred: {class_names[predictions[i]]}\nTrue: {class_names[true_labels[i]]}')
        plt.axis('off')
    plt.tight_layout()
    plt.show()