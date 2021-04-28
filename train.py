import argparse

import pytorch_lightning as pl
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from pytorch_lightning.callbacks.model_checkpoint import ModelCheckpoint

from src.model import FlexNet

import sys
import logging


# python train.py --auto_scale_batch_size power --gpus -1


def parse_program_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset",
        type=str,
        default="datasets/dataset.dat",
        help="Path to the dataset to be used for training, validating and evaluating",
    )

    parser.add_argument(
        "--patience",
        type=int,
        default=5,
        help="Patience for the EarlyStopping callback of PyTorch Lightning",
    )

    parser.add_argument(
        "--batch_size",
        type=int,
        default=512,
        help="Batch size for the dataset provided."
    )

    parser.add_argument(
        "--save_path",
        type=str,
        default="model_checkpoints",
        help="Save path for the model."
    )

    return parser


def main() -> None:
    parser = parse_program_args()
    parser = pl.Trainer.add_argparse_args(parser)
    args = parser.parse_args()

    model = FlexNet(args.dataset, args.batch_size)
    trainer = pl.Trainer.from_argparse_args(
        args,
        callbacks=[
            EarlyStopping("val_loss", patience=args.patience),
            ModelCheckpoint(
                dirpath=args.save_path, save_top_k=1, monitor="val_loss",
            ),
        ],
        progress_bar_refresh_rate=0
    )

    logger = logging.getLogger("pytorch_lightning")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.FileHandler("output.log"))
    trainer.tune(model)  # batch size
    trainer.fit(model)
    trainer.test(model)
    print("End of training.")


if __name__ == "__main__":
    main()