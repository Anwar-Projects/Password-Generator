"""QR code output formatter."""

from io import BytesIO
from pathlib import Path
from typing import Optional

import qrcode
from qrcode.image.pil import PilImage

from .base import OutputFormatter, PasswordRecord


class QRFormatter(OutputFormatter):
    """Format passwords as QR codes."""
    
    def __init__(
        self,
        box_size: int = 10,
        border: int = 4,
        error_correction: str = "M",
        image_format: str = "PNG",
    ):
        """Initialize QR formatter.
        
        Args:
            box_size: Size of each QR box.
            border: Border size.
            error_correction: Error correction level (L, M, Q, H).
            image_format: Output image format.
        """
        self.box_size = box_size
        self.border = border
        self.image_format = image_format.upper()
        
        ec_levels = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H,
        }
        self.error_correction = ec_levels.get(error_correction, qrcode.constants.ERROR_CORRECT_M)
    
    @property
    def format_name(self) -> str:
        return "qr"
    
    @property
    def file_extension(self) -> str:
        return ".png"
    
    def _create_qr(self, data: str) -> PilImage:
        """Create QR code image."""
        qr = qrcode.QRCode(
            version=None,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        return qr.make_image(fill_color="black", back_color="white")
    
    def format_single(self, record: PasswordRecord) -> str:
        """Save single password as QR code file path."""
        # Returns path info since actual file is saved
        return f"QR code for: {record.password[:4]}{'*' * (len(record.password) - 4)}"
    
    def format_batch(self, records: list[PasswordRecord]) -> str:
        """Format batch as list of paths."""
        return "\n".join(
            self.format_single(r) for r in records
        )
    
    def save_qr(
        self,
        password: str,
        output_path: str | Path,
        include_text: bool = True,
    ) -> Path:
        """Save QR code to file.
        
        Args:
            password: Password to encode.
            output_path: Output file path.
            include_text: Include password text in image.
            
        Returns:
            Path to saved file.
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        img = self._create_qr(password)
        
        if include_text:
            # Add password label at bottom
            from PIL import Image, ImageDraw, ImageFont
            
            # Create base image
            width, height = img.size
            new_height = height + 30
            new_img = Image.new('RGB', (width, new_height), 'white')
            new_img.paste(img, (0, 0))
            
            # Add text
            draw = ImageDraw.Draw(new_img)
            
            # Try to use a nice font, fall back to default
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            except:
                font = ImageFont.load_default()
            
            text = f"Password: {password[:4]}{'*' * (len(password) - 4)}"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = (width - text_width) // 2
            draw.text((text_x, height + 5), text, fill="black", font=font)
            
            img = new_img
        
        img.save(path, format=self.image_format)
        return path
    
    def to_base64(self, password: str) -> str:
        """Generate QR code as base64 string.
        
        Args:
            password: Password to encode.
            
        Returns:
            Base64 encoded image.
        """
        import base64
        
        img = self._create_qr(password)
        buffer = BytesIO()
        img.save(buffer, format=self.image_format)
        return base64.b64encode(buffer.getvalue()).decode()
