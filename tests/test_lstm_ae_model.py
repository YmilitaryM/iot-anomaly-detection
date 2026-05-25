import pytest
import torch
import numpy as np
from src.training.model import LSTMAutoencoder, reconstruction_error


class TestLSTMAutoencoder:
    @pytest.fixture
    def model(self):
        return LSTMAutoencoder(n_sensors=3, hidden_dim=32, window_size=64)

    def test_forward_shape(self, model):
        x = torch.randn(4, 64, 3)  # batch=4, window=64, sensors=3
        recon, latent = model(x)
        assert recon.shape == (4, 64, 3)
        assert latent.shape == (4, 32)

    def test_reconstruction_error_per_sensor(self):
        x = torch.ones(2, 10, 3)
        x_hat = x.clone()
        x_hat[:, :, 0] += 1.0  # error in sensor 0
        err = reconstruction_error(x, x_hat, per_sensor=True)
        assert err.shape == (2, 3)
        assert err[0, 0] > err[0, 1]

    def test_overfit_simple_signal(self, model):
        """Model should easily overfit a simple sine wave."""
        t = np.linspace(0, 8 * np.pi, 1000)
        data = np.column_stack([
            np.sin(t),
            np.cos(t),
            np.sin(t + np.pi / 4),
        ]).astype(np.float32)

        from src.training.train import train_model
        trained = train_model(data, n_sensors=3, hidden_dim=16,
                             window_size=64, epochs=50, lr=0.01,
                             device="cpu")
        trained.eval()
        with torch.no_grad():
            x = torch.FloatTensor(data[:64]).unsqueeze(0)
            recon, _ = trained(x)
            loss = torch.nn.functional.mse_loss(recon, x)
            assert loss.item() < 0.1  # should fit simple sine well
