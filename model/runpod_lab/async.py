import runpod
import asyncio
import random
import json
import sys

# 비동기 데이터 로더
async def fetch_weather_data(city, delay):
    await asyncio.sleep(delay)
    temperature = random.uniform(-10, 40)
    humidity = random.uniform(0, 100)

    return {
        "city" : city,
        "temperature" : round(temperature, 1),
        "humidity" : round(humidity, 1)
    }


# 비동기 생성기
async def async_generator_handler(job):
    job_input = job['input']
    cities = job_input.get('cities', [
        'New York', 'London', 'Tokyo', 'Sydney', 'Moscow'
    ])
    update_interval = job_input.get('update_interval', 2)
    duration = job_input.get('duration', 10)

    print(f"Weather Data Stream | Starting job {job['id']}")
    print(f"Monitoring cities: {', '.join(cities)}")

    start_time = asyncio.get_event_loop().time()

    while asyncio.get_event_loop().time() - start_time < duration:
        tasks = [fetch_weather_data(city, random.uniform(0.5, 2)) for city in cities]
        for completed_task in asyncio.as_completed(tasks):
            weather_data = await completed_task
            yield {
                "timestamp": round(asyncio.get_event_loop().time() - start_time, 2),
                "data": weather_data
            }
        
        await asyncio.sleep(update_interval)

    yield {"status": "completed", "message": "Weather monitoring completed"}

async def run_test(job):
    async for item in async_generator_handler(job):
        print(json.dumps(item))

if __name__ == "__main__":
    if "--test_input" in sys.argv:
        test_input_index = sys.argv.index("--test_input")
        if test_input_index + 1 < len(sys.argv):
            test_input_json = sys.argv[test_input_index + 1]
            try:
                job = json.loads(test_input_json)
                asyncio.run(run_test(job))
            except json.JSONDecodeError:
                print("Error: Invalid JSON in test_input")
        else:
            print("Error: --test_input requires a JSON string argument")
    else:
        runpod.serverless.start({
            "handler": async_generator_handler,
            "return_aggregate_stream": True
        })