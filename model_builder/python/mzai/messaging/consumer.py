import asyncio
from abc import ABC, abstractmethod

from aio_pika import ExchangeType, connect_robust
from aio_pika.abc import AbstractIncomingMessage
from loguru import logger


class MessageConsumer(ABC):
    def __init__(
        self,
        broker_url: str,
        exchange_name: str,
        exchange_type: ExchangeType = ExchangeType.DIRECT,
        queue_name: str | None = None,
        routing_keys: list[str] | None = None,
        durable: bool = True,
    ):
        self.broker_url = broker_url
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.queue_name = queue_name
        self.routing_keys = routing_keys or []
        self.durable = durable

    @abstractmethod
    async def handle_message(self, body: bytes) -> None:
        pass

    async def consume(self) -> None:
        connection = await connect_robust(url=self.broker_url)
        async with connection:
            channel = await connection.channel()

            # Initialize exchange and queue (idempotent operations)
            exchange = await channel.declare_exchange(self.exchange_name, type=self.exchange_type)
            queue = await channel.declare_queue(self.queue_name, durable=self.durable)
            for key in self.routing_keys:
                await queue.bind(exchange, routing_key=key)

            # Wrap handler with logging and message acknoledgement
            # If the handler fails within the message.process() block,
            # it is returned to the queue for another worker (i.e. it is not acknowledged)
            async def on_message_callback(message: AbstractIncomingMessage):
                logger.info(f"Received message: {message}")
                async with message.process():
                    await self.handle_message(message.body)

            await queue.consume(on_message_callback)

            logger.info("Waiting for messages async...")
            await asyncio.Future()
