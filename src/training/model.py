import torch
import torch.nn as nn


class LSTMAutoencoder(nn.Module):
    def __init__(self, n_sensors: int, hidden_dim: int = 64,
                 num_layers: int = 2, dropout: float = 0.2,
                 window_size: int = 128):
        super().__init__()
        self.n_sensors = n_sensors
        self.hidden_dim = hidden_dim
        self.window_size = window_size

        self.encoder = nn.LSTM(
            input_size=n_sensors, hidden_size=hidden_dim,
            num_layers=num_layers, batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
            bidirectional=True,
        )
        self.enc_proj = nn.Linear(hidden_dim * 2, hidden_dim)

        self.decoder = nn.LSTM(
            input_size=hidden_dim, hidden_size=hidden_dim,
            num_layers=num_layers, batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.output_layer = nn.Linear(hidden_dim, n_sensors)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        # x: (batch, window_size, n_sensors)
        batch_size = x.size(0)

        # Encode
        enc_out, (h_n, c_n) = self.encoder(x)
        # Use last hidden state from both directions
        h_forward = h_n[-2, :, :]  # last layer forward
        h_backward = h_n[-1, :, :]  # last layer backward
        h_cat = torch.cat([h_forward, h_backward], dim=-1)
        z = self.enc_proj(h_cat)  # (batch, hidden_dim)

        # Decode: repeat z for each time step
        z_repeated = z.unsqueeze(1).repeat(1, self.window_size, 1)
        dec_out, _ = self.decoder(z_repeated)
        reconstruction = self.output_layer(dec_out)

        return reconstruction, z


def reconstruction_error(x: torch.Tensor, x_hat: torch.Tensor,
                         per_sensor: bool = True) -> torch.Tensor:
    """MSE per sensor (batch, n_sensors) or global."""
    se = (x - x_hat) ** 2
    if per_sensor:
        return se.mean(dim=1)  # (batch, n_sensors)
    return se.mean(dim=[1, 2])  # (batch,)
