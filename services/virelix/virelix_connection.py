from sqlalchemy.orm import Session
from fastapi import BackgroundTasks, Request, status

from app.schema import GlobalResponse
from services import UserServices



class VirelixConnection:
    def __init__(
        self,
        db: Session,
        background_tasks: BackgroundTasks,
        request: Request,
        authorization: str
    ):
        self.db = db
        self.background_tasks = background_tasks
        self.request = request
        self.authorization = authorization


    def create_virelix_services(self, user_id: str):
        if not user_id:
            return GlobalResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False,
                message="User ID is required in header",
                data={}
            )

        service_slug: str = ""

        service_name = payload.service_name or next(
            (service["service_name"] for service in services if service["service_slug"] == service_slug),
            " ".join(part.capitalize() for part in service_slug.split("-"))
        )

        created = UserServices.add_user_service(
            db=self.db,
            user_id=user_id,
            service_slug=service_slug,
            service_name=service_name,
            service_details=payload.service_details,
            service_status=payload.status,
        )

        return GlobalResponse(
            status_code=200,
            success=True,
            action="add_service",
            message="Service added successfully",
            data={"service": created},
            next_step={}
        )

    def deactive_virelix_services(self, user_id: str):
        pass

    def delete_virelix_services(self, user_id: str):
        pass