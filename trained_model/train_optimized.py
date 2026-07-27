import os
import sys
import json
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks
from datasets import load_dataset
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best_model.keras")
METADATA_PATH = os.path.join(BASE_DIR, "model_metadata.json")

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 2

def apply_clahe_preprocessing(pil_img):
    """Applies CLAHE contrast enhancement to the image and converts back to 3-channel RGB."""
    # Convert PIL to Grayscale NumPy array
    img_gray = np.array(pil_img.convert('L'))
    # Resize to target size first to optimize memory
    img_gray = cv2.resize(img_gray, IMAGE_SIZE)
    # Apply CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img_enhanced = clahe.apply(img_gray)
    # Convert back to 3-channel RGB
    img_rgb = cv2.cvtColor(img_enhanced, cv2.COLOR_GRAY2RGB)
    # Normalize pixel values to [0.0, 1.0]
    return img_rgb.astype(np.float32) / 255.0

def load_and_preprocess_dataset(num_train_samples=250, num_val_samples=50):
    """Loads dataset from Hugging Face and extracts preprocessed samples."""
    print("Loading 'hf-vision/chest-xray-pneumonia' dataset from Hugging Face...")
    raw_dataset = load_dataset("hf-vision/chest-xray-pneumonia")
    
    splits = ['train', 'validation', 'test']
    dataset_processed = {}
    
    for split in splits:
        print(f"Preprocessing '{split}' split...")
        images = []
        labels = []
        
        # Categorize by class
        normal_idx = [i for i, x in enumerate(raw_dataset[split]) if x['label'] == 0]
        pneumonia_idx = [i for i, x in enumerate(raw_dataset[split]) if x['label'] == 1]
        
        # Sample subset size limit for CPU training speed
        limit = num_train_samples if split == 'train' else num_val_samples
        sampled_normal = normal_idx[:limit]
        sampled_pneumonia = pneumonia_idx[:limit]
        
        # Merge and preprocess
        combined_idx = sampled_normal + sampled_pneumonia
        np.random.shuffle(combined_idx)
        
        for idx in combined_idx:
            item = raw_dataset[split][int(idx)]
            img_processed = apply_clahe_preprocessing(item['image'])
            images.append(img_processed)
            labels.append(item['label'])
            
        dataset_processed[split] = (np.array(images), np.array(labels))
        print(f"Split '{split}' loaded. Normal: {len(sampled_normal)}, Pneumonia: {len(sampled_pneumonia)}")
        
    return dataset_processed

def build_robust_model():
    """Builds MobileNetV2 with data augmentation and custom classification head."""
    # Data Augmentation Layers
    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.1)
    ])
    
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False  # Freeze base network initial layers
    
    # Model architecture assembly
    inputs = layers.Input(shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3), name="input_layer")
    x = data_augmentation(inputs)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.4)(x)  # Dropouts to prevent overfitting
    outputs = layers.Dense(1, activation='sigmoid', name="predictions")(x)
    
    model = models.Model(inputs=inputs, outputs=outputs)
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    return model

def train_and_evaluate():
    # 1. Load Data
    data = load_and_preprocess_dataset(num_train_samples=250, num_val_samples=50)
    X_train, y_train = data['train']
    X_val, y_val = data['validation']
    X_test, y_test = data['test']
    
    # 2. Handle Class Imbalance via Class Weights
    total = len(y_train)
    c0 = np.sum(y_train == 0)
    c1 = np.sum(y_train == 1)
    weight_c0 = (1 / c0) * (total / 2.0)
    weight_c1 = (1 / c1) * (total / 2.0)
    class_weight = {0: weight_c0, 1: weight_c1}
    print(f"Calculated Class Weights -> Normal (0): {weight_c0:.2f}, Pneumonia (1): {weight_c1:.2f}")
    
    # 3. Build Model
    model = build_robust_model()
    
    # 4. Training Callbacks (Early Stopping to prevent overfitting)
    early_stop = callbacks.EarlyStopping(
        monitor='val_loss',
        patience=2,
        restore_best_weights=True
    )
    
    print("Beginning optimized model training on local CPU...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        class_weight=class_weight,
        callbacks=[early_stop]
    )
    
    # 5. Evaluate on Test split
    loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"Evaluation on held-out test split: Accuracy = {accuracy * 100:.2f}%")
    
    # 6. Save model
    model.save(MODEL_PATH)
    print(f"Trained model saved to: {MODEL_PATH}")
    
    # 7. Save metadata
    metadata = {
        "model_architecture": "MobileNetV2 (Transfer Learning + Augmentation + CLAHE)",
        "dataset_version": "Chest X-Ray Images (Pneumonia) - HuggingFace Dataset Split",
        "training_date": str(np.datetime64('now')),
        "hyperparameters": {
            "initial_learning_rate": 0.001,
            "batch_size": BATCH_SIZE,
            "optimizer": "Adam",
            "epochs": len(history.history['loss'])
        },
        "epochs_trained": len(history.history['loss']),
        "input_image_size": f"{IMAGE_SIZE[0]}x{IMAGE_SIZE[1]}x3",
        "evaluation_metrics": {
            "accuracy": float(accuracy),
            "loss": float(loss),
            "val_loss_curve": [float(x) for x in history.history['val_loss']],
            "train_loss_curve": [float(x) for x in history.history['loss']]
        }
    }
    
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=4)
    print("Model metadata successfully updated.")

if __name__ == '__main__':
    train_and_evaluate()
