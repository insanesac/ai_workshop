# resnet_demo.py

import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import numpy as np

# Load a pre-trained ResNet model
model = models.resnet18(pretrained=True)
model.eval()

# Define the image transformation
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Function to predict the class of an image
def predict(image_path):
    # Load and transform the image
    image = Image.open(image_path)
    image = transform(image).unsqueeze(0)  # Add batch dimension

    # Perform inference
    with torch.no_grad():
        output = model(image)

    # Get the predicted class
    _, predicted = torch.max(output, 1)
    return predicted.item()

# Example usage
if __name__ == "__main__":
    image_path = "path_to_your_image.jpg"  # Replace with your image path
    class_id = predict(image_path)
    print(f"Predicted class ID: {class_id}")