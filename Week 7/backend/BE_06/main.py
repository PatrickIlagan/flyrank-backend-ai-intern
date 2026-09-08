import datetime
import inngest
import inngest.fast_api
from fastapi import FastAPI

app = FastAPI(
    title="Background Jobs API (Inngest)",
    version="1.0",
    description="A resilient background jobs and durable workflow API using FastAPI and Inngest."
)

# 1. Initialize Inngest Client (Development Mode)
inngest_client = inngest.Inngest(
    app_id="report-api",
    is_production=False
)

# 2. Stage 1 Function: say-hello
@inngest_client.create_function(
    fn_id="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello")
)
async def say_hello(ctx: inngest.Context) -> str:
    # Sleep 5 seconds in the background
    await ctx.step.sleep("sleep-5-seconds", datetime.timedelta(seconds=5))
    return "Hello from the background!"

# 3. Mount Inngest Endpoint (/api/inngest)
inngest.fast_api.serve(app, inngest_client, [say_hello])

@app.get("/health", summary="Health Check", tags=["General"])
def health_check():
    return {"status": "ok"}

