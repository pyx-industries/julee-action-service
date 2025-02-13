# Protocol Developer's Guide - The Good Boy Edition 🦮

## HELLO FRIEND! 

Want to add a new way for Julee to fetch or send things? That's what protocols do! Just like how you have different ways to get a ball (fetch it, have someone throw it, find it under the couch), Julee needs different ways to get and send information.

## The Three Important Things

Just like learning "sit", "stay", and "fetch", there are three main things your protocol needs to do:

1. **CONNECT** - Make sure we can reach the thing we want to talk to
2. **FETCH/SEND** - Actually get or send the stuff
3. **TELL US IF IT WORKED** - Let us know if everything was okay or if something went wrong

## Let's Make a Protocol! 

Here's a simple example, like learning a new trick:

```python
from action_service.pdk import ProtocolHandler
from action_service.domain import Action, ActionResult

class MyNewProtocol(ProtocolHandler):
    """This is my new protocol that does something cool!"""
    
    def execute(self, action: Action) -> ActionResult:
        try:
            # 1. CONNECT
            connection = self.connect_to_service(action.config)
            
            # 2. FETCH/SEND
            response = connection.do_the_thing(action.config['what_to_do'])
            
            # 3. TELL US IF IT WORKED
            return ActionResult(
                action_id=action.id,
                success=True,
                result=response
            )
            
        except Exception as e:
            # Uh oh, something went wrong! Tell them what happened
            return ActionResult(
                action_id=action.id,
                success=False,
                error=str(e)
            )
```

## Testing Your Protocol

Just like practicing a new trick, we need to test our protocol:

```python
def test_my_new_protocol():
    # Set up the test
    action = Action(
        id="test-1",
        name="Test Action",
        config={
            "what_to_do": "fetch_the_ball"
        }
    )
    
    # Try it out!
    protocol = MyNewProtocol()
    result = protocol.execute(action)
    
    # Did it work?
    assert result.success == True
```

## Example: Fetching from a Website

Here's a real example, like learning to fetch a specific toy:

```python
class WebsiteFetcher(ProtocolHandler):
    """Gets content from websites!"""
    
    def execute(self, action: Action) -> ActionResult:
        try:
            # 1. CONNECT - Get ready to fetch from website
            import httpx
            client = httpx.Client()
            
            # 2. FETCH - Get the website content
            response = client.get(action.config['url'])
            
            # 3. TELL US - Did we get it?
            return ActionResult(
                action_id=action.id,
                success=True,
                result=response.text
            )
            
        except Exception as e:
            # Something went wrong!
            return ActionResult(
                action_id=action.id,
                success=False,
                error=f"Couldn't fetch website: {str(e)}"
            )
```

## Using Your Protocol

Once you've made your protocol, using it is as simple as:

```python
# Create an action
action = Action(
    id="fetch-1",
    name="Get Website",
    config={
        "url": "https://example.com"
    }
)

# Use the protocol
fetcher = WebsiteFetcher()
result = fetcher.execute(action)

# Did we get it?
if result.success:
    print("Good boy! We got:", result.result)
else:
    print("Uh oh, something went wrong:", result.error)
```

## Remember!

- Keep it simple! Each protocol should do one thing well
- Always tell us if something goes wrong
- Test your protocol to make sure it works
- Have fun! 🦴

Need help? That's okay! Just like learning new tricks, sometimes we need guidance. Ask questions and we'll help you get it right! 🐾
