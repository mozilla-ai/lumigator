import asyncio

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from loguru import logger
from pydantic import BaseModel


class MessageProducer:
    """Message producer bound to a single RabbitMQ broker/exchange.

    Individual routing settings per message can be specified when publishing
    rather than on instantiation of this class,
    allowing the producer to send messages to different queues that are bound to the exchange.
    """

    def __init__(
        self,
        broker_url: str,
        exchange_name: str,
        exchange_type: ExchangeType = ExchangeType.DIRECT,
    ):
        self.broker_url = broker_url
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type

    async def publish_async(
        self,
        body: BaseModel,
        routing_key: str,
        delivery_mode: DeliveryMode = DeliveryMode.PERSISTENT,
    ) -> None:
        connection = await connect_robust(url=self.broker_url)
        async with connection:
            channel = await connection.channel()

            exchange = await channel.declare_exchange(self.exchange_name, type=self.exchange_type)

            body_json = body.model_dump_json()
            logger.info(
                f"Publishing message: "
                f"Exchange = '{self.exchange_name}', "
                f"Routing key = '{routing_key}', "
                f"Body = {body_json}"
            )
            message = Message(body_json.encode(), delivery_mode=delivery_mode)
            await exchange.publish(message, routing_key=routing_key)

    def publish_sync(
        self,
        body: BaseModel,
        routing_key: str,
        delivery_mode: DeliveryMode = DeliveryMode.PERSISTENT,
    ) -> None:
        asyncio.run(self.publish_async(body, routing_key, delivery_mode))
