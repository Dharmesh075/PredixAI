"""
Modern PyTorch Deep Learning Architectures for Predictive Maintenance:
1. LSTM Classifier (Sequence Failure Prediction)
2. LSTM Regressor (Remaining Useful Life Prediction)
3. Autoencoder (Unsupervised Anomaly Detection via Reconstruction Error)
"""

import torch
import torch.nn as nn
from typing import Tuple


class LSTMClassifier(nn.Module):
    """
    Bi-directional / Multi-layer LSTM for binary failure classification
    (predicting if failure will occur within the lookahead window).
    """
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 64,
        num_layers: int = 2,
        dropout: float = 0.2,
        bidirectional: bool = False
    ):
        super(LSTMClassifier, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        num_directions = 2 if bidirectional else 1

        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
            bidirectional=bidirectional
        )

        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * num_directions, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch_size, seq_len, input_dim)
        out, _ = self.lstm(x)
        # Take the hidden state of the last time step
        last_out = out[:, -1, :]
        logits = self.fc(last_out)
        return logits.squeeze(-1)


class LSTMRegressor(nn.Module):
    """
    Multi-layer LSTM for Remaining Useful Life (RUL) Regression.
    """
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 64,
        num_layers: int = 2,
        dropout: float = 0.2,
        bidirectional: bool = False
    ):
        super(LSTMRegressor, self).__init__()
        num_directions = 2 if bidirectional else 1

        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
            bidirectional=bidirectional
        )

        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * num_directions, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.lstm(x)
        last_out = out[:, -1, :]
        rul_pred = self.fc(last_out)
        return rul_pred.squeeze(-1)


class AutoencoderAnomalyDetector(nn.Module):
    """
    Deep Autoencoder for detecting anomalous sensor readings based on reconstruction error.
    Trained on early, healthy engine cycles.
    """
    def __init__(self, input_dim: int, latent_dim: int = 16):
        super(AutoencoderAnomalyDetector, self).__init__()

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 48),
            nn.BatchNorm1d(48),
            nn.LeakyReLU(0.2),
            nn.Linear(48, 24),
            nn.BatchNorm1d(24),
            nn.LeakyReLU(0.2),
            nn.Linear(24, latent_dim)
        )

        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 24),
            nn.BatchNorm1d(24),
            nn.LeakyReLU(0.2),
            nn.Linear(24, 48),
            nn.BatchNorm1d(48),
            nn.LeakyReLU(0.2),
            nn.Linear(48, input_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        latent = self.encoder(x)
        reconstruction = self.decoder(latent)
        return reconstruction

    def compute_anomaly_score(self, x: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            recon = self.forward(x)
            # Mean Squared Error per sample across features
            error = torch.mean((x - recon) ** 2, dim=-1)
            return error
