"""
Sanos y Salvos — Notifications RabbitMQ Consumer
Listens for 'match.found' events and creates notifications.
"""

import json
import logging
import asyncio
import aio_pika

from app.config import RABBITMQ_URL
from app.services.notification_service import NotificationService

logger = logging.getLogger("notifications.consumer")

EXCHANGE_NAME = "sanos_y_salvos"
QUEUE_NAME = "notifications_queue"
ROUTING_KEY = "match.found"


async def on_message(message: aio_pika.IncomingMessage):
    """Process incoming match.found events."""
    async with message.process():
        try:
            match_data = json.loads(message.body.decode())
            logger.info(
                f"📥 Received match.found event — "
                f"Score: {match_data.get('score', 0):.0f}%"
            )
            await NotificationService.create_notification(match_data)
        except Exception as e:
            logger.error(f"❌ Error processing notification: {e}", exc_info=True)


async def start_consumer():
    """Start consuming match.found events."""
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        channel = await connection.channel()

        exchange = await channel.declare_exchange(
            EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True
        )
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        await queue.bind(exchange, ROUTING_KEY)

        await queue.consume(on_message)
        logger.info(f"✅ Notifications consumer started — Listening on '{ROUTING_KEY}'")
    except Exception as e:
        logger.error(f"❌ Failed to start consumer: {e}")
        await asyncio.sleep(5)
        await start_consumer()
