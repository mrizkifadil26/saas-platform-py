import asyncio


async def main() -> None:
    worker = create_worker()
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())