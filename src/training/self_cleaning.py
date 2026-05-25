import numpy as np
import torch
from torch.utils.data import DataLoader
from src.training.model import LSTMAutoencoder, reconstruction_error
from src.training.dataset import SlidingWindowDataset
from src.training.train import train_model
import logging

logger = logging.getLogger(__name__)


def self_cleaning_train(data: np.ndarray, n_sensors: int,
                        hidden_dim: int = 64, window_size: int = 128,
                        clean_fraction: float = 0.05, device: str = "cpu",
                        **train_kwargs) -> LSTMAutoencoder:
    # Round 1: train on all data
    logger.info("self-cleaning round 1: training on full data (%d points)", len(data))
    model = train_model(data, n_sensors, hidden_dim, window_size,
                        device=device, **train_kwargs)

    # Score all windows
    model.eval()
    dataset = SlidingWindowDataset(data, window_size=window_size, stride=32)
    loader = DataLoader(dataset, batch_size=64)
    errors = []
    with torch.no_grad():
        for batch in loader:
            batch = batch.to(device)
            recon, _ = model(batch)
            err = reconstruction_error(batch, recon, per_sensor=False)
            errors.extend(err.cpu().numpy().tolist())

    # Remove top clean_fraction windows
    threshold = np.percentile(errors, (1 - clean_fraction) * 100)
    keep_mask = np.array(errors) <= threshold
    keep_indices = np.array(dataset._indices)[keep_mask]

    # Rebuild clean dataset
    clean_windows = []
    for idx in keep_indices:
        clean_windows.append(data[idx:idx + window_size])
    if len(clean_windows) == 0:
        logger.warning("self-cleaning removed all windows, using original")
        return model

    clean_data = np.concatenate(clean_windows, axis=0)
    logger.info("self-cleaning round 2: %d/%d windows kept (removed %d)",
                len(clean_windows), len(errors), len(errors) - len(clean_windows))

    # Round 2
    return train_model(clean_data, n_sensors, hidden_dim, window_size,
                       device=device, **train_kwargs)
