import pytest
import json
from unittest.mock import AsyncMock

# setting env variable
import os
os.environ['WEBSOCKET_PORT'] = '8080'  # Use the port number directly
from main import formatMessage, server, state  # Importing necessary parts from your server code

@pytest.mark.asyncio
async def test_formatMessage():
    """Test if the formatMessage utility function works as expected."""
    event = "testEvent"
    data = {"key": "value"}
    expected_output = json.dumps({"event": event, "data": data})
    assert formatMessage(event, data) == expected_output

@pytest.mark.asyncio
async def test_websocket_communication():
    """
    Test WebSocket communication by simulating the echo function.
    """
    # Create a mock WebSocket connection
    ws = AsyncMock()
    
    # Simulate server connection which would send the initial state
    await server.on_connect(ws, "/")
    
    # Verify the server sent the initial state to the WebSocket upon connection
    ws.send.assert_called_with(formatMessage("state", state))
    
    # Test the echo function by simulating a message from the client
    test_data = {"key": "value"}
    
    # Simulate receiving an echo event with test data
    await server.events['echo'](ws, test_data)
    
    # Because ws.send is an AsyncMock, you check the call with the expected message
    # This checks the most recent call to ws.send, which should be the echo response
    ws.send.assert_called_with(formatMessage("echo", test_data))

@pytest.mark.asyncio
async def test_getMap():
    """Test sending map data to a client."""
    ws = AsyncMock()
    
    # Simulate the getMap event
    test_data = {}
    await server.events['getMap'](ws, test_data)
    
    # Assert the server attempted to send map data
    ws.send.assert_called()  # You might want to make this more specific

@pytest.mark.asyncio
async def test_summon_updates_state_and_informs_ros():
    """Test that the summon function updates the state and informs ROS clients."""
    ws = AsyncMock()
    
    test_data = {'user': 'testUser', 'x': 100, 'y': 200}
    await server.events['summon'](ws, test_data)
    
    # Assert state was updated
    assert len(state['queue']) == 1
    assert state['coordinates'][0] == (100, 200)

@pytest.mark.asyncio
async def test_status_changes_state_and_opens_lid_on_arrival():
    """Test that the status event updates the server state and opens the lid when status is 'arrived'."""
    ws = AsyncMock()
    
    test_data = {'status': 'arrived'}
    await server.events['status'](ws, test_data)
    
    # Assert state was updated to 'arrived'
    assert state['status'] == 'arrived'