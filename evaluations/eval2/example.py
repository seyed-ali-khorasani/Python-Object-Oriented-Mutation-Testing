import time
import asyncio,os
from openai import OpenAI

class WhisperModel:
    def __init__(self, model, audio, text_gather_callback):
        self.model = model
        self.audio = audio
        self.text_gather_callback = text_gather_callback

    async def transcribe(self,text):
        start = time.time()
        segments, _ = self.model.transcribe(
        self.audio,
        language="en",
        initial_prompt=text
        )
        end = time.time()
        
        gen_text = ""
        for segment in segments:
            
            gen_text += segment.text
        end = time.time()
        
        
        await self.text_gather_callback(gen_text) 
    async def transcribeapi(self):
        os.environ["OPENAI_API_KEY"] = "sample"
        client = OpenAI()

        audio= open(self.audio, "rb")
        start = time.time()
        transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio , 
                language="fa"
            )
        end = time.time()
        print(end-start)
        print(transcription.text)
        await self.text_gather_callback(transcription.text)
         
        
        
