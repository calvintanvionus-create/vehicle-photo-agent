\# Vehicle Photo Agent – Requirements



\## What I want to build

A Discord agent: when someone posts a photo of a car or motorcycle in a specific channel, it identifies whether it's a car or motorcycle, the brand, model, approximate year and body type, replies in the channel, and logs it to Excel.



\## What users do

\- Post a vehicle photo in the channel (optionally with a short message)

\- Wait for the agent's reply



\## What to record

\- Time, uploader, car/motorcycle, brand, model, estimated year, body type, confidence, photo location

\- How many vehicles were identified today (total, cars, motorcycles)



\## What I already know

\- Python, `claude -p` to look at photos, Discord Gateway (bot) mode

\- Records saved to an Excel file that keeps growing (append, not overwrite)



\## What I'm not sure about

\- What to do when the photo isn't a vehicle

\- What happens when many people post at once

