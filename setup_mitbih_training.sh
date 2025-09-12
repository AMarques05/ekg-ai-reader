#!/bin/bash
# Setup script to download MIT-BIH data and retrain the autoencoder

echo "Setting up MIT-BIH Normal Sinus Rhythm training data..."

# Install required packages
echo "Installing required packages..."
pip install wfdb requests

# Download MIT-BIH data
echo "Downloading MIT-BIH Normal Sinus Rhythm data..."
cd backend/data
python download_mitbih.py

# Go back to root and create training datasets
echo "Creating training datasets..."
cd ../..
python -m backend.training.make_datasets

# Train the autoencoder
echo "Training autoencoder with MIT-BIH data..."
python -m backend.training.train_autoencoder

echo "Training complete! Your autoencoder is now trained on MIT-BIH Normal Sinus Rhythm data."