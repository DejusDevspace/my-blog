"""Admin upload endpoints — authentication required."""

from fastapi import APIRouter, Depends, UploadFile

from app.auth.deps import get_current_admin
from app.schemas.common import MessageResponse
from app.schemas.upload import ImageDeleteRequest, ImageUploadResponse
from app.services import upload_service

router = APIRouter(
    prefix="/admin/uploads",
    tags=["Uploads (Admin)"],
    dependencies=[Depends(get_current_admin)],
)


@router.post("/image", response_model=ImageUploadResponse)
async def upload_image(file: UploadFile):
    """Upload an image to Cloudinary.

    Accepts a ``multipart/form-data`` file upload and returns the
    resulting CDN URL.
    """
    url = await upload_service.upload_image(file)
    return ImageUploadResponse(url=url)


@router.delete("/image", response_model=MessageResponse)
async def delete_image(data: ImageDeleteRequest):
    """Delete a previously uploaded image from Cloudinary.

    Accepts a JSON body with the Cloudinary ``url`` to remove.
    """
    await upload_service.delete_image(data.url)
    return MessageResponse(detail="Image deleted.")
