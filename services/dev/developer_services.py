from fastapi import HTTPException, Request, BackgroundTasks, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import or_
from decimal import Decimal

from app.constants import String, AnsiColor
from app.enums import TransactionType, PaymentMethods, TransactionDirection, TransactionStatus, NotificationType
from app.schema import PaymentRequest, GlobalResponse, GlobalRequest
from app.model import DevTable, UserTable
from app.utils import Generators, Helpers

from services.auth.user_verification import UserVerificationService
from services.notification.noticication_services import NotificationServices, NotificationData
from app.router.notify_router import check_online_user


class DeveloperServices:
    # Shared dictionary to store active developer websocket connections
    developer_connections = {}

    @staticmethod
    async def send_dev_event(user_id: str, payload: dict):
        ws = DeveloperServices.developer_connections.get(user_id)
        if ws:
            await ws.send_json(payload)

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
    
    def auto_payment(self, payload: PaymentRequest):
        try:
            if payload.amount <= 0:
                raise HTTPException(status_code=400, detail="Invalid amount")

            developer = self.db.query(DevTable).filter(
                DevTable.user_id == payload.user_id,
                DevTable.api_key == payload.api_key,
                DevTable.secret_key == payload.secret_key,
                DevTable.status == True
            ).first()

            if not developer:
                raise HTTPException(status_code=403, detail="Invalid developer credentials")

            dev_user = self.db.query(UserTable).filter(
                UserTable.user_id == payload.user_id
            ).first()

            if not dev_user:
                raise HTTPException(status_code=404, detail="Developer user not found")

            account = payload.user_account
            conditions = [
                UserTable.phone_number == account,
                UserTable.email_address == account,
                UserTable.user_id == account
            ]
            if account.startswith("880") and len(account) > 3:
                conditions.append(UserTable.phone_number == account[3:])

            payer = self.db.query(UserTable).filter(or_(*conditions)).first()

            if not payer:
                raise HTTPException(status_code=404, detail=String.USER_NOT_FOUND)

            if payer.user_id == dev_user.user_id:
                raise HTTPException(status_code=400, detail="Sender and receiver cannot be same")

            payer_wallet = self.db.query(WalletTable).filter(
                WalletTable.user_id == payer.user_id
            ).first()

            dev_wallet = self.db.query(WalletTable).filter(
                WalletTable.user_id == dev_user.user_id
            ).first()

            if not payer_wallet or not dev_wallet:
                raise HTTPException(status_code=404, detail=String.WALLET_NOT_FOUND)

            amount = Decimal(str(payload.amount))
            if payer_wallet.balance < amount:
                raise HTTPException(status_code=400, detail=String.INSUFFICIENT_BALANCE)

            transaction_id = Generators.generate_transaction_id()

            sender_account = payer.country_code + payer.phone_number if payer.phone_number else (payer.email_address or payer.user_id)
            receiver_account = dev_user.country_code + dev_user.phone_number if dev_user.phone_number else (dev_user.email_address or dev_user.user_id)

            transaction = TransactionTable(
                transaction_id=transaction_id,
                transaction_type=TransactionType.SENDMONEY,
                method=PaymentMethods.WALLET,
                sender_user_id=payer.user_id,
                sender_account=sender_account,
                receiver_user_id=dev_user.user_id,
                receiver_account=receiver_account,
                account_id=None,
                account_name=None,
                currency="BDT",
                amount=amount,
                service_charge=Decimal("0"),
                reference=payload.refarence or "N/A",
                meta_data={
                    "developer_user_id": dev_user.user_id,
                    "developer_api_key": developer.api_key
                },
                direction=TransactionDirection.OUT,
                status=TransactionStatus.SUCCESS
            )

            self.db.add(transaction)
            self.db.flush()

            payer_wallet.balance -= amount
            payer_wallet.last_updated = Helpers.utc6dhaka()

            dev_wallet.balance += amount
            dev_wallet.last_updated = Helpers.utc6dhaka()

            self.db.commit()
            self.db.refresh(transaction)

            # Notify the Payer
            notificationServices = NotificationServices(
                db=self.db,
                background_tasks=self.background_tasks
            )
            notificationServices.send_notification(
                NotificationData(
                    user_id=payer.user_id,
                    template="transaction.payment",
                    context={
                        "amount": amount,
                        "receiver": receiver_account,
                        "provider": dev_user.full_name,
                        "reference": payload.refarence or "N/A",
                        "transaction_id": transaction_id,
                    },
                    noty_type=NotificationType.DEFAULT,
                    email=False,
                    sms=False,
                    push=True,
                )
            )

            # Notify Developer via WebSocket
            self.background_tasks.add_task(
                DeveloperServices.send_dev_event,
                dev_user.user_id,
                {
                    "event": "payment_success",
                    "transaction_id": transaction_id,
                    "amount": float(amount),
                    "currency": "BDT",
                    "status": TransactionStatus.SUCCESS.value,
                    "reference": payload.refarence,
                    "payer_user_id": payer.user_id,
                    "payer_account": sender_account,
                    "created_at": transaction.created_at.isoformat() if transaction.created_at else None
                }
            )

            return GlobalResponse(
                success=True,
                message="Payment successful",
                data={
                    "transaction_id": transaction_id,
                    "amount": float(amount),
                    "status": TransactionStatus.SUCCESS.value
                }
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)
    
    async def dev_connect(self, websocket: WebSocket, user_id: str):
        api_key = websocket.query_params.get("api_key")
        secret_key = websocket.query_params.get("secret_key")

        if not api_key or not secret_key:
            await websocket.close(code=1008)
            return

        try:
            developer = self.db.query(DevTable).filter(
                DevTable.user_id == user_id,
                DevTable.api_key == api_key,
                DevTable.secret_key == secret_key,
                DevTable.status == True
            ).first()

            if not developer:
                await websocket.close(code=1008)
                return

            await websocket.accept()
            DeveloperServices.developer_connections[user_id] = websocket

            try:
                while True:
                    await websocket.receive_text()
            except WebSocketDisconnect:
                DeveloperServices.developer_connections.pop(user_id, None)
                print(f"{AnsiColor.GREEN}INFO{AnsiColor.RESET}:     developer {user_id} disconnected")
        except Exception as e:
            DeveloperServices.developer_connections.pop(user_id, None)
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            try:
                await websocket.close(code=1011)
            except Exception:
                pass

    def request_developer(self, payload: GlobalRequest):
        try:
            user_verification = UserVerificationService(self.db)
            user = user_verification.verify_user(
                user_id=payload.user_id,
                access_token=payload.access_token,
                device_id=payload.device_id,
                device_uuid=payload.device_uuid,
                password=None
            )

            existing = self.db.query(DevTable).filter(
                DevTable.user_id == user.user_id
            ).first()

            if existing:
                message = "Developer already approved" if existing.status else "Developer request pending"
                return GlobalResponse(
                    success=True,
                    message=message,
                    data={
                        "api_key": existing.api_key,
                        "secret_key": existing.secret_key,
                        "status": existing.status
                    }
                )

            api_key = "DEVAPI" + Generators.generate_id()
            secret_key = "DEVSEC" + Generators.generate_id()

            dev = DevTable(
                user_id=user.user_id,
                api_key=api_key,
                secret_key=secret_key,
                status=False
            )
            self.db.add(dev)
            self.db.commit()
            self.db.refresh(dev)

            return GlobalResponse(
                success=True,
                message="Developer request submitted",
                data={
                    "api_key": dev.api_key,
                    "secret_key": dev.secret_key,
                    "status": dev.status
                }
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)


    def cancel_developer(self, payload: GlobalRequest):
        try:
            user_verification = UserVerificationService(self.db)
            user = user_verification.verify_user(
                user_id=payload.user_id,
                access_token=payload.access_token,
                device_id=payload.device_id,
                device_uuid=payload.device_uuid,
                password=None
            )

            dev = self.db.query(DevTable).filter(
                DevTable.user_id == user.user_id
            ).first()

            if not dev:
                raise HTTPException(status_code=404, detail="Developer request not found")

            dev.status = False
            dev.updated_at = Helpers.utc6dhaka()
            self.db.commit()
            self.db.refresh(dev)

            return GlobalResponse(
                success=True,
                message="Developer request cancelled",
                data={
                    "api_key": dev.api_key,
                    "secret_key": dev.secret_key,
                    "status": dev.status
                }
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)
