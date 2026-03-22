import os
import asyncio
from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import deepgram, silero
from livekit.plugins.groq import STT as GroqSTT
from groq import Groq
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "back", "rag", "chroma_db")
MODEL_LOCAL_PATH = os.path.join(CURRENT_DIR, "all-MiniLM-L6-v2")

load_dotenv()

for key in list(os.environ.keys()):
    if "LIVEKIT" in key:
        del os.environ[key]

os.environ["LIVEKIT_URL"] = "http://127.0.0.1:7880"
os.environ["LIVEKIT_API_KEY"] = "devkey"
os.environ["LIVEKIT_API_SECRET"] = "devsecret"
os.environ["DEEPGRAM_API_KEY"] = "DEEPGRAM_API_KEYyyy"
os.environ["GROQ_API_KEY"] = "GROQ_API_KEYyyy"

class ArmenianBankAgent(Agent):
    def __init__(self, vector_db):
        instructions = "Դուք հայկական բանկերի օգնականն եք: Պատասխանեք հայերեն լեզվով."
        self._ollama = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.db = vector_db
        self.system_prompt = instructions

        deepgram_key = os.getenv("DEEPGRAM_API_KEY")
        if not deepgram_key:
            raise ValueError("Не задан DEEPGRAM_API_KEY в окружении")
        tts_model = deepgram.TTS(model="aura-asteria-en", api_key=deepgram_key)

        super().__init__(
            instructions=instructions,
            vad=silero.VAD.load(),
            stt=GroqSTT(model="whisper-large-v3", language="hy"),
            tts=tts_model,
        )

    async def on_enter(self):
        await self.session.say("Բարև, ես ձեր բանկային օգնականն եմ:", allow_interruptions=False)

    async def on_user_turn_completed(self, turn_ctx, new_message):
        user_text = getattr(new_message, 'content', str(new_message))
        if isinstance(user_text, list):
            user_text = " ".join([str(t) for t in user_text])
        if not user_text.strip():
            return

        print(f"🎤 You: {user_text}")

        try:
            docs = self.db.similarity_search(user_text, k=3)
            context = "\n\n".join([d.page_content for d in docs])
        except Exception as e:
            print(f"❌ Ошибка RAG: {e}")
            context = ""

        if not context.strip():
            answer = "Ներողություն, տվյալներ չեն գտնվել։"
            print(f"🤖 Agent: {answer}")
            await self.session.say(answer)
            return

        try:
            response = self._ollama.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"{self.system_prompt}\nՕգտագործիր միայն այս կոնտեքստը՝ պատասխանելու համար:\n{context}"},
                    {"role": "user", "content": user_text}
                ],
                temperature=0.0,
                max_tokens=500
            )
            answer = response.choices[0].message.content
            print(f"🤖 Agent: {answer}")
            await self.session.say(answer)
        except Exception as e:
            print(f"❌ LLM error: {e}")
            await self.session.say("Ներողություն, սխալ տեղի ունեցավ:")

async def entrypoint(ctx: JobContext):
    print(f"🎯 Connecting to room: {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    embeddings = HuggingFaceEmbeddings(model_name=MODEL_LOCAL_PATH, model_kwargs={"device": "cpu"})
    db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

    session = AgentSession(vad=silero.VAD.load())
    await session.start(agent=ArmenianBankAgent(vector_db=db), room=ctx.room)
    print("✅ Agent is running!")
    await asyncio.sleep(999999)

def generate_dev_token():
    from livekit import api
    token = api.AccessToken(os.environ["LIVEKIT_API_KEY"], os.environ["LIVEKIT_API_SECRET"]) \
        .with_identity("bank-customer-user") \
        .with_grants(api.VideoGrants(room_join=True, room="dev-room"))
    return token.to_jwt()

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Starting LOCAL LiveKit Agent")
    print(f"📡 Connecting to: ws://localhost:7880")
    print("=" * 50)
    print("\n" + "="*60)
    print("🔑 ТОКЕН ДЛЯ PLAYGROUND (Скопируй полностью):")
    print(generate_dev_token())
    print("="*60 + "\n")

    options = WorkerOptions(
        entrypoint_fnc=entrypoint,
        ws_url=os.environ["LIVEKIT_URL"],
        api_key=os.environ["LIVEKIT_API_KEY"],
        api_secret=os.environ["LIVEKIT_API_SECRET"],
    )
    cli.run_app(options)