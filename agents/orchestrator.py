import asyncio
from agents.medical import medical_triage
from agents.logistics import plan_route
from agents.reporting import generate_report
from agents.vision import analyze_disaster_image


async def orchestrate(symptoms, image_path=None):
    tasks = [
        medical_triage(symptoms),
        plan_route()
    ]

    if image_path:
        tasks.append(analyze_disaster_image(image_path))
    else:
        async def dummy(): return None
        tasks.append(dummy())

    results = await asyncio.gather(*tasks)
    
    medical_result = results[0]
    logistics_result = results[1]
    vision_result = results[2]

    report_data = {
        "medical": medical_result,
        "logistics": logistics_result,
        "vision": vision_result
    }

    final_report = await generate_report(report_data)

    return {
        "medical": medical_result,
        "logistics": logistics_result,
        "vision": vision_result,
        "report": final_report
    }