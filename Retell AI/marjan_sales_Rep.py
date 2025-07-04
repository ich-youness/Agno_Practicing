import speech_recognition as sr
import pyttsx3
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from agno.tools.reasoning import ReasoningTools

from dotenv import load_dotenv
import os

conversation_flow = {
    "welcome": {
        "script": """
        Hi, this is a quick call from Marjane’s customer team.
        We noticed that your loyalty card is either incomplete or about to expire, and we’d love to offer you a quick and free update to keep your benefits active.
        Do you have a moment?
        """,
        "routes": {
            "interested": "user_interested",
            "not_interested": "user_not_interested"
        }
    },
    "user_interested": {
        "script": """
        Great to hear that. So here's the deal. 
        Your Marjane loyalty card is still active, and we’d like to thank you for your trust.
        If you update your card this week, we’ll preserve all your current points, and you’ll receive a 30 MAD discount voucher, valid immediately.
        Plus, you’ll keep access to all exclusive promotions and private Marjane events.
        Would you like to update your card now while this offer is available?
        """,
        "routes": {
            "wants_offer": "user_wants_offer",
            "changed_mind": "user_changed_mind",
            "not_interested": "user_not_interested"
        }
    },
    "user_not_interested": {
        "script": """
        Totally understand. If you change your mind or have any questions later, feel free to reach out.
        Thanks for your time and have a wonderful day!  
        """,
        "routes": {
            "end": "end"
        }
    },
    "user_wants_offer": {
        "script": """
       Thank you for your interest.
        You can complete your card update online, It only takes a couple of minutes.
        Would you prefer to do it yourself, or would you like me to connect you with someone who can assist you?
        """,
        "routes": {
            "proceeds_independently": "using",
            "needs_assistance": "getting"
        }
    },
    "user_changed_mind": {
        "script": """
        That’s alright. If you change your mind later, the offer is still valid for a few more days.
        Thanks for your time and happy travels!
        """,
        "routes": {
            "end": "end"
        }
    },
    "using": {
        "script": """
        That sounds perfect. Go ahead and visit our portal to update your loyalty card.
        Once the update is complete, your current points will be retained and you'll receive your 30 MAD welcome discount.
        If you run into any issues or need help, just let me know. I'm here for you.
        """,
        "routes": {
            "completed": "getting",
            "needs_help": "getting"
        }
    },
    "getting": {
        "script": """
        You’re very welcome.
        Thank you for choosing Marjane. We truly appreciate your loyalty.
        If you have any further questions, feel free to reach out to us anytime.
        Have a wonderful day and we look forward to seeing you again soon.
        Goodbye.
        """,
        "routes": {
            "end": "end"
        }
    },
    "end": {
        "script": "Goodbye! 👋",
        "routes": {}
    }
}

load_dotenv()
id = os.getenv("id")
api_key = os.getenv("api_key")

# Voice setup
engine = pyttsx3.init()
recognizer = sr.Recognizer()
mic = sr.Microphone()

# Agent setup
intent_agent = Agent(
    name="Intent Router",
    model=Gemini(id=id, api_key=api_key),
    tools=[ReasoningTools()],
    instructions="""
    You are an intent routing assistant. Based on a customer's spoken input and current script context, classify their intent.
    Only reply with the route keyword that best matches: e.g., 'interested', 'not_interested', 'wants_offer', etc.
    If unsure, guess the closest.
    """
)

# Start conversation
current_state = "welcome"

while current_state != "end":
    state = conversation_flow[current_state]
    script = state["script"]
    
    print(f"\n🤖: {script}")
    engine.say(script)
    engine.runAndWait()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🟢 Listening...")
        audio = recognizer.listen(source)

    try:
        user_input = recognizer.recognize_google(audio, language="en-US")
        print(f"👤 You said: {user_input}")

        # Detect intent (route)
        prompt = f"""
        Current Script: {script}
        User Said: {user_input}
        Possible Routes: {', '.join(state['routes'].keys())}
        What is the correct route keyword?
        """
        # route = intent_agent.run(prompt).strip().lower()
        
        response = intent_agent.run(prompt)
        print("🧠 Raw intent response:", response.content)

        route = response.content.strip().lower()
        print(f"🔁 Route detected: {route}")


        # print(f"🔁 Route detected: {route}")

        # Move to next state
        if route in state["routes"]:
            current_state = state["routes"][route]
        else:
            print("❓ Unrecognized route. Repeating question.")
            engine.say("I didn’t quite get that. Could you repeat please?")
            engine.runAndWait()

    except sr.UnknownValueError:
        print("❌ Speech not understood.")
        engine.say("Sorry, I didn’t catch that. Could you say it again?")
        engine.runAndWait()
    except Exception as e:
        print(f"⚠️ Error: {e}")
        engine.say("An error occurred.")
        engine.runAndWait()

# Final goodbye
print("📞 Call Ended.")