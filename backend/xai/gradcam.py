import numpy as np
import tensorflow as tf
import cv2
import os
from backend.utils.logger import logger

def find_last_conv_layer(model_or_layer):
    """Recursively searches for the last 4D convolutional layer in a model or sub-model."""
    if hasattr(model_or_layer, "layers"):
        # Iterate backwards over layers
        for layer in reversed(model_or_layer.layers):
            # Recursively check sub-models or nested layers
            conv_layer = find_last_conv_layer(layer)
            if conv_layer is not None:
                return conv_layer
    else:
        # Check if the output of this leaf layer is a 4D tensor
        try:
            shape = model_or_layer.output.shape
            if len(shape) == 4:
                return model_or_layer
        except Exception:
            pass
    return None

def generate_gradcam(model, img_array: np.ndarray, original_img_path: str, output_path: str) -> bool:
    """
    Generates a Grad-CAM heatmap and overlays it onto the original chest X-ray.
    
    Args:
        model: Loaded Keras model.
        img_array: Preprocessed image array of shape (1, 224, 224, 3).
        original_img_path: Path to the original source image.
        output_path: Path where the overlay Grad-CAM image should be saved.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # 1. Identify last convolutional layer object
        conv_layer = None
        try:
            # Check if custom 'top_activation' layer from EfficientNet exists
            conv_layer = model.get_layer("top_activation")
        except ValueError:
            # Recursively search the graph for the last 4D conv layer
            conv_layer = find_last_conv_layer(model)
            
        if conv_layer is None:
            raise ValueError("No 4D convolutional layer found in model structure.")
            
        logger.info(f"Using convolutional layer '{conv_layer.name}' for Grad-CAM generation.")
        
        # Force Keras to build/trace the model nodes by executing a symbolic call on the input tensor
        _ = model(img_array)
        
        # 2. Set up a sub-model that outputs both the last conv activations and predictions
        grad_model = tf.keras.models.Model(
            inputs=model.inputs,
            outputs=[conv_layer.output, model.output]
        )
        
        # 3. Compute gradients of the predicted class with respect to the activations
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)
            # Binary classification: output is sigmoid probability
            loss = predictions[0]
            
        # Get gradients of the loss with respect to the final conv layer activations
        grads = tape.gradient(loss, conv_outputs)
        
        # Compute channel-wise mean of gradients
        # grads shape: (1, H, W, C) -> pooled_grads shape: (C,)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        # Multiply each channel in the feature map by 'how important this channel is'
        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        
        # 4. Apply ReLU to retain only positive features contributing to the class
        heatmap = tf.maximum(heatmap, 0) / (tf.reduce_max(heatmap) + 1e-10)
        heatmap = heatmap.numpy()
        
        # 5. Read original image for overlay
        orig_img = cv2.imread(original_img_path)
        if orig_img is None:
            raise FileNotFoundError(f"Original image not found at {original_img_path}")
            
        height, width, _ = orig_img.shape
        
        # Resize heatmap to match the original image size
        heatmap_resized = cv2.resize(heatmap, (width, height))
        
        # Scale to 0-255 range and convert to uint8
        heatmap_uint8 = np.uint8(255 * heatmap_resized)
        
        # Apply colormap (JET)
        colormap = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        
        # 6. Superimpose heatmap on original image
        # Using 60% original image and 40% heatmap color representation
        overlay = cv2.addWeighted(orig_img, 0.6, colormap, 0.4, 0)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save overlay image
        cv2.imwrite(output_path, overlay)
        logger.info(f"Grad-CAM overlay successfully written to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating Grad-CAM: {e}", exc_info=True)
        return False
