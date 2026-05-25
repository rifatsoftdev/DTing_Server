import cloudinary
import cloudinary.uploader

from sqlalchemy.orm import Session

from app.constants import ENV
from app.model import CloudinaryHistory


class CloudinaryStorage:
    def __init__(self, db: Session):
        self.db = db
        cloudinary.config(
            cloud_name=ENV.CLOUDINARY_CLOUD_NAME,
            api_key=ENV.CLOUDINARY_API_KEY,
            api_secret=ENV.CLOUDINARY_API_SECRET
        )
    
    def __save(self, public_id: str, secure_url: str, file_type: str):
        try:
            cloudinaryHistory = CloudinaryHistory(
                public_id=public_id,
                secure_url=secure_url,
                file_type=file_type
            )
            self.db.add(cloudinaryHistory)
            self.db.commit()
            self.db.refresh(cloudinaryHistory)

        except Exception as e:
            print(e)
    
    def __delete(self, public_id: str = None, secure_url: str = None):
        try:
            if (public_id):
                cloudinaryHistory = self.db.query(CloudinaryHistory).filter(
                    CloudinaryHistory.public_id == public_id
                ).first()

            elif (secure_url):
                cloudinaryHistory = self.db.query(CloudinaryHistory).filter(
                    CloudinaryHistory.secure_url == secure_url
                ).first()
            
            else:
                print("No public_id or secure_url provided for deletion")
                return
            
            
            if cloudinaryHistory:
                self.db.delete(cloudinaryHistory)
                
            self.db.commit()
            self.db.refresh(cloudinaryHistory)
            
        except Exception as e:
            print(e)

    def upload_file(self, file_path, public_id, file_type="image") -> dict | None:
        """
        file_type: image | video | raw
        """
        try:
            result = cloudinary.uploader.upload(
                file_path,
                resource_type=file_type,
                public_id=public_id,
                overwrite=True
            )
            self.__save(public_id=result["public_id"], secure_url=result["secure_url"], file_type=file_type)

            return {
                "public_id": result["public_id"],
                "url": result["secure_url"],
                "secure_url": result["secure_url"]
            }
        except Exception as e:
            print(f"Cloudinary upload error: {e}")
            return None
    
    def delete_file(self, public_id, file_type="image") -> dict | None:
        """
        public_id: id obtained during upload
        """
        try:
            result = cloudinary.uploader.destroy(
                public_id,
                resource_type=file_type
            )
            self.__delete(public_id=public_id)

            return result
        except Exception as e:
            print(f"Cloudinary delete error: {e}")
            return None
            
