import pytest
import numpy as np
import torch
from src.training.dataset import SlidingWindowDataset
from src.training.model import LSTMAutoencoder
from src.training.train import train_model
from src.training.self_cleaning import self_cleaning_train
from src.training.export_onnx import export_to_onnx


class TestSlidingWindowDataset:
    def test_len_and_getitem_shapes(self):
        data = np.random.randn(200, 3).astype(np.float32)
        ds = SlidingWindowDataset(data, window_size=64, stride=32)
        expected = max(0, (200 - 64) // 32 + 1)  # 5
        assert len(ds) == expected
        item = ds[0]
        assert item.shape == (64, 3)

    def test_stride_behavior(self):
        data = np.arange(100, dtype=np.float32).reshape(-1, 1)
        ds = SlidingWindowDataset(data, window_size=10, stride=10)
        assert len(ds) == 10
        assert ds[0][0, 0] == 0.0
        assert ds[1][0, 0] == 10.0


class TestTrainModel:
    def test_returns_lstm_autoencoder(self):
        t = np.linspace(0, 4 * np.pi, 300)
        data = np.column_stack([np.sin(t), np.cos(t)]).astype(np.float32)
        model = train_model(data, n_sensors=2, hidden_dim=16,
                           window_size=64, epochs=5, lr=0.01,
                           device="cpu")
        assert isinstance(model, LSTMAutoencoder)

    def test_loss_decreases(self):
        t = np.linspace(0, 8 * np.pi, 1000)
        data = np.column_stack([np.sin(t), np.cos(t)]).astype(np.float32)
        optim_params = {"lr": 0.01, "epochs": 15, "hidden_dim": 16, "window_size": 64, "device": "cpu"}
        model = train_model(data, n_sensors=2, **optim_params)
        model.eval()
        with torch.no_grad():
            x = torch.FloatTensor(data[:64]).unsqueeze(0)
            recon, _ = model(x)
            loss = torch.nn.functional.mse_loss(recon, x)
            assert loss.item() < 0.2


class TestSelfCleaningTrain:
    def test_returns_lstm_autoencoder(self):
        rng = np.random.RandomState(42)
        data = rng.randn(500, 3).astype(np.float32)
        model = self_cleaning_train(
            data, n_sensors=3, hidden_dim=16,
            window_size=64, clean_fraction=0.05,
            epochs=3, lr=0.01, device="cpu",
        )
        assert isinstance(model, LSTMAutoencoder)


class TestExportOnnx:
    def test_creates_file(self, tmp_path):
        model = LSTMAutoencoder(n_sensors=2, hidden_dim=16, window_size=32)
        path = str(tmp_path / "model.onnx")
        export_to_onnx(model, path, window_size=32, n_sensors=2)
        assert tmp_path.joinpath("model.onnx").exists()
        assert tmp_path.joinpath("model.onnx").stat().st_size > 0
