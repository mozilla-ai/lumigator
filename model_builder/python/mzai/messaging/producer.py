import asyncio

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from loguru import logger
from pydantic import BaseModel


class MessageProducer:
    def __init__(
        self,
        broker_url: str,
        exchange_name: str,
        routing_key: str,
        exchange_type: ExchangeType = ExchangeType.DIRECT,
        delivery_mode: DeliveryMode = DeliveryMode.PERSISTENT,
    ):
        self.broker_url = broker_url
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.routing_key = routing_key
        self.delivery_mode = delivery_mode

    async def publish_async(self, body: BaseModel) -> None:
        connection = await connect_robust(url=self.broker_url)
        async with connection:
            channel = await connection.channel()

            exchange = await channel.declare_exchange(self.exchange_name, type=self.exchange_type)

            body_json = body.model_dump_json()
            logger.info(
                f"Publishing message: "
                f"Exchange = '{self.exchange_name}', "
                f"Routing key = '{self.routing_key}', "
                f"Body = {body_json}"
            )
            message = Message(body_json.encode(), delivery_mode=self.delivery_mode)
            await exchange.publish(message, routing_key=self.routing_key)

    def publish_sync(self, body: BaseModel) -> None:
        asyncio.run(self.publish_async(body))
