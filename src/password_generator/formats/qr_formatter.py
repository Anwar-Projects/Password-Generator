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
            try:
                from PIL import Image, ImageDraw, ImageFont
                
                # Create base image with space for text
                width, height = img.size
                new_height = height + 30
                new_img = Image.new('RGB', (width, new_height), 'white')
                new_img.paste(img, (0, 0))
                
                # Add text
                draw = ImageDraw.Draw(new_img)
                
                # Try to use a nice font, fall back to default
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
                except Exception:
                    font = ImageFont.load_default()
                
                # Create masked password text
                text = f"Password: {password[:4]}{'*' * (len(password) - 4)}"
                
                # Simple center calculation - approximate
                text_x = max(10, (width - len(text) * 7) // 2)
                
                # Draw text without calculating bbox
                draw.text((text_x, height + 8), text, fill="black", font=font)
                
                img = new_img
            except Exception:
                # If text addition fails, just save the QR code
                pass
        
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
