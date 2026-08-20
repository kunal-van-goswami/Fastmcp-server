from fastmcp import FastMCP
import random
import json

#create the fastmcp server instance
mcp = FastMCP("Simple Calculator Server")

#tool:Add two numbers
@mcp.tool
def add(a:int, b:int) -> int:
    """Add two numbers
    Args:
        a (int): The first number
        b (int): The second number
    Returns:
        int: The sum of the two numbers
    """
    return a + b
  
#tool: Generate a randonuer
@mcp.tool
def random_number(min:int =1,max:int =100)->int:
    """Generate a random number between min and maxuv 
    Args:
        min (int): The minimum number
        max (int): The maximum number
    Returns:
        int: A random number between min and max
    """
    return random.randint(min, max)
  
#Resource:Server infortion
@mcp.resource("info://server")
def server_info()->str:
  """ Get infortion about this server"""
  info = {
    "name": "Simple Calculator Server",
    "version": "1.0",
    "description": "A simple calculator server that can add two numbers and generate random numbers",
    "tools": ["add", "random_number"],
    "author":"your Name"
  }
  return json.dumps(info,indent=4)

#start the server
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
    