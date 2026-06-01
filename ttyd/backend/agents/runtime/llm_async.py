import aioboto3


async def generate(ctx):
    async with aioboto3.Session().client("bedrock-runtime") as client:
        response = await client.invoke_model(...)
        return response
