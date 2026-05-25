import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
from src.training.model import LSTMAutoencoder, reconstruction_error
from src.training.dataset import SlidingWindowDataset
import logging

logger = logging.getLogger(__name__)


def train_model(data: np.ndarray, n_sensors: int, hidden_dim: int = 64,
                window_size: int = 128, epochs: int = 50,
                batch_size: int = 64, lr: float = 0.001,
                patience: int = 10, device: str = "cpu") -> LSTMAutoencoder:
    model = LSTMAutoencoder(n_sensors=n_sensors, hidden_dim=hidden_dim,
                            window_size=window_size).to(device)
    dataset = SlidingWindowDataset(data, window_size=window_size, stride=32)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    best_loss = float("inf")
    best_state = None
    patience_counter = 0

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        for batch in loader:
            batch = batch.to(device)
            optimizer.zero_grad()
            recon, _ = model(batch)
            loss = criterion(recon, batch)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(loader)
        logger.info("epoch %d/%d loss=%.6f", epoch + 1, epochs, avg_loss)

        if avg_loss < best_loss * 0.999:
            best_loss = avg_loss
            patience_counter = 0
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        else:
            patience_counter += 1
            if patience_counter >= patience:
                logger.info("early stopping at epoch %d", epoch + 1)
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    return model
