
from dotenv import load_dotenv
from livekit.agents import Agent, AgentServer, AgentSession, cli
from livekit.plugins import deepgram, inworld

load_dotenv()

server = AgentServer()


class JabariAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "You are Jabari, a professional and supportive "
                "technical interviewer for Coachify. Ask one "
                "question at a time, listen to the candidate's "
                "answer, and remain focused on the interview."
            )
        )

    async def on_enter(self):
        await self.session.say(
            "Welcome to Coachify. I'm Jabari, your interviewer. "
            "Let's begin.",
            allow_interruptions=False,
        )


@server.rtc_session(agent_name="jabari")
async def entrypoint(ctx):
    session = AgentSession(
        stt=deepgram.STTv2(
            model="flux-general-en",
            eager_eot_threshold=0.4,
        ),
        tts=inworld.TTS(
            model="inworld-tts-2",
            voice="sage-mocha-0150__design-voice-613b0a37",
        ),
    )

    await session.start(
        agent=JabariAgent(),
        room=ctx.room,
    )


if __name__ == "__main__":
    cli.run_app(server)
