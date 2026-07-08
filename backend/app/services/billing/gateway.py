"""
Nexora Platform — Provider-Independent Payment Gateway Abstraction
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any
from app.config.logging import get_logger

logger = get_logger(__name__)


class PaymentGateway(ABC):
    """
    Abstract Payment Gateway Interface.
    De-couples business services from merchant APIs (e.g. Stripe, JazzCash, EasyPaisa).
    """

    @abstractmethod
    async def create_customer(self, organization_name: str, organization_email: str) -> str:
        """Register client organization as a merchant customer."""
        pass

    @abstractmethod
    async def charge(
        self,
        customer_id: str,
        amount_cents: int,
        currency: str,
        payment_method_token: str,
    ) -> dict[str, Any]:
        """Process a one-off payment charge."""
        pass

    @abstractmethod
    async def create_subscription(
        self,
        customer_id: str,
        price_code: str,
    ) -> dict[str, Any]:
        """Initiate recurring subscription model."""
        pass

    @abstractmethod
    async def cancel_subscription(self, provider_sub_id: str) -> dict[str, Any]:
        """Cancel an active subscription model."""
        pass

    @abstractmethod
    async def refund(self, transaction_id: str, amount_cents: int) -> dict[str, Any]:
        """Process a billing refund."""
        pass


class StripeProvider(PaymentGateway):
    """Stripe Payment Provider Sandbox integration."""

    async def create_customer(self, organization_name: str, organization_email: str) -> str:
        logger.info("stripe_create_customer", name=organization_name, email=organization_email)
        return f"cus_str_{uuid.uuid4().hex[:12]}"

    async def charge(
        self,
        customer_id: str,
        amount_cents: int,
        currency: str,
        payment_method_token: str,
    ) -> dict[str, Any]:
        logger.info("stripe_charge_processed", customer=customer_id, amount=amount_cents)
        return {
            "success": True,
            "transaction_id": f"ch_str_{uuid.uuid4().hex[:16]}",
            "provider": "stripe",
            "amount": amount_cents,
            "status": "succeeded",
        }

    async def create_subscription(
        self,
        customer_id: str,
        price_code: str,
    ) -> dict[str, Any]:
        logger.info("stripe_subscription_initiated", customer=customer_id, price=price_code)
        return {
            "success": True,
            "subscription_id": f"sub_str_{uuid.uuid4().hex[:16]}",
            "status": "active",
        }

    async def cancel_subscription(self, provider_sub_id: str) -> dict[str, Any]:
        logger.info("stripe_subscription_canceled", sub_id=provider_sub_id)
        return {"success": True, "status": "canceled"}

    async def refund(self, transaction_id: str, amount_cents: int) -> dict[str, Any]:
        logger.info("stripe_refund_processed", tx_id=transaction_id, amount=amount_cents)
        return {"success": True, "status": "succeeded"}


class JazzCashProvider(PaymentGateway):
    """JazzCash Mobile Wallet Payment Provider integration."""

    async def create_customer(self, organization_name: str, organization_email: str) -> str:
        logger.info("jazzcash_create_customer", name=organization_name)
        return f"cus_jc_{uuid.uuid4().hex[:12]}"

    async def charge(
        self,
        customer_id: str,
        amount_cents: int,
        currency: str,
        payment_method_token: str,
    ) -> dict[str, Any]:
        logger.info("jazzcash_wallet_charged", customer=customer_id, amount=amount_cents)
        return {
            "success": True,
            "transaction_id": f"tx_jc_{uuid.uuid4().hex[:16]}",
            "provider": "jazzcash",
            "amount": amount_cents,
            "status": "succeeded",
        }

    async def create_subscription(
        self,
        customer_id: str,
        price_code: str,
    ) -> dict[str, Any]:
        logger.info("jazzcash_sub_initiated", customer=customer_id)
        return {
            "success": True,
            "subscription_id": f"sub_jc_{uuid.uuid4().hex[:16]}",
            "status": "active",
        }

    async def cancel_subscription(self, provider_sub_id: str) -> dict[str, Any]:
        logger.info("jazzcash_sub_canceled", sub_id=provider_sub_id)
        return {"success": True, "status": "canceled"}

    async def refund(self, transaction_id: str, amount_cents: int) -> dict[str, Any]:
        logger.info("jazzcash_refund_processed", tx_id=transaction_id)
        return {"success": True, "status": "succeeded"}


class EasyPaisaProvider(PaymentGateway):
    """EasyPaisa Mobile Wallet Payment Provider integration."""

    async def create_customer(self, organization_name: str, organization_email: str) -> str:
        logger.info("easypaisa_create_customer", name=organization_name)
        return f"cus_ep_{uuid.uuid4().hex[:12]}"

    async def charge(
        self,
        customer_id: str,
        amount_cents: int,
        currency: str,
        payment_method_token: str,
    ) -> dict[str, Any]:
        logger.info("easypaisa_wallet_charged", customer=customer_id, amount=amount_cents)
        return {
            "success": True,
            "transaction_id": f"tx_ep_{uuid.uuid4().hex[:16]}",
            "provider": "easypaisa",
            "amount": amount_cents,
            "status": "succeeded",
        }

    async def create_subscription(
        self,
        customer_id: str,
        price_code: str,
    ) -> dict[str, Any]:
        logger.info("easypaisa_sub_initiated", customer=customer_id)
        return {
            "success": True,
            "subscription_id": f"sub_ep_{uuid.uuid4().hex[:16]}",
            "status": "active",
        }

    async def cancel_subscription(self, provider_sub_id: str) -> dict[str, Any]:
        logger.info("easypaisa_sub_canceled", sub_id=provider_sub_id)
        return {"success": True, "status": "canceled"}

    async def refund(self, transaction_id: str, amount_cents: int) -> dict[str, Any]:
        logger.info("easypaisa_refund_processed", tx_id=transaction_id)
        return {"success": True, "status": "succeeded"}
