import os
import numpy as np
from PIL import Image
from pathlib import Path
import tensorflow.python.keras as tf_keras
from tensorflow.python.keras import layers, models, callbacks
from sklearn.model_selection import train_test_split
from tensorflow.python.keras.engine import data_adapter
from keras.layers import BatchNormalization

from keras import __version__
tf_keras.__version__ = __version__

from trained_models.model_version import VERSION

# Config
DATASET_DIR = "dataset/flattened_dataset"
OUTPUT_DIR = "trained_models"
MODEL_NAME = f"chess_piece_color_model{VERSION}.h5"
IMAGE_SIZE = (128, 128)
BATCH_SIZE = 32
EPOCHS = 20
SEED = 42

os.makedirs(OUTPUT_DIR, exist_ok=True)

def _is_distributed_dataset(ds):
    return isinstance(ds, data_adapter.input_lib.DistributedDatasetSpec)

data_adapter._is_distributed_dataset = _is_distributed_dataset

pieces = ["pawn", "rook", "knight", "bishop", "queen", "king"]
colors = ["black", "white"]

piece_to_idx = {p: i for i, p in enumerate(pieces)}
color_to_idx = {c: i for i, c in enumerate(colors)}

# TODO: Load dataset
image_paths, piece_labels, color_labels = [], [], []

for piece in pieces:
    for color in colors:
        folder = Path(DATASET_DIR) / piece / color
        if not folder.exists():
            continue
        for img_file in folder.glob("*.png"):
            image_paths.append(str(img_file))
            piece_labels.append(piece_to_idx[piece])
            color_labels.append(color_to_idx[color])

print(f"✅ Found {len(image_paths)} images")

# TODO: Convert to numpy arrays
def load_image(path):
    img = Image.open(path).convert("RGB").resize(IMAGE_SIZE)
    return np.array(img, dtype=np.float32) / 255.0

X = np.array([load_image(p) for p in image_paths], dtype=np.float32)
y_piece = np.array(piece_labels, dtype=np.int32)
y_color = np.array(color_labels, dtype=np.int32)

# Split dataset
X_train, X_val, y_piece_train, y_piece_val, y_color_train, y_color_val = train_test_split(
    X, y_piece, y_color, test_size=0.2, random_state=SEED, stratify=y_piece
)

# TODO: Build deeper CNN model (multi-output)
inputs = layers.Input(shape=IMAGE_SIZE + (3,))

# Layer 1
x = layers.Conv2D(32, (3, 3), activation="relu", padding="same")(inputs)
x = BatchNormalization()(x)
x = layers.Conv2D(32, (3, 3), activation="relu", padding="same")(x)
x = BatchNormalization()(x)
x = layers.MaxPooling2D()(x)
x = layers.Dropout(0.25)(x)

# Layer 2
x = layers.Conv2D(64, (3, 3), activation="relu", padding="same")(x)
x = BatchNormalization()(x)
x = layers.Conv2D(64, (3, 3), activation="relu", padding="same")(x)
x = BatchNormalization()(x)
x = layers.MaxPooling2D()(x)
x = layers.Dropout(0.25)(x)

# Layer 3
x = layers.Conv2D(128, (3, 3), activation="relu", padding="same")(x)
x = BatchNormalization()(x)
x = layers.Conv2D(128, (3, 3), activation="relu", padding="same")(x)
x = BatchNormalization()(x)
x = layers.MaxPooling2D()(x)
x = layers.Dropout(0.4)(x)

# Dense head
x = layers.Flatten()(x)
x = layers.Dense(256, activation="relu")(x)
x = BatchNormalization()(x)
x = layers.Dropout(0.5)(x)

# Outputs
piece_output = layers.Dense(len(pieces), activation="softmax", name="piece")(x)
color_output = layers.Dense(len(colors), activation="softmax", name="color")(x)

model = models.Model(inputs=inputs, outputs=[piece_output, color_output])

model.compile(
    optimizer="adam",
    loss={
        "piece": "sparse_categorical_crossentropy",
        "color": "sparse_categorical_crossentropy",
    },
    metrics={
        "piece": "accuracy",
        "color": "accuracy",
    },
)

model.summary()

# TODO: Train the model
history = model.fit(
    X_train,
    {"piece": y_piece_train, "color": y_color_train},
    validation_data=(X_val, {"piece": y_piece_val, "color": y_color_val}),
    batch_size=BATCH_SIZE,
    epochs=EPOCHS,
    callbacks=[callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)],
)

# Save model
save_path = os.path.join(OUTPUT_DIR, MODEL_NAME)
model.save(save_path)  # creates a SavedModel directory
print(f"✅ Model saved at {save_path}")

# Prediction helper
def predict_image(img_path, model):
    img = load_image(img_path)
    arr = np.expand_dims(img, axis=0)
    piece_pred, color_pred = model.predict(arr)
    piece = pieces[np.argmax(piece_pred[0])]
    color = colors[np.argmax(color_pred[0])]
    return piece, color

# Example:
# print(predict_image("flattened_dataset/pawn/black/Piece_1.png", model))