import asyncio
import time
from decimal import Decimal
from typing import Any, Dict, List, Optional
import httpx

from app.core.config import settings


class PayPalError(Exception):
    """Base exception for PayPal operations."""
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class PayPalAuthError(PayPalError):
    """Raised when PayPal authentication fails."""
    pass


class PayPalOrderCreationError(PayPalError):
    """Raised when creating an order on PayPal fails."""
    pass


class PayPalCaptureError(PayPalError):
    """Raised when capturing a payment on PayPal fails."""
    pass


class PayPalAmountMismatchError(PayPalCaptureError):
    """Raised when captured amount or currency does not match internal order."""
    pass


class PayPalTimeoutError(PayPalError):
    """Raised when a PayPal request times out ambiguously."""
    pass


class PayPalService:
    def __init__(
        self,
        base_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        timeout: float = 15.0,
    ):
        self._base_url = base_url
        self._client_id = client_id
        self._client_secret = client_secret
        self.timeout = timeout

        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0
        self._token_lock = asyncio.Lock()

    @property
    def base_url(self) -> str:
        url = self._base_url if self._base_url is not None else settings.paypal_base_url
        return url.rstrip("/")

    @property
    def client_id(self) -> str:
        return self._client_id if self._client_id is not None else settings.paypal_client_id

    @property
    def client_secret(self) -> str:
        return self._client_secret if self._client_secret is not None else settings.paypal_client_secret

    async def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Acquires or retrieves a cached OAuth 2.0 bearer token from PayPal Sandbox.
        Tokens are cached until 60 seconds before expiration.
        """
        if not self.client_id or not self.client_secret:
            raise PayPalAuthError("PayPal credentials not configured in backend environment.")

        async with self._token_lock:
            now = time.time()
            if not force_refresh and self._access_token and now < (self._token_expires_at - 60):
                return self._access_token

            token_url = f"{self.base_url}/v1/oauth2/token"
            auth = (self.client_id, self.client_secret)
            data = {"grant_type": "client_credentials"}
            headers = {
                "Accept": "application/json",
                "Accept-Language": "en_US",
            }

            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(token_url, data=data, auth=auth, headers=headers)
            except httpx.TimeoutException as e:
                raise PayPalTimeoutError(f"PayPal OAuth request timed out: {e}")
            except Exception as e:
                raise PayPalAuthError(f"Network error connecting to PayPal OAuth: {e}")

            if response.status_code == 401:
                raise PayPalAuthError("PayPal authentication failed: Invalid Client ID or Secret", status_code=401)
            elif response.status_code != 200:
                raise PayPalAuthError(
                    f"PayPal OAuth failed with status {response.status_code}",
                    status_code=response.status_code,
                    details={"status_code": response.status_code},
                )

            token_data = response.json()
            access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 32400)

            if not access_token:
                raise PayPalAuthError("PayPal OAuth response did not include access_token")

            self._access_token = access_token
            self._token_expires_at = now + float(expires_in)
            return self._access_token

    async def create_order(
        self,
        internal_order_id: str,
        total_amount: Decimal,
        currency: str,
        items: List[Dict[str, Any]],
        idempotency_key: str,
    ) -> Dict[str, Any]:
        """
        Creates an order on PayPal Sandbox Orders v2 API with intent CAPTURE.
        """
        token = await self.get_access_token()
        orders_url = f"{self.base_url}/v2/checkout/orders"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "PayPal-Request-Id": idempotency_key,
        }

        # Format items according to Orders v2 schema
        formatted_items = []
        for item in items:
            formatted_items.append({
                "name": str(item["name"])[:127],
                "unit_amount": {
                    "currency_code": currency,
                    "value": f"{Decimal(str(item['unit_price'])):.2f}",
                },
                "quantity": str(item["quantity"]),
                "sku": str(item["sku"])[:64],
                "category": "PHYSICAL_GOODS",
            })

        amount_str = f"{Decimal(str(total_amount)):.2f}"
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": str(internal_order_id),
                    "custom_id": str(internal_order_id),
                    "description": f"PayPilot AI Order {internal_order_id[:8]}",
                    "amount": {
                        "currency_code": currency,
                        "value": amount_str,
                        "breakdown": {
                            "item_total": {
                                "currency_code": currency,
                                "value": amount_str,
                            }
                        },
                    },
                    "items": formatted_items,
                }
            ],
            "application_context": {
                "brand_name": "PayPilot AI",
                "landing_page": "NO_PREFERENCE",
                "user_action": "PAY_NOW",
                "return_url": "https://example.com/return",
                "cancel_url": "https://example.com/cancel",
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(orders_url, json=payload, headers=headers)
        except httpx.TimeoutException as e:
            raise PayPalTimeoutError(f"PayPal order creation timed out: {e}")
        except Exception as e:
            raise PayPalOrderCreationError(f"Network error creating PayPal order: {e}")

        if response.status_code not in (200, 201):
            err_json = {}
            try:
                err_json = response.json()
            except Exception:
                pass
            name = err_json.get("name", "")
            desc = err_json.get("message", "")
            err_msg = f"PayPal order creation failed: {name}" if name else f"PayPal order creation failed with status {response.status_code}"
            if desc:
                err_msg += f" - {desc}"
            raise PayPalOrderCreationError(
                err_msg,
                status_code=response.status_code,
                details={"name": name, "status_code": response.status_code},
            )

        data = response.json()
        paypal_order_id = data.get("id")
        if not paypal_order_id:
            raise PayPalOrderCreationError("PayPal order creation response missing order 'id'")

        return data

    async def get_order_details(self, paypal_order_id: str) -> Dict[str, Any]:
        """
        Retrieves order details from PayPal for verification or reconciliation.
        """
        token = await self.get_access_token()
        url = f"{self.base_url}/v2/checkout/orders/{paypal_order_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
        except Exception as e:
            raise PayPalError(f"Failed to fetch PayPal order details: {e}")

        if response.status_code != 200:
            raise PayPalError(
                f"Failed to fetch PayPal order: HTTP {response.status_code}",
                status_code=response.status_code,
                details=response.text,
            )

        return response.json()

    async def capture_order(
        self,
        paypal_order_id: str,
        expected_amount: Decimal,
        expected_currency: str,
        idempotency_key: str,
    ) -> Dict[str, Any]:
        """
        Captures authorized payment on PayPal Sandbox.
        Uses stable idempotency key to prevent double charges on retries.
        Reconciles via get_order_details if network timeout occurs.
        """
        token = await self.get_access_token()
        capture_url = f"{self.base_url}/v2/checkout/orders/{paypal_order_id}/capture"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "PayPal-Request-Id": idempotency_key,
        }

        capture_response_data: Optional[Dict[str, Any]] = None

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(capture_url, json={}, headers=headers)

            if response.status_code in (200, 201):
                capture_response_data = response.json()
            elif response.status_code == 422:
                # Could be ORDER_ALREADY_CAPTURED - let's reconcile
                err_json = {}
                try:
                    err_json = response.json()
                except Exception:
                    pass
                details = err_json.get("details", [])
                issue = details[0].get("issue") if details else ""
                desc = details[0].get("description") if details else ""
                if issue == "ORDER_ALREADY_CAPTURED":
                    order_info = await self.get_order_details(paypal_order_id)
                    capture_response_data = order_info
                else:
                    err_msg = f"PayPal capture rejected: {issue}" if issue else f"PayPal capture rejected (HTTP 422)"
                    if desc:
                        err_msg += f" - {desc}"
                    raise PayPalCaptureError(
                        err_msg,
                        status_code=422,
                        details={"issue": issue, "status_code": 422},
                    )
            else:
                err_json = {}
                try:
                    err_json = response.json()
                except Exception:
                    pass
                name = err_json.get("name", "")
                desc = err_json.get("message", "")
                err_msg = f"PayPal capture failed: {name}" if name else f"PayPal capture failed with HTTP {response.status_code}"
                if desc:
                    err_msg += f" - {desc}"
                raise PayPalCaptureError(
                    err_msg,
                    status_code=response.status_code,
                    details={"name": name, "status_code": response.status_code},
                )

        except httpx.TimeoutException:
            # Network timeout: reconcile with PayPal order state before failing or re-trying
            try:
                order_info = await self.get_order_details(paypal_order_id)
                if order_info.get("status") == "COMPLETED":
                    capture_response_data = order_info
                else:
                    raise PayPalTimeoutError(
                        "PayPal capture timed out and order is not yet marked COMPLETED. Reconcile later."
                    )
            except Exception as reconcile_err:
                raise PayPalTimeoutError(
                    f"PayPal capture timed out and reconciliation failed: {reconcile_err}"
                )

        # Validate captured response payload
        return self._validate_and_extract_capture(
            data=capture_response_data,
            expected_amount=expected_amount,
            expected_currency=expected_currency,
            expected_order_id=paypal_order_id,
        )

    def _validate_and_extract_capture(
        self,
        data: Dict[str, Any],
        expected_amount: Decimal,
        expected_currency: str,
        expected_order_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Strictly verifies that:
        1. Order ID matches expected PayPal order ID (if provided).
        2. PayPal order status is COMPLETED.
        3. Valid capture record exists with status COMPLETED.
        4. Captured amount and currency match internal order expectations.
        """
        if expected_order_id:
            response_order_id = data.get("id")
            if response_order_id and response_order_id != expected_order_id:
                raise PayPalCaptureError(
                    f"PayPal order ID mismatch: expected {expected_order_id}, got {response_order_id}",
                    status_code=400,
                )

        order_status = data.get("status")
        if order_status != "COMPLETED":
            raise PayPalCaptureError(
                f"PayPal order status is '{order_status}', expected 'COMPLETED'",
                status_code=400,
            )

        purchase_units = data.get("purchase_units", [])
        if not purchase_units:
            raise PayPalCaptureError("PayPal capture response missing 'purchase_units'")

        payments = purchase_units[0].get("payments", {})
        captures = payments.get("captures", [])

        if not captures:
            raise PayPalCaptureError("PayPal capture response did not contain capture records")

        primary_capture = captures[0]
        capture_id = primary_capture.get("id")
        capture_status = primary_capture.get("status")

        if not capture_id:
            raise PayPalCaptureError("PayPal capture record missing capture 'id'")

        if capture_status != "COMPLETED":
            raise PayPalCaptureError(
                f"PayPal capture status is '{capture_status}', expected 'COMPLETED'",
                status_code=400,
            )

        amount_info = primary_capture.get("amount", {})
        captured_value = amount_info.get("value")
        captured_currency = amount_info.get("currency_code")

        expected_str = f"{Decimal(str(expected_amount)):.2f}"

        if captured_currency != expected_currency:
            raise PayPalAmountMismatchError(
                f"Currency mismatch: expected {expected_currency}, got {captured_currency}"
            )

        if captured_value != expected_str:
            raise PayPalAmountMismatchError(
                f"Amount mismatch: expected {expected_str}, got {captured_value}"
            )

        return {
            "capture_id": capture_id,
            "status": "COMPLETED",
            "amount": captured_value,
            "currency": captured_currency,
            "captured_at": primary_capture.get("create_time"),
            "raw_response": data,
        }


paypal_service = PayPalService()
