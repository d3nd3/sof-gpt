#!/usr/bin/env python3
"""
Advanced Command Optimization Examples for SOF-GPT

This file demonstrates several approaches to optimize the command system
beyond just removing lambdas.
"""

from sof.commands import commands

# ============================================================================
# OPTION 1: Direct Function References (What we implemented)
# ============================================================================
# This is the simplest and most efficient approach
sof_chat_commands_direct = {
    "test": commands.test,
    "kill": commands.kill,
    "help": commands.help,
    # ... etc
}

# ============================================================================
# OPTION 2: Dynamic Command Resolution
# ============================================================================
def get_command_handler(cmd_name):
    """Dynamically get command handler from commands object"""
    if hasattr(commands, cmd_name):
        return getattr(commands, cmd_name)
    return None

def execute_command_dynamic(cmd_name, player, data):
    """Execute command using dynamic resolution"""
    handler = get_command_handler(cmd_name)
    if handler:
        return handler(player, data)
    else:
        print(f"Unknown command: {cmd_name}")
        return False

# ============================================================================
# OPTION 3: Unified Command Dictionary with Auto-discovery
# ============================================================================
def build_unified_command_dict():
    """Automatically build a command dictionary from the commands object"""
    unified_commands = {}
    
    # Get all public methods from commands object
    for attr_name in dir(commands):
        if not attr_name.startswith('_') and callable(getattr(commands, attr_name)):
            unified_commands[attr_name] = getattr(commands, attr_name)
    
    return unified_commands

# ============================================================================
# OPTION 4: Command Registry with Metadata
# ============================================================================
class CommandRegistry:
    """Advanced command registry with metadata and validation"""
    
    def __init__(self):
        self.commands = {}
        self.aliases = {}
        self.categories = {}
    
    def register(self, name, handler, category="general", aliases=None, description=""):
        """Register a command with metadata"""
        self.commands[name] = {
            'handler': handler,
            'category': category,
            'description': description,
            'aliases': aliases or []
        }
        
        # Register aliases
        if aliases:
            for alias in aliases:
                self.aliases[alias] = name
        
        # Categorize
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(name)
    
    def execute(self, cmd_name, player, data):
        """Execute a command by name or alias"""
        # Check direct command name
        if cmd_name in self.commands:
            return self.commands[cmd_name]['handler'](player, data)
        
        # Check aliases
        if cmd_name in self.aliases:
            actual_cmd = self.aliases[cmd_name]
            return self.commands[actual_cmd]['handler'](player, data)
        
        print(f"Unknown command: {cmd_name}")
        return False
    
    def get_commands_by_category(self, category):
        """Get all commands in a specific category"""
        return self.categories.get(category, [])
    
    def list_all_commands(self):
        """List all registered commands with descriptions"""
        for name, info in self.commands.items():
            print(f"{name}: {info['description']} (Category: {info['category']})")

# ============================================================================
# OPTION 5: Decorator-based Command Registration
# ============================================================================
class CommandDecorator:
    """Decorator-based command registration system"""
    
    def __init__(self):
        self.commands = {}
    
    def command(self, name, category="general", aliases=None, description=""):
        """Decorator to register commands"""
        def decorator(func):
            self.commands[name] = {
                'handler': func,
                'category': category,
                'description': description,
                'aliases': aliases or []
            }
            return func
        return decorator
    
    def execute(self, cmd_name, player, data):
        """Execute a command"""
        if cmd_name in self.commands:
            return self.commands[cmd_name]['handler'](player, data)
        print(f"Unknown command: {cmd_name}")
        return False

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_usage():
    """Demonstrate the different optimization approaches"""
    
    print("=== OPTION 1: Direct Function References ===")
    print("Most efficient, simple to implement")
    print("Commands are directly mapped to functions")
    print()
    
    print("=== OPTION 2: Dynamic Command Resolution ===")
    # This would work like:
    # execute_command_dynamic("help", player, "")
    print("Dynamic lookup, good for runtime flexibility")
    print()
    
    print("=== OPTION 3: Unified Command Dictionary ===")
    unified = build_unified_command_dict()
    print(f"Auto-discovered {len(unified)} commands")
    print("Sample commands:", list(unified.keys())[:5])
    print()
    
    print("=== OPTION 4: Command Registry with Metadata ===")
    registry = CommandRegistry()
    
    # Register commands with metadata
    registry.register("help", commands.help, "system", ["h", "?"], "Show help information")
    registry.register("test", commands.test, "debug", ["t"], "Run test command")
    
    print("Registered commands:")
    registry.list_all_commands()
    print()
    
    print("=== OPTION 5: Decorator-based Registration ===")
    cmd_decorator = CommandDecorator()
    
    @cmd_decorator.command("custom_help", "system", ["h"], "Custom help command")
    def custom_help(player, data):
        print("This is a custom help command!")
        return True
    
    print("Decorator-registered commands:", list(cmd_decorator.commands.keys()))
    print()

def performance_comparison():
    """Compare performance of different approaches"""
    import time
    
    # Test data
    test_commands = ["help", "test", "kill", "quit", "reconnect"]
    
    # Option 1: Direct references (fastest)
    start = time.time()
    for _ in range(10000):
        for cmd in test_commands:
            if cmd in sof_chat_commands_direct:
                pass  # Simulate command lookup
    direct_time = time.time() - start
    
    # Option 2: Dynamic resolution (slower)
    start = time.time()
    for _ in range(10000):
        for cmd in test_commands:
            get_command_handler(cmd)
    dynamic_time = time.time() - start
    
    print(f"Direct references: {direct_time:.4f}s")
    print(f"Dynamic resolution: {dynamic_time:.4f}s")
    print(f"Dynamic is {dynamic_time/direct_time:.1f}x slower")

if __name__ == "__main__":
    example_usage()
    print("=== PERFORMANCE COMPARISON ===")
    performance_comparison()
