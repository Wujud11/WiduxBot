import pytest
from bot.engine import WiduxEngine
from types import SimpleNamespace

@pytest.fixture
def fake_bot():
    return SimpleNamespace()

@pytest.fixture
def engine(fake_bot):
    return WiduxEngine(fake_bot)

def test_initial_state(engine):
    assert engine.players == []
    assert engine.teams == {"أزرق": [], "أحمر": []}
    assert engine.mode is None
    assert engine.points != None

@pytest.mark.asyncio
async def test_set_mode(engine):
    class FakeChannel:
        async def send(self, msg):
            pass

    class FakeMessage:
        def __init__(self, content):
            self.content = content
            self.author = SimpleNamespace(name="player1")
            self.channel = FakeChannel()
            self.echo = False

    await engine.handle_message(FakeMessage("وج؟"))
    await engine.handle_message(FakeMessage("تيم"))
    assert engine.mode == "تيم"
