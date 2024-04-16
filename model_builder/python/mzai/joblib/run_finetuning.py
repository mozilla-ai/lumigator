import random

from mzai.messaging.producer import MessageProducer
from mzai.schemas.finetuning import FinetuningEvent, FinetuningMessage


def main():
    producer = MessageProducer()

    chance = random.randint(0, 10)
    if chance >= 5:
        message = FinetuningMessage(
            details="Job finished successfully!",
            event=FinetuningEvent.JOB_SUCCEEDED,
        )
    else:
        message = FinetuningMessage(
            details="Job failed horribly!",
            event=FinetuningEvent.JOB_FAILED,
        )

    producer.publish_sync(message)


if __name__ == "__main__":
    main()
