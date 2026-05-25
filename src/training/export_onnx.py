import torch
from src.training.model import LSTMAutoencoder


def export_to_onnx(model: LSTMAutoencoder, path: str,
                   window_size: int, n_sensors: int) -> None:
    model.eval()
    dummy_input = torch.randn(1, window_size, n_sensors)
    torch.onnx.export(
        model, dummy_input, path,
        input_names=["input"],
        output_names=["reconstruction", "latent"],
        dynamic_axes={"input": {0: "batch"},
                      "reconstruction": {0: "batch"},
                      "latent": {0: "batch"}},
        opset_version=17,
        dynamo=False,
    )
