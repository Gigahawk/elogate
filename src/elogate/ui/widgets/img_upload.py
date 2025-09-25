from pathlib import Path
from uuid import uuid4, UUID

import numpy as np
import identicons  # pyright: ignore [reportMissingTypeStubs]
from PIL import Image
from nicegui import ui
from nicegui.events import UploadEventArguments

from elogate.config import Settings


class NoImgUploaded(Exception):
    pass


def generate_identicon(txt: str, width: int = 250) -> Image.Image:
    icon = identicons.generate(txt)
    # Copied from identicons save source, can't be bothered to fix type issues
    i, j = icon.shape[:2]  # pyright: ignore [reportAny]
    h, w = width // i, width // j  # pyright: ignore [reportAny]
    large_icon = np.repeat(icon, repeats=h, axis=0)  # pyright: ignore [reportAny]
    large_icon = np.repeat(large_icon, repeats=w, axis=1)  # pyright: ignore [reportAny]
    return Image.fromarray(large_icon)


class ImgUpload(ui.upload):
    img_path: Path = Settings().resources_path / "images"

    def _handle_img_upload(self, evt: UploadEventArguments):
        self.image = Image.open(evt.content)

    def __init__(self, label: str):
        super().__init__(label=label, max_files=1, on_upload=self._handle_img_upload)
        _ = self.props("accept=.jpg,.jpeg,.png,.webp")
        self.image: Image.Image | None = None
        self.uuid: UUID | None = None

    def save(self):
        self.img_path.mkdir(parents=True, exist_ok=True)
        if self.image is None:
            raise NoImgUploaded
        self.uuid = uuid4()
        self.image.save(self.img_path / str(self.uuid), "WEBP")
        self.disable()
