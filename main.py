import json
import wave
from starlette import status
from starlette.responses import JSONResponse
from vosk import Model, KaldiRecognizer, SetLogLevel
from fastapi import FastAPI, UploadFile
import aiofiles
app = FastAPI()

# You can set log level to -1 to disable debug messages
SetLogLevel(0)


@app.post("/")
async def recog_file(file: UploadFile):
    try:
        async with aiofiles.open(file.filename, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write
        wf = wave.open(file.filename, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            return {"error": "Audio file must be WAV format mono PCM."}

        model = Model(lang="ru")

        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)
        rec.SetPartialWords(True)

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                return {"result": rec.Result()}
        return {"output": json.loads(rec.FinalResult())['text']}

    except Exception as e:
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = { 'message' : str(e) }
            )
