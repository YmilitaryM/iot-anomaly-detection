import numpy as np
import torch
from torch.utils.data import Dataset


class SlidingWindowDataset(Dataset):
    def __init__(self, data: np.ndarray, window_size: int = 128,
                 stride: int = 32):
        # data: (n_timesteps, n_sensors)
        self.data = torch.FloatTensor(data)
        self.window_size = window_size
        self.stride = stride
        n_windows = (len(data) - window_size) // stride + 1
        if n_windows <= 0:
            raise ValueError(
                f"Data length ({len(data)}) must be >= window_size ({window_size})"
            )
        self._indices = [i * stride for i in range(n_windows)]

    def __len__(self) -> int:
        return len(self._indices)

    def __getitem__(self, idx: int) -> torch.Tensor:
        start = self._indices[idx]
        return self.data[start:start + self.window_size]
